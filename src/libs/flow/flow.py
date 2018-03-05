import sublime, sublime_plugin
import os, tempfile, queue, subprocess, threading, json, shlex
from collections import namedtuple
import xml.etree.ElementTree as ET
from .. import util
from .. import NodeJS
from ..global_vars import *

flow_ide_clients = {}
flow_servers = {}

class CLIRequirements():
  filename = ""
  project_root = ""
  contents = ""
  cursor_pos = 0
  row = 0
  col = 0

  def __init__(self, filename, project_root, contents, cursor_pos, row, col):
    self.filename = filename
    self.project_root = project_root
    self.contents = contents
    self.cursor_pos = cursor_pos
    self.row = row
    self.col = col

def get_node_and_flow_path():
  
  node_and_flow_path = []
  flow_path = os.path.join(NODE_MODULES_BIN_PATH, "flow")
  is_from_bin = True
  use_node = True

  settings = util.get_project_settings()
  if settings and settings["project_settings"]["flow_cli_custom_path"]:
    flow_path = settings["project_settings"]["flow_cli_custom_path"]
    is_from_bin = False
    use_node = False

  node = NodeJS(check_local=True)

  if sublime.platform() == 'windows' and is_from_bin:
    node_and_flow_path = [flow_path+'.cmd']
  else :
    node_and_flow_path = ([node.node_js_path] if use_node else []) + [flow_path]

  return node_and_flow_path

class FlowServer():
  
  def __init__(self, root):
    self.process = None
    self.root = root

  def start(self, options = []):
    global flow_servers

    if self.root in flow_servers:
      print("flow server already running: " + self.root)
      return

    node_and_flow_path = get_node_and_flow_path()
    print("starting flow server: " + str(node_and_flow_path))
    si = None
    if os.name == "nt":
        si = subprocess.STARTUPINFO()  # type: ignore
        si.dwFlags |= subprocess.SW_HIDE | subprocess.STARTF_USESHOWWINDOW  # type: ignore
    try:
      self.process = subprocess.Popen(
          node_and_flow_path + ["server"] + options + [self.root],
          stdin=subprocess.PIPE,
          stdout=subprocess.PIPE,
          stderr=subprocess.PIPE,
          cwd=self.root,
          startupinfo=si)

      flow_servers[self.root] = self
      return self.process

    except Exception as err:
      print("Failed to start flow server: " + str(node_and_flow_path), err)

  def stop(self):
    global flow_servers
    
    if self.process and self.process.poll() is None:
      self.process.kill()

    self.process = None
    
    if self.root in flow_servers:
      del flow_servers[self.root]

# start default flow server
default_flow_server = FlowServer(root=FLOW_DEFAULT_CONFIG_PATH)
default_flow_server.start()

class FlowIDEServer():

  def __init__(self, root):
    self.process = None
    self.stdio_transport = None
    self.root = root

  def start_stdio_server(self, on_receive, on_closed, options = []):
    global flow_ide_client

    self.on_receive = on_receive
    self.on_closed = on_closed

    if self.root in flow_ide_clients:
      print("flow ide server already running: " + self.root)
      return

    node_and_flow_path = get_node_and_flow_path()
  
    si = None
    if os.name == "nt":
        si = subprocess.STARTUPINFO()  # type: ignore
        si.dwFlags |= subprocess.SW_HIDE | subprocess.STARTF_USESHOWWINDOW  # type: ignore

    args = node_and_flow_path + ["ide", "--protocol", "very-unstable", "--from", "sublime_text"] + options + ["--root", self.root]
    print("starting flow ide server: " + str(args))

    try:
      self.process = subprocess.Popen(
          args,
          stdin=subprocess.PIPE,
          stdout=subprocess.PIPE,
          stderr=subprocess.PIPE,
          cwd=self.root,
          startupinfo=si)

      self.stdio_transport = StdioTransport(self.process)
      self.stdio_transport.start(self.on_receive, self.on_closed)

      flow_ide_clients[self.root] = self

      return self.process

    except Exception as err:
      print("Failed to start flow ide server: " + str(node_and_flow_path), err)

  def send(self, message):
    if self.stdio_transport:
      self.stdio_transport.send(message)

  def stop(self):
    global flow_ide_clients

    if self.process and self.process.poll() is None:
      self.process.kill()

    self.process = None

    if self.root in flow_ide_clients:
      del flow_ide_clients[self.root]

  def prepare_json_rpc_message(self, json_rpc):
    json_rpc = json.dumps(json_rpc)
    message = """
Content-Length: """ + str(len(json_rpc) + 1) + """

""" + json_rpc + """
"""
    return message

  def autocomplete(self, params):
    json_rpc = {
      "jsonrpc":"2.0", 
      "method": "autocomplete", 
      "id": 1, 
      "params": params
    }
    
    message = self.prepare_json_rpc_message(json_rpc)

    flow_ide_clients[self.root].send(message)

