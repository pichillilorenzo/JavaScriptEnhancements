import sublime, sublime_plugin
import os, webbrowser, shlex, json

def create_ionic_project(json_data):

  sublime.active_window().run_command('create_new_project_ionic', {'json_data': json_data})

  return json_data

Hook.add("ionic_create_new_project", create_ionic_project)

Hook.add("ionic_add_new_project_type", create_ionic_project)

class enable_menu_ionicEventListener(enable_menu_project_typeEventListener):
  project_type = "ionic"
  path = os.path.join(PROJECT_FOLDER, "ionic", "Main.sublime-menu")
  path_disabled = os.path.join(PROJECT_FOLDER, "ionic", "Main_disabled.sublime-menu")

class ionic_baseCommand(manage_cliCommand):
  cli = "ionic"
  name_cli = "Ionic"
  bin_path = ""
  can_add_platform = False
  platform_list = []
  platform_list_on_success = None
  can_add_plugin = False
  plugin_list = []
  plugin_list_on_success = None

  def ask_platform(self, type, func):
    self.platform_list = []
    self.can_add_platform = False
    self.platform_list_on_success = func
    self.settings = get_project_settings()
    if self.settings :

      sublime.status_message(self.name_cli+": getting platform list...")

      node = NodeJS(check_local = True)
      cli = self.settings["ionic_settings"]["cli_custom_path"]

      if self.settings["ionic_settings"]["use_local_cli"] :
        bin_path = os.path.join(self.settings["settings_dir_name"], "node_modules", ".bin")
        node.execute(self.cli, ["platform", "list"], is_from_bin=True, bin_path=bin_path, chdir=self.settings["ionic_settings"]["working_directory"], wait_terminate=False, func_stdout=(self.get_list_installed_platform_window_panel if type == "installed" else self.get_list_available_platform_window_panel))
      elif cli :
        Util.execute(cli, ["platform", "list"], chdir=self.settings["ionic_settings"]["working_directory"], wait_terminate=False, func_stdout=(self.get_list_installed_platform_window_panel if type == "installed" else self.get_list_available_platform_window_panel))
      else :
        sublime.error_message('ERROR: No global or local ionic command specified!')
        return
    else :
      sublime.error_message("Error: can't get project settings")

  def get_list_installed_platform_window_panel(self, line, process):

    self.get_platform_list("installed", line, process, True)

  def get_list_available_platform_window_panel(self, line, process):

    self.get_platform_list("available", line, process, True)

  def get_platform_list(self, type, line, process, show_panel = False):
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
        if show_panel :
          self.window.show_quick_panel([ionic_platform for ionic_platform in self.platform_list], self.platform_list_on_success)
        elif self.platform_list_on_success :
          self.platform_list_on_success()
      else :
        if type == "installed" :
          sublime.message_dialog(self.name_cli+": No platforms installed")
        elif type == "available" :  
          sublime.message_dialog(self.name_cli+": No more platforms available")

  def ask_plugin(self, func):
    self.plugin_list = []
    self.can_add_plugin = False
    self.plugin_list_on_success = func
    self.settings = get_project_settings()
    if self.settings :

      sublime.status_message(self.name_cli+": getting plugin list...")

      node = NodeJS(check_local = True)
      cli = self.settings["ionic_settings"]["cli_custom_path"]

      if self.settings["ionic_settings"]["use_local_cli"] :
        bin_path = os.path.join(self.settings["settings_dir_name"], "node_modules", ".bin")
        node.execute(self.cli, ["plugin", "list"], is_from_bin=True, bin_path=bin_path, chdir=self.settings["ionic_settings"]["working_directory"], wait_terminate=False, func_stdout=self.get_plugin_list_window_panel)
      elif cli :
        Util.execute(cli, ["plugin", "list"], chdir=self.settings["ionic_settings"]["working_directory"], wait_terminate=False, func_stdout=self.get_plugin_list_window_panel)
      else :
        sublime.error_message('ERROR: No global or local ionic command specified!')
        return
    else :
      sublime.error_message("Error: can't get project settings")

  def get_plugin_list_window_panel(self, line, process):
    self.get_plugin_list(line, process, True)

  def get_plugin_list(self, line, process, show_panel = False):
    if line == "OUTPUT-DONE" or line == "OUTPUT-SUCCESS" or line == "OUTPUT-ERROR" :
      self.can_add_plugin = False
    else :
      self.can_add_plugin = True

    if line and self.can_add_plugin and line.strip() :
      self.plugin_list.append(line.strip().split(" ")[0])
    if line == "OUTPUT-DONE" :
      if self.plugin_list:
        if show_panel :
          self.window.show_quick_panel([cordova_plugin for cordova_plugin in self.plugin_list], self.plugin_list_on_success)
        elif self.plugin_list_on_success :
          self.plugin_list_on_success()
      else :
        sublime.message_dialog(self.name_cli+": No plugins installed")

  def append_args_execute(self):
    custom_args = []
    custom_args = custom_args + self.settings["ionic_settings"]["cli_global_options"]
    command = self.command_with_options[0]

    if command == "platform" or command == "build" or command == "run" or command == "emulate" :
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
      
    return custom_args

  def before_execute(self):

    if self.settings["ionic_settings"]["use_local_cli"] :
      self.bin_path = os.path.join(self.settings["settings_dir_name"], "node_modules", ".bin")
      self.is_node = True
    elif self.settings["ionic_settings"]["cli_custom_path"] :
      self.cli = self.settings["ionic_settings"]["cli_custom_path"]
      self.is_node = False
    else :
      sublime.error_message('ERROR: No global or local ionic command specified!')
      return

  def is_enabled(self):
    return is_type_javascript_project("ionic")

  def is_visible(self):
    return is_type_javascript_project("ionic")

