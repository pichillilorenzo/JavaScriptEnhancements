import sublime, sublime_plugin

class close_all_servers_and_flowEventListener(sublime_plugin.EventListener):

  def on_close(self, view) :

    if not sublime.windows() :

      from node.main import NodeJS
      node = NodeJS()

      global socket_server_list
      for key, value in socket_server_list.items() :
        if value["socket"] != None :
          sublime.status_message("socket server stopping")
          data = dict()
          data["command"] = "server_closing"
          data = json.dumps(data)
          value["socket"].send_all_clients(data)
          value["socket"].close()

      sublime.status_message("flow server stopping")
      node.execute("flow", ["stop"], True)
