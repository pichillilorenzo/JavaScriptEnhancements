import sublime, sublime_plugin
import os, webbrowser, shlex, json, collections

def angularv1_ask_custom_path(project_path, type):
    sublime.active_window().show_input_panel("Yeoman custom path", "yo", lambda angularv1_custom_path: angularv1_prepare_project(project_path, shlex.quote(angularv1_custom_path)) if type == "create_new_project" else add_angularv1_settings(project_path, shlex.quote(angularv1_custom_path)), None, None)

def add_angularv1_settings(working_directory, angularv1_custom_path):
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

  default_config = json.loads(open(os.path.join(PROJECT_FOLDER, "angularv1", "default_config.json")).read(), object_pairs_hook=collections.OrderedDict)
  default_config["working_directory"] = working_directory
  default_config["cli_custom_path"] = angularv1_custom_path

  angularv1_settings = os.path.join(PROJECT_SETTINGS_FOLDER_PATH, "angularv1_settings.json")

  with open(angularv1_settings, 'w+') as file:
    file.write(json.dumps(default_config, indent=2))

def angularv1_prepare_project(project_path, angularv1_custom_path):
  
  window = sublime.active_window()
  view = window.new_file() 

  if sublime.platform() in ("linux", "osx"): 
    args = {"cmd": "/bin/bash -l", "title": "Terminal", "cwd": project_path, "syntax": None, "keep_open": False} 
    view.run_command('terminal_view_activate', args=args)
    window.run_command("terminal_view_send_string", args={"string": angularv1_custom_path+" angular\n"})
  else:
    # windows
    pass

  add_angularv1_settings(project_path, angularv1_custom_path)

  open_project_folder(get_project_settings()["project_file_name"])

Hook.add("angularv1_after_create_new_project", angularv1_ask_custom_path)
Hook.add("angularv1_add_javascript_project_configuration", angularv1_ask_custom_path)

class enable_menu_angularv1EventListener(enable_menu_project_typeEventListener):
  project_type = "angularv1"
  path = os.path.join(PROJECT_FOLDER, "angularv1", "Main.sublime-menu")
  path_disabled = os.path.join(PROJECT_FOLDER, "angularv1", "Main_disabled.sublime-menu")

class angularv1_cliCommand(manage_cliCommand):

  cli = "yo"
  custom_name = "angularv1"
  settings_name = "angularv1_settings"

  def prepare_command(self, **kwargs):

    if self.command[0] in ["angular:controller", "angular:directive", "angular:filter", "angular:route", "angular:service", "angular:provider", "angular:factory", "angular:value", "angular:constant", "angular:decorator", "angular:view"]:
      sublime.active_window().show_input_panel( (self.command[0].replace("angular:", ""))+" name:", "", self.name_on_done, None, None )
    else :
      self._run()

  def name_on_done(self, name):
    self.placeholders[":name"] = shlex.quote(name)
    self.command = self.substitute_placeholders(self.command)
    self._run()

  def _run(self):
    # try:
    #   self.command = {
    #     'serve': lambda : self.command + self.settings["angularv1_settings"]
    #   }[self.command[0]]()
    # except KeyError as err:
    #   pass
    # except Exception as err:
    #   print(traceback.format_exc())
    #   pass

    super(angularv1_cliCommand, self)._run()

