import sublime, sublime_plugin
import os, shutil

class RefactorSafeMoveCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    window = view.window()
    file_name = view.file_name()
    inputs = args.get("inputs")
    view_id_caller = args.get("view_id_caller") if "view_id_caller" in args else None
    new_path = inputs["new_path"].strip()
    settings = get_project_settings()
    javascript_files = [file_name]

    if not file_name:
      sublime.error_message("Cannot move this file. File name is empty.")
      return 

    if not new_path:
      sublime.error_message("The File path is empty.")
      return 

    if new_path == file_name:
      sublime.message_dialog("The file path is the same as before.")
      return

    if settings:
      for root, dirs, files in os.walk(settings["project_dir_name"]):
        if "/node_modules" in root:
          continue
        for file in files:
          if file.endswith(".js"):
            javascript_files.append(os.path.join(root, file))

      if not args.get("preview"):

        if os.path.isfile(new_path):
          if not sublime.ok_cancel_dialog(new_path + " already exists.", "Move anyway"):
            return

        if not os.path.isdir(os.path.dirname(new_path)):
          os.makedirs(os.path.dirname(new_path))

      else:
        preview_view = None
        for v in window.views():
          if v.name() == "Refactor - Move Preview":
            preview_view = v
            preview_view.erase(edit, sublime.Region(0, preview_view.size()))
            window.focus_view(preview_view)
            break

        if not preview_view:
          preview_view = window.new_file()
          preview_view.set_name("Refactor - Move Preview")
          preview_view.set_syntax_file('Packages/Default/Find Results.hidden-tmLanguage')
          preview_view.set_scratch(True)

        preview_view.run_command("append_text_view", args={"text": "Refactor - Move Preview\n\nList of files that will be updated\n\n"})

      if javascript_files:
        imports = self.get_imports(settings, javascript_files)

        for k, v in imports.items():

          is_same_file = k == file_name

          if v["requirements"]:

            if is_same_file:
              with open(k, "r+") as file:
                content = file.read()
                preview_content = ""

                for req in v["requirements"]:
                  start_offset = int(req["loc"]["start"]["offset"]) + 1
                  end_offset = int(req["loc"]["end"]["offset"]) - 1

                  req_new_path = req["import"] if os.path.isabs(req["import"]) else os.path.abspath(os.path.dirname(k) + os.path.sep + req["import"])

                  if os.path.dirname(new_path) == os.path.dirname(req_new_path):
                    rel_new_path = "./" + os.path.basename(req_new_path)
                  else:
                    rel_new_path = os.path.relpath(req_new_path, start=os.path.dirname(new_path))
                    if not rel_new_path.startswith(".."):
                      rel_new_path = "./" + rel_new_path
                  content = content [:start_offset] + rel_new_path + content[end_offset:]

                  if args.get("preview"):
                    splitted_content = content.splitlines()

                    if not preview_content:
                      preview_content = "- From:\n" + file_name + "\n\n"
                      preview_content += "- To:\n" + new_path + "\n\n"

                    line = int(req["line"]) - 1
                    range_start = max(0, line - 2)
                    range_end = min(line + 2, len(splitted_content))
                    while range_start <= range_end:
                      preview_content += "    " + str(range_start + 1) + (": " if line == range_start else "  ") + splitted_content[range_start] + "\n"
                      range_start += 1
                    preview_content +=  "\n\n"
                    
                if args.get("preview"):
                  preview_view.run_command("append_text_view", args={"text": preview_content})
                else:
                  file.seek(0)
                  file.write(content)
                  file.truncate()

              if not args.get("preview"):
                shutil.move(file_name, new_path)
                window.focus_group(0)
                new_view = window.open_file(new_path)
                window.focus_group(1)

            else:
              for req in v["requirements"]:
                if file_name == ( req["import"] if os.path.isabs(req["import"]) else os.path.abspath(os.path.dirname(k) + os.path.sep + req["import"]) ):
                  with open(k, "r+") as file:
                    content = file.read()
                    start_offset = int(req["loc"]["start"]["offset"]) + 1
                    end_offset = int(req["loc"]["end"]["offset"]) - 1
                  
                    if os.path.dirname(k) == os.path.dirname(new_path):
                      rel_new_path = "./" + os.path.basename(new_path)
                    else:
                      rel_new_path = os.path.relpath(new_path, start=os.path.dirname(k))
                      if not rel_new_path.startswith(".."):
                        rel_new_path = "./" + rel_new_path
                    content = content [:start_offset] + rel_new_path + content[end_offset:]

                    if args.get("preview"):
                      splitted_content = content.splitlines()
                      preview_content = k + ":\n\n"
                      line = int(req["line"]) - 1
                      range_start = max(0, line - 2)
                      range_end = min(line + 2, len(splitted_content))
                      while range_start <= range_end:
                        preview_content += "    " + str(range_start + 1) + (": " if line == range_start else "  ") + splitted_content[range_start] + "\n"
                        range_start += 1
                      preview_content +=  "\n"
                      preview_view.run_command("append_text_view", args={"text": preview_content})
                    else:
                      file.seek(0)
                      file.write(content)
                      file.truncate()

      if not args.get("preview"):

        for v in window.views():
          if v.name() == "Refactor - Move Preview":
            v.close()
            break

        if view_id_caller:
          windowViewManager.get(view_id_caller).close()

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

    deps = flow_parse_cli_dependencies(view)

    node = NodeJS(check_local=True)
    
    result = node.execute_check_output(
      flow_cli,
      [
        'get-imports',
        '--from', 'sublime_text',
        '--root', deps.project_root,
        '--json'
      ] + javascript_files,
      is_from_bin=is_from_bin,
      use_fp_temp=True, 
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
    if not view.file_name():
      return False
    settings = get_project_settings()
    if not settings or not Util.selection_in_js_scope(view):
      return False
    return True

  def is_visible(self, **args) :
    view = self.view
    if not view.file_name():
      return False
    settings = get_project_settings()
    if not settings or not Util.selection_in_js_scope(view):
      return False
    return True
      