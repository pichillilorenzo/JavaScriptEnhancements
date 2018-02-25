import sublime, sublime_plugin
import shlex, json, os
from os.path import expanduser

class Terminal():

  def __init__(self, cmd="", title="", cwd="", syntax=None, keep_open=False, window=None):

    if sublime.platform() != "windows": 
      self.cmd = cmd or "/bin/bash -l"
    else :
      self.cmd = cmd or "cmd.exe"

    self.title = title or "Terminal"
    self.cwd = cwd or expanduser("~")
    self.syntax = syntax
    self.keep_open = keep_open
    self.window = window or sublime.active_window()

  def run(self, cmd_args):
    if sublime.platform() != "windows": 
      view = self.window.new_file() 
      view.run_command('terminal_view_activate', args={"cmd": self.cmd, "title": self.title, "cwd": self.cwd, "syntax": self.syntax, "keep_open": self.keep_open} )
      self.window.run_command("terminal_view_send_string", args={"string": " ".join(cmd_args) + "\n"})
    else:
      subprocess.Popen( [self.cmd] + 
        ( ["-NoExit", "-Command"] if self.cmd.startswith("powershell") else ["/K"] )
        + ( ["$Host.UI.RawUI.WindowTitle", "=", self.title] if self.cmd.startswith("powershell") else ["title", self.title] ) 
        + ( [";", "CD", "/d", self.cwd] if self.cmd.startswith("powershell") else ["&&", "CD", "/d", self.cwd] ) 
        + ( [";"] if self.cmd.startswith("powershell") else ["&&"] ) 
        + cmd_args 
      )
