import sublime, sublime_plugin
import os, shutil
from ...libs import util

class JavascriptEnhancementsAddJsdocConfCommand(sublime_plugin.WindowCommand) :
  def run(self, **args):
    settings = util.get_project_settings()
    if settings :
      if not settings['project_settings']['jsdoc']['conf_file']:
        settings['project_settings']['jsdoc']['conf_file'] = "conf.json"
        util.save_project_setting('project_settings.json', settings['project_settings'])
      jsdoc_conf_file = os.path.join(settings['project_dir_name'], settings['project_settings']['jsdoc']['conf_file'])
      shutil.copyfile( os.path.join(os.path.dirname(os.path.abspath(__file__)), "conf-default.json"), jsdoc_conf_file )
  
  def is_enabled(self):
    return True if util.is_javascript_project() else False