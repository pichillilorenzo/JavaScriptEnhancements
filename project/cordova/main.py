import sublime, sublime_plugin
import os
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
  def __init__(self, *args, **kwargs):  
    self.cli = "cordova"
    super(cordova_baseCommand, self).__init__(*args, **kwargs)

  def is_enabled(self):
    return is_type_javascript_project("cordova")

  def is_visible(self):
    return is_type_javascript_project("cordova")

class manage_cordovaCommand(cordova_baseCommand):

  def run(self, **kwargs):
    kwargs["cli"] = self.cli
    super(manage_cordovaCommand, self).run(**kwargs)
    

class manage_plugin_cordovaCommand(cordova_baseCommand):

  def run(self, **kwargs):
    kwargs["cli"] = self.cli
    super(manage_plugin_cordovaCommand, self).run(**kwargs)

  def manage(self) :
    action = self.command_with_options[1]
    if action == "add" :
      sublime.active_window().show_input_panel("Plugin name: ", "", lambda plugin_name: exec('self.command_with_options[2] = plugin_name') or exec('self.status_message = self.status_message % (plugin_name)') or super(manage_plugin_cordovaCommand, self).manage(), None, None)
    else :
      plugins_dir = os.path.join(self.settings["project_dir_name"], 'plugins')
      if os.path.isdir(plugins_dir) :
        self.plugin_list = list(filter(lambda dir: not dir.startswith('.') and os.path.isdir(os.path.join(plugins_dir, dir)), os.listdir(plugins_dir)))
        sublime.active_window().show_quick_panel(self.plugin_list, lambda index: index >= 0 and exec('self.command_with_options[2] = self.plugin_list[index]') or exec('self.status_message = self.status_message % (self.plugin_list[index])') or super(manage_plugin_cordovaCommand, self).manage())
