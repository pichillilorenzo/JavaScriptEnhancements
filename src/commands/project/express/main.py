import sublime, sublime_plugin
import os, shlex, json, collections, traceback
from ....libs.global_vars import *
from ....libs import util
from ....libs import JavascriptEnhancementsExecuteOnTerminalCommand
from ....libs import Terminal
from ....libs import Hook
from ....libs import NPM

def express_ask_custom_path(project_path, type):
    sublime.active_window().show_input_panel("Express generator CLI custom path", "express", lambda express_custom_path: express_prepare_project(project_path, express_custom_path) if type == "create_new_project" or type == "add_project_type" else add_express_settings(project_path, express_custom_path), None, None)

def add_express_settings(working_directory, express_custom_path):
  project_path = working_directory
  settings = util.get_project_settings()
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

  default_config = json.loads(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "default_config.json")).read(), object_pairs_hook=collections.OrderedDict)
  default_config["working_directory"] = working_directory
  default_config["cli_custom_path"] = express_custom_path

  express_settings = os.path.join(PROJECT_SETTINGS_FOLDER_PATH, "express_settings.json")

  with open(express_settings, 'w+', encoding="utf-8") as file:
    file.write(json.dumps(default_config, indent=2))

def express_prepare_project(project_path, express_custom_path):

  terminal = Terminal(cwd=project_path)
  
  if sublime.platform() != "windows": 
    open_project = ["&&", shlex.quote(util.sublime_executable_path()), shlex.quote(util.get_project_settings(project_path)["project_file_name"])] if not util.is_project_open(util.get_project_settings(project_path)["project_file_name"]) else []
    terminal.run([shlex.quote(express_custom_path), "my-app", ";", "mv", "./my-app/{.[!.],}*", "./", ";", "rm", "-rf", "my-app", ";", NPM(check_local=True).cli_path, "install"] + open_project)
  else:
    open_project = [util.sublime_executable_path(), util.get_project_settings(project_path)["project_file_name"], "&&", "exit"] if not util.is_project_open(util.get_project_settings(project_path)["project_file_name"]) else []
    terminal.run([express_custom_path, "my-app", "&", os.path.join(WINDOWS_BATCH_FOLDER_PATH, "move_all.bat"), "my-app", ".", "&", "rd", "/s", "/q", "my-app", "&", NPM(check_local=True).cli_path, "install"])
    if open_project:
      terminal.run(open_project)

  add_express_settings(project_path, express_custom_path)

Hook.add("express_after_create_new_project", express_ask_custom_path)
Hook.add("express_add_javascript_project_configuration", express_ask_custom_path)
Hook.add("express_add_javascript_project_type", express_ask_custom_path)

# import sublime, sublime_plugin
# import os
# from ... import JavascriptEnhancementsEnableProjectTypeMenuEventListener

# class JavascriptEnhancementsEnableExpressMenuEventListener(JavascriptEnhancementsEnableProjectTypeMenuEventListener, sublime_plugin.EventListener):
#   project_type = "express"
#   path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Main.sublime-menu")
#   path_disabled = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Main_disabled.sublime-menu")

# class JavascriptEnhancementsExpressCliCommand(JavascriptEnhancementsExecuteOnTerminalCommand, sublime_plugin.WindowCommand):

#   cli = "express"
#   custom_name = "express"
#   settings_name = "express_settings"

#   def prepare_command(self, **kwargs):

#     self._run()

#   def _run(self):

#     super(JavascriptEnhancementsExpressCliCommand, self)._run()

