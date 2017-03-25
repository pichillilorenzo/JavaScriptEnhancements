import sublime, sublime_plugin
import os, webbrowser
from node.main import NodeJS

class enable_menu_cordovaViewEventListener(enable_menu_cliViewEventListener):
  def __init__(self, *args, **kwargs):  
    self.cli = "cordova"
    self.path = os.path.join(PACKAGE_PATH, "project", "cordova", "Main.sublime-menu")
    self.path_disabled = os.path.join(PACKAGE_PATH, "project", "cordova", "Main_disabled.sublime-menu")
    super(enable_menu_cliViewEventListener, self).__init__(*args, **kwargs)

  def on_activated_async(self, **kwargs):
    kwargs["cli"] = self.cli
    kwargs["path"] = self.path
    kwargs["path_disabled"] = self.path_disabled
    sublime.set_timeout_async(lambda: enable_menu_cliViewEventListener.on_activated_async(self, **kwargs))

class cordova_baseCommand(manage_cliCommand):
  cli = "cordova"
  can_add_platform = False
  platform_list = []
  func_ask_platform = None
  can_add_plugin = False
  plugin_list = []
  func_ask_plugin = None

  def ask_platform(self, type, func):
    self.platform_list = []
    self.can_add_platform = False
    self.func_ask_platform = func
    self.settings = get_project_settings()
    if self.settings :
      sublime.status_message("Cordova: getting platform list...")
      node.execute(self.cli, ["platform", "list"], is_from_bin=True, chdir=self.settings["project_dir_name"], wait_terminate=False, func_stdout=(self.get_list_installed_platform if type == "installed" else self.get_list_available_platform))
    else :
      sublime.error_message("Error: can't get project settings")

  def get_list_installed_platform(self, line, process):

    self.get_platform_list("installed", line, process)

  def get_list_available_platform(self, line, process):

    self.get_platform_list("available", line, process)

  def get_platform_list(self, type, line, process):
    if line == "OUTPUT-DONE" or line == "OUTPUT-SUCCESS" or line == "OUTPUT-ERROR" :
      self.can_add_platform = False

    if type == "installed" :
      if line and line.strip().startswith("Available platforms") :
        self.can_add_platform = False

    elif type == "available" :  
      if line and line.strip().startswith("Installed platforms") :
        self.can_add_platform = False

    if line and self.can_add_platform and line.strip() :
      self.platform_list.append(line.strip().split(" ")[0])

    if type == "installed" :
      if line and line.strip().startswith("Installed platforms") :
        self.can_add_platform = True

    elif type == "available" :  
      if line and line.strip().startswith("Available platforms") :
        self.can_add_platform = True

    if line == "OUTPUT-DONE" :
      if self.platform_list :
        self.window.show_quick_panel([cordova_platform for cordova_platform in self.platform_list], self.func_ask_platform)
      else :
        if type == "installed" :
          sublime.message_dialog("Cordova: No platforms installed")
        elif type == "available" :  
          sublime.message_dialog("Cordova: No more platforms available")

  def ask_plugin(self, func):
    self.plugin_list = []
    self.can_add_plugin = False
    self.func_ask_plugin = func
    self.settings = get_project_settings()
    if self.settings :
      sublime.status_message("Cordova: getting plugin list...")
      node.execute(self.cli, ["plugin", "list"], is_from_bin=True, chdir=self.settings["project_dir_name"], wait_terminate=False, func_stdout=self.get_plugin_list)
    else :
      sublime.error_message("Error: can't get project settings")

  def get_plugin_list(self, line, process):
    if line == "OUTPUT-DONE" or line == "OUTPUT-SUCCESS" or line == "OUTPUT-ERROR" :
      self.can_add_plugin = False
    else :
      self.can_add_plugin = True

    if line and self.can_add_plugin and line.strip() :
      self.plugin_list.append(line.strip().split(" ")[0])
    if line == "OUTPUT-DONE" :
      if self.plugin_list :
        self.window.show_quick_panel([cordova_plugin for cordova_plugin in self.plugin_list], self.func_ask_plugin)
      else :
        sublime.message_dialog("Cordova: No plugins installed")

  def append_args_execute(self):
    return get_project_settings()["cordova_settings"]["cli_global_options"]

  def is_enabled(self):
    return is_type_javascript_project("cordova")

  def is_visible(self):
    return is_type_javascript_project("cordova")

