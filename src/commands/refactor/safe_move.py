import sublime, sublime_plugin
import os, shutil, traceback, json
from ...libs import util
from ...libs import window_view_manager
from ...libs import NodeJS
from ...libs import flow
from .refactor_preview import RefactorPreview

class JavascriptEnhancementsRefactorSafeMoveCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    window = view.window()
    file_name = view.file_name()
    inputs = args.get("inputs")
    view_id_caller = args.get("view_id_caller") if "view_id_caller" in args else None
    new_path = os.path.normpath(inputs["new_path"].strip())
    settings = util.get_project_settings()
    javascript_files = [file_name]
    preview_view = None

    if view.is_dirty():
      sublime.error_message("Cannot move this file. There are unsaved modifications to the buffer. Save the file before use this.")
      return 

    if not file_name:
      sublime.error_message("Cannot move this file. File name is empty.")
      return 

    if not new_path or new_path.endswith(os.path.sep) or os.path.isdir(new_path):
      sublime.error_message("The File path is empty or incorrect.")
      return 

    if new_path == file_name:
      sublime.error_message("The file path is the same as before.")
      return

    if settings:
      for root, dirs, files in os.walk(settings["project_dir_name"]):
        if os.path.sep + "node_modules" in root:
          continue
        for file in files:
          if file.endswith(".js"):
            javascript_files.append(os.path.join(root, file))

      if not args.get("preview"):

        if os.path.isfile(new_path):
          if not sublime.ok_cancel_dialog(new_path + " already exists.", "Move anyway"):
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
        preview_view = RefactorPreview("Refactor - Safe Move Preview")
        preview_view.append_text("Refactor - Safe Move Preview\n\nList of files that will be updated\n\n")

      if javascript_files:
        imports = self.get_imports(settings, javascript_files)
        for k, v in imports.items():

          is_same_file = k == file_name

          if v["requirements"]:

            if is_same_file:
              with open(k, "r+", encoding="utf-8") as file:
                content = file.read()
                preview_content = ""
                delta = 0
                lines_updated = []

                requirements_sorted = sorted(v["requirements"], key=lambda req: int(req["loc"]["start"]["offset"]))

                for req in requirements_sorted:
                  start_offset = int(req["loc"]["start"]["offset"]) + 1 + delta if sublime.platform() != "windows" else view.text_point(int(req["line"]) - 1, int(req["start"])) + delta
                  end_offset = int(req["loc"]["end"]["offset"]) - 1 + delta if sublime.platform() != "windows" else view.text_point(int(req["endline"]) - 1, int(req["end"]) - 1) + delta

                  req_new_path = req["import"] if os.path.isabs(req["import"]) else os.path.abspath(os.path.dirname(k) + os.path.sep + req["import"])

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

                  preview_content = "- Move From:\n" + file_name + "\n\n"
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
                else:
                  file.seek(0)
                  file.write(content)
                  file.truncate()

            else:
              for req in v["requirements"]:
                if file_name == ( req["import"] if os.path.isabs(req["import"]) else os.path.abspath(os.path.dirname(k) + os.path.sep + req["import"]) ):

                  with open(k, "r+", encoding="utf-8") as file:
                    content = file.read()
                    start_offset = int(req["loc"]["start"]["offset"]) + 1 if sublime.platform() != "windows" else view.text_point(int(req["line"]) - 1, int(req["start"]))
                    end_offset = int(req["loc"]["end"]["offset"]) - 1 if sublime.platform() != "windows" else view.text_point(int(req["endline"]) - 1, int(req["end"]) - 1)

                    if os.path.dirname(k) == os.path.dirname(new_path):
                      rel_new_path = "./" + os.path.basename(new_path)
                    else:
                      rel_new_path = os.path.relpath(new_path, start=os.path.dirname(k))

                      if sublime.platform() == "windows":
                        rel_new_path = util.convert_path_to_unix(rel_new_path)

                      if not rel_new_path.startswith(".."):
                        rel_new_path = "./" + rel_new_path

                    content = content[:start_offset] + rel_new_path + content[end_offset:]

                    if args.get("preview"):
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
                    else:
                      file.seek(0)
                      file.write(content)
                      file.truncate()

        if not args.get("preview"):
          shutil.move(file_name, new_path)
          window.focus_group(0)
          new_view = window.open_file(new_path)
          window.focus_group(1)


      if not args.get("preview"):
        RefactorPreview.close("Refactor - Safe Move Preview")
        window_view_manager.close(view.id())
        # added view.set_scratch(True) and sublime.set_timeout_async in order to not crash Sublime Text 3
        view.set_scratch(True)
        sublime.set_timeout_async(lambda: view.close())

    else:
      sublime.error_message("Error: can't get project settings")
      
  def get_imports(self, settings, javascript_files):

    view = self.view

    flow_cli = "flow"
    is_from_bin = True
    chdir = settings["project_dir_name"]
    use_node = True
    bin_path = ""

    if settings and settings["project_settings"]["flow_cli_custom_path"]:
      flow_cli = os.path.basename(settings["project_settings"]["flow_cli_custom_path"])
      bin_path = os.path.dirname(settings["project_settings"]["flow_cli_custom_path"])
      is_from_bin = False
      chdir = settings["project_dir_name"]
      use_node = False

    deps = flow.parse_cli_dependencies(view)

    node = NodeJS(check_local=True)
    
    if sublime.platform() == "windows":
      imports = {}
      javascript_files_temp = ""
      index = 0
      for i in range(0, len(javascript_files)):

        if len(javascript_files_temp + " " + json.dumps(javascript_files[i], ensure_ascii=False)) <= 7500 :

          if not javascript_files_temp:
            javascript_files_temp = json.dumps(javascript_files[i], ensure_ascii=False)
          else:
            javascript_files_temp += " " + json.dumps(javascript_files[i], ensure_ascii=False)
        
          if i < len(javascript_files) - 1:
            continue

        result = node.execute_check_output(
          flow_cli,
          [
            'get-imports',
            '--from', 'sublime_text',
            '--root', deps.project_root,
            '--json'
          ] + ( javascript_files[index:i] if i < len(javascript_files) - 1 else javascript_files[index:]),
          is_from_bin=is_from_bin,
          use_fp_temp=False, 
          is_output_json=True,
          chdir=chdir,
          bin_path=bin_path,
          use_node=use_node,
          command_arg_escape=False
        )

        if result[0]:
          imports.update(result[1])
        else:
          return {}

        index = i
        javascript_files_temp = json.dumps(javascript_files[i], ensure_ascii=False)

      return imports
    else:
      result = node.execute_check_output(
        flow_cli,
        [
          'get-imports',
          '--from', 'sublime_text',
          '--root', deps.project_root,
          '--json'
        ] + javascript_files,
        is_from_bin=is_from_bin,
        use_fp_temp=False, 
        is_output_json=True,
        chdir=chdir,
        bin_path=bin_path,
        use_node=use_node
      )

      if result[0]:
        return result[1]

    return {}

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
      