import sublime, sublime_plugin
import os, webbrowser, shlex, json, collections

def express_ask_custom_path(project_path, type):
    sublime.active_window().show_input_panel("Express generator CLI custom path", "express", lambda express_custom_path: express_prepare_project(project_path, express_custom_path) if type == "create_new_project" or type == "add_project_type" else add_express_settings(project_path, express_custom_path), None, None)

def add_express_settings(working_directory, express_custom_path):
  project_path = working_directory
  settings = get_project_settings()
  if settings :
    project_path = settings["project_dir_name"]
    
  # flowconfig_file_path = os.path.join(project_path, ".flowconfig")
  # with open(flowconfig_file_path, 'r+', encoding="utf-8") as file:
  #   content = file.read()
  #   content = content.replace("[ignore]", """[ignore]""")
  #   file.seek(0)
  #   file.truncate()
  #   file.write(content)

  PROJECT_SETTINGS_FOLDER_PATH = os.path.join(project_path, PROJECT_SETTINGS_FOLDER_NAME)

  default_config = json.loads(open(os.path.join(PROJECT_FOLDER, "express", "default_config.json")).read(), object_pairs_hook=collections.OrderedDict)
  default_config["working_directory"] = working_directory
  default_config["cli_custom_path"] = express_custom_path

  express_settings = os.path.join(PROJECT_SETTINGS_FOLDER_PATH, "express_settings.json")

  with open(express_settings, 'w+') as file:
    file.write(json.dumps(default_config, indent=2))

def express_prepare_project(project_path, express_custom_path):

  terminal = Terminal(cwd=project_path)
  
  if sublime.platform() != "windows": 
    open_project = ["&&", shlex.quote(sublime_executable_path()), shlex.quote(get_project_settings(project_path)["project_file_name"])] if not is_project_open(get_project_settings(project_path)["project_file_name"]) else []
    terminal.run([shlex.quote(express_custom_path), "myApp", ";", "mv", "./myApp/{.[!.],}*", "./", ";", "rm", "-rf", "myApp", ";", NPM().cli_path, "install"] + open_project)
  else:
    open_project = [sublime_executable_path(), get_project_settings(project_path)["project_file_name"], "&&", "exit"] if not is_project_open(get_project_settings(project_path)["project_file_name"]) else []
    terminal.run([express_custom_path, "myApp", "&", os.path.join(WINDOWS_BATCH_FOLDER, "move_all.bat"), "myApp", ".", "&", "rd", "/s", "/q", "myApp", "&", NPM().cli_path, "install"])
    if open_project:
      terminal.run(open_project)

  add_express_settings(project_path, express_custom_path)

Hook.add("express_after_create_new_project", express_ask_custom_path)
Hook.add("express_add_javascript_project_configuration", express_ask_custom_path)
Hook.add("express_add_javascript_project_type", express_ask_custom_path)

# class enable_menu_expressEventListener(enable_menu_project_typeEventListener):
#   project_type = "express"
#   path = os.path.join(PROJECT_FOLDER, "express", "Main.sublime-menu")
#   path_disabled = os.path.join(PROJECT_FOLDER, "express", "Main_disabled.sublime-menu")

# class express_cliCommand(manage_cliCommand):

#   cli = "express"
#   custom_name = "express"
#   settings_name = "express_settings"

#   def prepare_command(self, **kwargs):

#     self._run()

#   def _run(self):

#     super(express_cliCommand, self)._run()

