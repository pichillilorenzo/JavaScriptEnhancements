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

  def run(self, **kwargs):

    self.settings = get_project_settings()

    if self.settings:

      if not self.settings_name:
        self.working_directory = self.settings["project_dir_name"]
      else:
        self.working_directory =  self.settings[self.settings_name]["working_directory"]

      if self.isNode:
        self.path_cli = self.settings["project_settings"]["node_js_custom_path"] or get_node_js_custom_path() or NODE_JS_EXEC
      elif self.isNpm:
        if self.settings["project_settings"]["use_yarn"]:
          self.path_cli = self.settings["project_settings"]["yarn_custom_path"] or get_yarn_custom_path() or YARN_EXEC
        else:
          self.path_cli = self.settings["project_settings"]["npm_custom_path"] or get_npm_custom_path() or NPM_EXEC
      else:
        self.path_cli = self.settings[self.settings_name]["cli_custom_path"] if self.settings[self.settings_name]["cli_custom_path"] else ( javascriptCompletions.get(self.custom_name+"_custom_path") if javascriptCompletions.get(self.custom_name+"_custom_path") else self.cli )
      self.command = kwargs.get("command")

      self.prepare_command(**kwargs)

    else :
      sublime.error_message("Error: can't get project settings")

  def prepare_command(self):
    pass

  def _run(self):

    if self.isNode and self.isBinPath:
      self.command[0] = shlex.quote(os.path.join(NODE_MODULES_BIN_PATH, self.command[0] if not sublime.platform() == 'windows' else self.command[0]+".cmd"))

    self.working_directory = shlex.quote(self.working_directory)
    self.path_cli = shlex.quote(self.path_cli)

    views = self.window.views()
    view_with_term = None
    for view in views:
      if view.name() == "JavaScript Enhancements Terminal":
        view_with_term = view

    self.window.run_command("set_layout", args={"cells": [[0, 0, 1, 1], [0, 1, 1, 2]], "cols": [0.0, 1.0], "rows": [0.0, 0.7, 1.0]})
    self.window.focus_group(1)

    if view_with_term:
      self.window.focus_view(view_with_term)
      if sublime.platform() in ("linux", "osx"): 
        self.window.run_command("terminal_view_send_string", args={"string": "cd "+self.working_directory+"\n"})
      else:
        # windows
        pass
    else :
      view = self.window.new_file() 

      cmd = ""
      if sublime.platform() in ("linux", "osx"): 
        cmd = "/bin/bash -l"
      else:
        # windows
        pass

      args = {"cmd": cmd, "title": "JavaScript Enhancements Terminal", "cwd": self.working_directory, "syntax": None, "keep_open": False} 
      view.run_command('terminal_view_activate', args=args)

    # stop the current process with SIGINT and call the command
    sublime.set_timeout_async(lambda: self.window.run_command("terminal_view_send_string", args={"string": "\x03"}) or
      self.window.run_command("terminal_view_send_string", args={"string": self.path_cli+" "+(" ".join(self.command))+"\n"}), 500)

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