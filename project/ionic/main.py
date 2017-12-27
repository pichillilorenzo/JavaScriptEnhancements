import sublime, sublime_plugin
import os, webbrowser, shlex, json

def ionic_ask_custom_path(project_path):
  sublime.active_window().show_input_panel("Ionic custom path", "ionic", lambda ionic_custom_path: ionic_prepare_project(project_path, shlex.quote(ionic_custom_path)), None, None)

def ionic_prepare_project(project_path, ionic_custom_path):
  open_project_folder(project_path)
  window = sublime.active_window()
  view = window.new_file() 

  if sublime.platform() in ("linux", "osx"): 
    args = {"cmd": "/bin/bash -l", "title": "Terminal", "cwd": project_path, "syntax": None, "keep_open": False} 
    view.run_command('terminal_view_activate', args=args)
    window.run_command("terminal_view_send_string", args={"string": ionic_custom_path+" start myApp blank --type ionic1 && mv ./myApp/* ./ && rm -rf myApp\n"})
  else:
    # windows
    pass

  flowconfig_file_path = os.path.join(project_path, ".flowconfig")
  with open(flowconfig_file_path, 'r+', encoding="utf-8") as file:
    content = file.read()
    content = content.replace("[ignore]", """[ignore]
<PROJECT_ROOT>/platforms/.*
<PROJECT_ROOT>/hooks/.*
<PROJECT_ROOT>/plugins/.*
<PROJECT_ROOT>/resources/.*""")
    file.seek(0)
    file.truncate()
    file.write(content)

  PROJECT_SETTINGS_FOLDER_PATH = os.path.join(project_path, PROJECT_SETTINGS_FOLDER_NAME)

  default_config = json.loads(open(os.path.join(PROJECT_FOLDER, "ionic", "default_config.json")).read())
  default_config["working_directory"] = project_path
  default_config["cli_custom_path"] = ionic_custom_path

  ionic_settings = os.path.join(PROJECT_SETTINGS_FOLDER_PATH, "ionic_settings.json")

  with open(ionic_settings, 'w+') as file:
    file.write(json.dumps(default_config, indent=2))

Hook.add("ionic_after_create_new_project", ionic_ask_custom_path)

class enable_menu_ionicEventListener(enable_menu_project_typeEventListener):
  project_type = "ionic"
  path = os.path.join(PROJECT_FOLDER, "ionic", "Main.sublime-menu")
  path_disabled = os.path.join(PROJECT_FOLDER, "ionic", "Main_disabled.sublime-menu")

class ionic_cliCommand(manage_cliCommand):

  cli = "ionic"
  settings_name = "ionic_settings"

  def prepare_command(self, **kwargs):

    if ":platform" in self.command:
      self.window.show_input_panel("Platform:", "", self.platform_on_done, None, None)
    else :
      self._run()

  def platform_on_done(self, platform):
    self.placeholders[":platform"] = platform
    self.command = self.substitute_placeholders(self.command)
    self._run()

  def _run(self):
    try:
      self.command = {
        'run': lambda : self.command + self.settings["ionic_settings"]["platform_run_options"][self.command[2].replace('--', '')][self.command[1]],
        'compile': lambda : self.command + self.settings["ionic_settings"]["platform_compile_options"][self.command[2].replace('--', '')][self.command[1]],
        'build': lambda : self.command + self.settings["ionic_settings"]["platform_build_options"][self.command[2].replace('--', '')][self.command[1]],
        'serve': lambda : self.command + self.settings["ionic_settings"]["serve_options"]
      }[self.command[0]]()
    except Exception as err:
      print(traceback.format_exc())
      pass

    super(ionic_cliCommand, self)._run()

