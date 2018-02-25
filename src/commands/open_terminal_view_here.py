import sublime, sublime_plugin
import os, sys 

class JavascriptEnhancementsOpenTermivalViewHereCommand(sublime_plugin.WindowCommand):
  def run(self, **args):
    window = self.window
    view = window.active_view()

    paths = args.get("paths") if "paths" in args else []

    path = self.get_path(paths)
    if not path:
      return

    if os.path.isfile(path):
      path = os.path.dirname(path)

    window.run_command("set_layout", args={"cells": [[0, 0, 1, 1], [0, 1, 1, 2]], "cols": [0.0, 1.0], "rows": [0.0, 0.7, 1.0]})
    window.focus_group(1)
    terminal_view = window.new_file() 
    args = {"cmd": "/bin/bash -l", "title": "JavaScript Enhancements Terminal (bash)", "cwd": path, "syntax": None, "keep_open": False} 
    terminal_view.run_command('terminal_view_activate', args=args)

  def get_path(self, paths):
    if paths:
      return paths[0]
    elif self.window.active_view() and self.window.active_view().file_name():
      return self.window.active_view().file_name()
    elif self.window.folders():
      return self.window.folders()[0]
    else:
      sublime.error_message('JavaScript Enhancements: No place to open TerminalView to.')
      return False

  def is_visible(self):
    if sublime.platform() != 'windows':
      try:
        sys.modules["TerminalView"]
        return True
      except Exception as err:
        pass
    return False

  def is_enabled(self):
    if sublime.platform() != 'windows':
      try:
        sys.modules["TerminalView"]
        return True
      except Exception as err:
        pass
    return False