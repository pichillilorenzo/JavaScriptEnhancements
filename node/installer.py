import sublime
import traceback
import threading
import os
import tarfile, zipfile
import urllib
import json
import shutil
import node_variables
from animation_loader import AnimationLoader
from repeated_timer import RepeatedTimer
from main import NodeJS

class DownloadNodeJS(object):
  def __init__(self, node_version):
    self.NODE_JS_VERSION = node_version
    self.NODE_JS_TAR_EXTENSION = ".zip" if node_variables.NODE_JS_OS == "win" else ".tar.gz"
    self.NODE_JS_BINARY_URL = "https://nodejs.org/dist/"+self.NODE_JS_VERSION+"/node-"+self.NODE_JS_VERSION+"-"+node_variables.NODE_JS_OS+"-"+node_variables.NODE_JS_ARCHITECTURE+self.NODE_JS_TAR_EXTENSION
    self.NODE_JS_BINARY_TARFILE_NAME = self.NODE_JS_BINARY_URL.split('/')[-1]
    self.NODE_JS_BINARY_TARFILE_FULL_PATH = os.path.join(node_variables.NODE_JS_BINARIES_FOLDER_PLATFORM, self.NODE_JS_BINARY_TARFILE_NAME)
    self.animation_loader = AnimationLoader(["[=     ]", "[ =    ]", "[   =  ]", "[    = ]", "[     =]", "[    = ]", "[   =  ]", "[ =    ]"], 0.067, "Downloading: "+self.NODE_JS_BINARY_URL+" ")
    self.interval_animation = None
    self.thread = None
    if not os.path.exists(node_variables.NODE_JS_BINARIES_FOLDER_PLATFORM):
      os.makedirs(node_variables.NODE_JS_BINARIES_FOLDER_PLATFORM)
  def download(self):
    try :
      request = urllib.request.Request(self.NODE_JS_BINARY_URL)
      request.add_header('User-agent', r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1')
      with urllib.request.urlopen(request) as response, open(self.NODE_JS_BINARY_TARFILE_FULL_PATH, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    except Exception as err :
      traceback.print_exc()
      self.on_error(err)
      return
    self.extract()
    self.on_complete()
  def start(self):
    self.thread = threading.Thread(target=self.download, name="DownloadNodeJS")
    self.thread.setDaemon(True)
    self.thread.start()
    if self.animation_loader :
      self.interval_animation = RepeatedTimer(self.animation_loader.sec, self.animation_loader.animate)
  def extract(self):
    if self.NODE_JS_TAR_EXTENSION != ".zip" :
      with tarfile.open(self.NODE_JS_BINARY_TARFILE_FULL_PATH, "r:gz") as tar :
        for member in tar.getmembers() :
          if member.name.endswith("/bin/node") :
            member.name = node_variables.NODE_JS_PATH_EXECUTABLE
            tar.extract(member, node_variables.NODE_JS_BINARIES_FOLDER_PLATFORM)
            break
    else :
      with zipfile.ZipFile(self.NODE_JS_BINARY_TARFILE_FULL_PATH, "r") as zip_file :
        for member in zip_file.namelist() :
          if member.endswith("/node.exe") :
            with zip_file.open(member) as node_file:
              with open(os.path.join(node_variables.NODE_JS_BINARIES_FOLDER_PLATFORM, "node.exe"), "wb") as target :
                shutil.copyfileobj(node_file, target)
                break

  def on_error(self, err):
    self.animation_loader.on_complete()
    self.interval_animation.stop()
    sublime.active_window().status_message("Can't install Node.js! Check your internet connection!")
  def on_complete(self):
    self.animation_loader.on_complete()
    self.interval_animation.stop()
    if os.path.isfile(self.NODE_JS_BINARY_TARFILE_FULL_PATH) : 
      os.remove(self.NODE_JS_BINARY_TARFILE_FULL_PATH)
    node_js = NodeJS()
    if node_js.getCurrentNodeJSVersion() == self.NODE_JS_VERSION :
      sublime.active_window().status_message("Node.js "+self.NODE_JS_VERSION+" installed correctly!")
    else :
      sublime.active_window().status_message("Can't install Node.js! Something during installation went wrong.")


def checkUpgrade():
  try :
    response = urllib.request.urlopen(node_variables.NODE_JS_VERSION_URL_LIST_ONLINE)
    data = json.loads(response.read().decode("utf-8"))
    nodejs_latest_version = data[0]["version"]
    node_js = NodeJS()
    if node_js.getCurrentNodeJSVersion() != nodejs_latest_version :
      sublime.active_window().status_message("There is a new version ( "+nodejs_latest_version+" ) of Node.js available! Change your settings to download this version.")
    else :
      sublime.active_window().status_message("No need to update Node.js. Current version: "+node_js.getCurrentNodeJSVersion())
  except Exception as err :
    traceback.print_exc()

def already_installed():
  return os.path.isfile(node_variables.NODE_JS_PATH_EXECUTABLE)

def can_start_download():
  for thread in threading.enumerate() :
    if thread.getName() == "DownloadNodeJS" and thread.is_alive() :
      return False
  return True

def install(node_version=""):
  if node_version == "" :
    node_version = node_variables.NODE_JS_VERSION
  nodejs_can_start_download = can_start_download()
  nodejs_already_installed = already_installed()
  if nodejs_can_start_download and not nodejs_already_installed :
    DownloadNodeJS( node_version ).start()
  elif nodejs_can_start_download and nodejs_already_installed :
    node_js = NodeJS()
    if node_version != node_js.getCurrentNodeJSVersion() :
      DownloadNodeJS( node_version ).start()

  if nodejs_already_installed :
    for thread in threading.enumerate() :
      if thread.getName() == "checkUpgradeNodeJS" and thread.is_alive() :
        return
    thread = threading.Thread(target=checkUpgrade, name="checkUpgradeNodeJS")
    thread.setDaemon(True)
    thread.start()
