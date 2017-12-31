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

      flow_cli = "flow"
      is_from_bin = True
      chdir = settings["project_dir_name"]
      use_node = True
      bin_path = ""

      if settings["project_settings"]["flow_cli_custom_path"]:
        flow_cli = os.path.basename(settings["project_settings"]["flow_cli_custom_path"])
        bin_path = os.path.dirname(settings["project_settings"]["flow_cli_custom_path"])
        is_from_bin = False
        use_node = False
    
      sublime.set_timeout_async(lambda: node.execute(flow_cli, ["stop"], is_from_bin=is_from_bin, chdir=chdir, bin_path=bin_path, use_node=use_node))
