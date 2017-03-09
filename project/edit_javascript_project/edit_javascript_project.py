import sublime, sublime_plugin
import subprocess, shutil, traceback
from my_socket.main import mySocketServer  

socket_server_list["edit_javascript_project"] = dict()
socket_server_list["edit_javascript_project"]["client_process"] = None
socket_server_list["edit_javascript_project"]["client_ui_file"] = os.path.join(PROJECT_FOLDER, "edit_javascript_project", "ui.py")
socket_server_list["edit_javascript_project"]["socket"] = None
socket_server_list["edit_javascript_project"]["current_selected_view"] = None

class edit_javascript_projectCommand(sublime_plugin.WindowCommand):
  def run(self, *args):
    global socket_server_list

    if socket_server_list["edit_javascript_project"]["socket"] == None :

      socket_server_list["edit_javascript_project"]["socket"] = mySocketServer("edit_javascript_project") 
      socket_server_list["edit_javascript_project"]["socket"].bind("localhost", 11112)

      def recv(conn, addr, ip, port, client_data, client_fields):
        global socket_server_list

        json_data = json.loads(client_data)


      def client_connected(conn, addr, ip, port, client_fields):
        global socket_server_list 
        settings = get_project_settings()
        if settings :
          data = dict()
          data["command"] = "load_project_settings"
          data["settings"] = settings
          data = json.dumps(data)
          socket_server_list["edit_javascript_project"]["socket"].send_to(conn, addr, data) 

      def client_disconnected(conn, addr, ip, port):
        socket_server_list["edit_javascript_project"]["client_process"] = None
        if socket_server_list["edit_javascript_project"]["socket"].close_if_not_clients() :
          socket_server_list["edit_javascript_project"]["socket"] = None

      socket_server_list["edit_javascript_project"]["socket"].handle_recv(recv)
      socket_server_list["edit_javascript_project"]["socket"].handle_client_connection(client_connected)
      socket_server_list["edit_javascript_project"]["socket"].handle_client_disconnection(client_disconnected)
      socket_server_list["edit_javascript_project"]["socket"].listen()

    socket_server_list["edit_javascript_project"]["client_process"] = call_ui(socket_server_list["edit_javascript_project"]["client_ui_file"], "localhost", 11112)

  def is_enabled(self):
    return True if get_project_settings() else False

  def is_visible(self):
    return True if get_project_settings() else False