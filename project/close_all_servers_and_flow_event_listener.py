import sublime, sublime_plugin
import os, time

class close_all_servers_and_flowEventListener(sublime_plugin.EventListener):

  def on_pre_close(self, view) :

    from node.main import NodeJS
    node = NodeJS()

    global socket_server_list

    if not sublime.windows() :
      
      sublime.status_message("flow server stopping")
      sublime.set_timeout_async(lambda: node.execute("flow", ["stop"], True, os.path.join(PACKAGE_PATH, "flow")))

      for key, value in socket_server_list.items() :
        if value["socket"] != None :
          sublime.status_message("socket server stopping")
          data = dict()
          data["command"] = "server_closing"
          data = json.dumps(data)
          value["socket"].send_all_clients(data)
          value["socket"].close()

    if is_javascript_project() and view.window() and len(view.window().views()) == 1 :
      settings = get_project_settings()
      sublime.status_message("flow server stopping")
      sublime.set_timeout_async(lambda: node.execute("flow", ["stop"], True, os.path.join(settings["project_dir_name"])))
