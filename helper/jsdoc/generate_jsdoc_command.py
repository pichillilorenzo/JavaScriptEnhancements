class add_jsdoc_conf_to_curr_project_folder(sublime_plugin.WindowCommand) :
  def run(self, **args):
    settings = get_project_settings()
    if settings :
      jsdoc_conf_file = os.path.join(settings['project_dir_name'], settings['project_settings']['jsdoc']['conf_file'])
      shutil.copyfile( os.path.join(HELPER_FOLDER, "jsdoc", "conf-default.json"), jsdoc_conf_file )
  
  def is_enabled(self):
    return True if is_javascript_project() else False

class generate_jsdocCommand(sublime_plugin.WindowCommand):
  def run(self, **args):
    settings = get_project_settings()
    if settings :
      jsdoc_conf_file = os.path.join(settings['project_dir_name'], settings['project_settings']['jsdoc']['conf_file'])
      if os.path.isfile(jsdoc_conf_file) :
        node = NodeJS(check_local=True)
        panel = Util.create_and_show_panel("JSDoc", window=self.window)
        animation_loader = AnimationLoader(["[=     ]", "[ =    ]", "[   =  ]", "[    = ]", "[     =]", "[    = ]", "[   =  ]", "[ =    ]"], 0.067, "Generating docs ")
        interval_animation = RepeatedTimer(animation_loader.sec, animation_loader.animate)

        node.execute("jsdoc", ['-c', jsdoc_conf_file], is_from_bin=True, wait_terminate=False, func_stdout=self.print_panel, args_func_stdout=[panel, animation_loader, interval_animation])

      else :
        sublime.error_message("JSDOC ERROR: Can't load "+jsdoc_json+" file!\nConfiguration file REQUIRED!")
        return            

  def print_panel(self, line, process, panel, animation_loader, interval_animation) :
    
    if line != None :
      panel.run_command('print_panel_cli', {"line": line})
  
    if line == "OUTPUT-DONE":

      animation_loader.on_complete()
      interval_animation.stop()

  def is_enabled(self):
    return True if is_javascript_project() else False