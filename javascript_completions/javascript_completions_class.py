JC_SETTINGS_FOLDER_NAME = "javascript_completions"
JC_SETTINGS_FOLDER = os.path.join(PACKAGE_PATH, JC_SETTINGS_FOLDER_NAME)

class JavaScriptCompletions():
  def init(self):
    self.api = {}
    self.API_Setup = sublime.load_settings('JavaScript-Completions.sublime-settings').get('completion_active_list')

    # Caching completions
    if self.API_Setup:
      for API_Keyword in self.API_Setup:
        self.api[API_Keyword] = sublime.load_settings( API_Keyword + '.sublime-settings')

  def get(self, key):
    return sublime.load_settings('JavaScript-Completions.sublime-settings').get(key)