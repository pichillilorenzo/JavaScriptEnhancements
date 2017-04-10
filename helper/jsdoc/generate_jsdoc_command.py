class add_jsdoc_conf_to_curr_project_folder(sublime_plugin.WindowCommand) :
  def run(self, **args):
    window = self.window
    contextual_keys = window.extract_variables()
    folder_path = contextual_keys.get("folder")
    if folder_path and os.path.isdir(folder_path) :
      shutil.copyfile(os.path.join(H_SETTINGS_FOLDER, "jsdoc", "conf-default.json"), os.path.join(folder_path, javascriptCompletions.get("jsdoc_conf_file")))
      
  def is_enabled(self):
    window = self.window
    contextual_keys = window.extract_variables()
    folder_path = contextual_keys.get("folder")
    return True if folder_path and os.path.isdir(folder_path) else False

class generate_jsdocCommand(sublime_plugin.WindowCommand):
  def run(self, **args):
    window = self.window
    contextual_keys = window.extract_variables()
    folder_path = contextual_keys.get("folder")
    if folder_path and os.path.isdir(folder_path) :
      jsdoc_json = os.path.join(folder_path, javascriptCompletions.get("jsdoc_conf_file"))

      if os.path.isfile(jsdoc_json) :
        thread = Util.create_and_start_thread(self.exec_node, "JSDocGenerating", [folder_path, ["-c",jsdoc_json]])
      else :
        sublime.error_message("ERROR: Can't load "+jsdoc_json+" file!\nConfiguration file REQUIRED!")
        return            

  def exec_node(self, folder_path, node_command_args) :
    node = NodeJS(check_local=True)
    animation_loader = AnimationLoader(["[=     ]", "[ =    ]", "[   =  ]", "[    = ]", "[     =]", "[    = ]", "[   =  ]", "[ =    ]"], 0.067, "Generating docs ")
    interval_animation = RepeatedTimer(animation_loader.sec, animation_loader.animate)
    result = node.execute("jsdoc", node_command_args, is_from_bin=True, chdir=folder_path)

    if not result[0] :
      sublime.error_message(result[1])
      
    elif result[1].startswith("There are no input files to process") :
      sublime.error_message(result[1])

    animation_loader.on_complete()
    interval_animation.stop()

  def is_enabled(self):
    window = self.window
    contextual_keys = window.extract_variables()
    folder_path = contextual_keys.get("folder")
    return True if folder_path and os.path.isdir(folder_path) else False