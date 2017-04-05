import sublime, sublime_plugin
import subprocess, shutil, traceback
from my_socket.main import mySocketServer  
from node.main import NodeJS
node = NodeJS()

socket_server_list["create_new_project"] = SocketCallUI("create_new_project", "localhost", 11111, os.path.join(PROJECT_FOLDER, "create_new_project", "ui", "client.js"))

class create_new_projectCommand(sublime_plugin.WindowCommand):
  def run(self, *args):
    global socket_server_list

    if not socket_server_list["create_new_project"].is_socket_closed() :
      socket_server_list["create_new_project"].socket.close_if_not_clients()

    if socket_server_list["create_new_project"].is_socket_closed() :

      def recv(conn, addr, ip, port, client_data, client_fields):
        global socket_server_list

        json_data = json.loads(client_data)

        if json_data["command"] == "open_project":

          json_data = Hook.apply("before_create_new_project", json_data)

          if "type" in json_data["project"] :
            for project_type in json_data["project"]["type"]:
              json_data = Hook.apply(project_type+"_create_new_project", json_data)

          json_data = Hook.apply("after_create_new_project", json_data)

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
        global socket_server_list  
        socket_server_list["create_new_project"].socket.close_if_not_clients()

      socket_server_list["create_new_project"].start(recv, client_connected, client_disconnected)

    else :
      socket_server_list["create_new_project"].call_ui()
