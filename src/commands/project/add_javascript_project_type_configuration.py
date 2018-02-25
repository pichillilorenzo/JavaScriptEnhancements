import sublime, sublime_plugin
import os, shlex
from ...libs.global_vars import *
from ...libs import util
from ...libs import Hook

class JavascriptEnhancementsAddProjectTypeConfigurationCommand(sublime_plugin.WindowCommand):
  project_type = None
  settings = None

  def run(self, *args):
    self.settings = util.get_project_settings()
    if self.settings:
      self.window.show_quick_panel([ item for item in PROJECT_TYPE_SUPPORTED if item != ['Yeoman', 'yeoman'] ], self.project_type_selected)
    else:
      sublime.error_message("No JavaScript project found.")

  def project_type_selected(self, index):

    if index == -1:
      return

    self.project_type = [ item for item in PROJECT_TYPE_SUPPORTED if item != ['Yeoman', 'yeoman'] ][index][1]
    self.window.show_input_panel("Working directory:", self.settings["project_dir_name"]+os.path.sep, self.working_directory_on_done, None, None)

  def working_directory_on_done(self, working_directory):

    working_directory = shlex.quote( working_directory.strip() )

    if not os.path.isdir(working_directory):
      os.makedirs(working_directory)

    Hook.apply("add_javascript_project_configuration", working_directory, "add_project_configuration")
    Hook.apply(self.project_type+"_add_javascript_project_configuration", working_directory, "add_project_configuration")

  def is_visible(self):
    return util.is_javascript_project()

  def is_enabled(self):
    return util.is_javascript_project()
