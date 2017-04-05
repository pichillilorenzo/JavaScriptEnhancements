import sublime, sublime_plugin
import os, webbrowser, shlex
from node.main import NodeJS

def create_ionic_project_process(line, process, panel, project, sublime_project_file_name) :

  if line != None and panel:
    panel.run_command("print_panel_cli", {"line": line, "hide_panel_on_success": True})

  if line == "OUTPUT-SUCCESS":
    Util.move_content_to_parent_folder(os.path.join(project["path"], "temp"))
    open_project_folder(sublime_project_file_name)

def create_ionic_project(json_data):
  project = json_data["project"]
  project_folder = project["path"]
  types_options = []

  if "ionic" in project["types_options"]:
    types_options = project["types_options"]["ionic"]

  panel = Util.create_and_show_panel("ionic_panel_installer_project")
  node.execute('ionic', ["start", "temp"] + types_options, is_from_bin=True, chdir=project_folder, wait_terminate=False, func_stdout=create_ionic_project_process, args_func_stdout=[panel, project, json_data["sublime_project_file_name"]])

  return json_data

Hook.add("ionic_create_new_project", create_ionic_project)

class enable_menu_ionicEventListener(enable_menu_cliEventListener):
  cli = "ionic"
  path = os.path.join(PACKAGE_PATH, "project", "ionic", "Main.sublime-menu")
  path_disabled = os.path.join(PACKAGE_PATH, "project", "ionic", "Main_disabled.sublime-menu")

class ionic_baseCommand(cordova_baseCommand):
  cli = "ionic"
  name_cli = "Ionic"

  def append_args_execute(self) :
    custom_args = []
    command = self.command_with_options[0]

    if command == "serve" :
      custom_args = custom_args + ["--port"] + [self.settings["cordova_settings"]["serve_port"]]

    elif command == "platform" or command == "build" or command == "run" or command == "emulate" :
      custom_args = custom_args + self.settings["ionic_settings"]["cli_"+command+"_options"]
      if command == "emulate":
        mode = self.command_with_options[2][2:]
        platform = self.placeholders[":platform"]
        custom_args_platform = ""
        custom_args_platform = Util.getDictItemIfExists(self.settings["ionic_settings"]["platform_"+command+"_options"][mode], platform)
        if custom_args_platform :
          custom_args = custom_args + ["--"] + shlex.split(custom_args_platform)

    elif "cli_"+command+"_options" in self.settings["ionic_settings"] :
      custom_args = custom_args + self.settings["ionic_settings"]["cli_"+command+"_options"]

    return super(ionic_baseCommand, self).append_args_execute() + custom_args

  def before_execute(self):
    command = self.command_with_options[0]
    if command == "serve" :
      del self.command_with_options[1]

  def is_enabled(self):
    return is_type_javascript_project("ionic") and is_type_javascript_project("cordova")

  def is_visible(self):
    return is_type_javascript_project("ionic") and is_type_javascript_project("cordova")

class manage_ionicCommand(ionic_baseCommand, manage_cordovaCommand):

  def run(self, **kwargs):
    super(manage_ionicCommand, self).run(**kwargs)

class manage_serve_ionicCommand(ionic_baseCommand, manage_serve_cordovaCommand):
  
  def run(self, **kwargs):
    super(manage_serve_ionicCommand, self).run(**kwargs)

class manage_plugin_ionicCommand(manage_ionicCommand, manage_plugin_cordovaCommand):

  def run(self, **kwargs):
    super(manage_plugin_ionicCommand, self).run(**kwargs)

class manage_add_platform_ionicCommand(manage_ionicCommand, manage_add_platform_cordovaCommand):

  def run(self, **kwargs):
    super(manage_add_platform_ionicCommand, self).run(**kwargs)

class manage_remove_platform_ionicCommand(manage_ionicCommand, manage_remove_platform_cordovaCommand):

  def run(self, **kwargs):
    super(manage_remove_platform_ionicCommand, self).run(**kwargs)

  def on_success(self):
    Util.delItemIfExists(self.settings["ionic_settings"]["platform_emulate_options"]["debug"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["ionic_settings"]["platform_emulate_options"]["release"], self.placeholders[":platform"])
    super(manage_remove_platform_ionicCommand, self).on_success()

class sync_ionic_projectCommand(ionic_baseCommand, sync_cordova_projectCommand):

  platform_list = []
  plugin_list = []

  def run(self, **kwargs):
    super(sync_ionic_projectCommand, self).run(**kwargs)
