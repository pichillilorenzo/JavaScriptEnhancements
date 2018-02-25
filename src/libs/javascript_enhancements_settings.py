import sublime 

class JavaScriptEnhancements():

  def get(self, key):
    return sublime.load_settings('JavaScript Enhancements.sublime-settings').get(key)

javaScriptEnhancements = JavaScriptEnhancements()