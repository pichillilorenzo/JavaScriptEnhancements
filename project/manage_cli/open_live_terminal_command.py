class open_live_terminalCommand(manage_cliCommand):
  cli = "/bin/bash" if sublime.platform() != 'windows' else "cmd.exe"
  name_cli = "Bash"
  is_node = False
  is_npm = False
  show_animation_loader = False
  hide_panel_on_success = True
  output_panel_name = "panel_terminal"
  line_prefix = "$ "
  syntax = "Packages/ShellScript/Shell-Unix-Generic.tmLanguage"
  wait_panel = 0

  def callback_after_get_settings(self, **kwargs) :

    shell = self.settings['project_settings']['live_terminal']['shell']

    if shell :
      self.cli = shell

  def is_enabled(self) :

    return True if is_javascript_project() else False

  def is_visible(self) :

    return True if is_javascript_project() else False