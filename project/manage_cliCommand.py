class print_panel_cliCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):   
    line = args.get("line")
    if line == "OUTPUT-SUCCESS":
      if self.view.window() and args.get("hide_panel_on_success") :
        sublime.set_timeout_async(lambda: self.view.window().run_command("hide_panel"), args.get("wait_panel") if args.get("wait_panel") else 1000 )
      return
    elif line == "OUTPUT-ERROR" or line == "OUTPUT-DONE":
      return
    self.view.set_read_only(False)
    self.view.insert(edit, self.view.size(), line)
    self.view.show_at_center(self.view.size())
    self.view.set_read_only(True)

class enable_menu_cliViewEventListener(sublime_plugin.ViewEventListener):

  def on_activated_async(self, **kwargs):
    cli = kwargs.get("cli")
    path = kwargs.get("path")
    path_disabled = kwargs.get("path_disabled")
    if cli and path and path_disabled:
      if is_type_javascript_project(cli) :
        if os.path.isfile(path_disabled):
          os.rename(path_disabled, path)
      else :
        if os.path.isfile(path):
          os.rename(path, path_disabled)

class manage_cliCommand(sublime_plugin.WindowCommand):
  cli = ""
  panel = None
  output_panel_name = "output_panel_cli"
  panel_command = "print_panel_cli"
  status_message = ""
  settings = {}
  command_with_options = []
  placeholders = {}
  hide_panel_on_success = True
  process = None
  is_stoppable = False
  stop_now = None
  command_stopped_text = "\n\nCommand Stopped\n\n"

  def run(self, **kwargs):
    if self.is_stoppable and self.stop_process():
      return
    self.settings = get_project_settings()
    if self.settings:

      self.cli = kwargs.get("cli") if kwargs.get("cli") else self.cli
      if not self.cli:
        raise Exception("'cli' field of the manage_cliCommand not defined.")

      self.command_with_options = self.substitute_placeholders(kwargs.get("command_with_options"))
      if not self.command_with_options or len(self.command_with_options) <= 0:
        raise Exception("'command_with_options' field of the manage_cliCommand not defined.")
      self.output_panel_name = self.substitute_placeholders( self.output_panel_name if not kwargs.get("output_panel_name") else str(kwargs.get("output_panel_name")) )
      self.status_message = self.substitute_placeholders( self.status_message if not kwargs.get("status_message") else str(kwargs.get("status_message")) )
      self.hide_panel_on_success = True if kwargs.get("hide_panel_on_success") else False

      sublime.set_timeout_async(lambda: self.manage())

  def manage(self) :
    if self.status_message:
      self.window.status_message("Cordova: "+self.status_message)
    node = NodeJS()
    self.panel = self.window.create_output_panel(self.output_panel_name, False)
    self.window.run_command("show_panel", {"panel": "output."+self.output_panel_name})
    node.execute(self.cli, self.command_with_options, is_from_bin=True, chdir=self.settings["project_dir_name"], wait_terminate=False, func_stdout=self.print_panel)

  def print_panel(self, line, process):
    if not self.process :
      self.process = process

    self.process_communicate(line, process)
    if line != None:
      self.panel.run_command(self.panel_command, {"line": line, "hide_panel_on_success": self.hide_panel_on_success})

    if line == "OUTPUT-DONE":
      self.process = None

  def process_communicate(self, line, process):
    return

  def stop_process(self):
    if self.stop_now == None:
      self.stop_now = False
    elif self.stop_now == False and self.process != None:
      self.stop_now = True

    if self.stop_now:
      self.process.terminate()
      self.process = None
      self.stop_now = None
      self.panel.run_command(self.panel_command, {"line": self.command_stopped_text})
      self.panel.run_command(self.panel_command, {"line": "OUTPUT-SUCCESS", "hide_panel_on_success": True, "wait_panel": 3000})
      return True

    return False

  def substitute_placeholders(self, variable):
    if isinstance(variable, list) :
      return list(map(lambda x: self.placeholders[x] if self.placeholders.get(x) else x, variable))
    elif isinstance(variable, str) :
      for key, placeholder in self.placeholders.items():
        variable = variable.replace(key, placeholder)
      return variable
