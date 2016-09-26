EJ_SETTINGS_FOLDER_NAME = "evaluate_javascript"
EJ_SETTINGS_FOLDER = os.path.join(PACKAGE_PATH, EJ_SETTINGS_FOLDER_NAME)

class EvaluateJavascript():

  def init(self):
    self.api = {}
    self.settings = sublime.load_settings('Evaluate-JavaScript.sublime-settings')

    if self.settings.get("enable_context_menu_option") :
      enable_setting(EJ_SETTINGS_FOLDER, "Context", "sublime-menu")
    else :
      disable_setting(EJ_SETTINGS_FOLDER, "Context", "sublime-menu")

    if self.settings.get("enable_key_map") :
      enable_setting(EJ_SETTINGS_FOLDER, "Default ("+PLATFORM+")", "sublime-keymap")
    else :
      disable_setting(EJ_SETTINGS_FOLDER, "Default ("+PLATFORM+")", "sublime-keymap")