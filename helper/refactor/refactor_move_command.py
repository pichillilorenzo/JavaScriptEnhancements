import sublime, sublime_plugin
import os, shutil

class RefactorMoveCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    file_name = view.file_name()
    inputs = args.get("inputs")
    new_path = inputs["new_path"]
    settings = get_project_settings()
    javascript_files = []

    if new_path == file_name:
      return

    if settings:
      for root, dirs, files in os.walk(settings["project_dir_name"]):
        if "/node_modules" in root:
          continue
        for file in files:
          if file.endswith(".js"):
            javascript_files.append(os.path.join(root, file))

      if not args.get("preview"):
        shutil.move(file_name, new_path)
        new_view = view.window().open_file(new_path)
      else:
        preview_view = view.window().new_file()
        preview_view.set_name("Refactor - Move Preview")
        preview_view.set_syntax_file('Packages/Default/Find Results.hidden-tmLanguage')
        preview_view.run_command("append_text_view", args={"text": "Refactor - Move Preview\n\n"})

      if javascript_files:
        imports = self.get_imports(settings, javascript_files)
        for k, v in imports.items():
          if v["requirements"]:
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
                  content = content [:start_offset] + rel_new_path + content[end_offset:]

                  if args.get("preview"):
                    splitted_content = content.splitlines()
                    preview_content = k + ":\n\n"
                    line = int(req["line"]) - 1
                    range_start = max(0, line - 2)
                    range_end = min(line + 2, len(splitted_content))
                    while range_start <= range_end:
                      preview_content += "    " + str(range_start) + (": " if line == range_start else "  ") + splitted_content[range_start] + "\n"
                      range_start += 1
                    preview_content +=  "\n"
                    preview_view.run_command("append_text_view", args={"text": preview_content})

                  else:
                    file.seek(0)
                    file.write(content)
                    file.truncate()

      if not args.get("preview"):
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
    settings = get_project_settings()
    if not settings or not Util.selection_in_js_scope(view):
      return False
    return True

  def is_visible(self, **args) :
    view = self.view
    settings = get_project_settings()
    if not settings or not Util.selection_in_js_scope(view):
      return False
    return True
      