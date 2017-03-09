import sublime, sublime_plugin
import subprocess, time
from my_socket.main import mySocketServer  
from node.main import NodeJS
import util.main as Util
node = NodeJS()

socket_server_list["structure_javascript"] = SocketCallUI("structure_javascript", "localhost", 11113, os.path.join("structure_javascript", "ui", "client.js"), 1)

def update_structure_javascript(view, filename, clients=[]):
  global socket_server_list 

  deps = flow_parse_cli_dependencies(view)

  output = node.execute_check_output(
    "flow",
    [
      'ast',
      '--from', 'sublime_text'
    ],
    is_from_bin=True,
    use_fp_temp=True, 
    fp_temp_contents=deps.contents,
    is_output_json=True
  )
  
  if output[0] :
    errors = node.execute_check_output(
      "flow",
      [
        'check-contents',
        '--from', 'sublime_text',
        '--root', deps.project_root,
        '--json',
        deps.filename
      ],
      is_from_bin=True,
      use_fp_temp=True, 
      fp_temp_contents=deps.contents,
      is_output_json=True
    )

    output[1]["command"] = "show_structure_javascript"
    output[1]["filename"] = filename
    output[1]["file_content"] = deps.contents
    output[1]["errors"] = errors[1]["errors"] if errors[0] else None

    data = json.dumps(output[1])

    for client in clients :
      socket_server_list["structure_javascript"].socket.send_to(client["socket"], client["addr"], data)
  else :
    output[1] = dict()
    output[1]["command"] = "show_structure_javascript"
    output[1]["filename"] = "Error during loading structure"
    output[1]["file_content"] = ""
    output[1]["errors"] = None
    data = json.dumps(output[1])
    socket_server_list["structure_javascript"].socket.send_to(conn, addr, data)

class update_structure_javascriptViewEventListener(sublime_plugin.ViewEventListener):
  def on_modified_async(self) :
    global socket_server_list 
  
    if socket_server_list["structure_javascript"].socket :
      
      filename = self.view.file_name()
      filename = filename if filename else ""

      clients = socket_server_list["structure_javascript"].socket.find_clients_by_field("filename", filename)
      
      if clients:
        socket_server_list["structure_javascript"].update_time()
        socket_server_list["structure_javascript"].handle_new_changes(update_structure_javascript, "update_structure_javascript"+filename, self.view, filename, clients)

class view_structure_javascriptCommand(sublime_plugin.TextCommand):
  def run(self, edit, *args):
    global socket_server_list

    if socket_server_list["structure_javascript"].socket and socket_server_list["structure_javascript"].socket.close_if_not_clients():
      socket_server_list["structure_javascript"].socket = None
      
    if socket_server_list["structure_javascript"].socket == None :
      
      socket_server_list["structure_javascript"].current_selected_view = self.view

      def recv(conn, addr, ip, port, client_data, client_fields):
        global socket_server_list
        json_data = json.loads(client_data)

        if json_data["command"] == "ready":
          filename = socket_server_list["structure_javascript"].get_file_name()
          filename = filename if filename else ""

          update_structure_javascript(socket_server_list["structure_javascript"].current_selected_view, filename, [{"socket": conn, "addr": addr}])

        elif json_data["command"] == "set_dot_line" and os.path.isfile(client_fields["filename"]):
          other_view = sublime.active_window().open_file(client_fields["filename"])
          sublime.set_timeout_async(lambda: self.set_dot_line(other_view, json_data["line"]))    

      def client_connected(conn, addr, ip, port, client_fields):
        global socket_server_list   
        filename = socket_server_list["structure_javascript"].get_file_name()
        filename = filename if filename else ""
        client_fields["filename"] = filename

      def client_disconnected(conn, addr, ip, port):
        socket_server_list["structure_javascript"].client_thread = None
        if socket_server_list["structure_javascript"].socket.close_if_not_clients() :
            socket_server_list["structure_javascript"].socket = None

      socket_server_list["structure_javascript"].start(recv, client_connected, client_disconnected)

  def set_dot_line(self, view, line) :

    while view.is_loading() :
      time.sleep(.1)

    line = int(line)-1
    point = view.text_point(line, 0)
    view.show_at_center(point)
    view.sel().clear()
    view.sel().add(point)
    view.add_regions("structure-javascript-dot", [view.sel()[0]],  "code", "dot", sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE)
    sublime.set_timeout_async(lambda: view.erase_regions("structure-javascript-dot"), 500)

  def is_enabled(self):
    view = self.view
    if Util.split_string_and_find(view.scope_name(0), "source.js") < 0 :
      return False
    return True

  def is_visible(self):
    view = self.view
    if Util.split_string_and_find(view.scope_name(0), "source.js") < 0 :
      return False
    return True
