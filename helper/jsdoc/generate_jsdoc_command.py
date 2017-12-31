class add_jsdoc_conf(sublime_plugin.WindowCommand) :
  def run(self, **args):
    settings = get_project_settings()
    if settings :
      if not settings['project_settings']['jsdoc']['conf_file']:
        settings['project_settings']['jsdoc']['conf_file'] = "conf.json"
        save_project_setting('project_settings.json', settings['project_settings'])
      jsdoc_conf_file = os.path.join(settings['project_dir_name'], settings['project_settings']['jsdoc']['conf_file'])
      shutil.copyfile( os.path.join(HELPER_FOLDER, "jsdoc", "conf-default.json"), jsdoc_conf_file )
  
  def is_enabled(self):
    return True if is_javascript_project() else False

class generate_jsdocCommand(manage_cliCommand):

  isNode = True
  isBinPath = True

  def prepare_command(self):

    jsdoc_conf_file = self.settings['project_settings']['jsdoc']['conf_file']
    if os.path.isfile(jsdoc_conf_file) :
      self.command = ["jsdoc", "-c", jsdoc_conf_file]

    else :
      sublime.error_message("JSDOC ERROR: Can't load "+jsdoc_conf_file+" file!\nConfiguration file REQUIRED!")
      return  

    self._run()

  def _run(self):
    super(generate_jsdocCommand, self)._run()

  def is_enabled(self):
    return True if is_javascript_project() else False