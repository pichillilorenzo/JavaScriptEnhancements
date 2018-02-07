import sublime, sublime_plugin
import os

class RefactorSafeCopyCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    window = view.window()
    file_name = view.file_name()
    inputs = args.get("inputs")
    view_id_caller = args.get("view_id_caller") if "view_id_caller" in args else None
    new_path = os.path.normpath(inputs["new_path"].strip())
    settings = get_project_settings()

    if not file_name:
      sublime.error_message("Cannot copy this file. File name is empty.")
      return 

    if not new_path:
      sublime.error_message("The File path is empty.")
      return 

    if new_path == file_name:
      sublime.message_dialog("The file path is the same as before.")
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
        preview_view = None
        for v in window.views():
          if v.name() == "Refactor - Safe Copy Preview":
            preview_view = v
            preview_view.erase(edit, sublime.Region(0, preview_view.size()))
            window.focus_view(preview_view)
            break

        if not preview_view:
          window.focus_group(1)
          preview_view = window.new_file()
          preview_view.set_name("Refactor - Safe Copy Preview")
          preview_view.set_syntax_file('Packages/Default/Find Results.hidden-tmLanguage')
          preview_view.set_scratch(True)

        preview_view.run_command("append_text_view", args={"text": "Refactor - Safe Copy Preview\n\nList of files that will be updated\n\n"})

      imports = self.get_imports(settings, [file_name])

      if imports[file_name]["requirements"]:
        content = ""

        with open(file_name, "r") as file:
          content = file.read()
          preview_content = ""

          for req in imports[file_name]["requirements"]:
            start_offset = int(req["loc"]["start"]["offset"]) + 1
            end_offset = int(req["loc"]["end"]["offset"]) - 1

            req_new_path = req["import"] if os.path.isabs(req["import"]) else os.path.abspath(os.path.dirname(file_name) + os.path.sep + req["import"])

            if os.path.dirname(new_path) == os.path.dirname(req_new_path):
              rel_new_path = "./" + os.path.basename(req_new_path)
            else:
              rel_new_path = os.path.relpath(req_new_path, start=os.path.dirname(new_path))

              if sublime.platform() == "windows":
                rel_new_path = Util.convert_path_to_unix(rel_new_path)

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
              while range_start <= range_end and range_start < len(splitted_content):
                preview_content += "    " + str(range_start + 1) + (": " if line == range_start else "  ") + splitted_content[range_start] + "\n"
                range_start += 1
              preview_content +=  "\n\n"
              
          if args.get("preview"):
            preview_view.run_command("append_text_view", args={"text": preview_content})

        if not args.get("preview"):
          with open(new_path, "w+") as file:
            file.seek(0)
            file.write(content)
            file.truncate()

      if not args.get("preview"):

        for v in window.views():
          if v.name() == "Refactor - Safe Copy Preview":
            v.close()
            break

        if view_id_caller:
          windowViewManager.get(view_id_caller).close()

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
    
    if sublime.platform() == "windows":
      imports = {}
      javascript_files_temp = ""
      index = 0
      for i in range(0, len(javascript_files)):

        if len(javascript_files_temp + " " + json.dumps(javascript_files[i])) <= 7500 :

          if not javascript_files_temp:
            javascript_files_temp = json.dumps(javascript_files[i])
          else:
            javascript_files_temp += " " + json.dumps(javascript_files[i])
        
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
        javascript_files_temp = json.dumps(javascript_files[i])

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
      