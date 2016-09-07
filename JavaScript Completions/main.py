import sublime, sublime_plugin
import string


class JavaScriptCompletionsPackage():
  def init(self):
    self.api = {}
    self.settings = sublime.load_settings('JavaScript-Completions.sublime-settings')
    self.API_Setup = self.settings.get('completion_active_list')

    # Caching completions
    if self.API_Setup:
      for API_Keyword in self.API_Setup:
        self.api[API_Keyword] = sublime.load_settings( API_Keyword + '.sublime-settings')

# In Sublime Text 3 things are loaded async, using plugin_loaded() callback before try accessing.
javascriptCompletions = JavaScriptCompletionsPackage()

if int(sublime.version()) < 3000:
  javascriptCompletions.init()
else:
  def plugin_loaded():
    global javascriptCompletions
    javascriptCompletions.init()



class JavaScriptCompletionsPackageEventListener(sublime_plugin.EventListener):
  global javascriptCompletions

  def on_query_completions(self, view, prefix, locations):
    self.completions = []

    for API_Keyword in javascriptCompletions.api:
      # If completion active
      if (javascriptCompletions.API_Setup and javascriptCompletions.API_Setup.get(API_Keyword)):
        scope = javascriptCompletions.api[API_Keyword].get('scope')
        if scope and view.match_selector(locations[0], scope):
          self.completions += javascriptCompletions.api[API_Keyword].get('completions')

    if not self.completions:
      return []

    # extend word-completions to auto-completions
    compDefault = [view.extract_completions(prefix)]
    compDefault = [(item, item) for sublist in compDefault for item in sublist if len(item) > 3]
    compDefault = list(set(compDefault))
    completions = list(self.completions)
    completions = [tuple(attr) for attr in self.completions]
    completions.extend(compDefault)
    return (completions)