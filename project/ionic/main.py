import sublime, sublime_plugin
import os, webbrowser, shlex
from node.main import NodeJS

class enable_menu_ionicViewEventListener(enable_menu_cliViewEventListener):
  cli = "ionic"
  path = os.path.join(PACKAGE_PATH, "project", "ionic", "Main.sublime-menu")
  path_disabled = os.path.join(PACKAGE_PATH, "project", "ionic", "Main_disabled.sublime-menu")

  def on_activated_async(self, **kwargs):
    kwargs["cli"] = self.cli
    kwargs["path"] = self.path
    kwargs["path_disabled"] = self.path_disabled
    sublime.set_timeout_async(lambda: enable_menu_cliViewEventListener.on_activated_async(self, **kwargs))

class ionic_baseCommand(cordova_baseCommand):
  cli = "ionic"
  name_cli = "Ionic"

  def append_args_execute(self) :
    custom_args = []
    command = self.command_with_options[0]
    if command == "serve" :
      custom_args = custom_args + ["--port"] + [self.settings["cordova_settings"]["serve_port"]]
    elif command == "platform" or command == "build" or command == "run" or command == "emulate":
      custom_args = custom_args + self.settings["ionic_settings"]["cli_"+command+"_options"]
      if command == "emulate":
        mode = self.command_with_options[2][2:]
        platform = self.placeholders[":platform"]
        custom_args_platform = ""
        custom_args_platform = Util.getDictItemIfExists(self.settings["ionic_settings"]["platform_"+command+"_options"][mode], platform)
        if custom_args_platform :
          custom_args = custom_args + ["--"] + shlex.split(custom_args_platform)

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

  def process_communicate(self, line):
    global manage_cli_window_command_processes

    if not self.settings["project_dir_name"]+"_"+self.output_panel_name in manage_cli_window_command_processes :
      manage_cli_window_command_processes[self.settings["project_dir_name"]+"_"+self.output_panel_name] = {
        "process": self.process
      }

  def on_done(self):
    global manage_cli_window_command_processes
    if self.settings["project_dir_name"]+"_"+self.output_panel_name in manage_cli_window_command_processes :
      del manage_cli_window_command_processes[self.settings["project_dir_name"]+"_"+self.output_panel_name]

  def can_execute(self):
    global manage_cli_window_command_processes
    if not self.settings["project_dir_name"]+"_"+self.output_panel_name in manage_cli_window_command_processes :
      return True
    else :
      if (manage_cli_window_command_processes[self.settings["project_dir_name"]]["process"].poll() == None) :
        self.stop_now = True
        self.process = manage_cli_window_command_processes[self.settings["project_dir_name"]+"_"+self.output_panel_name]["process"]
        del manage_cli_window_command_processes[self.settings["project_dir_name"]+"_"+self.output_panel_name]
        self.stop_process()
      else :
        del manage_cli_window_command_processes[self.settings["project_dir_name"]+"_"+self.output_panel_name]
    return False


class manage_plugin_ionicCommand(manage_ionicCommand, manage_plugin_cordovaCommand):

  def run(self, **kwargs):
    super(manage_plugin_ionicCommand, self).run(**kwargs)

class manage_add_platform_ionicCommand(manage_ionicCommand, manage_add_platform_cordovaCommand):

  def run(self, **kwargs):
    super(manage_add_platform_ionicCommand, self).run(**kwargs)

class manage_remove_platform_ionicCommand(manage_ionicCommand, manage_remove_platform_cordovaCommand):

  def run(self, **kwargs):
    super(manage_remove_platform_ionicCommand, self).run(**kwargs)

class sync_ionic_projectCommand(ionic_baseCommand, sync_cordova_projectCommand):

  platform_list = []
  plugin_list = []

  def run(self, **kwargs):
    super(sync_ionic_projectCommand, self).run(**kwargs)
