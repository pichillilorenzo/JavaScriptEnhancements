import sublime, sublime_plugin
import shlex, json, os

class manage_cliCommand(sublime_plugin.WindowCommand):
  
  custom_name = ""
  cli = ""
  path_cli = ""
  settings_name = ""
  placeholders = {}
  settings = None
  command = []
  working_directory = ""
  isNode = False
  isNpm = False
  isBinPath = False
  alsoNonProject = False

  def run(self, **kwargs):

    self.settings = get_project_settings()

    if self.settings:

      if not self.settings_name:
        self.working_directory = self.settings["project_dir_name"]
      else:
        self.working_directory =  self.settings[self.settings_name]["working_directory"]

      if self.isNode:
        self.path_cli = self.settings["project_settings"]["node_js_custom_path"] or javascriptCompletions.get("node_js_custom_path") or NODE_JS_EXEC
      elif self.isNpm:
        if self.settings["project_settings"]["use_yarn"]:
          self.path_cli = self.settings["project_settings"]["yarn_custom_path"] or javascriptCompletions.get("yarn_custom_path") or YARN_EXEC
        else:
          self.path_cli = self.settings["project_settings"]["npm_custom_path"] or javascriptCompletions.get("npm_custom_path") or NPM_EXEC
      else:
        self.path_cli = self.settings[self.settings_name]["cli_custom_path"] if self.settings[self.settings_name]["cli_custom_path"] else ( javascriptCompletions.get(self.custom_name+"_custom_path") if javascriptCompletions.get(self.custom_name+"_custom_path") else self.cli )    

        if sublime.platform() != "windows" and (self.settings["project_settings"]["node_js_custom_path"] or javascriptCompletions.get("node_js_custom_path")):
          if os.path.isabs(self.path_cli) :
            self.command = [shlex.quote(self.path_cli)]
          else:
            self.command = ["$(which "+shlex.quote(self.path_cli)+")"]
          self.path_cli = self.settings["project_settings"]["node_js_custom_path"] or javascriptCompletions.get("node_js_custom_path")

      if not self.command:
        self.command = kwargs.get("command")
      else:
        self.command += [kwargs.get("command")]

      self.prepare_command(**kwargs)

    elif self.alsoNonProject:

      self.working_directory = os.path.expanduser("~")

      if self.isNode:
        self.path_cli = javascriptCompletions.get("node_js_custom_path") or NODE_JS_EXEC
      elif self.isNpm:
        if self.settings["project_settings"]["use_yarn"]:
          self.path_cli = javascriptCompletions.get("yarn_custom_path") or YARN_EXEC
        else:
          self.path_cli = javascriptCompletions.get("npm_custom_path") or NPM_EXEC
      else:
        self.path_cli = javascriptCompletions.get(self.custom_name+"_custom_path") if javascriptCompletions.get(self.custom_name+"_custom_path") else self.cli

        if sublime.platform() != "windows" and javascriptCompletions.get("node_js_custom_path"):
          if os.path.isabs(self.path_cli) :
            self.command = [shlex.quote(self.path_cli)]
          else:
            self.command = ["$(which "+shlex.quote(self.path_cli)+")"]
          self.path_cli = javascriptCompletions.get("node_js_custom_path")


      if not self.command:
        self.command = kwargs.get("command")
      else:
        self.command += [kwargs.get("command")]

      self.prepare_command(**kwargs)

    else :
      sublime.error_message("Error: can't get project settings")


  def prepare_command(self):
    pass

  def _run(self):

    if self.isNode and self.isBinPath:
      self.command[0] = shlex.quote(os.path.join(NODE_MODULES_BIN_PATH, self.command[0])) if sublime.platform() != "windows" else os.path.join(NODE_MODULES_BIN_PATH, self.command[0]+".cmd")

    self.working_directory = shlex.quote(self.working_directory) if sublime.platform() != "windows" else self.working_directory
    self.path_cli = shlex.quote(self.path_cli) if sublime.platform() != "windows" else self.path_cli

    if sublime.platform() != "windows": 
      views = self.window.views()
      view_with_term = None
      for view in views:
        if view.name() == "JavaScript Enhancements Terminal (bash)":
          view_with_term = view

      if view_with_term:
        self.window.focus_view(view_with_term)
        self.window.run_command("terminal_view_send_string", args={"string": "cd "+self.working_directory+"\n"})
      else :
        self.window.run_command("set_layout", args={"cells": [[0, 0, 1, 1], [0, 1, 1, 2]], "cols": [0.0, 1.0], "rows": [0.0, 0.7, 1.0]})
        self.window.focus_group(1)
        view = self.window.new_file() 
        args = {"cmd": "/bin/bash -l", "title": "JavaScript Enhancements Terminal (bash)", "cwd": self.working_directory, "syntax": None, "keep_open": False} 
        view.run_command('terminal_view_activate', args=args)

      # stop the current process with SIGINT and call the command
      sublime.set_timeout_async(lambda: self.window.run_command("terminal_view_send_string", args={"string": "\x03"}) or
        self.window.run_command("terminal_view_send_string", args={"string": self.path_cli+" "+(" ".join(self.command))+"\n"}), 500)

    else:
      terminal = Terminal(cwd=self.working_directory, title="JavaScript Enhancements Terminal (bash)")
      terminal.run([self.path_cli]+self.command)

  def substitute_placeholders(self, variable):
    
    if isinstance(variable, list) :

      for index in range(len(variable)):
        for key, placeholder in self.placeholders.items():
          variable[index] = variable[index].replace(key, placeholder)

      return variable

    elif isinstance(variable, str) :

      for key, placeholder in self.placeholders.items():
        variable = variable.replace(key, placeholder)
        
      return variable