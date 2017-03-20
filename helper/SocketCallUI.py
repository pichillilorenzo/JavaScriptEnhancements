import os, time
from my_socket.main import mySocketServer 
import util.main as Util

class SocketCallUI(object):

  def __init__(self, name, host, port, client_ui_file, wait_for_new_changes=1):
    super(SocketCallUI, self).__init__()
    self.name = name
    self.host = host
    self.port = port
    self.client_thread = None
    self.client_ui_file = client_ui_file
    self.socket = None
    self.current_selected_view = None
    self.last_modified = None
    self.wait_for_new_changes = wait_for_new_changes

  def init(self):
    if not os.path.isfile(self.client_ui_file):
      raise Exception("Client UI file \""+self.client_ui_file+"\" not found.")
    self.last_modified = time.time()

  def start(self, handle_recv, handle_client_connection, handle_client_disconnection):
    self.init()
    self.listen(handle_recv, handle_client_connection, handle_client_disconnection)
    self.client_thread = call_ui(self.client_ui_file , self.host, self.port)

  def listen(self, handle_recv, handle_client_connection, handle_client_disconnection):
    self.socket = mySocketServer(self.name) 
    self.socket.bind(self.host, self.port)
    self.socket.handle_recv(handle_recv)
    self.socket.handle_client_connection(handle_client_connection)
    self.socket.handle_client_disconnection(handle_client_disconnection)
    self.socket.listen()

  def update_time(self):
    self.last_modified = time.time()

  def handle_new_changes(self, fun, thread_name, *args):
    args = (fun,) + args
    return Util.create_and_start_thread(self.check_changes, args=args, thread_name=thread_name)

  def check_changes(self, fun, *args):
    while True:
      time.sleep(.1)
      now = time.time()
      if now - self.last_modified >= self.wait_for_new_changes :
        break
    fun(*args)
    
  def get_file_name(self):
    return self.current_selected_view.file_name()
