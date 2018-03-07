import sublime, sublime_plugin
import os, shutil, traceback, json
from ...libs import util
from ...libs import window_view_manager
from ...libs import FlowCLI
from .refactor_preview import RefactorPreview

class JavascriptEnhancementsRefactorSafeCopyCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    window = view.window()
    file_name = view.file_name()
    inputs = args.get("inputs")
    new_path = os.path.normpath(inputs["new_path"].strip())
    settings = util.get_project_settings()
    preview_view = None

    if view.is_dirty():
      sublime.error_message("Cannot copy this file. There are unsaved modifications to the buffer. Save the file before use this.")
      return 

    if not file_name:
      sublime.error_message("Cannot copy this file. File name is empty.")
      return 

    if not new_path or new_path.endswith(os.path.sep) or os.path.isdir(new_path):
      sublime.error_message("The File path is empty or incorrect.")
      return 

    if new_path == file_name:
      sublime.error_message("The file path is the same as before.")
      return

    if settings:

      if not args.get("preview"):

        if os.path.isfile(new_path):
          if not sublime.ok_cancel_dialog(new_path + " already exists.", "Copy anyway"):
            return

        if not os.path.isdir(os.path.dirname(new_path)):
          try:
            os.makedirs(os.path.dirname(new_path))
          except FileNotFoundError as e:
            print(traceback.format_exc())
            sublime.error_message("Cannot create the path. On Windows could be caused by the '[WinError 206] The filename or extension is too long' error.")
            return
          except Exception as e:
            print(traceback.format_exc())
            sublime.error_message("Cannot create the path. The filename, directory name, or volume label syntax could be incorrect.")
            return

      else:
        preview_view = RefactorPreview("Refactor - Safe Copy Preview")
        preview_view.append_text("Refactor - Safe Copy Preview\n\nList of files that will be updated\n\n")

      imports = self.get_imports(settings, [file_name])

      if imports[file_name]["requirements"]:
        content = ""

        with open(file_name, "r", encoding="utf-8") as file:
          content = file.read()
          preview_content = ""
          delta = 0
          lines_updated = []

          requirements_sorted = sorted(imports[file_name]["requirements"], key=lambda req: int(req["loc"]["start"]["offset"]))

          for req in requirements_sorted:
            start_offset = int(req["loc"]["start"]["offset"]) + 1 + delta if sublime.platform() != "windows" else view.text_point(int(req["line"]) - 1, int(req["start"])) + delta
            end_offset = int(req["loc"]["end"]["offset"]) - 1 + delta if sublime.platform() != "windows" else view.text_point(int(req["endline"]) - 1, int(req["end"]) - 1) + delta

            req_new_path = req["import"] if os.path.isabs(req["import"]) else os.path.abspath(os.path.dirname(file_name) + os.path.sep + req["import"])

            if os.path.dirname(new_path) == os.path.dirname(req_new_path):
              rel_new_path = "./" + os.path.basename(req_new_path)
            else:
              rel_new_path = os.path.relpath(req_new_path, start=os.path.dirname(new_path))

              if sublime.platform() == "windows":
                rel_new_path = util.convert_path_to_unix(rel_new_path)

              if not rel_new_path.startswith(".."):
                rel_new_path = "./" + rel_new_path
              
            delta += len(rel_new_path) - len(content[start_offset:end_offset])
            content = content[:start_offset] + rel_new_path + content[end_offset:]

            if args.get("preview"):
              line = int(req["line"]) - 1
              lines_updated.append(line)
              
          if args.get("preview"):
            splitted_content = content.splitlines()

            preview_content = "- Copy From:\n" + file_name + "\n\n"
            preview_content += "- To:\n" + new_path + "\n\n"

            range_start_before = -1
            is_first_range_start = True

            for range_start in lines_updated:
              line_number = str(range_start + 1)
              space_before_line_number = " " * ( 5 - len(line_number) )
              if range_start - 1 != range_start_before and not is_first_range_start:
                space_before_line_number = space_before_line_number + ("." * len(line_number) ) + "\n" + space_before_line_number
              is_first_range_start = False
              preview_content += space_before_line_number + line_number + (": " if range_start in lines_updated else "  ") + splitted_content[range_start] + "\n"
              range_start_before = range_start
              range_start += 1

            preview_content += "\n\n"
            preview_view.append_text(preview_content)

        if not args.get("preview"):
          with open(new_path, "w+", encoding="utf-8") as file:
            file.seek(0)
            file.write(content)
            file.truncate()

      if not args.get("preview"):
        RefactorPreview.close("Refactor - Safe Copy Preview")
        window_view_manager.close(view.id())

    else:
      sublime.error_message("Error: can't get project settings.")

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
      