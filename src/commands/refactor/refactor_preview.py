import sublime, sublime_plugin
from ...libs import util

class RefactorPreview():
  view = None
  title = None
  window = None

  def __init__(self, title):
    self.title = title
    self.window = sublime.active_window()
    self.view = None
    for v in self.window.views():
      if v.name() == self.title:
        self.view = v
        self.view.run_command("javascript_enhancements_erase_text_view")
        self.window.focus_view(self.view)
        break

    if not self.view:       
      self.window.focus_group(1)
      self.view = self.window.new_file()
      self.view.set_name(self.title)
      self.view.set_syntax_file('Packages/Default/Find Results.hidden-tmLanguage')
      self.view.set_scratch(True)

  def append_text(self, text):
    if self.view:
      self.view.run_command("javascript_enhancements_append_text_view", args={"text": text})

  @staticmethod
  def close(title):
    window = sublime.active_window()
    for v in window.views():
      if v.name() == title:
        v.close()
        break