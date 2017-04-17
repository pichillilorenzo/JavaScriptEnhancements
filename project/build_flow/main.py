class enable_menu_build_flowEventListener(enable_menu_project_typeEventListener):
  path = os.path.join(PROJECT_FOLDER, "build_flow", "Main.sublime-menu")
  path_disabled = os.path.join(PROJECT_FOLDER, "build_flow", "Main_disabled.sublime-menu")

class build_flowCommand(manage_cliCommand):
  cli = "flow-remove-types"
  name_cli = "Flow Remove Types"
  bin_path = ""

  def callback_after_get_settings(self, **kwargs):
    self.placeholders[":source_folder"] = self.settings["project_settings"]["build_flow"]["source_folder"]
    self.placeholders[":destination_folder"] = self.settings["project_settings"]["build_flow"]["destination_folder"]

  def append_args_execute(self) :
    custom_args = []
    custom_args = custom_args + self.settings["project_settings"]["build_flow"]["options"]

    return custom_args

  def is_enabled(self) :
    settings = get_project_settings()
    if settings and settings["project_settings"]["build_flow"]["source_folder"] and settings["project_settings"]["build_flow"]["destination_folder"] :
      return True
    return False