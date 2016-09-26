H_SETTINGS_FOLDER_NAME = "helper"
H_SETTINGS_FOLDER = os.path.join(PACKAGE_PATH, H_SETTINGS_FOLDER_NAME)

class JavaScriptCompletionsHelper():

  def init(self):
    self.api = {}
    self.settings = sublime.load_settings('helper.sublime-settings')