import sublime, sublime_plugin
import os, subprocess, threading, json
from ..hook import Hook
from .flow_cli import FlowCLI
from .main import get_flow_path
from ..node import NodeJS
from ..javascript_enhancements_settings import *

flow_ide_clients = {}

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

    flow_path = get_flow_path()
    node_path = []

    if sublime.platform() != 'windows':
      node = NodeJS()
      node_path = [node.node_js_path]

    si = None
    if os.name == "nt":
        si = subprocess.STARTUPINFO()  # type: ignore
        si.dwFlags |= subprocess.SW_HIDE | subprocess.STARTF_USESHOWWINDOW  # type: ignore

    args = node_path + flow_path + ["ide", "--protocol", "very-unstable", "--from", "sublime_text"] + options + ["--root", self.root]
    print("starting flow ide server: " + str(args))
    sublime.status_message('Starting flow ide server, root: ' + self.root)

    old_env = os.environ.copy()

    new_env = old_env.copy()
    new_env["PATH"] = new_env["PATH"] + javaScriptEnhancements.get("PATH")

    # update the PATH environment variable
    os.environ.update(new_env)

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
      print("Failed to start flow ide server: " + str(args), err)

    # reset the PATH environment variable
    os.environ.update(old_env)

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
    json_rpc = json.dumps(json_rpc, ensure_ascii=False)
    # number of bytes in a string
    json_rpc_length = len(json_rpc.encode('utf-8'))
    message = """Content-Length: """ + str(json_rpc_length + 1) + """

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

        print("flow ide stdout process ended. Possible errors:")
        # print possible errors
        error = self.process.stderr.readline()
        while error:
          print(error.decode("UTF-8").strip())
          error = self.process.stderr.readline()

        self.close()

    def send(self, message):
      if self.process:
        try:
          self.process.stdin.write(bytes(message, 'UTF-8'))
          self.process.stdin.flush()
        except (BrokenPipeError, OSError) as err:
          print("Failure writing to flow ide stdout", err)
          self.close()

class JavascriptEnhancementsStartFlowIDEServerEventListener(sublime_plugin.EventListener):
  
  def start_server(self, view):
    deps = FlowCLI.parse_cli_dependencies(view)

    if deps.project_root and not deps.project_root in flow_ide_clients:
      flow_ide = FlowIDEServer(deps.project_root)
      flow_ide.start_stdio_server(self.dispatch_event, lambda: flow_ide.stop())

  def on_load(self, view):
    self.start_server(view)

  def on_activated(self, view):
    self.start_server(view)

  def dispatch_event(self, result):

    result = json.loads(result)

    if "id" in result:
      Hook.apply("flow_ide_server.autocomplete", result["result"])