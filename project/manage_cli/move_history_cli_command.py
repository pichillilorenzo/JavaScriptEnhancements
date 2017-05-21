class move_history_cliCommand(sublime_plugin.TextCommand) :

  def run(self, edit, **args):
    
    if "action" in args :
      view = self.view

      view_settings = view.settings()

      if not view_settings.has("index_lines") or not view.substr(view.line(view.size())).strip() :
        index_lines = len(view_settings.get("lines", [])) - 1

      else :
        if args.get("action") == "move_down" :
          index_lines = view_settings.get("index_lines", len(view_settings.get("lines", [])) ) + 1
        else :
          index_lines = view_settings.get("index_lines", len(view_settings.get("lines", [])) ) - 1

      if index_lines < 0 or index_lines >= len(view_settings.get("lines")) : 
        return

      if index_lines >= 0 :
        line = view_settings.get("lines")[index_lines]
        view.replace(edit, view.line(view.size()), '')
        view.insert(edit, view.size(), line)
        view.show_at_center(view.size())
        view_settings.set("index_lines", index_lines)

  def is_enabled(self) :

    view = self.view
    return True if view.settings().get("is_output_cli_panel", False) else False

  def is_visible(self) :
    
    view = self.view
    return True if view.settings().get("is_output_cli_panel", False) else False

