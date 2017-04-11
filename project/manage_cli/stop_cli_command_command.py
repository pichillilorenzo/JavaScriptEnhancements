class stop_cli_commandCommand(sublime_plugin.TextCommand):
  last_output_panel_name = None
  window = None
  def run(self, edit, **args):
    self.window = self.view.window()
    panel = self.window.active_panel()
    if panel :
      self.last_output_panel_name = panel.replace("output.", "")
    sublime.set_timeout_async(self.stop_command)

  def stop_command(self) :
    global manage_cli_window_command_processes
    settings = get_project_settings()
    if self.window and self.last_output_panel_name and settings and settings["project_dir_name"]+"_"+self.last_output_panel_name in manage_cli_window_command_processes :
      process = manage_cli_window_command_processes[settings["project_dir_name"]+"_"+self.last_output_panel_name]["process"]
      if (process.poll() == None) :
        process.terminate()
        del manage_cli_window_command_processes[settings["project_dir_name"]+"_"+self.last_output_panel_name]
      else :
        del manage_cli_window_command_processes[settings["project_dir_name"]+"_"+self.last_output_panel_name]

      panel = self.window.get_output_panel(self.last_output_panel_name)
      if panel :
        panel.run_command("print_panel_cli", {"line": "\n\nCommand Stopped\n\n"})
        panel.run_command("print_panel_cli", {"line": "OUTPUT-SUCCESS", "hide_panel_on_success": True, "wait_panel": 3000})

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
 