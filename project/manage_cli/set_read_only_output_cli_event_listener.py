class set_read_only_output_cliEventListener(sublime_plugin.EventListener) :

  def on_activated_async(self, view) :

    if not view.settings().get("is_output_cli_panel", False) :
      return 

    is_in = False
    for region in view.get_regions("output_cli"): 
      if region.contains(view.sel()[0]) or region.intersects(view.sel()[0]) :
        is_in = True
        view.set_read_only(True)
        break

    if not is_in :
      view.set_read_only(False)

  def on_selection_modified_async(self, view) :

    if not view.settings().get("is_output_cli_panel", False) :
      return 

    is_in = False
    for region in view.get_regions("output_cli"): 
      if region.contains(view.sel()[0]) or region.intersects(view.sel()[0]) :
        is_in = True
        view.set_read_only(True)
        break

    if not is_in :
      view.set_read_only(False)

  def on_modified_async(self, view) :

    if not view.settings().get("is_output_cli_panel", False) :
      return 

    is_in = False
    for region in view.get_regions("output_cli"): 
      if region.contains(view.sel()[0]) or region.intersects(view.sel()[0]) :
        is_in = True
        view.set_read_only(True)
        break

    if not is_in :
      view.set_read_only(False)

  def on_text_command(self, view, command_name, args) :

    if not view.settings().get("is_output_cli_panel", False) :
      return 

    is_in = False

    if command_name == "left_delete" :
      for region in view.get_regions("output_cli"): 
        if region.intersects(sublime.Region( view.sel()[0].begin() - 2, view.sel()[0].end() ) ):
          is_in = True
          view.set_read_only(True)
          break

    elif command_name == "insert" and "characters" in args and args["characters"] == '\n' :
      view.set_read_only(True)
      window = view.window()
      panel = window.active_panel()
      if panel :
        last_output_panel_name = panel.replace("output.", "")
        global manage_cli_window_command_processes
        settings = get_project_settings()
        if window and last_output_panel_name and settings and settings["project_dir_name"]+"_"+last_output_panel_name in manage_cli_window_command_processes :
          process = manage_cli_window_command_processes[settings["project_dir_name"]+"_"+last_output_panel_name]["process"]

          regions = view.lines(sublime.Region(0, view.size()))

          line = ""
          for i in range(1, len(regions)+1):
            line = view.substr(regions[-i]).strip()
            if line and not line.startswith("$ ") :
              break
            line = ""
            i = i + 1

          if line :

            view_settings = view.settings()
            view_settings.set("lines", view_settings.get("lines", []) + [line] )

            view.add_regions(
              'output_cli',
              view.split_by_newlines(sublime.Region(0, view.size()))
            )

            view_settings.set( "index_lines", len(view_settings.get("lines")) -1 )

            view.sel().clear()
            view.sel().add(sublime.Region(view.size(), view.size()))

            process.stdin.write("{}\n".format(line).replace("PROJECT_PATH", shlex.quote(settings["project_dir_name"])).encode("utf-8"))
            process.stdin.flush()

            window.run_command("show_panel", {"panel": "output."+last_output_panel_name})

    if not is_in :
      view.set_read_only(False)
