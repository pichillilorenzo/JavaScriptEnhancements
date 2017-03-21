import sublime, sublime_plugin
import os
from node.main import NodeJS

MENU_CORDOVA_PATH = os.path.join(PACKAGE_PATH, "project", "cordova", "Main.sublime-menu")
MENU_CORDOVA_DISABLED_PATH = os.path.join(PACKAGE_PATH, "project", "cordova", "Main_disabled.sublime-menu")

class enable_menu_cordovaViewEventListener(sublime_plugin.ViewEventListener):
  def on_activated_async(self):
    if is_type_javascript_project("cordova") :
      if os.path.isfile(MENU_CORDOVA_DISABLED_PATH):
        os.rename(MENU_CORDOVA_DISABLED_PATH, MENU_CORDOVA_PATH)
    else :
      if os.path.isfile(MENU_CORDOVA_PATH):
        os.rename(MENU_CORDOVA_PATH, MENU_CORDOVA_DISABLED_PATH)

class print_panel_cordovaCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    self.view.set_read_only(False)
    self.view.insert(edit, self.view.size(), args.get("line"))
    self.view.show_at_center(self.view.size())
    self.view.set_read_only(True)

class add_platform_cordovaCommand(sublime_plugin.WindowCommand):
  panel = None
  def run(self, **kwargs):
    settings = get_project_settings()
    if settings:
      os_system = kwargs.get("os")
      if os_system :
        sublime.set_timeout_async(lambda: self.add_platform(settings, os_system))

  def add_platform(self, settings, os_system):
    sublime.active_window().status_message("Cordova: adding "+os_system+" platform...")
    node = NodeJS()
    self.panel = self.window.create_output_panel("panel_emulate_cordova", False)
    self.window.run_command("show_panel", {"panel": "output.panel_emulate_cordova"})
    node.execute('cordova', ["platform", "add", os_system, "--save"], is_from_bin=True, chdir=settings["project_dir_name"], wait_terminate=False, func_stdout=self.print_panel)
  
  def print_panel(self, line):
    self.panel.run_command("print_panel_cordova", {"line": line})

  def is_enabled(self):
    return is_type_javascript_project("cordova")

  def is_visible(self):
    return is_type_javascript_project("cordova")

class emulate_cordovaCommand(sublime_plugin.WindowCommand):

  panel = None
  def run(self, **kwargs):
    settings = get_project_settings()
    if settings:
      os_emulator = kwargs.get("os")
      if os_emulator :
        sublime.set_timeout_async(lambda: self.emulate(settings, os_emulator))

  def emulate(self, settings, os_emulator):
    sublime.active_window().status_message("Cordova: launching "+os_emulator+" platform...")
    node = NodeJS()
    self.panel = self.window.create_output_panel("panel_emulate_cordova", False)
    self.window.run_command("show_panel", {"panel": "output.panel_emulate_cordova"})
    node.execute('cordova', ["run", os_emulator], is_from_bin=True, chdir=settings["project_dir_name"], wait_terminate=False, func_stdout=self.print_panel)

  def print_panel(self, line):
    self.panel.run_command("print_panel_cordova", {"line": line})

  def is_enabled(self):
    return is_type_javascript_project("cordova")

  def is_visible(self):
    return is_type_javascript_project("cordova")