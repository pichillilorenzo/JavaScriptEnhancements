import sublime, sublime_plugin
import os, shlex, json, collections, traceback
from ....libs.global_vars import *
from ....libs import util
from ....libs import JavascriptEnhancementsExecuteOnTerminalCommand
from ....libs import Terminal
from ....libs import Hook

def vue_ask_custom_path(project_path, type):
    sublime.active_window().show_input_panel("Vue CLI custom path", "vue", lambda vue_custom_path: vue_prepare_project(project_path, vue_custom_path) if type == "create_new_project" or type == "add_project_type" else add_vue_settings(project_path, vue_custom_path), None, None)

def add_vue_settings(working_directory, vue_custom_path):
  project_path = working_directory
  settings = util.get_project_settings()
  if settings :
    project_path = settings["project_dir_name"]
    
  flowconfig_file_path = os.path.join(project_path, ".flowconfig")
  with open(flowconfig_file_path, 'r+', encoding="utf-8") as file:
    content = file.read()
    content = content.replace("[include]", """[include]
<PROJECT_ROOT>/src""")

    content = content.replace("[ignore]", """[ignore]
<PROJECT_ROOT>/build/.*
<PROJECT_ROOT>/dist/.*""")

    content = content.replace("[options]", """[options]
module.file_ext=.vue
module.file_ext=.js
module.name_mapper='vue' -> 'js'""")
    file.seek(0)
    file.truncate()
    file.write(content)

  PROJECT_SETTINGS_FOLDER_PATH = os.path.join(project_path, PROJECT_SETTINGS_FOLDER_NAME)

  default_config = json.loads(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "default_config.json")).read(), object_pairs_hook=collections.OrderedDict)
  default_config["working_directory"] = working_directory
  default_config["cli_custom_path"] = vue_custom_path

  vue_settings = os.path.join(PROJECT_SETTINGS_FOLDER_PATH, "vue_settings.json")

  with open(vue_settings, 'w+', encoding="utf-8") as file:
    file.write(json.dumps(default_config, indent=2))

def vue_prepare_project(project_path, vue_custom_path):

  terminal = Terminal(cwd=project_path)
  
  if sublime.platform() != "windows": 
    open_project = ["&&", shlex.quote(util.sublime_executable_path()), shlex.quote(util.get_project_settings(project_path)["project_file_name"])] if not util.is_project_open(util.get_project_settings(project_path)["project_file_name"]) else []
    terminal.run([shlex.quote(vue_custom_path), "init", "webpack", "."] + open_project)
  else:
    open_project = [util.sublime_executable_path(), util.get_project_settings(project_path)["project_file_name"], "&&", "exit"] if not util.is_project_open(util.get_project_settings(project_path)["project_file_name"]) else []
    terminal.run([vue_custom_path, "init", "webpack", "."])
    if open_project:
      terminal.run(open_project)

  add_vue_settings(project_path, vue_custom_path)

Hook.add("vue_after_create_new_project", vue_ask_custom_path)
Hook.add("vue_add_javascript_project_configuration", vue_ask_custom_path)
Hook.add("vue_add_javascript_project_type", vue_ask_custom_path)

# import sublime, sublime_plugin
# import os
# from ... import JavascriptEnhancementsEnableProjectTypeMenuEventListener

# class JavascriptEnhancementsEnableVueMenuEventListener(JavascriptEnhancementsEnableProjectTypeMenuEventListener, sublime_plugin.EventListener):
#   project_type = "react"
#   path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Main.sublime-menu")
#   path_disabled = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Main_disabled.sublime-menu")

# class JavascriptEnhancementsVueCliCommand(JavascriptEnhancementsExecuteOnTerminalCommand, sublime_plugin.WindowCommand):

#   cli = "vue"
#   custom_name = "vue"
#   settings_name = "vue_settings"

#   def prepare_command(self, **kwargs):

#     self._run()

#   def _run(self):

#     super(JavascriptEnhancementsVueCliCommand, self)._run()
