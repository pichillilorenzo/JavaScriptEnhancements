import sublime, sublime_plugin
import subprocess, shutil, traceback
from my_socket.main import mySocketServer  

socket_server_list["edit_project"] = SocketCallUI("edit_project", "localhost", 11112, os.path.join(PROJECT_FOLDER, "edit_project", "ui", "client.js"))

class edit_javascript_projectCommand(sublime_plugin.WindowCommand):
  def run(self, *args):
    global socket_server_list

    settings = get_project_settings()
    
    if not socket_server_list["edit_project"].is_socket_closed() :
      socket_server_list["edit_project"].socket.close_if_not_clients()

    if socket_server_list["edit_project"].is_socket_closed() :

      def recv(conn, addr, ip, port, client_data, client_fields):
        global socket_server_list

        json_data = json.loads(client_data)

        if json_data["command"] == "ready":
          if settings :
            data = dict()
            data["command"] = "load_project_settings"
            data["settings"] = settings
            data = json.dumps(data)
            socket_server_list["edit_project"].socket.send_to(conn, addr, data) 

      def client_connected(conn, addr, ip, port, client_fields):
        global socket_server_list 
      
      def client_disconnected(conn, addr, ip, port):
        global socket_server_list  
        socket_server_list["edit_project"].socket.close_if_not_clients()

      socket_server_list["edit_project"].start(recv, client_connected, client_disconnected)
      
    else :
      socket_server_list["edit_project"].call_ui()

  def is_enabled(self):
    return is_javascript_project()

  def is_visible(self):
    return is_javascript_project()