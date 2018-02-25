import sublime, sublime_plugin
import os, shlex, json, collections, traceback
from ....libs.global_vars import *
from ....libs import util
from ....libs import JavascriptEnhancementsExecuteOnTerminalCommand
from ....libs import Terminal
from ....libs import Hook

class JavascriptEnhancementsIonicv2CliCommand(JavascriptEnhancementsExecuteOnTerminalCommand, sublime_plugin.WindowCommand):

  cli = "ionic"
  custom_name = "ionicv2"
  settings_name = "ionicv2_settings"

  def prepare_command(self, **kwargs):

    if ":platform" in self.command:
      self.window.show_input_panel("Platform:", "", self.platform_on_done, None, None)
    elif ":integration_id" in self.command:
      self.window.show_input_panel("Integration id:", "", self.integration_id_on_done, None, None)
    else :
      self._run()

  def platform_on_done(self, platform):
    self.placeholders[":platform"] = shlex.quote(platform.strip())
    self.command = self.substitute_placeholders(self.command)
    self._run()

  def integration_id_on_done(self, integration_id):
    self.placeholders[":integration_id"] = shlex.quote(integration_id.strip())
    self.command = self.substitute_placeholders(self.command)
    self._run()

  def _run(self):
    try:
      if self.command[0] == "cordova":
        self.command = {
          'run': lambda : self.command + self.settings["ionicv2_settings"]["platform_run_options"][self.command[3].replace('--', '')][self.command[2]],
          'compile': lambda : self.command + self.settings["ionicv2_settings"]["platform_compile_options"][self.command[3].replace('--', '')][self.command[2]],
          'build': lambda : self.command + self.settings["ionicv2_settings"]["platform_build_options"][self.command[3].replace('--', '')][self.command[2]],
          'emulate': lambda : self.command + self.settings["ionicv2_settings"]["platform_emulate_options"][self.command[3].replace('--', '')][self.command[2]],
          'prepare': lambda : self.command + self.settings["ionicv2_settings"]["platform_prepare_options"][self.command[2]]
        }[self.command[1]]()
      else:
        self.command = {
          'serve': lambda : self.command + self.settings["ionicv2_settings"]["serve_options"]
        }[self.command[0]]()
    except KeyError as err:
      pass
    except Exception as err:
      print(traceback.format_exc())
      pass

    super(JavascriptEnhancementsIonicv2CliCommand, self)._run()


def ionicv2_ask_custom_path(project_path, type):
    sublime.active_window().show_input_panel("Ionic v2 CLI custom path", "ionic", lambda ionicv2_custom_path: ionicv2_prepare_project(project_path, ionicv2_custom_path) if type == "create_new_project" or type == "add_project_type" else add_ionicv2_settings(project_path, ionicv2_custom_path), None, None)

def add_ionicv2_settings(working_directory, ionicv2_custom_path):
  project_path = working_directory
  settings = util.get_project_settings()
  if settings :
    project_path = settings["project_dir_name"]
    
  flowconfig_file_path = os.path.join(project_path, ".flowconfig")
  with open(flowconfig_file_path, 'r+', encoding="utf-8") as file:
    content = file.read()
    content = content.replace("[ignore]", """[ignore]
<PROJECT_ROOT>/platforms/.*
<PROJECT_ROOT>/hooks/.*
<PROJECT_ROOT>/plugins/.*
<PROJECT_ROOT>/resources/.*
<PROJECT_ROOT>/.sourcemaps/.*""")
    file.seek(0)
    file.truncate()
    file.write(content)

  PROJECT_SETTINGS_FOLDER_PATH = os.path.join(project_path, PROJECT_SETTINGS_FOLDER_NAME)

  default_config = json.loads(open(os.path.join(PROJECT_FOLDER, "ionicv2", "default_config.json")).read(), object_pairs_hook=collections.OrderedDict)
  default_config["working_directory"] = working_directory
  default_config["cli_custom_path"] = ionicv2_custom_path

  ionicv2_settings = os.path.join(PROJECT_SETTINGS_FOLDER_PATH, "ionicv2_settings.json")

  with open(ionicv2_settings, 'w+', encoding="utf-8") as file:
    file.write(json.dumps(default_config, indent=2))

def ionicv2_prepare_project(project_path, ionicv2_custom_path):
  
  terminal = Terminal(cwd=project_path)
  
  if sublime.platform() != "windows": 
    open_project = ["&&", shlex.quote(util.sublime_executable_path()), shlex.quote(util.get_project_settings(project_path)["project_file_name"])] if not util.is_project_open(util.get_project_settings(project_path)["project_file_name"]) else []
    terminal.run([shlex.quote(ionicv2_custom_path), "start", "my-app", ";", "mv", "./my-app/{.[!.],}*", "./", ";", "rm", "-rf", "my-app"] + open_project)
  else:
    open_project = [util.sublime_executable_path(), util.get_project_settings(project_path)["project_file_name"], "&&", "exit"] if not util.is_project_open(util.get_project_settings(project_path)["project_file_name"]) else []
    terminal.run([ionicv2_custom_path, "start", "my-app", "&", os.path.join(WINDOWS_BATCH_FOLDER_PATH, "move_all.bat"), "my-app", ".", "&", "rd", "/s", "/q", "my-app"])
    if open_project:
      terminal.run(open_project)

  add_ionicv2_settings(project_path, ionicv2_custom_path)

Hook.add("ionicv2_after_create_new_project", ionicv2_ask_custom_path)
Hook.add("ionicv2_add_javascript_project_configuration", ionicv2_ask_custom_path)
Hook.add("ionicv2_add_javascript_project_type", ionicv2_ask_custom_path)
