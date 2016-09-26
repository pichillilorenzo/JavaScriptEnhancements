class add_jsdoc_settings_to_curr_project_folder(sublime_plugin.WindowCommand) :
  def run(self, **args):
    window = self.window
    contextual_keys = window.extract_variables()
    folder_path = contextual_keys.get("folder")
    if folder_path and os.path.isdir(folder_path) :
      shutil.copyfile(os.path.join(H_SETTINGS_FOLDER, "jsdoc", "jsdoc-settings-default.json"), os.path.join(folder_path, "jsdoc-settings.json"))
      
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
      jsdoc_json = os.path.join(folder_path, "jsdoc-settings.json")
      jsdoc_settings = dict()
      node_command_args = list()

      if os.path.isfile(jsdoc_json) :
         with open(jsdoc_json) as json_file: 
          try :
            jsdoc_settings = json.load(json_file)
          except Exception as e:
            sublime.error_message("ERROR: Can't load "+jsdoc_json+" file!")
            return           

      jsdoc_conf_path_file = os.path.join(folder_path, jsdoc_settings.get("jsdoc_conf_file")) if jsdoc_settings.get("jsdoc_conf_file") else os.path.join(folder_path, "conf.json")
      if os.path.isfile(jsdoc_conf_path_file) :
        node_command_args.append("-c")
        node_command_args.append(jsdoc_conf_path_file)
      else :
        sublime.error_message("ERROR: Can't load "+jsdoc_conf_path_file+" file!\nConfiguration file REQUIRED!")
        return  

      display_symbols_access_property = jsdoc_settings.get("display_symbols_access_property") if jsdoc_settings.get("display_symbols_access_property") in ["private", "protected", "public", "undefined", "all"] else "all"
      node_command_args.append("-a")
      node_command_args.append(display_symbols_access_property)

      destination_folder = os.path.join(folder_path, jsdoc_settings.get("destination_folder")) if jsdoc_settings.get("destination_folder") else os.path.join(folder_path, "out")
      node_command_args.append("-d")
      node_command_args.append(destination_folder)

      if jsdoc_settings.get("include_symbols_marked_with_the_private_tag") :
        node_command_args.append("-p")

      if jsdoc_settings.get("pedantic_mode") :
        node_command_args.append("--pedantic")

      query_string_to_parse_and_store_in_global_variable = jsdoc_settings.get("query_string_to_parse_and_store_in_global_variable")
      if query_string_to_parse_and_store_in_global_variable :
        node_command_args.append("-q")
        node_command_args.append(query_string_to_parse_and_store_in_global_variable)

      tutorials_path = os.path.join(folder_path, jsdoc_settings.get("tutorials_path")) if jsdoc_settings.get("tutorials_path") else ""
      if tutorials_path :
        node_command_args.append("-u")
        node_command_args.append(tutorials_path)

      encoding_when_reading_all_source_files = jsdoc_settings.get("encoding_when_reading_all_source_files") or "utf-8";
      node_command_args.append("-e")
      node_command_args.append(encoding_when_reading_all_source_files)

      template_path = os.path.join(folder_path, jsdoc_settings.get("template_path")) if jsdoc_settings.get("template_path") else "templates/default";
      node_command_args.append("-t")
      node_command_args.append(template_path)

      if jsdoc_settings.get("search_within_subdirectories") :
        node_command_args.append("-r")

      thread = Util.create_and_start_thread(self.exec_node, "JSDocGenerating", [folder_path, node_command_args])

  def exec_node(self, folder_path, node_command_args) :
    os.chdir(folder_path)
    from node.main import NodeJS
    node = NodeJS()
    animation_loader = AnimationLoader(["[=     ]", "[ =    ]", "[   =  ]", "[    = ]", "[     =]", "[    = ]", "[   =  ]", "[ =    ]"], 0.067, "Generating docs ")
    interval_animation = RepeatedTimer(animation_loader.sec, animation_loader.animate)
    result = node.execute("jsdoc", node_command_args, True)
    if not result[0] :
      sublime.error_message(result[1])
    animation_loader.on_complete()
    interval_animation.stop()

  def is_enabled(self):
    window = self.window
    contextual_keys = window.extract_variables()
    folder_path = contextual_keys.get("folder")
    return True if folder_path and os.path.isdir(folder_path) else False