class create_new_project_ionicCommand(ionic_baseCommand):

  def run(self, **kwargs):

    json_data = kwargs.get('json_data')
    project_data = json_data["project_data"]
    create_options = []

    if "create_options" in project_data and project_data["create_options"]:
      create_options = project_data["create_options"]

    self.custom_project_dir_name = project_data["project_dir_name"]

    self.command_with_options = ["start", "temp"] + create_options

    super(create_new_project_ionicCommand, self).run(**kwargs)

  def on_done(self) :
    
    Util.move_content_to_parent_folder(os.path.join(self.settings["ionic_settings"]["working_directory"], "temp"))
    open_project_folder(self.settings['project_file_name'])

  def is_enabled(self):
    return True

  def is_visible(self):
    return True

class manage_ionicCommand(ionic_baseCommand):

  def run(self, **kwargs):
    flag = False

    if kwargs.get("ask_platform") and kwargs.get("ask_platform_type"):
      self.ask_platform(kwargs.get("ask_platform_type"), lambda index: self.set_platform(index, **kwargs))
      flag = True

    if kwargs.get("ask_plugin"):
      self.ask_plugin(lambda index: self.set_plugin(index, **kwargs))
      flag = True

    if not flag :
      super(manage_ionicCommand, self).run(**kwargs)

  def set_platform(self, index, **kwargs):
    if index >= 0:
      self.placeholders[":platform"] = self.platform_list[index]
      super(manage_ionicCommand, self).run(**kwargs)

  def set_plugin(self, index, **kwargs):
    if index >= 0:
      self.placeholders[":plugin"] = self.plugin_list[index]
      super(manage_ionicCommand, self).run(**kwargs)

class manage_serve_ionicCommand(ionic_baseCommand):

  def run(self, **kwargs):
    super(manage_serve_ionicCommand, self).run(**kwargs)

class manage_plugin_ionicCommand(manage_ionicCommand):

  def run(self, **kwargs):
    if kwargs.get("command_with_options") :
      if kwargs["command_with_options"][1] == "add" :
        self.window.show_input_panel("Plugin name: ", "", lambda plugin_name="": self.add_plugin(plugin_name.strip(), **kwargs), None, None)
        return
    super(manage_plugin_ionicCommand, self).run(**kwargs)

  def add_plugin(self, plugin_name, **kwargs):
    self.placeholders[":plugin"] = plugin_name
    super(manage_plugin_ionicCommand, self).run(**kwargs)

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

