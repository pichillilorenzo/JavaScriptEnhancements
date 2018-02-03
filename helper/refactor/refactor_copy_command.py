import sublime, sublime_plugin
import os, shutil

class RefactorCopyCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    file_name = view.file_name()

    if not file_name:
      return

    view.window().show_input_panel("Copy to", file_name, self.on_done, None, None)

  def on_done(self, answer):
    view = self.view
    file_name = view.file_name()
    answer = answer.strip()

    if os.path.isfile(answer):
      if not sublime.ok_cancel_dialog(answer + " already exists.", "Copy anyway"):
        return

    if not os.path.isdir(os.path.dirname(answer)):
      os.makedirs(os.path.dirname(answer))

    shutil.copy(file_name, answer)

  def is_enabled(self, **args) :
    view = self.view
    file_name = view.file_name()
    if not file_name or not Util.selection_in_js_scope(view):
      return False
    return True

  def is_visible(self, **args) :
    view = self.view
    file_name = view.file_name()
    if not file_name or not Util.selection_in_js_scope(view):
      return False
    return True