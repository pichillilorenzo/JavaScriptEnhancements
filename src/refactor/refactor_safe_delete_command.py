import sublime, sublime_plugin
import os, shutil

class RefactorSafeDeleteCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    window = view.window()
    file_name = view.file_name()
    settings = get_project_settings()
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
          imports = self.get_imports(settings, javascript_files)
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
        windowViewManager.close(view.id())
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
      