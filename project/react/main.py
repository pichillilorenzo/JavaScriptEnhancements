import sublime, sublime_plugin
import os, webbrowser, shlex, json, collections

def react_ask_custom_path(project_path, type):
    sublime.active_window().show_input_panel("React custom path", "create-react-app", lambda react_custom_path: react_prepare_project(project_path, shlex.quote(react_custom_path)) if type == "create_new_project" else add_react_settings(project_path, shlex.quote(react_custom_path)), None, None)

def add_react_settings(working_directory, react_custom_path):
  project_path = working_directory
  settings = get_project_settings()
  if settings :
    project_path = settings["project_dir_name"]
    
  flowconfig_file_path = os.path.join(project_path, ".flowconfig")
  with open(flowconfig_file_path, 'r+', encoding="utf-8") as file:
    content = file.read()
    content = content.replace("[ignore]", """[ignore]""")
    file.seek(0)
    file.truncate()
    file.write(content)

  PROJECT_SETTINGS_FOLDER_PATH = os.path.join(project_path, PROJECT_SETTINGS_FOLDER_NAME)

  default_config = json.loads(open(os.path.join(PROJECT_FOLDER, "react", "default_config.json")).read(), object_pairs_hook=collections.OrderedDict)
  default_config["working_directory"] = working_directory
  default_config["cli_custom_path"] = react_custom_path

  react_settings = os.path.join(PROJECT_SETTINGS_FOLDER_PATH, "react_settings.json")

  with open(react_settings, 'w+') as file:
    file.write(json.dumps(default_config, indent=2))

def react_prepare_project(project_path, react_custom_path):

  window = sublime.active_window()
  view = window.new_file() 

  if sublime.platform() in ("linux", "osx"): 
    args = {"cmd": "/bin/bash -l", "title": "Terminal", "cwd": project_path, "syntax": None, "keep_open": False} 
    view.run_command('terminal_view_activate', args=args)
    window.run_command("terminal_view_send_string", args={"string": react_custom_path+" myApp && mv ./myApp/{.[!.],}* ./ && rm -rf myApp\n"})
  else:
    # windows
    pass

  add_react_settings(project_path, react_custom_path)

  open_project_folder(get_project_settings()["project_file_name"])

Hook.add("react_after_create_new_project", react_ask_custom_path)
Hook.add("react_add_javascript_project_configuration", react_ask_custom_path)

class enable_menu_reactEventListener(enable_menu_project_typeEventListener):
  project_type = "react"
  path = os.path.join(PROJECT_FOLDER, "react", "Main.sublime-menu")
  path_disabled = os.path.join(PROJECT_FOLDER, "react", "Main_disabled.sublime-menu")

class react_cliCommand(manage_cliCommand):

  cli = "create-react-app"
  custom_name = "react"
  settings_name = "react_settings"

  def prepare_command(self, **kwargs):

    self._run()

  def _run(self):

    super(react_cliCommand, self)._run()