class manage_cordovaCommand(cordova_baseCommand):

  def run(self, **kwargs):
    flag = False

    if kwargs.get("ask_platform") and kwargs.get("ask_platform_type"):
      self.ask_platform(kwargs.get("ask_platform_type"), lambda index: self.set_platform(index, **kwargs))
      flag = True

    if kwargs.get("ask_plugin"):
      self.ask_plugin(lambda index: self.set_plugin(index, **kwargs))
      flag = True

    if not flag :
      super(manage_cordovaCommand, self).run(**kwargs)

  def set_platform(self, index, **kwargs):
    if index >= 0:
      self.placeholders[":platform"] = self.platform_list[index]
      super(manage_cordovaCommand, self).run(**kwargs)

  def set_plugin(self, index, **kwargs):
    if index >= 0:
      self.placeholders[":plugin"] = self.plugin_list[index]
      super(manage_cordovaCommand, self).run(**kwargs)

class manage_serve_cordovaCommand(cordova_baseCommand):

  is_stoppable = True

  def process_communicate(self, line):
    if line and line.strip().startswith("Static file server running on: "):
      line = line.strip()
      url = line.replace("Static file server running on: ", "")
      url = url.replace(" (CTRL + C to shut down)", "")
      url = url.strip()
      webbrowser.open(url)

class manage_plugin_cordovaCommand(manage_cordovaCommand):

  def run(self, **kwargs):
    if kwargs.get("command_with_options") :
      if kwargs["command_with_options"][1] == "add" :
        self.window.show_input_panel("Plugin name: ", "", lambda plugin_name="": self.add_plugin(plugin_name.strip(), **kwargs), None, None)
        return
    super(manage_plugin_cordovaCommand, self).run(**kwargs)

  def add_plugin(self, plugin_name, **kwargs):
    self.placeholders[":plugin"] = plugin_name
    super(manage_plugin_cordovaCommand, self).run(**kwargs)

  def on_success(self):
    plugin_name = self.placeholders[":plugin"]
    plugin_lib_path = os.path.join(PACKAGE_PATH, "flow", "libs", "cordova", plugin_name+".js")
    plugin_lib_path_with_placeholder = os.path.join(":PACKAGE_PATH", "flow", "libs", "cordova", plugin_name+".js")
    if os.path.isfile(plugin_lib_path) :
      if self.command_with_options[1] == "add" :
        self.settings["flow_settings"]["libs"].append(plugin_lib_path_with_placeholder)
        save_project_flowconfig(self.settings["flow_settings"])
      elif self.command_with_options[1] == "remove" :
        Util.removeItemIfExists(self.settings["flow_settings"]["libs"], plugin_lib_path_with_placeholder)
        save_project_flowconfig(self.settings["flow_settings"])

class manage_add_platform_cordovaCommand(manage_cordovaCommand):

  def callback_after_get_settings(self, **kwargs):

    if not self.settings["cordova_settings"]["platform_versions"].get(self.placeholders[":platform"]) :
      self.settings["cordova_settings"]["platform_versions"][self.placeholders[":platform"]] = ""

    self.placeholders[":version"] = self.settings["cordova_settings"]["platform_versions"][self.placeholders[":platform"]]

  def on_success(self):
    save_project_setting("cordova_settings.json", self.settings["cordova_settings"])

class manage_remove_platform_cordovaCommand(manage_cordovaCommand):

  def on_success(self):
    del self.settings["cordova_settings"]["platform_versions"][self.placeholders[":platform"]]
    save_project_setting("cordova_settings.json", self.settings["cordova_settings"])
