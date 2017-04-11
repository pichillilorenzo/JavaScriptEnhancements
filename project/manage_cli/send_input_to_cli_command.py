class send_input_to_cliCommand(sublime_plugin.TextCommand):
  last_output_panel_name = None
  window = None
  def run(self, edit, **args):
    self.window = self.view.window()
    panel = self.window.active_panel()
    if panel :
      self.last_output_panel_name = panel.replace("output.", "")
    sublime.set_timeout_async(lambda : self.window.show_input_panel("Input: ", "", self.send_input, None, None))

  def send_input(self, input) :
    global manage_cli_window_command_processes
    settings = get_project_settings()
    if self.window and self.last_output_panel_name and settings and settings["project_dir_name"]+"_"+self.last_output_panel_name in manage_cli_window_command_processes :
      process = manage_cli_window_command_processes[settings["project_dir_name"]+"_"+self.last_output_panel_name]["process"]
      process.stdin.write("{}\n".format(input).encode("utf-8"))
      process.stdin.flush()
      self.window.run_command("show_panel", {"panel": "output."+self.last_output_panel_name})

  def is_enabled(self):
    global manage_cli_window_command_processes
    self.window = self.view.window()
    panel = self.window.active_panel()
    if panel :
      self.last_output_panel_name = panel.replace("output.", "")
    settings = get_project_settings()
    return True if ( self.window and self.last_output_panel_name and settings and settings["project_dir_name"]+"_"+self.last_output_panel_name in manage_cli_window_command_processes ) else False
  
  def is_visible(self):
    global manage_cli_window_command_processes
    self.window = self.view.window()
    panel = self.window.active_panel()
    if panel :
      self.last_output_panel_name = panel.replace("output.", "")
    settings = get_project_settings()
    return True if ( self.window and self.last_output_panel_name and settings and settings["project_dir_name"]+"_"+self.last_output_panel_name in manage_cli_window_command_processes ) else False
