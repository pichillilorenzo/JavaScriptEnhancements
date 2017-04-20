class print_panel_cliCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):   
    line = args.get("line") or ""
    prefix = args.get("prefix") or ""
    postfix = args.get("postfix") or ""
    if line.strip() :
      if line == "OUTPUT-SUCCESS":
        if self.view.window() and args.get("hide_panel_on_success") :
          sublime.set_timeout_async(self.hide_window_panel, args.get("wait_panel") if "wait_panel" in args else 2000 )
        return
      elif line == "OUTPUT-ERROR" or line == "OUTPUT-DONE":
        return

      is_read_only = self.view.is_read_only()
      self.view.set_read_only(False)
      self.view.insert(edit, self.view.size(), prefix + line + postfix)
      self.view.set_read_only(is_read_only)
      self.view.show_at_center(self.view.size())
      self.view.add_regions(
        'output_cli',
        self.view.split_by_newlines(sublime.Region(0, self.view.size()))
      )

  def hide_window_panel(self):
    try :
      self.view.window().run_command("hide_panel")
    except AttributeError as e:
      pass