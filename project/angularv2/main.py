import sublime, sublime_plugin
import os, webbrowser, shlex, json, collections

def angularv2_ask_custom_path(project_path, type):
    sublime.active_window().show_input_panel("@angular/cli custom path", "ng", lambda angularv2_custom_path: angularv2_prepare_project(project_path, shlex.quote(angularv2_custom_path)) if type == "create_new_project" else add_angularv2_settings(project_path, shlex.quote(angularv2_custom_path)), None, None)

def add_angularv2_settings(working_directory, angularv2_custom_path):
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

  default_config = json.loads(open(os.path.join(PROJECT_FOLDER, "angularv2", "default_config.json")).read(), object_pairs_hook=collections.OrderedDict)
  default_config["working_directory"] = working_directory
  default_config["cli_custom_path"] = angularv2_custom_path

  angularv2_settings = os.path.join(PROJECT_SETTINGS_FOLDER_PATH, "angularv2_settings.json")

  with open(angularv2_settings, 'w+') as file:
    file.write(json.dumps(default_config, indent=2))

def angularv2_prepare_project(project_path, angularv2_custom_path):
  
  window = sublime.active_window()
  view = window.new_file() 

  if sublime.platform() in ("linux", "osx"): 
    args = {"cmd": "/bin/bash -l", "title": "Terminal", "cwd": project_path, "syntax": None, "keep_open": False} 
    view.run_command('terminal_view_activate', args=args)
    window.run_command("terminal_view_send_string", args={"string": angularv2_custom_path+" new myApp && mv ./myApp/{.[!.],}* ./ && rm -rf myApp\n"})
  else:
    # windows
    pass

  add_angularv2_settings(project_path, angularv2_custom_path)

  open_project_folder(get_project_settings()["project_file_name"])

Hook.add("angularv2_after_create_new_project", angularv2_ask_custom_path)
Hook.add("angularv2_add_javascript_project_configuration", angularv2_ask_custom_path)

class enable_menu_angularv2EventListener(enable_menu_project_typeEventListener):
  project_type = "angularv2"
  path = os.path.join(PROJECT_FOLDER, "angularv2", "Main.sublime-menu")
  path_disabled = os.path.join(PROJECT_FOLDER, "angularv2", "Main_disabled.sublime-menu")

class angularv2_cliCommand(manage_cliCommand):

  cli = "ng"
  custom_name = "angularv2"
  settings_name = "angularv2_settings"

  def prepare_command(self, **kwargs):

    if ":name_and_options" in self.command:
      sublime.active_window().show_input_panel( self.command[0] + " " + self.command[1] + " name and options:", "", self.name_and_options_on_done, None, None )
    else :
      self._run()

  def name_and_options_on_done(self, name_and_options):
    self.placeholders[":name_and_options"] = name_and_options.strip()
    self.command = self.substitute_placeholders(self.command)
    self._run()

  def _run(self):

    try:
      self.command = {
        'build': lambda : self.command + self.settings["angularv2_settings"]["platform_run_options"][self.command[2].replace('--', '')],
        'serve': lambda : self.command + self.settings["angularv2_settings"]["serve_options"],
        'lint': lambda : self.command + self.settings["angularv2_settings"]["lint_options"],
        'test': lambda : self.command + self.settings["angularv2_settings"]["test_options"],
        'e2e': lambda : self.command + self.settings["angularv2_settings"]["e2e_options"],
        'eject': lambda : self.command + self.settings["angularv2_settings"]["eject_options"],
        'xi18n': lambda : self.command + self.settings["angularv2_settings"]["xi18n_options"]
      }[self.command[0]]()
    except KeyError as err:
      pass
    except Exception as err:
      print(traceback.format_exc())
      pass
 
    super(angularv2_cliCommand, self)._run()

