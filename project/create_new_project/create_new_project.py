import sublime, sublime_plugin
import subprocess, shutil, traceback
from my_socket.main import mySocketServer  
from node.main import NodeJS
node = NodeJS()

socket_server_list["create_new_project"] = SocketCallUI("create_new_project", "localhost", 11111, os.path.join(PROJECT_FOLDER, "create_new_project", "ui", "client.js"))

def open_project_folder(project):
  
  subl(["--project", project])

class create_new_projectCommand(sublime_plugin.WindowCommand):
  def run(self, *args):
    global socket_server_list

    if socket_server_list["create_new_project"].socket and socket_server_list["create_new_project"].socket.close_if_not_clients():
      socket_server_list["create_new_project"].socket = None

    if socket_server_list["create_new_project"].socket == None :

      def recv(conn, addr, ip, port, client_data, client_fields):
        global socket_server_list

        json_data = json.loads(client_data)

        if json_data["command"] == "open_project":

          if json_data.get("type") :
            project_folder = os.path.dirname(json_data["project"])
            if "ionic" in json_data["type"]:
              node.execute('ionic', ["start", "temp"], is_from_bin=True, chdir=project_folder)
              Util.move_content_to_parent_folder(os.path.join(project_folder, "temp"))
            elif "cordova" in json_data["type"]:
              node.execute('cordova', ["create", "temp"], is_from_bin=True, chdir=project_folder)
              Util.move_content_to_parent_folder(os.path.join(project_folder, "temp"))

          open_project_folder(json_data["project"])
          data = dict()
          data["command"] = "close_window"
          data = json.dumps(data)
          socket_server_list["create_new_project"].socket.send_to(conn, addr, data)

        elif json_data["command"] == "try_flow_init":
          
          data = dict()
          data["command"] = "result_flow_init"
          data["result"] = node.execute("flow", ["init"], is_from_bin=True, chdir=json_data["project"]["path"])
          data["project"] = json_data["project"]
          data = json.dumps(data)

          socket_server_list["create_new_project"].socket.send_to(conn, addr, data)

      def client_connected(conn, addr, ip, port, client_fields):
        global socket_server_list   

      def client_disconnected(conn, addr, ip, port):
        socket_server_list["create_new_project"].client_thread = None
        if socket_server_list["create_new_project"].socket.close_if_not_clients() :
          socket_server_list["create_new_project"].socket = None

      socket_server_list["create_new_project"].start(recv, client_connected, client_disconnected)