class manage_add_platform_ionicCommand(manage_ionicCommand):

  def callback_after_get_settings(self, **kwargs):

    self.placeholders[":version"] = Util.getDictItemIfExists(self.settings["ionic_settings"]["platform_version_options"], self.placeholders[":platform"]) or ""

  def on_success(self):
    if not self.placeholders[":platform"] in self.settings["ionic_settings"]["installed_platform"] :
      self.settings["ionic_settings"]["installed_platform"].append(self.placeholders[":platform"])
    save_project_setting("ionic_settings.json", self.settings["ionic_settings"])

class manage_remove_platform_ionicCommand(manage_ionicCommand):

  def on_success(self):
    Util.removeItemIfExists(self.settings["ionic_settings"]["installed_platform"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["ionic_settings"]["platform_version_options"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["ionic_settings"]["platform_compile_options"]["debug"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["ionic_settings"]["platform_compile_options"]["release"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["ionic_settings"]["platform_build_options"]["debug"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["ionic_settings"]["platform_build_options"]["release"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["ionic_settings"]["platform_run_options"]["debug"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["ionic_settings"]["platform_run_options"]["release"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["ionic_settings"]["platform_emulate_options"]["debug"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["ionic_settings"]["platform_emulate_options"]["release"], self.placeholders[":platform"])
    save_project_setting("ionic_settings.json", self.settings["ionic_settings"])

class sync_ionic_projectCommand(ionic_baseCommand):

  platform_list = []
  plugin_list = []

  def run(self, **kwargs):
    self.platform_list = []
    self.plugin_list = []
    self.settings = get_project_settings()

    if self.settings :
      sublime.status_message(self.name_cli+": synchronizing project...")
      
      node = NodeJS(check_local = True)
      cli = self.settings["ionic_settings"]["cli_custom_path"]

      if self.settings["ionic_settings"]["use_local_cli"] :
        bin_path = os.path.join(self.settings["settings_dir_name"], "node_modules", ".bin")
        node.execute(self.cli, ["platform", "list"], is_from_bin=True, bin_path=bin_path, chdir=self.settings["ionic_settings"]["working_directory"], wait_terminate=False, func_stdout=lambda line, process: self.get_platform_list("installed", line, process))
        node.execute(self.cli, ["plugin", "list"], is_from_bin=True, bin_path=bin_path, chdir=self.settings["ionic_settings"]["working_directory"], wait_terminate=False, func_stdout=self.get_plugin_list)
      elif cli :
        Util.execute(cli, ["platform", "list"], chdir=self.settings["ionic_settings"]["working_directory"], wait_terminate=False, func_stdout=lambda line, process: self.get_platform_list("installed", line, process))
        Util.execute(cli, ["plugin", "list"], chdir=self.settings["ionic_settings"]["working_directory"], wait_terminate=False, func_stdout=self.get_plugin_list)
      else :
        sublime.error_message('ERROR: No global or local ionic command specified!')
        return

    else :
      sublime.error_message("Error: can't get project settings")

  def platform_list_on_success(self):
    self.settings["ionic_settings"]["installed_platform"] = []
    for platform_name in self.platform_list:
      self.settings["ionic_settings"]["installed_platform"].append(platform_name)

    save_project_setting("ionic_settings.json", self.settings["ionic_settings"])
    sublime.status_message(self.name_cli+": platforms synchronized")

  def plugin_list_on_success(self):
    plugin_list_to_remove = []
    for lib in self.settings["flow_settings"]["libs"]:
      if lib.startswith(":PACKAGE_PATH/flow/libs/cordova/") and lib != ":PACKAGE_PATH/flow/libs/cordova/cordova.js":
        plugin_list_to_remove.append(lib)
    for lib in plugin_list_to_remove:
      self.settings["flow_settings"]["libs"].remove(lib)

    for plugin_name in self.plugin_list:
      plugin_lib_path = os.path.join(PACKAGE_PATH, "flow", "libs", "cordova", plugin_name+".js")
      plugin_lib_path_with_placeholder = os.path.join(":PACKAGE_PATH", "flow", "libs", "cordova", plugin_name+".js")
      if os.path.isfile(plugin_lib_path) :
        self.settings["flow_settings"]["libs"].append(plugin_lib_path_with_placeholder)

    save_project_flowconfig(self.settings["flow_settings"])
    sublime.status_message(self.name_cli+": plugins synchronized")
