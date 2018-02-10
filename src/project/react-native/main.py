import sublime, sublime_plugin
import os, webbrowser, shlex, json, collections

def react_native_ask_custom_path(project_path, type):
    sublime.active_window().show_input_panel("Create-react-native-app CLI custom path", "create-react-native-app", lambda react_native_custom_path: react_native_prepare_project(project_path, react_native_custom_path) if type == "create_new_project" or type == "add_project_type" else add_react_native_settings(project_path, react_native_custom_path), None, None)

def add_react_native_settings(working_directory, react_native_custom_path):
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

  default_config = json.loads(open(os.path.join(PROJECT_FOLDER, "react-native", "default_config.json")).read(), object_pairs_hook=collections.OrderedDict)
  default_config["working_directory"] = working_directory
  default_config["cli_custom_path"] = react_native_custom_path

  react_native_settings = os.path.join(PROJECT_SETTINGS_FOLDER_PATH, "react_native_settings.json")

  with open(react_native_settings, 'w+', encoding="utf-8") as file:
    file.write(json.dumps(default_config, indent=2))

def react_native_prepare_project(project_path, react_native_custom_path):

  terminal = Terminal(cwd=project_path)
  
  if sublime.platform() != "windows": 
    open_project = ["&&", shlex.quote(sublime_executable_path()), shlex.quote(get_project_settings(project_path)["project_file_name"])] if not is_project_open(get_project_settings(project_path)["project_file_name"]) else []
    terminal.run([shlex.quote(react_native_custom_path), "my-app", ";", "mv", "./my-app/{.[!.],}*", "./", ";", "rm", "-rf", "my-app"] + open_project)
  else:
    open_project = [sublime_executable_path(), get_project_settings(project_path)["project_file_name"], "&&", "exit"] if not is_project_open(get_project_settings(project_path)["project_file_name"]) else []
    terminal.run([react_native_custom_path, "my-app", "&", os.path.join(WINDOWS_BATCH_FOLDER, "move_all.bat"), "my-app", ".", "&", "rd", "/s", "/q", "my-app"])
    if open_project:
      terminal.run(open_project)

  add_react_native_settings(project_path, react_native_custom_path)

Hook.add("react-native_after_create_new_project", react_native_ask_custom_path)
Hook.add("react-native_add_javascript_project_configuration", react_native_ask_custom_path)
Hook.add("react-native_add_javascript_project_type", react_native_ask_custom_path)

# class enable_menu_react_nativeEventListener(enable_menu_project_typeEventListener):
#   project_type = "react-native"
#   path = os.path.join(PROJECT_FOLDER, "react_native", "Main.sublime-menu")
#   path_disabled = os.path.join(PROJECT_FOLDER, "react_native", "Main_disabled.sublime-menu")

# class react_native_cliCommand(manage_cliCommand):

#   cli = "create-react-native-app"
#   custom_name = "react_native"
#   settings_name = "react_native_settings"

#   def prepare_command(self, **kwargs):

#     self._run()

#   def _run(self):

#     super(react_native_cliCommand, self)._run()

