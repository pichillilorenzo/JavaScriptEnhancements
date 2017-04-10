import sublime
import traceback, threading, os, sys, imp, tarfile, zipfile, urllib, json, shutil

class NodeJSInstaller(object):
  def __init__(self, node_version):
    self.NODE_JS_VERSION = node_version
    self.NODE_JS_TAR_EXTENSION = ".zip" if NODE_JS_OS == "win" else ".tar.gz"
    self.NODE_JS_BINARY_URL = "https://nodejs.org/dist/"+self.NODE_JS_VERSION+"/node-"+self.NODE_JS_VERSION+"-"+NODE_JS_OS+"-"+NODE_JS_ARCHITECTURE+self.NODE_JS_TAR_EXTENSION
    self.NODE_JS_BINARY_TARFILE_NAME = self.NODE_JS_BINARY_URL.split('/')[-1]
    self.NODE_JS_BINARY_TARFILE_FULL_PATH = os.path.join(NODE_JS_BINARIES_FOLDER_PLATFORM, self.NODE_JS_BINARY_TARFILE_NAME)
    self.animation_loader = AnimationLoader(["[=     ]", "[ =    ]", "[   =  ]", "[    = ]", "[     =]", "[    = ]", "[   =  ]", "[ =    ]"], 0.067, "Downloading: "+self.NODE_JS_BINARY_URL+" ")
    self.interval_animation = None
    self.thread = None
  def download(self):
    try :
      if os.path.exists(NODE_JS_BINARIES_FOLDER_PLATFORM):
        self.rmtree(NODE_JS_BINARIES_FOLDER_PLATFORM)
        os.makedirs(NODE_JS_BINARIES_FOLDER_PLATFORM)
      else :
        os.makedirs(NODE_JS_BINARIES_FOLDER_PLATFORM)
      if os.path.exists(NODE_MODULES_PATH):
        self.rmtree(NODE_MODULES_PATH)
      request = urllib.request.Request(self.NODE_JS_BINARY_URL)
      request.add_header('User-agent', r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1')
      with urllib.request.urlopen(request) as response :
        with open(self.NODE_JS_BINARY_TARFILE_FULL_PATH, 'wb') as out_file :
          shutil.copyfileobj(response, out_file)
    except Exception as err :
      traceback.print_exc()
      self.on_error(err)
      return
    self.extract()
    self.on_complete()
  def start(self):
    self.thread = Util.create_and_start_thread(self.download, "NodeJSInstaller")
    if self.animation_loader :
      self.interval_animation = RepeatedTimer(self.animation_loader.sec, self.animation_loader.animate)
  def extract(self):
    sep = os.sep
    if self.NODE_JS_TAR_EXTENSION != ".zip" :
      with tarfile.open(self.NODE_JS_BINARY_TARFILE_FULL_PATH, "r:gz") as tar :
        for member in tar.getmembers() :
          member.name = sep.join(member.name.split(sep)[1:])
          tar.extract(member, NODE_JS_BINARIES_FOLDER_PLATFORM)
    else :
      if NODE_JS_OS == "win" :
        import string
        from ctypes import windll, c_int, c_wchar_p
        UNUSUED_DRIVE_LETTER = ""
        for letter in string.ascii_uppercase:
          if not os.path.exists(letter+":") :
            UNUSUED_DRIVE_LETTER = letter+":"
            break
        if not UNUSUED_DRIVE_LETTER :
          sublime.message_dialog("Can't install node.js and npm! UNUSUED_DRIVE_LETTER not found.")
          return
        DefineDosDevice = windll.kernel32.DefineDosDeviceW
        DefineDosDevice.argtypes = [ c_int, c_wchar_p, c_wchar_p ]
        DefineDosDevice(0, UNUSUED_DRIVE_LETTER, NODE_JS_BINARIES_FOLDER_PLATFORM)
        try:
          with zipfile.ZipFile(self.NODE_JS_BINARY_TARFILE_FULL_PATH, "r") as zip_file :
            for member in zip_file.namelist() :
              if not member.endswith("/") :
                with zip_file.open(member) as node_file:
                  with open(UNUSUED_DRIVE_LETTER + "\\" + member.replace("node-"+self.NODE_JS_VERSION+"-"+NODE_JS_OS+"-"+NODE_JS_ARCHITECTURE+"/", ""), "wb+") as target :
                    shutil.copyfileobj(node_file, target)
              elif not member.endswith("node-"+self.NODE_JS_VERSION+"-"+NODE_JS_OS+"-"+NODE_JS_ARCHITECTURE+"/"):
                os.mkdir(UNUSUED_DRIVE_LETTER + "\\" + member.replace("node-"+self.NODE_JS_VERSION+"-"+NODE_JS_OS+"-"+NODE_JS_ARCHITECTURE+"/", ""))
        except Exception as e:
          print("Error: "+traceback.format_exc())
        finally:
          DefineDosDevice(2, UNUSUED_DRIVE_LETTER, NODE_JS_BINARIES_FOLDER_PLATFORM)

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
    npm = NPM()
    self.animation_loader = AnimationLoader(["[=     ]", "[ =    ]", "[   =  ]", "[    = ]", "[     =]", "[    = ]", "[   =  ]", "[ =    ]"], 0.067, "Installing npm dependencies ")
    self.interval_animation = RepeatedTimer(self.animation_loader.sec, self.animation_loader.animate)
    try :
      npm.getCurrentNPMVersion() 
    except Exception as e:
      print("Error: "+traceback.format_exc())
    try :
      npm.install_all() 
    except Exception as e:
      print("Error: "+traceback.format_exc())
    self.animation_loader.on_complete()
    self.interval_animation.stop()
    if node_js.getCurrentNodeJSVersion() == self.NODE_JS_VERSION :
      sublime.active_window().status_message("Node.js "+self.NODE_JS_VERSION+" installed correctly! NPM version: "+npm.getCurrentNPMVersion())
    else :
      sublime.active_window().status_message("Can't install Node.js! Something went wrong during installation.")

  def rmtree(self, path) :
    if NODE_JS_OS == "win" :
      import string
      from ctypes import windll, c_int, c_wchar_p
      UNUSUED_DRIVE_LETTER = ""
      for letter in string.ascii_uppercase:
        if not os.path.exists(letter+":") :
          UNUSUED_DRIVE_LETTER = letter+":"
          break
      if not UNUSUED_DRIVE_LETTER :
        sublime.message_dialog("Can't remove node.js! UNUSUED_DRIVE_LETTER not found.")
        return
      DefineDosDevice = windll.kernel32.DefineDosDeviceW
      DefineDosDevice.argtypes = [ c_int, c_wchar_p, c_wchar_p ]
      DefineDosDevice(0, UNUSUED_DRIVE_LETTER, path)
      try:
        shutil.rmtree(UNUSUED_DRIVE_LETTER)
      except Exception as e:
        print("Error: "+traceback.format_exc())
      finally:
        DefineDosDevice(2, UNUSUED_DRIVE_LETTER, path)  
    else :
      shutil.rmtree(path)

  @staticmethod
  def updateNPMDependencies():
    npm = NPM()
    try :
      npm.getCurrentNPMVersion()
    except Exception as e:
      print("Error: "+traceback.format_exc())
      return
      
    animation_loader = AnimationLoader(["[=     ]", "[ =    ]", "[   =  ]", "[    = ]", "[     =]", "[    = ]", "[   =  ]", "[ =    ]"], 0.067, "Updating npm dependencies ")
    interval_animation = RepeatedTimer(animation_loader.sec, animation_loader.animate)
    try :
      npm.update_all() 
    except Exception as e:
      pass
    animation_loader.on_complete()
    interval_animation.stop()

  @staticmethod
  def already_installed():
    return os.path.isfile(NODE_JS_PATH_EXECUTABLE)

  @staticmethod
  def can_start_download():
    for thread in threading.enumerate() :
      if thread.getName() == "NodeJSInstaller" and thread.is_alive() :
        return False
    return True

  @staticmethod
  def install(node_version=""):
    if node_version == "" :
      node_version = NODE_JS_VERSION
    nodejs_can_start_download = NodeJSInstaller.can_start_download()
    nodejs_already_installed = NodeJSInstaller.already_installed()
    if nodejs_can_start_download and not nodejs_already_installed :
      NodeJSInstaller( node_version ).start()
    elif nodejs_can_start_download and nodejs_already_installed :
      node_js = NodeJS()
      if node_version != node_js.getCurrentNodeJSVersion() :
        NodeJSInstaller( node_version ).start()

    if nodejs_already_installed :
      Util.create_and_start_thread(NodeJSInstaller.updateNPMDependencies, "checkUpgradeNPM")

# def checkUpgrade():
#   updateNPMDependencies()
#   try :
#     response = urllib.request.urlopen(NODE_JS_VERSION_URL_LIST_ONLINE)
#     data = json.loads(response.read().decode("utf-8"))
#     nodejs_latest_version = data[0]["version"]
#     node_js = NodeJS()
#     if node_js.getCurrentNodeJSVersion() != nodejs_latest_version :
#       sublime.active_window().status_message("There is a new version ( "+nodejs_latest_version+" ) of Node.js available! Change your settings to download this version.")
#     else :
#       try :
#         npm = NPM()
#         npm_version = npm.getCurrentNPMVersion() 
#         sublime.active_window().status_message("No need to update Node.js. Current version: "+node_js.getCurrentNodeJSVersion()+", npm: "+npm_version)
#       except Exception as e:
#         sublime.active_window().status_message("No need to update Node.js. Current version: "+node_js.getCurrentNodeJSVersion()+", npm not installed!")

#   except Exception as err :
#     traceback.print_exc()

  
