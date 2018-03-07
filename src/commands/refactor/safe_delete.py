import sublime, sublime_plugin
import os, shutil, traceback, json
from ...libs import util
from ...libs import window_view_manager
from ...libs import FlowCLI
from .refactor_preview import RefactorPreview

class JavascriptEnhancementsRefactorSafeDeleteCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    window = view.window()
    file_name = view.file_name()
    settings = util.get_project_settings()
    javascript_files = []
    preview_view = None

    if not file_name:
      sublime.error_message("Cannot delete this file. File name is empty.")
      return 

    if settings:
      for root, dirs, files in os.walk(settings["project_dir_name"]):
        if os.path.sep + "node_modules" in root:
          continue
        for file in files:
          if file.endswith(".js"):
            javascript_files.append(os.path.join(root, file))

      if not args.get("preview"):

        if not sublime.ok_cancel_dialog("Are you sure you want to delete this file: \""+file_name+"\"?", "Yes"):
          return

        try:
          os.remove(file_name)
        except Exception as e:
          print(traceback.format_exc())
          sublime.error_message("Cannot delete the file. Some problems occured.")
          return

      else:
        preview_view = RefactorPreview("Refactor - Safe Delete Preview")
        preview_view.append_text("Refactor - Safe Delete Preview\n\nList of files that uses it\n\n")

        if javascript_files:

          imports = {}
          flow_cli = FlowCLI(view)
          result = flow_cli.get_imports(files=javascript_files)
          if result [0]:
            imports = result[1]

          for k, v in imports.items():
            if v["requirements"]:
              for req in v["requirements"]:
                if file_name == ( req["import"] if os.path.isabs(req["import"]) else os.path.abspath(os.path.dirname(k) + os.path.sep + req["import"]) ):
                  with open(k, "r+", encoding="utf-8") as file:
                    content = file.read()
                    splitted_content = content.splitlines()
                    preview_content = k + ":\n\n"
                    line = int(req["line"]) - 1
                    range_start = max(0, line - 2)
                    range_end = min(line + 2, len(splitted_content) - 1)
                    while range_start <= range_end:
                      line_number = str(range_start + 1)
                      space_before_line_number = " " * ( 5 - len(line_number) )
                      preview_content += space_before_line_number + line_number + (": " if line == range_start else "  ") + splitted_content[range_start] + "\n"
                      range_start += 1
                    preview_content += "\n"
                    preview_view.append_text(preview_content)

      if not args.get("preview"):
        RefactorPreview.close("Refactor - Safe Delete Preview")
        window_view_manager.close(view.id())
        # added view.set_scratch(True) and sublime.set_timeout_async in order to not crash Sublime Text 3
        view.set_scratch(True)
        sublime.set_timeout_async(lambda: view.close())

    else:
      sublime.error_message("Error: can't get project settings")
      
  def is_enabled(self, **args) :
    view = self.view
    return util.selection_in_js_scope(view)

  def is_visible(self, **args) :
    view = self.view
    if not view.file_name():
      return False
    settings = util.get_project_settings()
    if not settings or not util.selection_in_js_scope(view):
      return False
    return True
      