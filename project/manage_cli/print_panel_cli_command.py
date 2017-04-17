class print_panel_cliCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):   
    line = args.get("line")
    if line.strip() :
      if line == "OUTPUT-SUCCESS":
        if self.view.window() and args.get("hide_panel_on_success") :
          sublime.set_timeout_async(self.hide_window_panel, args.get("wait_panel") if args.get("wait_panel") else 2000 )
        return
      elif line == "OUTPUT-ERROR" or line == "OUTPUT-DONE":
        return
      self.view.set_read_only(False)
      self.view.insert(edit, self.view.size(), line)
      self.view.show_at_center(self.view.size())
      self.view.set_read_only(True)

  def hide_window_panel(self):
    try :
      self.view.window().run_command("hide_panel")
    except AttributeError as e:
      pass