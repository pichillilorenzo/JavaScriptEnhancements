class print_panel_cliCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):   
    line = args.get("line")
    if line == "OUTPUT-SUCCESS":
      self.view.window().run_command("hide_panel")
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
  status_message = ""
  settings = {}
  command_with_options = []
  def run(self, **kwargs):
    self.settings = get_project_settings()
    if self.settings:
      self.cli = kwargs.get("cli")
      if not self.cli:
        raise Exception("'cli' field of the manage_cliCommand not defined.")
      self.cli = str(kwargs.get("cli"))
      self.command_with_options = kwargs.get("command_with_options")
      if not self.command_with_options or len(self.command_with_options) <= 0:
        raise Exception("'command_with_options' field of the manage_cliCommand not defined.")
      self.output_panel_name = self.output_panel_name if not kwargs.get("output_panel_name") else str(kwargs.get("output_panel_name"))
      self.status_message = self.status_message if not kwargs.get("status_message") else str(kwargs.get("status_message"))
      sublime.set_timeout_async(lambda: self.manage())

  def manage(self) :
    if self.status_message:
      sublime.active_window().status_message("Cordova: "+self.status_message)
    node = NodeJS()
    self.panel = self.window.create_output_panel(self.output_panel_name, False)
    self.window.run_command("show_panel", {"panel": "output."+self.output_panel_name})
    node.execute(self.cli, self.command_with_options, is_from_bin=True, chdir=self.settings["project_dir_name"], wait_terminate=False, func_stdout=self.print_panel)

  def print_panel(self, line):
    self.panel.run_command("print_panel_cli", {"line": line})
