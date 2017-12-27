import sublime, sublime_plugin
import os, time, signal

class close_flowEventListener(sublime_plugin.EventListener):

  def on_pre_close(self, view) :

    node = NodeJS()

    if not sublime.windows() :
      
      sublime.status_message("flow server stopping")
      sublime.set_timeout_async(lambda: node.execute("flow", ["stop"], is_from_bin=True, chdir=os.path.join(PACKAGE_PATH, "flow")))

    settings = get_project_settings()

    if settings and view.window() and len(view.window().views()) == 1 :
      settings = get_project_settings()
      sublime.status_message("flow server stopping")

      flow_cli_path = "flow"
      is_from_bin = True

      if settings and settings["project_settings"]["flow_cli_custom_path"]:
        flow_cli_path = shlex.quote( settings["project_settings"]["flow_cli_custom_path"] )
        is_from_bin = False
    
      sublime.set_timeout_async(lambda: node.execute(flow_cli_path, ["stop"], is_from_bin=is_from_bin, chdir=os.path.join(settings["project_dir_name"])))
