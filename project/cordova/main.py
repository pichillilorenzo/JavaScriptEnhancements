import sublime, sublime_plugin
import os, webbrowser
from node.main import NodeJS

cordova_platforms = [
  ["android", "Android"],
  ["ios", "iOS"]
]

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

  def ask_platform(self, func):
    global cordova_platforms
    sublime.active_window().show_quick_panel([cordova_platform[1] for cordova_platform in cordova_platforms], func)

  def append_args_execute(self):
    return get_project_settings()["cordova_settings"]["cli_global_options"]

  def is_enabled(self):
    return is_type_javascript_project("cordova")

  def is_visible(self):
    return is_type_javascript_project("cordova")

class manage_cordovaCommand(cordova_baseCommand):

  def run(self, **kwargs):

    if kwargs.get("ask_platform"):
      global cordova_platforms
      self.ask_platform(lambda index: self.set_platform(index, **kwargs))
    else :
      super(manage_cordovaCommand, self).run(**kwargs)
  
  def set_platform(self, index, **kwargs):
    if index >= 0:
      self.placeholders[":platform"] = cordova_platforms[index][0]
      super(manage_cordovaCommand, self).run(**kwargs)

class manage_serve_cordovaCommand(cordova_baseCommand):

  is_stoppable = True

  def process_communicate(self, line, process):
    if line and line.strip().startswith("Static file server running on: "):
      line = line.strip()
      url = line.replace("Static file server running on: ", "")
      url = url.replace(" (CTRL + C to shut down)", "")
      url = url.strip()
      webbrowser.open(url)

class manage_plugin_cordovaCommand(cordova_baseCommand):

  def run(self, **kwargs):
    if kwargs.get("command_with_options") :
      if kwargs["command_with_options"][1] == "add" :
        sublime.active_window().show_input_panel("Plugin name: ", "", lambda plugin_name="": self.add_plugin(plugin_name.strip(), **kwargs), None, None)
        return
      elif kwargs["command_with_options"][1] == "remove" :
        settings = get_project_settings()
        plugins_dir = os.path.join(settings["project_dir_name"], 'plugins')
        if os.path.isdir(plugins_dir) :
          plugin_list = list(filter(lambda dir: not dir.startswith('.') and os.path.isdir(os.path.join(plugins_dir, dir)), os.listdir(plugins_dir)))
          sublime.active_window().show_quick_panel(plugin_list, lambda index: self.remove_plugin(index, plugin_list, **kwargs))
          return
    super(manage_plugin_cordovaCommand, self).run(**kwargs)

  def add_plugin(self, plugin_name, **kwargs):
    self.placeholders[":plugin"] = plugin_name
    super(manage_plugin_cordovaCommand, self).run(**kwargs)

  def remove_plugin(self, index, plugin_list, **kwargs):
    if index >= 0:
      self.placeholders[":plugin"] = plugin_list[index]
      super(manage_plugin_cordovaCommand, self).run(**kwargs)

