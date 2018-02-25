import sublime, sublime_plugin

class JavascriptEnhancementsEraseTextViewCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    region = sublime.Region(0, view.size())
    view.erase(edit, region)