#
# @tomv564 - LSP plugin 
# StdioTransport class from https://github.com/tomv564/LSP/blob/master/plugin/core/rpc.py
#
class StdioTransport():
    def __init__(self, process):
        self.process = process

    def start(self, on_receive, on_closed):
        self.on_receive = on_receive
        self.on_closed = on_closed
        self.stdout_thread = threading.Thread(target=self.read_stdout)
        self.stdout_thread.start()

    def close(self):
        self.process = None
        self.on_closed()

    def read_stdout(self):
        """
        Reads JSON responses from process and dispatch them to response_handler
        """
        ContentLengthHeader = b"Content-Length: "

        running = True
        while running:
            running = self.process.poll() is None

            try:
                content_length = 0
                while self.process:
                    header = self.process.stdout.readline()
                    if header:
                        header = header.strip()
                    if not header:
                        break
                    if header.startswith(ContentLengthHeader):
                        content_length = int(header[len(ContentLengthHeader):])

                if (content_length > 0):
                    content = self.process.stdout.read(content_length)

                    self.on_receive(content.decode("UTF-8"))

            except IOError as err:
                self.close()
                print("Failure reading stdout", err)
                break

        print("flow stdout process ended.")

    def send(self, message):
        if self.process:
            try:
                self.process.stdin.write(bytes(message, 'UTF-8'))
                self.process.stdin.flush()
            except (BrokenPipeError, OSError) as err:
                print("Failure writing to stdout", err)
                self.close()


def parse_cli_dependencies(view, **kwargs):
  filename = view.file_name()
  
  project_settings = util.get_project_settings()
  if project_settings:
    project_root = project_settings["project_dir_name"]
  else:
    contextual_keys = sublime.active_window().extract_variables()
    folder_path = contextual_keys.get("folder")
    if folder_path and os.path.isdir(folder_path) and os.path.isfile(os.path.join(folder_path, '.flowconfig')) :  
      project_root = folder_path
    else :
      project_root = FLOW_DEFAULT_CONFIG_PATH

  cursor_pos = 0
  if kwargs.get('cursor_pos') :
    cursor_pos = kwargs.get('cursor_pos')
  else :
    if len(view.sel()) > 0 :
      cursor_pos = view.sel()[0].begin()
    
  row, col = view.rowcol(cursor_pos)

  if view.match_selector(
        cursor_pos,
        'source.js'
    ) and view.substr( sublime.Region(0, view.size()) ) == "" :
  
      current_contents = ""

  else :
    scope = view.scope_name(cursor_pos)
    embedded_regions = []

    if scope.startswith("source.js"):
      current_contents = view.substr(
        sublime.Region(0, view.size())
      )

    else:
      # add vue.js support
      if view.find_by_selector("text.html.vue source.js.embedded.html"):
        vue_regions = view.find_by_selector("text.html.vue source.js.embedded.html")
        for region in vue_regions:
          old_region = region
          new_region = util.trim_region(view, old_region)

          # vue.js regions contains <script> and </script> in their contents, so I need to remove it
          script_str = view.substr(new_region)
          root = ET.fromstring(script_str)
          content = root.text
          offset = script_str.split(content)
          new_region = sublime.Region(new_region.begin() + len(offset[0]), new_region.end() - len(offset[1]))

          embedded_regions.append(new_region)
      elif view.find_by_selector("source.js.embedded.html"):
        embedded_regions = view.find_by_selector("source.js.embedded.html")

      if not embedded_regions:
        return CLIRequirements(
            filename=None,
            project_root=None,
            contents="",
            cursor_pos=None,
            row=None, col=None
          )

      current_contents = ""
      prev_row_offset_end = 0
      prev_col_scope_end = 0
      for region in embedded_regions:
        row_scope, col_scope = view.rowcol(region.begin())
        row_offset = row_scope
        row_offset_end, col_scope_end = view.rowcol(region.end())
        row_scope = row - row_scope
        
        current_contents += (" " * (col_scope - prev_col_scope_end)) + ("\n" * (row_offset - prev_row_offset_end))
        prev_row_offset_end = row_offset_end
        prev_col_scope_end = col_scope_end
        current_contents += view.substr(region)
  
  if kwargs.get('add_magic_token'):
    current_lines = current_contents.splitlines()

    try :
      current_line = current_lines[row]
    except IndexError as e:
      return CLIRequirements(
          filename=None,
          project_root=None,
          contents="",
          cursor_pos=None,
          row=None, col=None
        )

    tokenized_line = ""
    if not kwargs.get('not_add_last_part_tokenized_line') :
      tokenized_line = current_line[0:col] + 'AUTO332' + current_line[col:-1]
    else :
      tokenized_line = current_line[0:col] + 'AUTO332'
    current_lines[row] = tokenized_line
    current_contents = '\n'.join(current_lines)

  return CLIRequirements(
    filename=filename,
    project_root=project_root,
    contents=current_contents,
    cursor_pos=cursor_pos,
    row=row, col=col
  )

def hide_errors(view) :
  view.erase_regions('flow_error')
  view.erase_status('flow_error')

