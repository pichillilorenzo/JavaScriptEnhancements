import shlex, shutil

class enable_menu_build_flowEventListener(enable_menu_project_typeEventListener):
  path = os.path.join(PROJECT_FOLDER, "build_flow", "Main.sublime-menu")
  path_disabled = os.path.join(PROJECT_FOLDER, "build_flow", "Main_disabled.sublime-menu")

class build_flowCommand(manage_cliCommand):

  isNode = True
  isBinPath = True

  def prepare_command(self, **kwargs):

    # dest_folder = self.settings["project_settings"]["build_flow"]["destination_folder"]

    # if os.path.isabs(dest_folder):
    #   shutil.rmtree(dest_folder)
    # elif os.path.exists(os.path.join(self.settings["project_dir_name"], dest_folder)):
    #   shutil.rmtree(os.path.join(self.settings["project_dir_name"], dest_folder))

    self.placeholders[":source_folders"] = " ".join(self.settings["project_settings"]["build_flow"]["source_folders"])
    self.placeholders[":destination_folder"] = self.settings["project_settings"]["build_flow"]["destination_folder"]
    self.command += self.settings["project_settings"]["build_flow"]["options"]
    self.command = self.substitute_placeholders(self.command)

    if self.settings["project_settings"]["flow_remove_types_custom_path"]:
      self.isBinPath = False
      self.command[0] = shlex.quote(self.settings["project_settings"]["flow_remove_types_custom_path"])

    self._run()

  def _run(self):
    super(build_flowCommand, self)._run()

  def is_enabled(self) :
    settings = get_project_settings()
    if settings and len(settings["project_settings"]["build_flow"]["source_folders"]) > 0 and settings["project_settings"]["build_flow"]["destination_folder"] :
      return True
    return False

class build_flow_on_save(sublime_plugin.EventListener):

  def on_post_save_async(self, view):
    settings = get_project_settings()
    if Util.selection_in_js_scope(view) and settings and settings["project_settings"]["build_flow"]["on_save"] and len(settings["project_settings"]["build_flow"]["source_folders"]) > 0 and settings["project_settings"]["build_flow"]["destination_folder"] :
      view.window().run_command("build_flow", args={"command": ["flow-remove-types", ":source_folders", "--out-dir", ":destination_folder"]})

