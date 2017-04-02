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

          if json_data.get("type") :
            project_folder = os.path.dirname(json_data["project"])

            if "ionic" in json_data["type"]:
              panel = self.create_panel_installer("ionic_panel_installer_project")
              node.execute('ionic', ["start", "temp"], is_from_bin=True, chdir=project_folder, wait_terminate=False, func_stdout=create_ionic_project, args_func_stdout=[panel, project_folder, json_data["project"]])
              
            elif "cordova" in json_data["type"]:
              panel = self.create_panel_installer("cordova_panel_installer_project")
              node.execute('cordova', ["create", "temp"], is_from_bin=True, chdir=project_folder, wait_terminate=False, func_stdout=create_cordova_project, args_func_stdout=[panel, project_folder, json_data["project"]])

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

  def create_panel_installer(self, output_panel_name):
    window = sublime.active_window()
    panel = window.create_output_panel(output_panel_name, False)
    panel.set_read_only(True)
    panel.set_syntax_file(os.path.join("Packages", "JavaScript Completions", "javascript_completions.sublime-syntax"))
    window.run_command("show_panel", {"panel": "output."+output_panel_name})
    return panel