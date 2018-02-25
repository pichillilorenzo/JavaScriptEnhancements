import sublime, sublime_plugin
import os
from ....libs import util
from ....libs import JavascriptEnhancementsExecuteOnTerminalCommand

class JavascriptEnhancementsNpmCliCommand(JavascriptEnhancementsExecuteOnTerminalCommand, sublime_plugin.WindowCommand):

  is_npm = True

  def prepare_command(self, **kwargs):

    self._run()

  def is_enabled(self):
    settings = util.get_project_settings()
    return True if settings and os.path.isfile( os.path.join(settings["project_dir_name"], "package.json") ) else False

  def is_visible(self):
    settings = util.get_project_settings()
    return True if settings and os.path.isfile( os.path.join(settings["project_dir_name"], "package.json") ) else False
