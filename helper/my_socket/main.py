import time, os, re, threading, socket, traceback, sys, struct

class mySocketClient():
  def __init__(self, socket_name) :
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.socket_name = socket_name
    self.func_on_recv = None

  def connect(self, host, port):
    self.socket_name += "_"+host+":"+str(port)
    try:
      self.socket.connect((host, port))
      self.socket.setblocking(False)
      self.log('Client connected')
      Util.create_and_start_thread(target=self.on_recv)
    except socket.error as msg:
      self.log('Connection failed. Error : ' + str(sys.exc_info()))
      sys.exit()

  def on_recv(self):
    while True:
      time.sleep(.1)
      
      input_from_server_bytes = self.recv_data() # the number means how the response can be in bytes  
      if input_from_server_bytes is False :
        break
      if input_from_server_bytes :
        input_from_server = input_from_server_bytes.decode("utf8") # the return will be in bytes, so decode
        if self.func_on_recv :
          self.func_on_recv(input_from_server)

  def recv_data(self):
    try:
      size = self.socket.recv(struct.calcsize("<i"))
      if size :
        size = struct.unpack("<i", size)[0]
        data = b""
        while len(data) < size:
          try:
            msg = self.socket.recv(size - len(data))
            if not msg:
              return None
            data += msg
          except socket.error:
            pass
        return data
      else :
        return False
    except socket.error:
      pass
    except OSError as e:
      self.log(traceback.format_exc())
      return False

  def send_to_server(self, data) :
    self.socket.settimeout(1)
    try :
      data = struct.pack("<i", len(data)) + data.encode("utf-8")
      self.socket.sendall(data)
      return True
    except socket.timeout:
      self.log("Socket server dead. Closing connection...")
      self.close()
      return False
    except socket.error :
      self.log("Socket server dead. Closing connection...")
      self.close()
      return False

  def handle_recv(self, func):
    self.func_on_recv = func

  def get_socket(self):
    return self.socket

  def log(self, message) :
    print(self.socket_name + ": "+message)

  def close(self) :
    if self.socket :
      self.socket.close()
      self.socket = None

class mySocketServer():
  def __init__(self, socket_name, accept=False) :
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.clients = dict()
    self.socket_name = socket_name
    self.accept_only_one_client = accept
    self.func_on_client_connected = None
    self.func_on_client_disconnected = None
    self.func_on_recv = None
    self.log('Socket created')

  def bind(self, host, port):
    self.socket_name += "_"+host+":"+str(port)
    try:
      self.socket.bind((host, port))
      self.log('Socket bind complete')
    except socket.error as msg:
      self.log('Bind failed. Error : ' + traceback.format_exc())

  def listen(self, backlog=5) :
    self.socket.listen(backlog)
    self.log('Socket now listening')
    Util.create_and_start_thread(target=self.main_loop)

  def main_loop(self):
    while True:
      time.sleep(.1)

      try :
        conn, addr = self.socket.accept()   
        if len(self.clients) > 0 and self.accept_only_one_client :
          self.send_to(conn, addr, "server_accept_only_one_client")
          continue
        conn.setblocking(False)
        ip, port = str(addr[0]), str(addr[1])
        self.clients[ip+":"+str(port)] = dict()
        self.clients[ip+":"+str(port)]["socket"] = conn
        self.clients[ip+":"+str(port)]["addr"] = addr

        self.log('Accepting connection from ' + ip + ':' + port)

        if self.func_on_client_connected :
          self.func_on_client_connected(conn, addr, ip, port, self.clients[ip+":"+str(port)])

        try:
          Util.create_and_start_thread(target=self.on_recv, args=(conn, addr, ip, port))
        except:
          self.log(traceback.format_exc())
      except ConnectionAbortedError:
        self.log("Connection aborted")
        break

  def on_recv(self, conn, addr, ip, port):
    while True:
      time.sleep(.1)

      input_from_client_bytes = self.recv_data(conn)

      if input_from_client_bytes is False :

        self.delete_client(conn, addr)
        if self.func_on_client_disconnected :
          self.func_on_client_disconnected(conn, addr, ip, port)
        self.log('Connection ' + ip + ':' + port + " ended")
        break

      if input_from_client_bytes :

        # decode input and strip the end of line
        input_from_client = input_from_client_bytes.decode("utf8").rstrip()

        if self.func_on_recv :
          self.func_on_recv(conn, addr, ip, port, input_from_client, self.clients[ip+":"+str(port)])

  def recv_data(self, conn):
    try:
      size = conn.recv(struct.calcsize("<i"))
      if size :
        size = struct.unpack("<i", size)[0]
        data = b""
        while len(data) < size:
          try:
            msg = conn.recv(size - len(data))
            if not msg:
              return None
            data += msg
          except socket.error as e:
            pass
        return data
      else :
        return False
    except socket.error as e:
      pass
    except OSError as e:
      self.log(traceback.format_exc())
      return False

  def send_to(self, conn, addr, data) :
    conn.settimeout(1)
    try:
      data = struct.pack("<i", len(data)) + data.encode("utf-8")
      return self.send_all_data_to(conn, addr, data)
    except socket.timeout:
      self.delete_client(conn, addr)
      self.log("Timed out "+str(addr[0])+":"+str(addr[1]))
      return False
    except OSError as e:
      self.delete_client(conn, addr)
      self.log(traceback.format_exc())
      return False

  def send_all_data_to(self, conn, addr, data):
    totalsent = 0
    data_size = len(data)
    while totalsent < data_size:
      sent = conn.sendto(data[totalsent:], addr)
      if sent == 0:
        self.delete_client(conn, addr)
        self.log(traceback.format_exc())
        return False
      totalsent = totalsent + sent
    return True

  def send_all_clients(self, data) :
    for key, value in self.clients.items() :
      self.send_to(value["socket"], value["addr"], data)

  def handle_recv(self, func):
    self.func_on_recv = func

  def handle_client_connection(self, func):
    self.func_on_client_connected = func

  def handle_client_disconnection(self, func):
    self.func_on_client_disconnected = func

  def get_socket(self):
    return self.socket

  def set_accept_only_one_client(accept):
    self.accept_only_one_client = accept

  def get_clients(self) :
    return self.clients

  def find_clients_by_field(self, field, field_value) :
    clients_found = list()
    for key, value in self.clients.items() :
      if field in value and value[field] == field_value :
        clients_found.append(value)
    return clients_found

  def get_first_client(self) :
    for client in self.clients :
      return client

  def delete_client(self, conn, addr) :
    try :
      del self.clients[str(addr[0])+":"+str(addr[1])]
    except KeyError:
      pass
    conn.close()

  def log(self, message) :
    print(self.socket_name + ": "+message)

  def close_if_not_clients(self) :
    if not self.clients:
      self.close()
      return True
    return False

  def close(self) :
    if self.socket :
      self.socket.close()
      self.socket = None
