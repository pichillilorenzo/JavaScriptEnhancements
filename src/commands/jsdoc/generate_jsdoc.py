import sublime, sublime_plugin
import os
from ...libs import util
from ...libs import JavascriptEnhancementsExecuteOnTerminalCommand

class JavascriptEnhancementsGenerateJsdocCommand(JavascriptEnhancementsExecuteOnTerminalCommand, sublime_plugin.WindowCommand):

  is_node = True
  is_bin_path = True

  def prepare_command(self):

    jsdoc_conf_file = os.path.join(self.settings['project_dir_name'], self.settings['project_settings']['jsdoc']['conf_file'])
    if os.path.isfile(jsdoc_conf_file) :
      self.command = ["jsdoc", "-c", jsdoc_conf_file]

    else :
      sublime.error_message("JSDOC ERROR: Can't load "+jsdoc_conf_file+" file!\nConfiguration file REQUIRED!")
      return  

    self._run()

  def _run(self):
    super(JavascriptEnhancementsGenerateJsdocCommand, self)._run()

  def is_enabled(self):
    return True if util.is_javascript_project() else False