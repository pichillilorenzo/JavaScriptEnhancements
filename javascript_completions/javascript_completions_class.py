JC_SETTINGS_FOLDER_NAME = "javascript_completions"
JC_SETTINGS_FOLDER = os.path.join(PACKAGE_PATH, JC_SETTINGS_FOLDER_NAME)

class JavaScriptCompletions():
  def init(self):
    self.api = {}
    self.settings = sublime.load_settings('JavaScript-Completions.sublime-settings')
    self.API_Setup = self.settings.get('completion_active_list')

    # Caching completions
    if self.API_Setup:
      for API_Keyword in self.API_Setup:
        self.api[API_Keyword] = sublime.load_settings( API_Keyword + '.sublime-settings')
      
    if self.settings.get("enable_key_map") :
      enable_setting(JC_SETTINGS_FOLDER, "Default ("+PLATFORM+")", "sublime-keymap")
    else :
      disable_setting(JC_SETTINGS_FOLDER, "Default ("+PLATFORM+")", "sublime-keymap")