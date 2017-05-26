import sublime, sublime_plugin
import os, sys, imp, platform, json, traceback, threading, urllib, shutil, re
from shutil import copyfile
from threading import Timer

PACKAGE_PATH = os.path.abspath(os.path.dirname(__file__))
PACKAGE_NAME = os.path.basename(PACKAGE_PATH)
SUBLIME_PACKAGES_PATH = os.path.dirname(PACKAGE_PATH)

JC_SETTINGS_FOLDER_NAME = "javascript_completions"
JC_SETTINGS_FOLDER = os.path.join(PACKAGE_PATH, "helper", JC_SETTINGS_FOLDER_NAME)

PROJECT_FOLDER_NAME = "project"
PROJECT_FOLDER = os.path.join(PACKAGE_PATH, PROJECT_FOLDER_NAME)
socket_server_list = dict()

HELPER_FOLDER_NAME = "helper"
HELPER_FOLDER = os.path.join(PACKAGE_PATH, HELPER_FOLDER_NAME)

BOOKMARKS_FOLDER = os.path.join(HELPER_FOLDER, 'bookmarks')

platform_switcher = {"osx": "OSX", "linux": "Linux", "windows": "Windows"}
os_switcher = {"osx": "darwin", "linux": "linux", "windows": "win"}
PLATFORM = platform_switcher.get(sublime.platform())
PLATFORM_ARCHITECTURE = "64bit" if platform.architecture()[0] == "64bit" else "32bit" 

class Hook(object):
  hook_list = {}

  @staticmethod
  def add (hook_name, hook_func, priority = 10) :
    if not hook_name in Hook.hook_list :
      Hook.hook_list[hook_name] = []

    Hook.hook_list[hook_name].append({
      "hook_func": hook_func,
      "priority": priority if priority >= 0 else 0
    })

    Hook.hook_list[hook_name] = sorted(Hook.hook_list[hook_name], key=lambda hook: hook["priority"])

  @staticmethod
  def apply(hook_name, value='', *args, **kwargs) :

    args = (value,) + args

    if hook_name in Hook.hook_list :
      for hook in Hook.hook_list[hook_name] :
        value = hook["hook_func"](*args, **kwargs)
        args = (value,) + args[1:]

    return value

  @staticmethod
  def count(hook_name) :

    if hook_name in Hook.hook_list :
      return len(Hook.hook_list[hook_name])
    return 0

  @staticmethod
  def removeHook(hook_name, hook_func, priority = -1) :

    if hook_name in Hook.hook_list :
      if priority >= 0 :
        hook = { 
          "hook_func": hook_func, 
          "priority": priority 
        }
        while hook in Hook.hook_list[hook_name] : 
          Hook.hook_list[hook_name].remove(hook)
      else :
         for hook in Hook.hook_list[hook_name] :
          if hook["hook_func"] == hook_func :
            Hook.hook_list[hook_name].remove(hook)

  @staticmethod
  def removeAllHook(hook_name) :

    if hook_name in Hook.hook_list :
      Hook.hook_list[hook_name] = []
      

import sublime

class AnimationLoader(object):
  def __init__(self, animation, sec, str_before="", str_after=""):
    self.animation = animation
    self.sec = sec
    self.animation_length = len(animation)
    self.str_before = str_before
    self.str_after = str_after
    self.cur_anim = 0
  def animate(self):
    sublime.active_window().status_message(self.str_before+self.animation[self.cur_anim % self.animation_length]+self.str_after)
    self.cur_anim = self.cur_anim + 1
  def on_complete(self):
    sublime.active_window().status_message("")
from threading import Timer

class RepeatedTimer(object):
  def __init__(self, interval, function, *args, **kwargs):
    self._timer     = None
    self.interval   = interval
    self.function   = function
    self.args       = args
    self.kwargs     = kwargs
    self.is_running = False
    self.start()

  def _run(self):
    self.is_running = False
    self.start()
    self.function(*self.args, **self.kwargs)

  def start(self):
    if not self.is_running:
      self._timer = Timer(self.interval, self._run)
      self._timer.start()
      self.is_running = True

  def stop(self):
    self._timer.cancel()
    self.is_running = False
import subprocess, threading
import sys, imp, codecs, shlex, os, json, traceback, tempfile

import platform
import os

NODE_JS_VERSION = "v6.10.1"
NODE_JS_BINARIES_FOLDER_NAME = "node_binaries"
NODE_JS_VERSION_URL_LIST_ONLINE = "https://nodejs.org/dist/index.json"
NODE_JS_BINARIES_FOLDER = os.path.join(PACKAGE_PATH, NODE_JS_BINARIES_FOLDER_NAME)
NODE_JS_OS = os_switcher.get(sublime.platform())
NODE_JS_BINARIES_FOLDER_PLATFORM = os.path.join(NODE_JS_BINARIES_FOLDER, NODE_JS_OS + "-" + PLATFORM_ARCHITECTURE)
NODE_JS_ARCHITECTURE = "x64" if PLATFORM_ARCHITECTURE == "64bit" else "x86"
NODE_JS_BINARY_NAME = "node" if NODE_JS_OS != 'win' else "node.exe"

NODE_MODULES_FOLDER_NAME = "node_modules"
NODE_MODULES_PATH = os.path.join(PACKAGE_PATH, NODE_MODULES_FOLDER_NAME)
NODE_MODULES_BIN_PATH = os.path.join(NODE_MODULES_PATH, ".bin")

NODE_JS_PATH_EXECUTABLE = os.path.join(NODE_JS_BINARIES_FOLDER_PLATFORM, "bin", NODE_JS_BINARY_NAME) if NODE_JS_OS != 'win' else os.path.join(NODE_JS_BINARIES_FOLDER_PLATFORM, NODE_JS_BINARY_NAME)

NPM_NAME = "npm" if NODE_JS_OS != 'win' else "npm.cmd"
NPM_PATH_EXECUTABLE = os.path.join(NODE_JS_BINARIES_FOLDER_PLATFORM, "bin", NPM_NAME) if NODE_JS_OS != 'win' else os.path.join(NODE_JS_BINARIES_FOLDER_PLATFORM, NPM_NAME)

YARN_NAME = "yarn" if NODE_JS_OS != 'win' else "yarn.cmd"
YARN_PATH_EXECUTABLE = os.path.join(NODE_MODULES_BIN_PATH, YARN_NAME)



def get_node_js_custom_path():
  json_file = Util.open_json(os.path.join(PACKAGE_PATH,  "settings.sublime-settings"))
  if json_file and "node_js_custom_path" in json_file :
    return json_file.get("node_js_custom_path").strip()
  return ""

def get_npm_custom_path():
  json_file = Util.open_json(os.path.join(PACKAGE_PATH, "settings.sublime-settings"))
  if json_file and "npm_custom_path" in json_file :
    return json_file.get("npm_custom_path").strip()
  return ""

def get_yarn_custom_path():
  json_file = Util.open_json(os.path.join(PACKAGE_PATH, "settings.sublime-settings"))
  if json_file and "yarn_custom_path" in json_file :
    return json_file.get("yarn_custom_path").strip()
  return ""

class NodeJS(object):
  def __init__(self, check_local = False):
    self.check_local = check_local
    self.node_js_path = ""

    if self.check_local :
      settings = get_project_settings()
      if settings :
        self.node_js_path = settings["project_settings"]["node_js_custom_path"] or get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
      else :
        self.node_js_path = get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
    else :
      self.node_js_path = NODE_JS_PATH_EXECUTABLE

  def eval(self, js, eval_type="eval", strict_mode=False):

    js = ("'use strict'; " if strict_mode else "") + js
    eval_type = "--eval" if eval_type == "eval" else "--print"

    args = [eval_type, js]

    return self.execute(args[0], args[1:])

  def getCurrentNodeJSVersion(self) :

    args = [self.node_js_path, "-v"]

    result = Util.execute(args[0], args[1:])

    if result[0] :
      return result[1].strip()

    raise Exception(result[1])

  def execute(self, command, command_args, is_from_bin=False, chdir="", wait_terminate=True, func_stdout=None, args_func_stdout=[], bin_path="") :

    if NODE_JS_OS == 'win':
      if is_from_bin :
        args = [os.path.join( (bin_path or NODE_MODULES_BIN_PATH), command+".cmd")] + command_args
      else :
        args = [self.node_js_path, os.path.join( (bin_path or NODE_MODULES_BIN_PATH), command)] + command_args
    else :
      args = [self.node_js_path, os.path.join( (bin_path or NODE_MODULES_BIN_PATH), command)] + command_args
    
    return Util.execute(args[0], args[1:], chdir=chdir, wait_terminate=wait_terminate, func_stdout=func_stdout, args_func_stdout=args_func_stdout)
    
  def execute_check_output(self, command, command_args, is_from_bin=False, use_fp_temp=False, use_only_filename_view_flow=False, fp_temp_contents="", is_output_json=False, chdir="", clean_output_flow=False) :

    fp = None
    if use_fp_temp :
      
      fp = tempfile.NamedTemporaryFile()
      fp.write(str.encode(fp_temp_contents))
      fp.flush()

    if NODE_JS_OS == 'win':
      if is_from_bin :
        args = [os.path.join(NODE_MODULES_BIN_PATH, command+".cmd")] + command_args
      else :
        args = [self.node_js_path, os.path.join(NODE_MODULES_BIN_PATH, command)] + command_args
      if fp :
        args += ["<", fp.name]
    else :
      command_args_list = list()
      for command_arg in command_args :
        command_args_list.append(shlex.quote(command_arg))
      command_args = " ".join(command_args_list)
      args = shlex.quote(self.node_js_path)+" "+shlex.quote(os.path.join(NODE_MODULES_BIN_PATH, command))+" "+command_args+(" < "+shlex.quote(fp.name) if fp and not use_only_filename_view_flow else "")

    try:
      output = None
      result = None

      owd = os.getcwd()
      if chdir :
        os.chdir(chdir)

      output = subprocess.check_output(
          args, shell=True, stderr=subprocess.STDOUT
      )
      
      if chdir:
        os.chdir(owd)

      if clean_output_flow :
        out = output.decode("utf-8", "ignore").strip()
        out = out.split("\n")
        # if len(out) > 1 and out[3:][0].startswith("Started a new flow server: -flow is still initializing; this can take some time. [processing] "):
        #   out = out[3:]
        #   out[0] = out[0].replace("Started a new flow server: -flow is still initializing; this can take some time. [processing] ", "")[1:]
        #   out = "\n".join(out)
        #   print(out)
        #   result = json.loads(out) if is_output_json else out
        # elif len(out) > 1 and out[3:][0].startswith("Started a new flow server: -flow is still initializing; this can take some time. [merging inference] "):
        #   out = out[3:]
        #   out[0] = out[0].replace("Started a new flow server: -flow is still initializing; this can take some time. [merging inference] ", "")[1:]
        #   out = "\n".join(out)
        #   result = json.loads(out) if is_output_json else out
        # elif len(out) > 1 and out[3:][0].startswith("Started a new flow server: -"):
        #   out = out[3:]
        #   out[0] = out[0].replace("Started a new flow server: -", "")
        #   out = "\n".join(out)
        #   result = json.loads(out) if is_output_json else out
        out = out[ len(out) - 1 ]
        if '{"flowVersion":"' in out :
          index = out.index('{"flowVersion":"')
          out = out[index:]
          result = json.loads(out) if is_output_json else out
        else :
          return [False, {}]
      else :
        try:
          result = json.loads(output.decode("utf-8", "ignore")) if is_output_json else output.decode("utf-8", "ignore")
        except ValueError as e:
          print(traceback.format_exc())
          print(output.decode("utf-8", "ignore"))
          return [False, {}]

      if use_fp_temp :
        fp.close()
      return [True, result]
    except subprocess.CalledProcessError as e:
      #print(traceback.format_exc())
      try:
        result = json.loads(output.decode("utf-8", "ignore")) if is_output_json else output.decode("utf-8", "ignore")
        if use_fp_temp :
          fp.close()
        return [False, result]
      except:
        #print(traceback.format_exc())
        if use_fp_temp :
          fp.close()

        return [False, None]
    except:
      print(traceback.format_exc())
      if use_fp_temp :
        fp.close()
      return [False, None]

class NPM(object):
  def __init__(self, check_local = False):
    self.check_local = check_local
    self.node_js_path = ""
    self.npm_path = ""
    self.yarn_path = ""
    self.cli_path = ""

    if self.check_local :
      settings = get_project_settings()
      if settings :
        self.node_js_path = settings["project_settings"]["node_js_custom_path"] or get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
        self.npm_path = settings["project_settings"]["npm_custom_path"] or get_npm_custom_path() or NPM_PATH_EXECUTABLE
        self.yarn_path = settings["project_settings"]["yarn_custom_path"] or get_yarn_custom_path() or YARN_PATH_EXECUTABLE

        if settings["project_settings"]["use_yarn"] and self.yarn_path :
          self.cli_path = self.yarn_path
        else :
          self.cli_path = self.npm_path

      else :
        self.node_js_path = get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
        self.npm_path = get_npm_custom_path() or NPM_PATH_EXECUTABLE
        self.yarn_path = get_yarn_custom_path() or YARN_PATH_EXECUTABLE

        self.cli_path = self.npm_path
    else :
      self.node_js_path = NODE_JS_PATH_EXECUTABLE
      self.npm_path = NPM_PATH_EXECUTABLE
      self.yarn_path = YARN_PATH_EXECUTABLE

      self.cli_path = self.npm_path

  def execute(self, command, command_args, chdir="", wait_terminate=True, func_stdout=None, args_func_stdout=[]) :

    args = []

    if NODE_JS_OS == 'win':
      args = [self.cli_path, command] + command_args
    else :
      args = [self.node_js_path, self.cli_path, command] + command_args
    
    return Util.execute(args[0], args[1:], chdir=chdir, wait_terminate=wait_terminate, func_stdout=func_stdout, args_func_stdout=args_func_stdout)

  def install_all(self, save=False, chdir="", wait_terminate=True, func_stdout=None, args_func_stdout=[]) :

    return self.execute('install', (["--save"] if save else []), chdir=(PACKAGE_PATH if not chdir else chdir), wait_terminate=wait_terminate, func_stdout=func_stdout, args_func_stdout=args_func_stdout)

  def update_all(self, save=False, chdir="", wait_terminate=True, func_stdout=None, args_func_stdout=[]) :

    return self.execute('update', (["--save"] if save else []), chdir=(PACKAGE_PATH if not chdir else chdir), wait_terminate=wait_terminate, func_stdout=func_stdout, args_func_stdout=args_func_stdout)

  def install(self, package_name, save=False, chdir="", wait_terminate=True, func_stdout=None, args_func_stdout=[]) :
    
    return self.execute('install', (["--save"] if save else []) + [package_name], chdir=(PACKAGE_PATH if not chdir else chdir), wait_terminate=wait_terminate, func_stdout=func_stdout, args_func_stdout=args_func_stdout)
  
  def update(self, package_name, save=False, chdir="", wait_terminate=True, func_stdout=None, args_func_stdout=[]) :

    return self.execute('update', (["--save"] if save else []) + [package_name], chdir=(PACKAGE_PATH if not chdir else chdir), wait_terminate=wait_terminate, func_stdout=func_stdout, args_func_stdout=args_func_stdout)

  def getPackageJson(self):

    package_json_path = ""
    settings = get_project_settings()

    if self.check_local and settings and os.path.isfile( os.path.join(settings["project_dir_name"], "package.json") ) :
      package_json_path = os.path.join(settings["project_dir_name"], "package.json")
    elif self.check_local and (not settings or not os.path.isfile( os.path.join(settings["project_dir_name"], "package.json") ) ) :
      return None
    else :
      package_json_path = os.path.join(PACKAGE_PATH, "package.json")

    return Util.open_json(package_json_path)

  def getCurrentNPMVersion(self) :

    if NODE_JS_OS == 'win':
      args = [self.cli_path, "-v"]
    else :
      args = [self.node_js_path, self.cli_path, "-v"]

    result = Util.execute(args[0], args[1:])

    if result[0] :
      return result[1].strip()

    raise Exception(result[1])

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

  

import sublime, sublime_plugin
import re, urllib, shutil, traceback, threading, time, os, hashlib, json, multiprocessing, shlex, pty

class Util(object) :

  multiprocessing_list = []

  @staticmethod
  def download_and_save(url, where_to_save) :
    if where_to_save :
      try :
        request = urllib.request.Request(url)
        request.add_header('User-agent', r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1')
        with urllib.request.urlopen(request) as response :
          with open(where_to_save, 'wb+') as out_file :
            shutil.copyfileobj(response, out_file)
            return True
      except Exception as e:
        traceback.print_exc()
    return False

  @staticmethod
  def open_json(path):
    with open(path) as json_file :    
      try :
        return json.load(json_file)
      except Exception as e :
        print("Error: "+traceback.format_exc())
    return None

  @staticmethod
  def check_thread_is_alive(thread_name) :
    for thread in threading.enumerate() :
      if thread.getName() == thread_name and thread.is_alive() :
        return True
    return False

  @staticmethod
  def create_and_start_thread(target, thread_name="", args=[], kwargs={}, daemon=True) :
    if not Util.check_thread_is_alive(thread_name) :
      thread = threading.Thread(target=target, name=thread_name, args=args, kwargs=kwargs, daemon=daemon)
      thread.start()
      return thread
    return None

  @staticmethod
  def check_process_is_alive(process_name) :
    Util.multiprocessing_list
    for process in Util.multiprocessing_list :
      if process.name == process_name :
        if process.is_alive() :
          return True
        else :
          Util.multiprocessing_list.remove(process)
    return False

  @staticmethod
  def create_and_start_process(target, process_name="", args=[], kwargs={}, daemon=True) :
    Util.multiprocessing_list
    if not Util.check_process_is_alive(process_name) :
      process = multiprocessing.Process(target=target, name=process_name, args=args, kwargs=kwargs, daemon=daemon)
      process.start()
      Util.multiprocessing_list.append(process)
      return process
    return None

  @staticmethod
  def setTimeout(time, func):
    timer = threading.Timer(time, func)
    timer.start()
    return timer

  @staticmethod
  def checksum_sha1(fname):
    hash_sha1 = hashlib.sha1()
    with open(fname, "rb") as f:
      for chunk in iter(lambda: f.read(4096), b""):
        hash_sha1.update(chunk)
    return hash_sha1.hexdigest()

  @staticmethod
  def checksum_sha1_equalcompare(fname1, fname2):
    return Util.checksum_sha1(fname1) == Util.checksum_sha1(fname2)

  @staticmethod
  def split_string_and_find(string_to_split, search_value, split_delimiter=" ") :
    string_splitted = string_to_split.split(split_delimiter)
    return Util.indexOf(string_splitted, search_value) 

  @staticmethod
  def split_string_and_find_on_multiple(string_to_split, search_values, split_delimiter=" ") :
    string_splitted = string_to_split.split(split_delimiter)
    for search_value in search_values :
      index = Util.indexOf(string_splitted, search_value) 
      if index >= 0 :
        return index
    return -1

  @staticmethod
  def split_string_and_findLast(string_to_split, search_value, split_delimiter=" ") :
    string_splitted = string_to_split.split(split_delimiter)
    return Util.lastIndexOf(string_splitted, search_value) 

  @staticmethod
  def indexOf(list_to_search, search_value) :
    index = -1
    try :
      index = list_to_search.index(search_value)
    except Exception as e:
      pass
    return index

  @staticmethod
  def lastIndexOf(list_to_search, search_value) :
    index = -1
    list_to_search_reversed = reversed(list_to_search)
    list_length = len(list_to_search)
    try :
      index = next(i for i,v in zip(range(list_length-1, 0, -1), list_to_search_reversed) if v == search_value)
    except Exception as e:
      pass
    return index

  @staticmethod
  def firstIndexOfMultiple(list_to_search, search_values) :
    index = -1
    string = ""
    for search_value in search_values :
      index_search = Util.indexOf(list_to_search, search_value)
      if index_search >= 0 and index == -1 :
        index = index_search
        string = search_value
      elif index_search >= 0 :
        index = min(index, index_search)
        string = search_value
    return {
      "index": index,
      "string": string
    }

  @staticmethod
  def find_and_get_pre_string_and_first_match(string, search_value) :
    result = None
    index = Util.indexOf(string, search_value)
    if index >= 0 :
      result = string[:index+len(search_value)]
    return result

  @staticmethod
  def find_and_get_pre_string_and_matches(string, search_value) :
    result = None
    index = Util.indexOf(string, search_value)
    if index >= 0 :
      result = string[:index+len(search_value)]
      string = string[index+len(search_value):]
      count_occ = string.count(search_value)
      i = 0
      while i < count_occ :
        result += " "+search_value
        i = i + 1
    return result

  @staticmethod
  def get_region_scope_first_match(view, scope, selection, selector) :
    scope = Util.find_and_get_pre_string_and_first_match(scope, selector)
    if scope :
      for region in view.find_by_selector(scope) :
        if region.contains(selection):
          selection.a = region.begin()
          selection.b = selection.a
          return {
            "scope": scope,
            "region": region,
            "region_string": view.substr(region),
            "region_string_stripped": view.substr(region).strip(),
            "selection": selection
          }
    return None

  @staticmethod
  def get_region_scope_last_match(view, scope, selection, selector) :
    scope = Util.find_and_get_pre_string_and_matches(scope, selector)
    if scope :
      for region in view.find_by_selector(scope) :
        if region.contains(selection):
          selection.a = region.begin()
          selection.b = selection.a
          return {
            "scope": scope,
            "region": region,
            "region_string": view.substr(region),
            "region_string_stripped": view.substr(region).strip(),
            "selection": selection
          }
    return None

  @staticmethod
  def find_regions_on_same_depth_level(view, scope, selection, selectors, depth_level, forward) :
    scope_splitted = scope.split(" ")
    regions = list()
    add_unit = 1 if forward else -1
    if len(scope_splitted) >= depth_level :  
      for selector in selectors :
        while Util.indexOf(scope_splitted, selector) == -1 :
          if selection.a == 0 or len(scope_splitted) < depth_level :
            return list()
          selection.a = selection.a + add_unit
          selection.b = selection.a 
          scope = view.scope_name(selection.begin()).strip()
          scope_splitted = scope.split(" ")
        region = view.extract_scope(selection.begin())
        regions.append({
          "scope": scope,
          "region": region,
          "region_string": view.substr(region),
          "region_string_stripped": view.substr(region).strip(),
          "selection": selection
        })
    return regions

  @staticmethod
  def get_current_region_scope(view, selection) :
    scope = view.scope_name(selection.begin()).strip()
    for region in view.find_by_selector(scope) :
      if region.contains(selection):
        selection.a = region.begin()
        selection.b = selection.a
        return {
          "scope": scope,
          "region": region,
          "region_string": view.substr(region),
          "region_string_stripped": view.substr(region).strip(),
          "selection": selection
        }
    return None

  @staticmethod
  def get_parent_region_scope(view, selection) :
    scope = view.scope_name(selection.begin()).strip()
    scope = " ".join(scope.split(" ")[:-1])
    for region in view.find_by_selector(scope) :
      if region.contains(selection):
        selection.a = region.begin()
        selection.b = selection.a
        return {
          "scope": scope,
          "region": region,
          "region_string": view.substr(region),
          "region_string_stripped": view.substr(region).strip(),
          "selection": selection
        }
    return None

  @staticmethod
  def get_specified_parent_region_scope(view, selection, parent) :
    scope = view.scope_name(selection.begin()).strip()
    scope = scope.split(" ")
    index_parent = Util.lastIndexOf(scope, parent)
    scope = " ".join(scope[:index_parent+1])
    for region in view.find_by_selector(scope) :
      if region.contains(selection):
        selection.a = region.begin()
        selection.b = selection.a
        return {
          "scope": scope,
          "region": region,
          "region_string": view.substr(region),
          "region_string_stripped": view.substr(region).strip(),
          "selection": selection
        }
    return None

  @staticmethod
  def cover_regions(regions) :
    first_region = regions[0]
    other_regions = regions[1:]
    for region in other_regions :
      first_region = first_region.cover(region)
    return first_region

  @staticmethod
  def rowcol_to_region(view, row, col, endcol):
    start = view.text_point(row, col)
    end = view.text_point(row, endcol)
    return sublime.Region(start, end)
  
  @staticmethod
  def trim_Region(view, region):
    new_region = sublime.Region(region.begin(), region.end())
    while(view.substr(new_region).startswith(" ") or view.substr(new_region).startswith("\n")):
      new_region.a = new_region.a + 1
    while(view.substr(new_region).endswith(" ") or view.substr(new_region).startswith("\n")):
      new_region.b = new_region.b - 1
    return new_region

  @staticmethod
  def selection_in_js_scope(view, point = -1, except_for = ""):
    sel_begin = view.sel()[0].begin() if point == -1 else point
    return view.match_selector(
      sel_begin,
      'source.js ' + except_for
    ) or view.match_selector(
      sel_begin,
      'source.js.embedded.html ' + except_for
    )
  
  @staticmethod
  def replace_with_tab(view, region, pre="", after="", add_to_each_line_before="", add_to_each_line_after="") :
    lines = view.substr(region).split("\n")
    body = list()
    empty_line = 0
    for line in lines :
      if line.strip() == "" :
        empty_line = empty_line + 1
        if empty_line == 2 :
          empty_line = 1 # leave at least one empty line
          continue
      else :
        empty_line = 0
      line = "\t"+add_to_each_line_before+line+add_to_each_line_after
      body.append(line)
    if body[len(body)-1].strip() == "" :
      del body[len(body)-1]
    body = "\n".join(body)
    return pre+body+after

  @staticmethod
  def replace_without_tab(view, region, pre="", after="", add_to_each_line_before="", add_to_each_line_after="") :
    lines = view.substr(region).split("\n")
    body = list()
    empty_line = 0
    for line in lines :
      if line.strip() == "" :
        empty_line = empty_line + 1
        if empty_line == 2 :
          empty_line = 1 # leave at least one empty line
          continue
      else :
        empty_line = 0
      body.append(add_to_each_line_before+line+add_to_each_line_after)
    if body[len(body)-1].strip() == "" :
      del body[len(body)-1]
    body = "\n".join(body)
    return pre+body+after

  @staticmethod
  def get_whitespace_from_line_begin(view, region) :
    line = view.line(region)
    whitespace = ""
    count = line.begin()
    sel_begin = region.begin()
    while count != sel_begin :
      count = count + 1
      whitespace = whitespace + " "
    return whitespace

  @staticmethod
  def add_whitespace_indentation(view, region, string, replace="\t", add_whitespace_end=True) :
    whitespace = Util.get_whitespace_from_line_begin(view, region)
    if replace == "\n" :
      lines = string.split("\n")
      lines = [whitespace+line for line in lines]
      lines[0] = lines[0].lstrip()
      string = "\n".join(lines)
      return string
    if add_whitespace_end :
      lines = string.split("\n")
      lines[len(lines)-1] = whitespace + lines[-1:][0]
    string = "\n".join(lines)
    string = re.sub("(["+replace+"]+)", whitespace+r"\1", string)
    return string

  @staticmethod
  def go_to_centered(view, row, col):
    while view.is_loading() :
      time.sleep(.1)
    point = view.text_point(row, col)
    view.sel().clear()
    view.sel().add(point)
    view.show_at_center(point)

  @staticmethod
  def wait_view(view, fun):
    while view.is_loading() :
      time.sleep(.1)
    fun()

  @staticmethod
  def move_content_to_parent_folder(path):
    for filename in os.listdir(path):
      shutil.move(os.path.join(path, filename), os.path.dirname(path)) 
    os.rmdir(path)

  @staticmethod
  def merge_dicts(*dict_args):
      result = {}
      for dictionary in dict_args:
          result.update(dictionary)
      return result

  @staticmethod
  def removeItemIfExists(arr, item):
    if item in arr: arr.remove(item)

  @staticmethod
  def getListItemIfExists(arr, item):
    if item in arr : 
      return item
    return None

  @staticmethod
  def delItemIfExists(obj, key):
    try :
      del obj[key]
    except KeyError as e:
      pass

  @staticmethod
  def getDictItemIfExists(obj, key):
    try :
      return obj[key]
    except KeyError as e:
      pass
    return None

  @staticmethod
  def create_and_show_panel(output_panel_name, window = None, syntax=os.path.join("Packages", PACKAGE_NAME,"javascript_enhancements.sublime-syntax")):
    window = sublime.active_window() if not window else window
    panel = window.create_output_panel(output_panel_name, False)
    panel.set_read_only(True)
    if syntax :
      panel.set_syntax_file(syntax)
    window.run_command("show_panel", {"panel": "output."+output_panel_name})
    return panel

  @staticmethod
  def execute(command, command_args, chdir="", wait_terminate=True, func_stdout=None, args_func_stdout=[]) :

    if sublime.platform() == 'windows':
      args = [command] + command_args
    else :
      command_args_list = list()
      for command_arg in command_args :
        command_args_list.append(shlex.quote(command_arg))
      command_args = " ".join(command_args_list)
      args = shlex.quote(command)+" "+command_args
    
    print(args)

    if wait_terminate :

      with subprocess.Popen(args, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=(None if not chdir else chdir)) as p:

        lines_output = []
        lines_error = []

        thread_output = Util.create_and_start_thread(Util._wrapper_func_stdout_listen_output, "", (p, None, [], lines_output))

        thread_error = Util.create_and_start_thread(Util._wrapper_func_stdout_listen_error, "", (p, None, [], lines_error))

        if thread_output:
          thread_output.join()

        if thread_error:
          thread_error.join()

        lines = "\n".join(lines_output) + "\n" + "\n".join(lines_error)

        return [True if p.wait() == 0 else False, lines]

    elif not wait_terminate and func_stdout :

      return Util.create_and_start_thread(Util._wrapper_func_stdout, "", (args, func_stdout, args_func_stdout, chdir))
  
  @staticmethod
  def _wrapper_func_stdout(args, func_stdout, args_func_stdout=[], chdir=""):

    with subprocess.Popen(args, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, preexec_fn=os.setsid, cwd=(None if not chdir else chdir)) as p:

      func_stdout(None, p, *args_func_stdout)
      
      thread_output = Util.create_and_start_thread(Util._wrapper_func_stdout_listen_output, "", (p, func_stdout, args_func_stdout))

      thread_error = Util.create_and_start_thread(Util._wrapper_func_stdout_listen_error, "", (p, func_stdout, args_func_stdout))

      if thread_output:
        thread_output.join()
        
      if thread_error:
        thread_error.join()

      if p.wait() == 0:
        func_stdout("OUTPUT-SUCCESS", p, *args_func_stdout)
      else :
        func_stdout("OUTPUT-ERROR", p, *args_func_stdout)

      func_stdout("OUTPUT-DONE", p, *args_func_stdout)

  @staticmethod
  def _wrapper_func_stdout_listen_output(process, func_stdout=None, args_func_stdout=[], lines_output=[]):
    for line in process.stdout:
      # if (line.strip().endswith(b"Looks like this is an Ionic 1 project, would you like to install @ionic/cli-pl")) :
      #   line = line.strip() + process.stdout.read(len("gin-ionic1 and continue? (Y/n)")+1)
      # print(line)
      line = codecs.decode(line, "utf-8", "ignore").strip()
      line = re.sub(r'\x1b(\[.*?[@-~]|\].*?(\x07|\x1b\\))', '', line)
      line = re.sub(r'[\n\r]', '\n', line)
      lines_output.append(line)
      line = line + ( b"\n" if type(line) is bytes else "\n" ) 
      if func_stdout :
        func_stdout(line, process, *args_func_stdout)
  
  @staticmethod
  def _wrapper_func_stdout_listen_error(process, func_stdout=None, args_func_stdout=[], lines_error=[]):
    for line in process.stderr:
      line = codecs.decode(line, "utf-8", "ignore").strip()
      line = re.sub(r'\x1b(\[.*?[@-~]|\].*?(\x07|\x1b\\))', '', line)
      line = re.sub(r'[\n\r]', '\n', line)
      lines_error.append(line)
      line = line + ( b"\n" if type(line) is bytes else "\n" ) 
      if func_stdout :
        func_stdout(line, process, *args_func_stdout)

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


def subl(args):
  
  executable_path = sublime.executable_path()
  if sublime.platform() == 'osx':
    app_path = executable_path[:executable_path.rfind(".app/") + 5]
    executable_path = app_path + "Contents/SharedSupport/bin/subl"

  if sublime.platform() == 'windows' :
    args = [executable_path] + args
  else :
    args_list = list()
    for arg in args :
      args_list.append(shlex.quote(arg))
    args = shlex.quote(executable_path) + " " + " ".join(args_list)

  return subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def overwrite_default_javascript_snippet():
  if not os.path.isdir(os.path.join(SUBLIME_PACKAGES_PATH, "JavaScript")) :
    os.mkdir(os.path.join(SUBLIME_PACKAGES_PATH, "JavaScript"))
  if not os.path.isdir(os.path.join(SUBLIME_PACKAGES_PATH, "JavaScript", "Snippets")) :
    os.mkdir(os.path.join(SUBLIME_PACKAGES_PATH, "JavaScript", "Snippets"))
  for file_name in os.listdir(os.path.join(PACKAGE_PATH, "JavaScript-overwrite-default-snippet")) :
    if file_name.endswith(".sublime-snippet") and os.path.isfile(os.path.join(PACKAGE_PATH, "JavaScript-overwrite-default-snippet", file_name)) :
      shutil.copy(os.path.join(PACKAGE_PATH, "JavaScript-overwrite-default-snippet", file_name), os.path.join(SUBLIME_PACKAGES_PATH, "JavaScript", "Snippets", file_name))

class startPlugin():
  def init(self):
    
    sublime.set_timeout_async(lambda: overwrite_default_javascript_snippet())

    sublime.set_timeout_async(lambda: NodeJSInstaller.install(NODE_JS_VERSION))

    window = sublime.active_window()
    view = window.active_view()

    sublime.set_timeout_async(lambda: show_flow_errorsViewEventListener(view).on_activated_async())
    sublime.set_timeout_async(lambda: load_bookmarks_viewViewEventListener(view).on_load_async())

mainPlugin = startPlugin()

import sublime, sublime_plugin
import os
from collections import namedtuple

flowCLIRequirements = namedtuple('flowCLIRequirements', [
    'filename', 'project_root', 'contents', 'cursor_pos', 'row', 'col', 'row_offset'
])

FLOW_DEFAULT_CONFIG_PATH = os.path.join(PACKAGE_PATH, "flow", ".flowconfig")

def find_flow_config(filename):
  if not filename or filename is '/':
    return FLOW_DEFAULT_CONFIG_PATH

  potential_root = os.path.dirname(filename)
  if os.path.isfile(os.path.join(potential_root, '.flowconfig')):
    return potential_root

  return find_flow_config(potential_root)

def flow_parse_cli_dependencies(view, **kwargs):
  filename = view.file_name()
  contextual_keys = sublime.active_window().extract_variables()
  folder_path = contextual_keys.get("folder")
  if folder_path and os.path.isdir(folder_path) and os.path.isfile(os.path.join(folder_path, '.flowconfig')) :    
    project_root = folder_path
  else :
    project_root = find_flow_config(filename)

  cursor_pos = 0
  if kwargs.get('cursor_pos') :
    cursor_pos = kwargs.get('cursor_pos')
  else :
    if len(view.sel()) > 0 :
      cursor_pos = view.sel()[0].begin()
    
  row, col = view.rowcol(cursor_pos)

  if kwargs.get('check_all_source_js_embedded'):
    embedded_regions = view.find_by_selector("source.js.embedded.html")
    if not embedded_regions :
      return flowCLIRequirements(
        filename=None,
        project_root=None,
        contents="",
        cursor_pos=None,
        row=None, col=None,
        row_offset=0
      )
    flowCLIRequirements_list = list()
    for region in embedded_regions:
      current_contents = view.substr(region)
      row_scope, col_scope = view.rowcol(region.begin())
      row_offset = row_scope
      row_scope = row - row_scope

      flowCLIRequirements_list.append(flowCLIRequirements(
        filename=filename,
        project_root=project_root,
        contents=current_contents,
        cursor_pos=cursor_pos,
        row=row, col=col,
        row_offset=row_offset
      ))
    return flowCLIRequirements_list
  else :
    scope_region = None
    if view.match_selector(
        cursor_pos,
        'source.js'
    ) and view.substr(sublime.Region(0, view.size()) ) == "" :
      scope_region = sublime.Region(0, 0)
    else :
      scope = view.scope_name(cursor_pos)
      result = Util.get_region_scope_first_match(view, scope, sublime.Region(cursor_pos, cursor_pos), "source.js")
      if not result:
        result = Util.get_region_scope_first_match(view, scope, sublime.Region(cursor_pos, cursor_pos), "source.js.embedded.html")
        if not result:
          return flowCLIRequirements(
            filename=None,
            project_root=None,
            contents="",
            cursor_pos=None,
            row=None, col=None,
            row_offset=0
          )
      scope_region = result["region"]
    current_contents = view.substr(scope_region)
    row_scope, col_scope = view.rowcol(scope_region.begin())
    row_offset = row_scope
    row_scope = row - row_scope
    """
    current_contents = view.substr(
      sublime.Region(0, view.size())
    )
    """
    
    if kwargs.get('add_magic_token'):
      current_lines = current_contents.splitlines()
      try :
        current_line = current_lines[row_scope]
      except IndexError as e:
        return flowCLIRequirements(
            filename=None,
            project_root=None,
            contents="",
            cursor_pos=None,
            row=None, col=None,
            row_offset=0
          )
      tokenized_line = ""
      if not kwargs.get('not_add_last_part_tokenized_line') :
        tokenized_line = current_line[0:col] + 'AUTO332' + current_line[col:-1]
      else :
        tokenized_line = current_line[0:col] + 'AUTO332'
      current_lines[row_scope] = tokenized_line
      current_contents = '\n'.join(current_lines)

    return flowCLIRequirements(
      filename=filename,
      project_root=project_root,
      contents=current_contents,
      cursor_pos=cursor_pos,
      row=row, col=col,
      row_offset=row_offset
    )


import sublime, sublime_plugin
import json, os, re, webbrowser, cgi, threading, shutil
from distutils.version import LooseVersion

import os, time

class SocketCallUI(object):

  def __init__(self, name, host, port, client_ui_file, wait_for_new_changes=1):
    super(SocketCallUI, self).__init__()
    self.name = name
    self.host = host
    self.port = port
    self.client_ui_file = client_ui_file
    self.socket = None
    self.last_modified = None
    self.wait_for_new_changes = wait_for_new_changes

  def init(self):
    if not os.path.isfile(self.client_ui_file):
      raise Exception("Client UI file \""+self.client_ui_file+"\" not found.")
    self.last_modified = time.time()

  def start(self, handle_recv, handle_client_connection, handle_client_disconnection):
    self.init()
    self.listen(handle_recv, handle_client_connection, handle_client_disconnection)
    self.call_ui()

  def call_ui(self):
    call_ui(self.client_ui_file , self.host, self.port)

  def listen(self, handle_recv, handle_client_connection, handle_client_disconnection):
    self.socket = mySocketServer(self.name) 
    self.socket.bind(self.host, self.port)
    self.socket.handle_recv(handle_recv)
    self.socket.handle_client_connection(handle_client_connection)
    self.socket.handle_client_disconnection(handle_client_disconnection)
    self.socket.listen()
    
  def is_socket_closed(self):
    return True if not self.socket or not self.socket.get_socket() else False

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
    

class wait_modified_asyncViewEventListener():
  last_change = time.time()
  waiting = False
  prefix_thread_name = ""
  wait_time = 1

  def on_modified_async(self, *args, **kwargs) :
    self.last_change = time.time()
    if not self.prefix_thread_name :
      raise Exception("No prefix_thread_name to wait_modified_asyncViewEventListener")
    Util.create_and_start_thread(self.on_modified_async_with_thread, self.prefix_thread_name+"_"+str(self.view.id()), args=args, kwargs=kwargs)

  def wait(self):
    if time.time() - self.last_change <= self.wait_time:
      if not self.waiting:
        self.waiting = True
      else :
        return
      self.last_change = time.time()
      while time.time() - self.last_change <= self.wait_time:
        time.sleep(.1)
      self.waiting = False

  def on_modified_async_with_thread(self, *args, **kwargs):
    return


class surround_withCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    selections = view.sel()
    region = None
    sub = None
    case = args.get("case")
    if case == "if_else_statement" :
      if len(selections) != 2 :
        return

      sel_1 = Util.trim_Region(view, selections[0])
      space_1 = Util.get_whitespace_from_line_begin(view, sel_1)
      new_text = Util.replace_with_tab(view, sel_1, space_1+"\n"+space_1+"if (bool) {\n"+space_1, "\n"+space_1+"} ")
      view.replace(edit, sel_1, new_text.strip())

      sel_2 = Util.trim_Region(view, selections[1])
      space_2 = Util.get_whitespace_from_line_begin(view, sel_2)
      new_text = Util.replace_with_tab(view, sel_2, " else {\n"+space_2, "\n"+space_2+"}\n"+space_2)
      view.replace(edit, sel_2, new_text.strip())
    else :
      for selection in selections :
        selection = Util.trim_Region(view, selection)
        if view.substr(selection).strip() == "" :
          continue
        space = Util.get_whitespace_from_line_begin(view, selection)

        if case == "if_statement" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"if (bool) {\n"+space, "\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "while_statement" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"while (bool) {\n"+space, "\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "do_while_statement" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"do {\n"+space, "\n"+space+"} while (bool);\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "for_statement" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"for ( ; bool ; ) {\n"+space, "\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "try_catch_statement" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"try {\n"+space, "\n"+space+"} catch (e) {\n"+space+"\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "try_catch_finally_statement" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"try {\n"+space, "\n"+space+"} catch (e) {\n"+space+"\n"+space+"} finally {\n"+space+"\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)
          
  def is_enabled(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    selections = view.sel()
    for selection in selections :
      if view.substr(selection).strip() != "" :
        return True
    return False

  def is_visible(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    selections = view.sel()
    for selection in selections :
      if view.substr(selection).strip() != "" :
        return True
    return False

class delete_surroundedCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    selections = view.sel()
    case = args.get("case")
    for selection in selections :
      scope = view.scope_name(selection.begin()).strip()
      scope_splitted = scope.split(" ")
      if case == "strip_quoted_string" :
        result = Util.firstIndexOfMultiple(scope_splitted, ("string.quoted.double.js", "string.quoted.single.js", "string.template.js"))
        selector = result.get("string")
        item = Util.get_region_scope_first_match(view, scope, selection, selector)
        if item :
          region_scope = item.get("region")
          new_str = item.get("region_string")
          new_str = new_str[1:-1]
          view.replace(edit, region_scope, new_str)

  def is_enabled(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True
    
  def is_visible(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True

class sort_arrayCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    node = NodeJS()
    view = self.view
    selections = view.sel()
    for selection in selections :
      scope = view.scope_name(selection.begin()).strip()
      result = Util.get_region_scope_first_match(view, scope, selection, "meta.brackets.js")
      if result :
        region = result.get("region")
        array_string = result.get("region_string_stripped")
        node = NodeJS()
        case = args.get("case")
        sort_func = ""
        if case == "compare_func_desc" :
          sort_func = "function(x,y){return y-x;}"
        elif case == "compare_func_asc" :
          sort_func = "function(x,y){return x-y;}"
        elif case == "alpha_asc" :
          sort_func = ""
        elif case == "alpha_desc" :
          sort_func = ""
        sort_result = node.eval("var array = "+array_string+"; console.log(array.sort("+sort_func+")"+( ".reverse()" if case == "alpha_desc" else "" )+")").strip()
        view.replace(edit, region, sort_result)

  def is_enabled(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    selections = view.sel()
    for selection in selections :
      scope = view.scope_name(selection.begin()).strip()
      index = Util.split_string_and_find(scope, "meta.brackets.js")
      if index < 0 :
        return False
    return True

  def is_visible(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    selections = view.sel()
    for selection in selections :
      scope = view.scope_name(selection.begin()).strip()
      index = Util.split_string_and_find(scope, "meta.brackets.js")
      if index < 0 :
        return False
    return True

import re

class create_class_from_object_literalCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    selections = view.sel()
    for selection in selections :
      scope = view.scope_name(selection.begin()).strip()
      depth_level = Util.split_string_and_find(scope, "meta.object-literal.js")
      item_object_literal = Util.get_region_scope_first_match(view, scope, selection, "meta.object-literal.js")

      if item_object_literal :

        scope = item_object_literal.get("scope")
        object_literal_region = item_object_literal.get("region")
        selection = item_object_literal.get("selection")
        object_literal = item_object_literal.get("region_string_stripped")
        node = NodeJS()
        object_literal = re.sub(r'[\n\r\t]', ' ', object_literal)
        object_literal = json.loads(node.eval("JSON.stringify("+object_literal+")", "print"))
        object_literal = [(key, json.dumps(value)) for key, value in object_literal.items()]

        list_ordered = ("keyword.operator.assignment.js", "variable.other.readwrite.js", "storage.type.js")
        items = Util.find_regions_on_same_depth_level(view, scope, selection, list_ordered, depth_level, False)
        if items :
          last_selection = items[-1:][0].get("selection")
          class_name = items[1].get("region_string_stripped")
          regions = [(item.get("region")) for item in items]
          regions.append(object_literal_region)
          regions = Util.cover_regions(regions)
          parameters = list()
          constructor_body = list()
          get_set = list()
          for parameter in object_literal: 
            parameters.append( parameter[0] + ( "="+parameter[1] if json.loads(parameter[1]) != "required" else "") )
            constructor_body.append( "\t\tthis."+parameter[0]+" = "+parameter[0]+";" )
            get_set.append("\tget "+parameter[0]+"() {\n\t\treturn this."+parameter[0]+";\n\t}")
            get_set.append("\tset "+parameter[0]+"("+parameter[0]+") {\n\t\tthis."+parameter[0]+" = "+parameter[0]+";\n\t}")
          parameters = ", ".join(parameters)
          constructor_body = '\n'.join(constructor_body)
          get_set = '\n\n'.join(get_set)
          js_syntax  = "class "+class_name+" {\n"
          js_syntax += "\n\tconstructor ("+parameters+") {\n"
          js_syntax += constructor_body
          js_syntax += "\n\t}\n\n"
          js_syntax += get_set
          js_syntax += "\n}"
          js_syntax = Util.add_whitespace_indentation(view, regions, js_syntax)
          view.replace(edit, regions, js_syntax)

  def is_enabled(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    selection = view.sel()[0]
    scope = view.scope_name(selection.begin()).strip()
    index = Util.split_string_and_find(scope, "meta.object-literal.js")
    if index < 0 :
      return False
    return True

  def is_visible(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    selection = view.sel()[0]
    scope = view.scope_name(selection.begin()).strip()
    index = Util.split_string_and_find(scope, "meta.object-literal.js")
    if index < 0 :
      return False
    return True
      
class split_string_lines_to_variableCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    selections = view.sel()
    for selection in selections :
      scope = view.scope_name(selection.begin()).strip()
      scope_splitted = scope.split(" ")
      case = args.get("case")
      if case == "split" :
        result = Util.firstIndexOfMultiple(scope_splitted, ("string.quoted.double.js", "string.quoted.single.js", "string.template.js"))
        scope_string = scope_splitted[result.get("index")]
        selector = result.get("string")
        item = Util.get_region_scope_first_match(view, scope, selection, selector)
        if item :
          lines = item.get("region_string_stripped")[1:-1].split("\n")
          str_splitted = list()
          str_splitted.append("var str = \"\"")
          for line in lines :
            line = line if scope_string == "string.template.js" else line.strip()[0:-1]
            line = line.strip()
            if line :
              str_splitted.append( "str += "+"%r"%line )
          str_splitted = "\n".join(str_splitted)
          str_splitted = Util.add_whitespace_indentation(view, selection, str_splitted, "\n")
          view.replace(edit, item.get("region"), str_splitted)
          
  def is_visible(self, **args) :
    view = self.view
    if Util.split_string_and_find(view.scope_name(0), "source.js") < 0 :
      return False
    selection = view.sel()[0]
    scope = view.scope_name(selection.begin()).strip()
    scope_splitted = scope.split(" ")
    result = Util.firstIndexOfMultiple(scope_splitted, ("string.quoted.double.js", "string.quoted.single.js", "string.template.js"))
    if result.get("index") < 0 :
      return False
    return True

add_type_any_parameter_list = []
class add_type_any_parameterCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    global add_type_any_parameter_list
    view = self.view
    params = []
    if not "recall" in args :
      params = view.find_by_selector("variable.parameter.function.js")
      add_type_any_parameter_list = params
    else :
      params = add_type_any_parameter_list

    if "recall" in args and args["recall"] >= 0 :
      args["recall"] = args["recall"] + 1

    if params :
      view.insert(edit, params[0].end() + ( args["recall"]*len("/* : any */") if "recall" in args else 0 ) , "/* : any */")
      del params[0]
      if not "recall" in args :
        view.run_command("add_type_any_parameter", {"recall" : 0})
      else :
        view.run_command("add_type_any_parameter", {"recall": args["recall"]})

import sublime, sublime_plugin
import sys, imp, os, webbrowser, re, cgi

class JavaScriptCompletions():

  def get(self, key):
    return sublime.load_settings('settings.sublime-settings').get(key)

javascriptCompletions = JavaScriptCompletions()

import sublime, sublime_plugin
import os

def build_type_from_func_details(comp_details):
  if comp_details :

    paramText = ""
    for param in comp_details["params"]:
      if not paramText:
        paramText += param['name'] + (": " + param['type'] if param['type'] else "")
      else:
        paramText += ", " + param['name'] + (": " + param['type'] if param['type'] else "")

    return ("("+paramText+")" if paramText else "()") + " => " + comp_details["return_type"]

  return ""

def build_completion_snippet(name, params):
  snippet = name + '({})'
  paramText = ''

  count = 1
  for param in params:
    if not paramText:
      paramText += "${" + str(count) + ":" + param['name'] + "}"
    else:
      paramText += ', ' + "${" + str(count) + ":" + param['name'] + "}"
    count = count + 1

  return snippet.format(paramText)

def create_completion(comp_name, comp_type, comp_details) :
  t = tuple()
  t += (comp_name + '\t' + comp_type, )
  t += (build_completion_snippet(
      comp_name,
      comp_details["params"]
    )
    if comp_details else comp_name, )
  return t

class javascript_completionsEventListener(sublime_plugin.EventListener):
  completions = None
  completions_ready = False

  # Used for async completions.
  def run_auto_complete(self):
    sublime.active_window().active_view().run_command("auto_complete", {
      'disable_auto_insert': True,
      'api_completions_only': False,
      'next_completion_if_showing': False,
      'auto_complete_commit_on_tab': True
    })

  def on_query_completions(self, view, prefix, locations):
    # Return the pending completions and clear them

    if not view.match_selector(
        locations[0],
        'source.js - string - comment'
    ):
      return

    view = sublime.active_window().active_view()

    scope = view.scope_name(view.sel()[0].begin()-1).strip()

    if not prefix and not scope.endswith(" punctuation.accessor.js") :
      sublime.active_window().active_view().run_command(
        'hide_auto_complete'
      )
      return []

    if self.completions_ready and self.completions:
      self.completions_ready = False
      return self.completions

    sublime.set_timeout_async(
      lambda: self.on_query_completions_async(
        view, prefix, locations
      )
    )

    if not self.completions_ready or not self.completions:
      return ([], sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

  def on_query_completions_async(self, view, prefix, locations):
    self.completions = None

    if not view.match_selector(
        locations[0],
        'source.js - string - comment'
    ):
      return

    deps = flow_parse_cli_dependencies(view, add_magic_token=True, cursor_pos=locations[0])

    if deps.project_root is '/':
      return

    node = NodeJS()
    
    result = node.execute_check_output(
      "flow",
      [
        'autocomplete',
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

    if result[0]:
      result = result[1]
      self.completions = list()
      for match in result['result'] :

        comp_name = match['name']
        comp_type = match['type'] if match['type'] else build_type_from_func_details(match.get('func_details'))

        if comp_type.startswith("((") or comp_type.find("&") >= 0 :
          sub_completions = comp_type.split("&")
          for sub_comp in sub_completions :
            sub_comp = sub_comp.strip()
            sub_type = sub_comp[1:-1] if comp_type.startswith("((") else sub_comp
            
            if not match.get('func_details') :
              text_params = sub_type[ : sub_type.rfind(" => ") if sub_type.rfind(" => ") >= 0 else None ]
              text_params = text_params.strip()
              match["func_details"] = dict()
              match["func_details"]["params"] = list()
              start = 1 if sub_type.find("(") == 0 else sub_type.find("(")+1
              end = text_params.rfind(")")
              params = text_params[start:end].split(",")
              for param in params :
                param_dict = dict()
                param_info = param.split(":")
                param_dict["name"] = param_info[0].strip()
                match['func_details']["params"].append(param_dict)

            completion = create_completion(comp_name, sub_type, match.get('func_details'))
            self.completions.append(completion)
        else :
          completion = create_completion(comp_name, comp_type, match.get('func_details'))
          self.completions.append(completion)

      self.completions += load_default_autocomplete(view, self.completions, prefix, locations[0])
      self.completions = (self.completions, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)
      self.completions_ready = True

      sublime.active_window().active_view().run_command(
        'hide_auto_complete'
      )
      
      view = sublime.active_window().active_view()
      sel = view.sel()[0]
      if view.substr(view.word(sel)).strip() :
        self.run_auto_complete()

  def on_text_command(self, view, command_name, args):
    sel = view.sel()[0]
    if not view.match_selector(
        sel.begin(),
        'source.js - string - comment'
    ):
      return

    if command_name == "left_delete" :
      scope = view.scope_name(view.sel()[0].begin()-1).strip()
      if scope.endswith(" punctuation.accessor.js") :
        sublime.active_window().active_view().run_command(
          'hide_auto_complete'
        )

  def on_selection_modified_async(self, view) :

    selections = view.sel()
    if len(selections) == 0:
      return
      
    sel = selections[0]
    if not view.match_selector(
        sel.begin(),
        'source.js - string - comment'
    ):
      return

    scope1 = view.scope_name(selections[0].begin()-1).strip()
    scope2 = view.scope_name(selections[0].begin()-2).strip()

    if scope1.endswith(" punctuation.accessor.js") and not scope2.endswith(" punctuation.accessor.js") and view.substr(selections[0].begin()-2).strip() :
    
      locations = list()
      locations.append(selections[0].begin())

      sublime.set_timeout_async(
        lambda: self.on_query_completions_async(
          view, "", locations
        )
      )


import sublime, sublime_plugin
import os



class go_to_defCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    if args and "point" in args :
      point = args["point"]
    else :
      point = view.sel()[0].begin()
    self.go_to_def(view, point)

  def go_to_def(self, view, point):
    view = sublime.active_window().active_view()
    view.sel().clear()
    view.sel().add(point)
    sublime.active_window().run_command("goto_definition")
    if view.sel()[0].begin() == point :
      # try flow get-def
      sublime.status_message("")
      deps = flow_parse_cli_dependencies(view)
      node = NodeJS()
      result = node.execute_check_output(
        "flow",
        [
          'get-def',
          '--from', 'sublime_text',
          '--root', deps.project_root,
          '--json',
          view.file_name(),
          str(deps.row + 1), str(deps.col + 1)
        ],
        is_from_bin=True,
        use_fp_temp=True, 
        fp_temp_contents=deps.contents, 
        is_output_json=True,
        use_only_filename_view_flow=True
      )
      if result[0] :
        row = result[1]["line"]-1
        col = result[1]["start"]-1
        if result[1]["path"] != "-" and os.path.isfile(result[1]["path"]) :
          view = sublime.active_window().open_file(result[1]["path"])     
        sublime.set_timeout_async(lambda: Util.go_to_centered(view, row, col))

  def is_enabled(self):
    view = self.view
    if not Util.selection_in_js_scope(view, -1, "- string - comment"):
      return False
    return True

  def is_visible(self):
    view = self.view
    if not Util.selection_in_js_scope(view, -1, "- string - comment"):
      return False
    return True

js_css = ""
with open(os.path.join(JC_SETTINGS_FOLDER, "style.css")) as css_file:
  js_css = "<style>"+css_file.read()+"</style>"

if int(sublime.version()) >= 3124 :

  default_completions = Util.open_json(os.path.join(PACKAGE_PATH, 'default_autocomplete.json')).get('completions')

  def load_default_autocomplete(view, comps_to_campare, prefix, location, isHover = False):

    if not prefix :
      return []
    
    scope = view.scope_name(location-(len(prefix)+1)).strip()

    if scope.endswith(" punctuation.accessor.js") :
      return []

    prefix = prefix.lower()
    completions = default_completions
    completions_to_add = []
    for completion in completions: 
      c = completion[0].lower()
      if not isHover:
        if c.startswith(prefix):
          completions_to_add.append((completion[0], completion[1]))
      else :
        if len(completion) == 3 and c.startswith(prefix) :
          completions_to_add.append(completion[2])
    final_completions = []
    for completion in completions_to_add:
      flag = False
      for c_to_campare in comps_to_campare:
        if not isHover and completion[0].split("\t")[0] == c_to_campare[0].split("\t")[0] :
          flag = True
          break
        elif isHover and completion["name"] == c_to_campare["name"] :
          flag = True
          break
      if not flag :
        final_completions.append(completion)

    return final_completions

  import sublime, sublime_plugin
  
  def description_details_html(description):
    description_name = "<span class=\"name\">" + cgi.escape(description['name']) + "</span>"
    description_return_type = ""
  
    text_pre_params = ""
  
    parameters_html = ""
    if description['func_details'] :
  
      if not description['type'].startswith("(") :
        text_pre_params = description['type'][ : description['type'].rfind(" => ") if description['type'].rfind(" => ") >= 0 else None ]
        text_pre_params = "<span class=\"text-pre-params\">" + cgi.escape(text_pre_params[:text_pre_params.find("(")]) + "</span>"
  
      for param in description['func_details']["params"]:
        is_optional = True if param['name'].find("?") >= 0 else False
        param['name'] = cgi.escape(param['name'].replace("?", ""))
        param['type'] = cgi.escape(param['type']) if param.get('type') else None
        if not parameters_html:
          parameters_html += "<span class=\"parameter-name\">" + param['name'] + "</span>" + ( "<span class=\"parameter-is-optional\">?</span>" if is_optional else "" ) + ( ": <span class=\"parameter-type\">" + param['type'] + "</span>" if param['type'] else "" )
        else:
          parameters_html += ', ' + "<span class=\"parameter-name\">" + param['name'] + "</span>" + ( "<span class=\"parameter-is-optional\">?</span>" if is_optional else "" ) + ( ": <span class=\"parameter-type\">" + param['type'] + "</span>" if param['type'] else "" )
      parameters_html = "("+parameters_html+")"
  
      description_return_type = cgi.escape(description['func_details']["return_type"]) if description['func_details']["return_type"] else ""
    elif description['type'] :
      description_return_type = cgi.escape(description['type'])
    if description_return_type :
      description_return_type = " => <span class=\"return-type\">"+description_return_type+"</span>"
  
    html = """ 
    <div class=\"container-description\">
      <div>"""+description_name+text_pre_params+parameters_html+description_return_type+"""</div>
      <div class=\"container-go-to-def\"><a href="go_to_def" class="go-to-def">Go to definition</a></div>
    </div>
    """
    return html
  
  class on_hover_descriptionEventListener(sublime_plugin.EventListener):
  
    def on_hover(self, view, point, hover_zone) :
      sublime.set_timeout_async(lambda: on_hover_description_async(view, point, hover_zone, point))
  
  def on_hover_description_async(view, point, hover_zone, popup_position) :
    if not view.match_selector(
        point,
        'source.js - comment'
    ):
      return
  
    if hover_zone != sublime.HOVER_TEXT :
      return
  
    region = view.word(point)
    word = view.substr(region)
    if not word.strip() :
      return
      
    cursor_pos = region.end()
  
    deps = flow_parse_cli_dependencies(view, cursor_pos=cursor_pos, add_magic_token=True, not_add_last_part_tokenized_line=True)
  
    if deps.project_root is '/':
      return
  
    node = NodeJS()
  
    result = node.execute_check_output(
      "flow",
      [
        'autocomplete',
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
  
    html = ""
  
    if result[0]:
      descriptions = result[1]["result"] + load_default_autocomplete(view, result[1]["result"], word, region.begin(), True)
  
      for description in descriptions :
        if description['name'] == word :
  
          if description['type'].startswith("((") or description['type'].find("&") >= 0 :
            sub_completions = description['type'].split("&")
            for sub_comp in sub_completions :
  
              sub_comp = sub_comp.strip()
              sub_type = sub_comp[1:-1] if description['type'].startswith("((") else sub_comp
                         
              text_params = sub_type[ : sub_type.rfind(" => ") if sub_type.rfind(" => ") >= 0 else None ]
              text_params = text_params.strip()
              description["func_details"] = dict()
              description["func_details"]["params"] = list()
              description["func_details"]["return_type"] = ""
              if sub_type.rfind(" => ") >= 0 :
                description["func_details"]["return_type"] = sub_type[sub_type.rfind(" => ")+4:].strip()
              start = 1 if sub_type.find("(") == 0 else sub_type.find("(")+1
              end = text_params.rfind(")")
              params = text_params[start:end].split(",")
              for param in params :
                param_dict = dict()
                param_info = param.split(":")
                param_dict["name"] = param_info[0].strip()
                if len(param_info) > 1 :
                  param_dict["type"] = param_info[1].strip()
                description['func_details']["params"].append(param_dict)
  
              html += description_details_html(description)
          else :
  
            html += description_details_html(description)
  
    if not html :
      deps = flow_parse_cli_dependencies(view)
      if deps.project_root is '/':
        return
      row, col = view.rowcol(point)
      node = NodeJS()
      result = node.execute_check_output(
        "flow",
        [
          'type-at-pos',
          '--from', 'sublime_text',
          '--root', deps.project_root,
          '--path', deps.filename,
          '--json',
          str(row - deps.row_offset + 1), str(col + 1)
        ],
        is_from_bin=True,
        use_fp_temp=True, 
        fp_temp_contents=deps.contents, 
        is_output_json=True
      )
  
      if result[0] and result[1].get("type") and result[1]["type"] != "(unknown)":
        description = dict()
        description["name"] = ""
        description['func_details'] = dict()
        description['func_details']["params"] = list()
        description['func_details']["return_type"] = ""
        is_function = False
        matches = re.match("^([a-zA-Z_]\w+)", result[1]["type"])
        if matches :
          description["name"] = matches.group()
        if result[1]["type"].find(" => ") >= 0 :
          description['func_details']["return_type"] = cgi.escape(result[1]["type"][result[1]["type"].find(" => ")+4:])
        else :
          description['func_details']["return_type"] = cgi.escape(result[1]["type"])
        if result[1]["type"].find("(") == 0:
          is_function = True
          start = 1
          end = result[1]["type"].find(")")
          params = result[1]["type"][start:end].split(",")
          description['func_details']["params"] = list()
          for param in params :
            param_dict = dict()
            param_info = param.split(":")
            param_dict["name"] = cgi.escape(param_info[0].strip())
            if len(param_info) == 2 :
              param_dict["type"] = cgi.escape(param_info[1].strip())
            else :
              param_dict["type"] = None
            description['func_details']["params"].append(param_dict)
  
        description_name = "<span class=\"name\">" + cgi.escape(description['name']) + "</span>"
        description_return_type = ""
  
        parameters_html = ""
        if description['func_details'] :
  
          for param in description['func_details']["params"]:
            is_optional = True if param['name'].find("?") >= 0 else False
            param['name'] = param['name'].replace("?", "")
            if not parameters_html:
              parameters_html += "<span class=\"parameter-name\">" + param['name'] + "</span>" + ( "<span class=\"parameter-is-optional\">?</span>" if is_optional else "" ) + ( ": <span class=\"parameter-type\">" + param['type'] + "</span>" if param['type'] else "" )
            else:
              parameters_html += ', ' + "<span class=\"parameter-name\">" + param['name'] + "</span>" + ( "<span class=\"parameter-is-optional\">?</span>" if is_optional else "" ) + ( ": <span class=\"parameter-type\">" + param['type'] + "</span>" if param['type'] else "" )
          parameters_html = "("+parameters_html+")" if is_function else ""
  
          description_return_type = description['func_details']["return_type"]
        elif description['type'] :
          description_return_type = description['type']
        if description_return_type :
          description_return_type = (" => " if description['name'] or is_function else "") + "<span class=\"return-type\">"+description_return_type+"</span>"
  
        html += """ 
        <div class=\"container-description\">
          <div>"""+description_name+parameters_html+description_return_type+"""</div>
          <div class=\"container-go-to-def\"><a href="go_to_def" class="go-to-def">Go to definition</a></div>
        </div>
        """
  
    func_action = lambda x: view.run_command("go_to_def", args={"point": point}) if x == "go_to_def" else ""
  
    if html :
        view.show_popup("""
        <html><head></head><body>
        """+js_css+"""
          <div class=\"container-hint-popup\">
            """ + html + """    
          </div>
        </body></html>""", sublime.COOPERATE_WITH_AUTO_COMPLETE | sublime.HIDE_ON_MOUSE_MOVE_AWAY, popup_position, 1150, 60, func_action )
    

  import sublime, sublime_plugin
  
  class show_hint_parametersCommand(sublime_plugin.TextCommand):
    
    def run(self, edit, **args):
      view = self.view
  
      scope = view.scope_name(view.sel()[0].begin()).strip()
  
      meta_fun_call = "meta.function-call.method.js"
      result = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call+" meta.group.js")
  
      if not result :
        meta_fun_call = "meta.function-call.js"
        result = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call+" meta.group.js")
  
      if result :
        point = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call)["region"].begin()
        sublime.set_timeout_async(lambda: on_hover_description_async(view, point, sublime.HOVER_TEXT, view.sel()[0].begin()))
  
    def is_enabled(self) :
      view = self.view
      sel = view.sel()[0]
      if not view.match_selector(
          sel.begin(),
          'source.js - comment'
      ):
        return False
  
      scope = view.scope_name(view.sel()[0].begin()).strip()
      
      meta_fun_call = "meta.function-call.method.js"
      result = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call+" meta.group.js")
  
      if not result :
        meta_fun_call = "meta.function-call.js"
        result = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call+" meta.group.js")
  
      if result :
        point = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call)["region"].begin()
        scope_splitted = scope.split(" ")
        find_and_get_scope = Util.find_and_get_pre_string_and_matches(scope, meta_fun_call+" meta.group.js")
        find_and_get_scope_splitted = find_and_get_scope.split(" ")
        if (
            (
              len(scope_splitted) == len(find_and_get_scope_splitted) + 1 
              or scope == find_and_get_scope 
              or (
                  len(scope_splitted) == len(find_and_get_scope_splitted) + 2 
                  and ( Util.get_parent_region_scope(view, view.sel()[0])["scope"].split(" ")[-1] == "string.quoted.double.js"
                      or Util.get_parent_region_scope(view, view.sel()[0])["scope"].split(" ")[-1] == "string.quoted.single.js"
                      or Util.get_parent_region_scope(view, view.sel()[0])["scope"].split(" ")[-1] == "string.template.js"
                    ) 
                ) 
            ) 
            and not scope.endswith("meta.block.js") 
            and not scope.endswith("meta.object-literal.js")
          ) :
          return True
      return False
  
    def is_visible(self) :
      view = self.view
      sel = view.sel()[0]
      if not view.match_selector(
          sel.begin(),
          'source.js - comment'
      ):
        return False
  
      scope = view.scope_name(view.sel()[0].begin()).strip()
      
      meta_fun_call = "meta.function-call.method.js"
      result = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call+" meta.group.js")
  
      if not result :
        meta_fun_call = "meta.function-call.js"
        result = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call+" meta.group.js")
  
      if result :
        point = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call)["region"].begin()
        scope_splitted = scope.split(" ")
        find_and_get_scope = Util.find_and_get_pre_string_and_matches(scope, meta_fun_call+" meta.group.js")
        find_and_get_scope_splitted = find_and_get_scope.split(" ")
        if (
            (
              len(scope_splitted) == len(find_and_get_scope_splitted) + 1 
              or scope == find_and_get_scope 
              or (
                  len(scope_splitted) == len(find_and_get_scope_splitted) + 2 
                  and ( Util.get_parent_region_scope(view, view.sel()[0])["scope"].split(" ")[-1] == "string.quoted.double.js"
                      or Util.get_parent_region_scope(view, view.sel()[0])["scope"].split(" ")[-1] == "string.quoted.single.js"
                      or Util.get_parent_region_scope(view, view.sel()[0])["scope"].split(" ")[-1] == "string.template.js"
                    ) 
                ) 
            ) 
            and not scope.endswith("meta.block.js") 
            and not scope.endswith("meta.object-literal.js")
          ) :
          return True
      return False

  def show_flow_errors(view) :
  
    view_settings = view.settings()
    sel = view.sel()[0]
    if not view.match_selector(
        sel.begin(),
        'source.js'
    ) and not view.find_by_selector("source.js.embedded.html") :
      return None
  
    deps_list = list()
    if view.find_by_selector("source.js.embedded.html") :
      deps_list = flow_parse_cli_dependencies(view, check_all_source_js_embedded=True)
    else :
      deps_list = [flow_parse_cli_dependencies(view)]
  
    errors = []
    description_by_row = {}
    regions = []
    for deps in deps_list:
      if deps.project_root is '/':
        return None
  
      # if view_settings.get("flow_weak_mode") :
      #   deps = deps._replace(contents = "/* @flow weak */" + deps.contents)
  
      node = NodeJS()
      
      result = node.execute_check_output(
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
        is_output_json=True,
        clean_output_flow=True
      )
  
      if result[0]:
  
        if result[1]['passed']:
          continue
  
        for error in result[1]['errors']:
          description = ''
          operation = error.get('operation')
          row = -1
          for i in range(len(error['message'])):
            message = error['message'][i]
            if i == 0 :
              row = int(message['line']) + deps.row_offset - 1
              col = int(message['start']) - 1
              endcol = int(message['end'])
  
              # if row == 0 and view_settings.get("flow_weak_mode") : #fix when error start at the first line with @flow weak mode
              #   col = col - len("/* @flow weak */")
              #   endcol = endcol - len("/* @flow weak */")
  
              regions.append(Util.rowcol_to_region(view, row, col, endcol))
  
              if operation:
                description += operation["descr"]
  
            if not description :
              description += message['descr']
            else :
              description += ". " + message['descr']
  
          if row >= 0 :
            row_description = description_by_row.get(row)
            if not row_description:
              description_by_row[row] = {
                "col": col,
                "description": description
              }
            if row_description and description not in row_description:
              description_by_row[row]["description"] += '; ' + description
              
        errors = result[1]['errors']
  
    if errors :
      view.add_regions(
        'flow_error', regions, 'scope.js', 'dot',
        sublime.DRAW_SQUIGGLY_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
      )
      return {"errors": errors, "description_by_row": description_by_row}
    
    view.erase_regions('flow_error')
    view.set_status('flow_error', 'Flow: no errors')
    return None
  
  def hide_flow_errors(view) :
    view.erase_regions('flow_error')
    view.erase_status('flow_error')
  
  class handle_flow_errorsCommand(sublime_plugin.TextCommand):
  
    def run(self, edit, **args):
      if args :
        if args["type"] == "show" :
          show_flow_errors(self.view)
        elif args["type"] == "hide" :
          hide_flow_errors(self.view)
  

  import cgi, time
  
  class show_flow_errorsViewEventListener(wait_modified_asyncViewEventListener, sublime_plugin.ViewEventListener):
  
    description_by_row = {}
    errors = []
    callback_setted_use_flow_checker_on_current_view = False
    prefix_thread_name = "show_flow_errors_view_event_listener"
    wait_time = .35
  
    def on_activated_async(self) :
      
      view = self.view
  
      selections = view.sel()
   
      if len(selections) == 0:
        return
        
      sel = selections[0]
      if not view.match_selector(
          sel.begin(),
          'source.js'
      ) and not view.find_by_selector("source.js.embedded.html"):
        hide_flow_errors(view)
        return
  
      settings = get_project_settings()
      if settings :
        if not settings["flow_settings"]["flow_checker_enabled"] or not is_project_view(view) :
          hide_flow_errors(view)
          return
        elif settings["flow_settings"]["flow_checker_enabled"] :
          comments = view.find_by_selector('source.js comment')
          flow_comment_found = False
          for comment in comments:
            if "@flow" in view.substr(comment) :
              flow_comment_found = True
              break
          if not flow_comment_found :
            hide_flow_errors(view)
            return
      else :
        settings = view.settings()
        if not self.callback_setted_use_flow_checker_on_current_view :
          settings.clear_on_change("use_flow_checker_on_current_view")
          settings.add_on_change("use_flow_checker_on_current_view", lambda: sublime.set_timeout_async(lambda: self.on_modified_async()))
          self.callback_setted_use_flow_checker_on_current_view = True
        if not settings.get("use_flow_checker_on_current_view") :
          hide_flow_errors(view)
          return 
  
      sublime.set_timeout_async(lambda: self.on_modified_async())
  
    def on_modified_async(self):
      super(show_flow_errorsViewEventListener, self).on_modified_async()
      
    def on_modified_async_with_thread(self, recheck=True) : 
      view = self.view
  
      selections = view.sel()
   
      if len(selections) == 0:
        return
        
      sel = selections[0]
      if not view.match_selector(
          sel.begin(),
          'source.js'
      ) and not view.find_by_selector("source.js.embedded.html"):
        hide_flow_errors(view)
        return
      
      self.wait()  
  
      settings = get_project_settings()
      if settings :
        if not settings["flow_settings"]["flow_checker_enabled"] or not is_project_view(view) :
          hide_flow_errors(view)
          return
        elif settings["flow_settings"]["flow_checker_enabled"] :
          comments = view.find_by_selector('source.js comment')
          flow_comment_found = False
          for comment in comments:
            if "@flow" in view.substr(comment) :
              flow_comment_found = True
              break
          if not flow_comment_found :
            hide_flow_errors(view)
            return
      elif not view.settings().get("use_flow_checker_on_current_view") :
        hide_flow_errors(view)
        return 
  
      self.errors = []
      self.description_by_row = {}
      result = show_flow_errors(view)
  
      if result :
        self.errors = result["errors"]
        self.description_by_row = result["description_by_row"]
  
      sublime.set_timeout_async(lambda: self.on_selection_modified_async())
  
      # recheck only first time to avoid error showing bug (because of async method)
      # while the code execution is here but the user is modifying content
      if (recheck) :
        sublime.set_timeout_async(lambda: self.on_modified_async_with_thread(recheck=False))
  
  
    def on_hover(self, point, hover_zone) :
      view = self.view
      view.erase_phantoms("flow_error")
      if hover_zone != sublime.HOVER_GUTTER :
        return
  
      sel = sublime.Region(point, point)
      if (not view.match_selector(
          sel.begin(),
          'source.js'
      ) and not view.find_by_selector("source.js.embedded.html")) or not self.errors or not view.get_regions("flow_error"):
        hide_flow_errors(view)
        return
      
      settings = get_project_settings()
      if settings :
        if not settings["flow_settings"]["flow_checker_enabled"] or not is_project_view(view) :
          hide_flow_errors(view)
          return
        elif settings["flow_settings"]["flow_checker_enabled"] :
          comments = view.find_by_selector('source.js comment')
          flow_comment_found = False
          for comment in comments:
            if "@flow" in view.substr(comment) :
              flow_comment_found = True
              break
          if not flow_comment_found :
            hide_flow_errors(view)
            return
      elif not view.settings().get("use_flow_checker_on_current_view") :
        hide_flow_errors(view)
        return 
  
      row, col = view.rowcol(sel.begin())
  
      error_for_row = self.description_by_row.get(row)
      
      if error_for_row:
        text = cgi.escape(error_for_row["description"]).split(" ")
        html = ""
        i = 0
        while i < len(text) - 1:
          html += text[i] + " " + text[i+1] + " "
          i += 2
          if i % 10 == 0 :
            html += " <br> "
        if len(text) % 2 != 0 :
          html += text[len(text) - 1]
  
        region_phantom = sublime.Region( view.text_point(row, error_for_row["col"]), view.text_point(row, error_for_row["col"]) )
        sublime.set_timeout_async(lambda: view.add_phantom("flow_error", region_phantom, '<html style="padding: 0px; margin: 5px; background-color: rgba(255,255,255,0);"><body style="border-radius: 10px; padding: 10px; background-color: #F44336; margin: 0px;">'+html+'</body></html>', sublime.LAYOUT_BELOW))
  
  
    def on_selection_modified_async(self, *args) :
  
      view = self.view
      
      selections = view.sel()
   
      if len(selections) == 0:
        return
        
      sel = selections[0]
      if (not view.match_selector(
          sel.begin(),
          'source.js'
      ) and not view.find_by_selector("source.js.embedded.html")) or not self.errors or not view.get_regions("flow_error"):
        hide_flow_errors(view)
        return
   
      view.erase_phantoms("flow_error")
  
      settings = get_project_settings()
      if settings :
        if not settings["flow_settings"]["flow_checker_enabled"] or not is_project_view(view) :
          hide_flow_errors(view)
          return
        elif settings["flow_settings"]["flow_checker_enabled"] :
          comments = view.find_by_selector('source.js comment')
          flow_comment_found = False
          for comment in comments:
            if "@flow" in view.substr(comment) :
              flow_comment_found = True
              break
          if not flow_comment_found :
            hide_flow_errors(view)
            return
      elif not view.settings().get("use_flow_checker_on_current_view") :
        hide_flow_errors(view)
        return 
  
      row, col = view.rowcol(sel.begin())
  
      error_count = len(self.errors)
      error_count_text = 'Flow: {} error{}'.format(
        error_count, '' if error_count is 1 else 's'
      )
      error_for_row = self.description_by_row.get(row)
      if error_for_row:
        view.set_status(
          'flow_error', error_count_text + ': ' + error_for_row["description"]
        )
      else:
        view.set_status('flow_error', error_count_text)
  

  import sublime, sublime_plugin
  
  class navigate_flow_errorsCommand(sublime_plugin.TextCommand):
  
    def run(self, edit, **args) :
      
      view = self.view
  
      regions = view.get_regions("flow_error")
      if not regions:
        return
  
      move_type = args.get("type")
  
      if move_type == "next" :
  
        r_next = self.find_next(regions)
        if r_next :
          row, col = view.rowcol(r_next.begin())
  
          Util.go_to_centered(view, row, col)
  
      elif move_type == "previous" :
  
        r_prev = self.find_prev(regions)
        if r_prev :
          row, col = view.rowcol(r_prev.begin())
  
          Util.go_to_centered(view, row, col)
  
    def find_next(self, regions):
      view = self.view
  
      sel = view.sel()[0]
  
      for region in regions :
        if region.begin() > sel.begin() :
          return region
  
      if(len(regions) > 0) :
        return regions[0]
  
      return None
  
    def find_prev(self, regions):
      view = self.view
  
      sel = view.sel()[0]
  
      previous_regions = []
      for region in regions :
        if region.begin() < sel.begin() :
          previous_regions.append(region)
  
      if not previous_regions and len(regions) > 0:
        previous_regions.append(regions[len(regions)-1])
  
      return previous_regions[len(previous_regions)-1] if len(previous_regions) > 0 else None
  

import sublime, sublime_plugin
import traceback, os, json, io, sys, imp

result_js = ""
region_selected = None
popup_is_showing = False
ej_css = """
<style>
html{
  margin: 0;
  padding: 0;
}
body{
  color: #fff;
  margin: 0;
  padding: 0;
}
.container{
  background-color: #202A31;
  padding: 10px;
}
a{
  color: #fff;
  display: block;
  margin: 10px 0;
}
</style>
"""

def action_result(action):
  global result_js
  global region_selected

  view = sublime.active_window().active_view()
  sel = region_selected
  str_selected = view.substr(sel).strip()

  if action == "copy_to_clipboard" :
    sublime.set_clipboard(result_js[1])

  elif action == "replace_text" :
    view.run_command("replace_text")

  elif action == "view_result_formatted":
    view.run_command("view_result_formatted")

  view.hide_popup()
  result_js = []

class view_result_formattedCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    global result_js
    global region_selected

    sublime.active_window().show_input_panel("Result", result_js[1], back_to_popup, back_to_popup, back_to_popup)

class replace_textCommand(sublime_plugin.TextCommand):

  def run(self, edit):
    global result_js
    global region_selected

    view = self.view
    sel = Util.trim_Region(view, region_selected)
    view.replace(edit, sel, result_js[1])
    if region_selected.a < region_selected.b :
      region_selected.b = region_selected.a+len(result_js[1])
    else :
      region_selected.a = region_selected.b+len(result_js[1])

class ej_hide_popupEventListener(sublime_plugin.EventListener):
  def on_modified_async(self, view) :
    global popup_is_showing
    if popup_is_showing :
      view.hide_popup()
      popup_is_showing = False

class evaluate_javascriptCommand(sublime_plugin.TextCommand):

  def run(self, edit, is_line=False, eval_type="eval"):
    global result_js
    global region_selected
    global popup_is_showing

    view = self.view
    sel = view.sel()[0]
    popup_is_showing = False
    str_selected = view.substr(sel).strip()

    if is_line:
      lines = view.lines(sel)
      region_selected = lines[0]
      str_selected = view.substr(region_selected)
    else: 
      if not str_selected and region_selected : 
        region = get_start_end_code_highlights_eval()
        region_selected = sublime.Region(region[0], region[1])
        lines = view.lines(region_selected)
        str_selected = ""
        for line in lines:
          str_selected += view.substr(view.full_line(line))
      elif str_selected:
        lines = view.lines(sel)
        region_selected = sublime.Region if not region_selected else region_selected
        region_selected = sublime.Region(lines[0].begin(), lines[-1:][0].end())
      elif not str_selected :
        return
    
    if not region_selected :
      return

    view.run_command("show_start_end_dot_eval")

    try:
      node = NodeJS(check_local=True)
      result_js = node.eval(str_selected, eval_type=eval_type, strict_mode=True)
      if result_js[0] :
        popup_is_showing = True
        view.show_popup("<html><head></head><body>"+ej_css+"""<div class=\"container\">
          <p class="result">Result: """+result_js[1]+"""</p>
          <div><a href="view_result_formatted">View result formatted with space(\\t,\\n,...)</a></div>
          <div><a href="copy_to_clipboard">Copy result to clipboard</a></div>
          <div><a href="replace_text">Replace text with result</a></div>
          </div>
        </body></html>""", sublime.COOPERATE_WITH_AUTO_COMPLETE, -1, 400, 400, action_result)
      else :
        sublime.active_window().show_input_panel("Result", "Error: "+result_js[1], None , None, None)
    except Exception as e:
      #sublime.error_message("Error: "+traceback.format_exc())
      sublime.active_window().show_input_panel("Result", "Error: "+traceback.format_exc(), None , None, None)

  def is_enabled(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True

  def is_visible(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True

class show_start_end_dot_evalCommand(sublime_plugin.TextCommand) :
  def run(self, edit) :
    global region_selected
    view = self.view
    lines = view.lines(region_selected)
    view.add_regions("region-dot", [lines[0], lines[-1:][0]],  "code", "dot", sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE)
    #view.add_regions("region-body", [region_selected],  "code", "", sublime.DRAW_NO_FILL)
  
  def is_enabled(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True

  def is_visible(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True

class hide_start_end_dot_evalCommand(sublime_plugin.TextCommand) :
  def run(self, edit) :
    view = self.view
    view.erase_regions("region-dot")
    #view.erase_regions("region-body")
  
  def is_enabled(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True

  def is_visible(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True

def get_start_end_code_highlights_eval() :
  view = sublime.active_window().active_view()
  return [view.line(view.get_regions("region-dot")[0]).begin(), view.line(view.get_regions("region-dot")[1]).end()]

def back_to_popup(*str_arg):
  view = sublime.active_window().active_view()
  view.run_command("evaluate_javascript")
  return



import sublime, sublime_plugin
import subprocess, time, json

socket_server_list["structure_javascript"] = SocketCallUI("structure_javascript", "localhost", 11113, os.path.join(HELPER_FOLDER, "structure_javascript", "ui", "client.js"), 1)

def update_structure_javascript(view, filename, clients=[]):
  global socket_server_list 

  deps = flow_parse_cli_dependencies(view)
  
  node = NodeJS()

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
  
    if not socket_server_list["structure_javascript"].is_socket_closed() :
      
      filename = self.view.file_name()
      filename = filename if filename else ""

      clients = socket_server_list["structure_javascript"].socket.find_clients_by_field("filename", filename)
      
      if clients:
        socket_server_list["structure_javascript"].update_time()
        socket_server_list["structure_javascript"].handle_new_changes(update_structure_javascript, "update_structure_javascript"+filename, self.view, filename, clients)

class close_structure_javascriptEventListener(sublime_plugin.EventListener):
  closing_view = None
  def on_close(self, view):
    self.closing_view = view
    sublime.set_timeout_async(self.on_close_async)

  def on_close_async(self):
    global socket_server_list 
  
    if self.closing_view and not socket_server_list["structure_javascript"].is_socket_closed() :
      
      filename = self.closing_view.file_name()
      filename = filename if filename else ""

      clients = socket_server_list["structure_javascript"].socket.find_clients_by_field("filename", filename)
      
      if clients:
        data = dict()
        data["command"] = "close_window"
        data = json.dumps(data)
        socket_server_list["structure_javascript"].socket.send_to(clients[0]["socket"], clients[0]["addr"], data)

class view_structure_javascriptCommand(sublime_plugin.TextCommand):
  def run(self, edit, *args):
    global socket_server_list

    if not socket_server_list["structure_javascript"].is_socket_closed() :
      socket_server_list["structure_javascript"].socket.close_if_not_clients()
      
    if socket_server_list["structure_javascript"].is_socket_closed() :
    
      def recv(conn, addr, ip, port, client_data, client_fields):
        global socket_server_list
        json_data = json.loads(client_data)

        if json_data["command"] == "ready":
          filename = client_fields["view"].file_name()
          filename = filename if filename else ""

          update_structure_javascript(client_fields["view"], filename, [{"socket": conn, "addr": addr}])

        elif json_data["command"] == "set_dot_line" and os.path.isfile(client_fields["filename"]):
          other_view = sublime.active_window().open_file(client_fields["filename"])
          sublime.set_timeout_async(lambda: self.set_dot_line(other_view, json_data["line"]))    

      def client_connected(conn, addr, ip, port, client_fields):
        global socket_server_list   
        view = sublime.active_window().active_view()
        filename = view.file_name()
        filename = filename if filename else ""
        client_fields["filename"] = filename
        client_fields["view"] = view

      def client_disconnected(conn, addr, ip, port):
        global socket_server_list
        socket_server_list["structure_javascript"].socket.close_if_not_clients()

      socket_server_list["structure_javascript"].start(recv, client_connected, client_disconnected)

    else :
      socket_server_list["structure_javascript"].call_ui()

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


import sublime, sublime_plugin
import json, time

bookmarks = []
latest_bookmarks_view = dict()

def set_bookmarks(is_project = False, set_dot = False):
  global bookmarks
  view = sublime.active_window().active_view()

  if is_project and ( not is_project_view(view) or not is_javascript_project() ) :
    sublime.error_message("Can't recognize JavaScript Project.")
    return
  elif is_project and is_project_view(view) and is_javascript_project() :
    project_settings = get_project_settings()
    bookmarks = Util.open_json(os.path.join(project_settings["settings_dir_name"], 'bookmarks.json')) or []
  else :
    bookmarks = Util.open_json(os.path.join(BOOKMARKS_FOLDER, 'bookmarks.json')) or []

  view.erase_regions("region-dot-bookmarks")
  if set_dot :
    lines = []
    lines = [view.line(view.text_point(bookmark["line"], 0)) for bookmark in search_bookmarks_by_view(view, is_project, is_from_set = True)]
    view.add_regions("region-dot-bookmarks", lines,  "code", "bookmark", sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE)

def update_bookmarks(is_project = False, set_dot = False):
  global bookmarks
  path = ""
  view = sublime.active_window().active_view()

  if is_project and ( not is_project_view(view) or not is_javascript_project() ) :
    sublime.error_message("Can't recognize JavaScript Project.")
    return
  elif is_project and is_project_view(view) and is_javascript_project() :
    project_settings = get_project_settings()
    path = os.path.join(project_settings["settings_dir_name"], 'bookmarks.json')
  else :
    path = os.path.join(BOOKMARKS_FOLDER, 'bookmarks.json')

  with open(path, 'w+') as bookmarks_json:
    bookmarks_json.write(json.dumps(bookmarks))

  view.erase_regions("region-dot-bookmarks")
  if set_dot :
    lines = []
    lines = [view.line(view.text_point(bookmark["line"], 0)) for bookmark in search_bookmarks_by_view(view, is_project)]

    view.add_regions("region-dot-bookmarks", lines,  "code", "bookmark", sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE)

def add_bookmark(view, line, name = "", is_project = False) :
  if not view.file_name() or line < 0:
    return False

  global bookmarks

  if is_project :
    set_bookmarks(True, True)
  else :
    set_bookmarks(False, True)

  bookmark = {
    "file_name": view.file_name(),
    "line": line,
    "name": name.strip()
  }

  if get_index_bookmark(bookmark) == -1:

    bookmarks.append(bookmark)
    update_bookmarks(is_project, True)

def remove_bookmark(bookmark, is_project = False) :

  if not bookmark["file_name"] or bookmark["line"] < 0:
    return False

  if is_project :
    set_bookmarks(True, True)
  else :
    set_bookmarks(False, True)

  global bookmarks

  if bookmark in bookmarks :
    bookmarks.remove(bookmark)
    update_bookmarks(is_project, True)

def search_bookmarks_by_view(view, is_project = False, is_from_set = False):
  if not view.file_name():
    return []

  global bookmarks

  if not is_from_set :
    if is_project :
      set_bookmarks(True, True)
    else :
      set_bookmarks(False, True)

  view_bookmarks = []

  for bookmark in bookmarks:
    if bookmark['file_name'] == view.file_name() :
      view_bookmarks.append(bookmark)

  return view_bookmarks

def delete_bookmarks_by_view(view, is_project = False):
  if not view.file_name():
    return False

  global bookmarks

  if is_project :
    set_bookmarks(True, True)
  else :
    set_bookmarks(False, True)

  new_bookmarks = []

  for bookmark in bookmarks:
    if bookmark['file_name'] != view.file_name() :
      new_bookmarks.append(bookmark)

  bookmarks = new_bookmarks
  update_bookmarks(is_project, True)

def get_index_bookmark(bookmark) :
  global bookmarks

  if bookmark in bookmarks :
    return bookmarks.index(bookmark)

  return -1

def open_bookmarks_and_show(index, bookmarks_view = []) :

  if index < 0 :
    return

  global bookmarks
  global latest_bookmarks_view

  if len(bookmarks_view) > 0 :
    bookmark = bookmarks_view[index]
  else :
    bookmark = bookmarks[index]

  latest_bookmarks_view = {"index": index, "bookmarks": bookmarks_view} if bookmarks_view else dict()

  view = sublime.active_window().open_file(bookmark["file_name"])

  sublime.set_timeout_async(lambda: Util.go_to_centered(view, bookmark["line"], 0))

def set_multiple_bookmarks_names(view, index, selections, is_project = False):

  if len(selections) <= 0:
    return

  row = selections[0].begin()

  new_selections = []

  for index, sel in enumerate(selections):
    if index == 0:
      continue
    new_selections.append(sel)

  sublime.active_window().show_input_panel("Bookmark Name "+str(index+1)+": ", "",
    lambda name: add_bookmark(view, view.rowcol(row)[0], name, is_project) or set_multiple_bookmarks_names(view, index+1, new_selections),
    None,
    None
  )

class add_global_bookmark_hereCommand(sublime_plugin.TextCommand) :

  def run(self, edit):

    view = self.view

    selections = view.sel()

    set_multiple_bookmarks_names(view, 0, selections, False)
      
class add_project_bookmark_hereCommand(sublime_plugin.TextCommand) :

  def run(self, edit):

    if not is_javascript_project() :
      sublime.error_message("Can't recognize JavaScript Project.")
      return 

    view = self.view

    selections = view.sel()

    set_multiple_bookmarks_names(view, 0, selections, True)


class show_bookmarksCommand(sublime_plugin.TextCommand):

  def run(self, edit, **args) :
    global bookmarks
    global latest_bookmarks_view

    window = sublime.active_window()
    view = self.view

    show_type = args.get("type")

    if show_type == "global" or show_type == "view" :
      set_bookmarks(False, True)
    else :
      set_bookmarks(True, True)

    if len(bookmarks) <= 0:
      return 

    if show_type == "global" or show_type == "global_project" :

      items = [ ( bookmark['name'] + ", line: " + str(bookmark["line"]) ) if bookmark['name'] else ( bookmark['file_name'] + ", line: " + str(bookmark["line"]) ) for bookmark in bookmarks]

      window.show_quick_panel(items, lambda index: open_bookmarks_and_show(index))

    elif show_type == "view" or show_type == "view_project" : 

      bookmarks_view = search_bookmarks_by_view(view, False if show_type == "view" else True)

      latest_bookmarks_view = {"index": 0, "bookmarks": bookmarks_view} if bookmarks_view else dict()

      items = [ ( bookmark['name'] + ", line: " + str(bookmark["line"]) ) if bookmark['name'] else ( "line: " + str(bookmark["line"]) ) for bookmark in bookmarks_view]
      
      window.show_quick_panel(items, lambda index: open_bookmarks_and_show(index, bookmarks_view))

class delete_bookmarksCommand(sublime_plugin.TextCommand):

  def run(self, edit, **args) :
    global bookmarks

    window = sublime.active_window()
    view = self.view

    show_type = args.get("type")

    if show_type == "global" or show_type == "global_project" :

      bookmarks = []
      update_bookmarks(False if show_type == "global" else True, True)

    elif show_type == "view" or show_type == "view_project" : 

      delete_bookmarks_by_view(view, False if show_type == "view" else True)

    elif show_type == "single_global" or show_type == "single_global_project" : 

      items = [ ( bookmark['name'] + ", line: " + str(bookmark["line"]) ) if bookmark['name'] else ( bookmark['file_name'] + ", line: " + str(bookmark["line"]) ) for bookmark in bookmarks]

      window.show_quick_panel(items, lambda index: remove_bookmark(bookmarks[index], False if show_type == "single_global" else True))

class navigate_bookmarksCommand(sublime_plugin.TextCommand):

  def run(self, edit, **args) :

    window = sublime.active_window()
    view = self.view

    move_type = args.get("type")

    regions = view.get_regions("region-dot-bookmarks")

    if move_type == "next" :

      r_next = self.find_next(regions)
      if r_next :
        row, col = view.rowcol(r_next.begin())

        Util.go_to_centered(view, row, col)

    elif move_type == "previous" :

      r_prev = self.find_prev(regions)
      if r_prev :
        row, col = view.rowcol(r_prev.begin())

        Util.go_to_centered(view, row, col)

  def find_next(self, regions):
    view = self.view

    sel = view.sel()[0]

    for region in regions :
      if region.begin() > sel.begin() :
        return region

    if(len(regions) > 0) :
      return regions[0]

    return None

  def find_prev(self, regions):
    view = self.view

    sel = view.sel()[0]

    previous_regions = []
    for region in regions :
      if region.begin() < sel.begin() :
        previous_regions.append(region)

    if not previous_regions and len(regions) > 0:
      previous_regions.append(regions[len(regions)-1])

    return previous_regions[len(previous_regions)-1] if len(previous_regions) > 0 else None
      
class load_bookmarks_viewViewEventListener(sublime_plugin.ViewEventListener):

  def on_load_async(self) :

    view = self.view

    view.erase_regions("region-dot-bookmarks")
    lines = []
    lines = [view.line(view.text_point(bookmark["line"], 0)) for bookmark in search_bookmarks_by_view(view, ( True if is_project_view(view) and is_javascript_project() else False ))]
    view.add_regions("region-dot-bookmarks", lines,  "code", "bookmark", sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE)

import sublime, sublime_plugin
import re

class expand_modelCommand(sublime_plugin.TextCommand):

  def run(self, edit, *args) :

    view = self.view

    for sel in view.sel():

      row, col = view.rowcol(sel.begin())

      string = view.substr(sel).strip()

      index = string.rfind("*")

      n_times = int(string[index+1:])

      string = string[:index]

      final_string =  ""
      string_pieces = re.split(r"\$+", string)
      delimeters = re.findall(r"(\$+)", string)

      for x in range(1, n_times+1):
        for y in range(len(string_pieces)):
          if y < len(string_pieces) - 1:
            final_string += string_pieces[y] + str(x).zfill(len(delimeters[y]))
          else :
            final_string += string_pieces[y] + "\n" + ( " " * col)

      view.replace(edit, sel, final_string)

  def is_enabled(self) :

    view = self.view

    sel = view.sel()[0]
    string = view.substr(sel).strip()
    index = string.rfind("*")
    if index >= 0 :
      try :
        int(string[index+1:])
        return True
      except ValueError as e:
        pass

    return False

  def is_visible(self) :

    view = self.view

    sel = view.sel()[0]
    string = view.substr(sel).strip()
    index = string.rfind("*")
    if index >= 0 :
      try :
        int(string[index+1:])
        return True
      except ValueError as e:
        pass

    return False

if int(sublime.version()) >= 3124 :

  items_found_can_i_use = None
  can_i_use_file = None
  can_i_use_popup_is_showing = False
  can_i_use_list_from_main_menu = False
  path_to_can_i_use_data = os.path.join(HELPER_FOLDER, "can_i_use", "can_i_use_data.json")
  path_to_test_can_i_use_data = os.path.join(HELPER_FOLDER, "can_i_use", "can_i_use_data2.json")
  url_can_i_use_json_data = "https://raw.githubusercontent.com/Fyrd/caniuse/master/data.json"
  
  can_i_use_css = ""
  with open(os.path.join(HELPER_FOLDER, "can_i_use", "style.css")) as css_file:
    can_i_use_css = "<style>"+css_file.read()+"</style>"
  
  def donwload_can_i_use_json_data() :
    global can_i_use_file
  
    if os.path.isfile(path_to_can_i_use_data) :
      with open(path_to_can_i_use_data) as json_file:    
        try :
          can_i_use_file = json.load(json_file)
        except Exception as e :
          print("Error: "+traceback.format_exc())
          sublime.active_window().status_message("Can't use \"Can I use\" json data from: https://raw.githubusercontent.com/Fyrd/caniuse/master/data.json")
  
    if Util.download_and_save(url_can_i_use_json_data, path_to_test_can_i_use_data) :
      if os.path.isfile(path_to_can_i_use_data) :
        if not Util.checksum_sha1_equalcompare(path_to_can_i_use_data, path_to_test_can_i_use_data) :
          with open(path_to_test_can_i_use_data) as json_file:    
            try :
              can_i_use_file = json.load(json_file)
              if os.path.isfile(path_to_can_i_use_data) :
                os.remove(path_to_can_i_use_data)
              os.rename(path_to_test_can_i_use_data, path_to_can_i_use_data)
            except Exception as e :
              print("Error: "+traceback.format_exc())
              sublime.active_window().status_message("Can't use new \"Can I use\" json data from: https://raw.githubusercontent.com/Fyrd/caniuse/master/data.json")
        if os.path.isfile(path_to_test_can_i_use_data) :
          os.remove(path_to_test_can_i_use_data)
      else :
        os.rename(path_to_test_can_i_use_data, path_to_can_i_use_data)
        with open(path_to_can_i_use_data) as json_file :    
          try :
            can_i_use_file = json.load(json_file)
          except Exception as e :
            print("Error: "+traceback.format_exc())
            sublime.active_window().status_message("Can't use \"Can I use\" json data from: https://raw.githubusercontent.com/Fyrd/caniuse/master/data.json")
  
  Util.create_and_start_thread(donwload_can_i_use_json_data, "DownloadCanIuseJsonData")
  
  def find_in_can_i_use(word) :
    global can_i_use_file
    can_i_use_data = can_i_use_file.get("data")
    word = word.lower()
    return [value for key, value in can_i_use_data.items() if value["title"].lower().find(word) >= 0]
  
  def back_to_can_i_use_list(action):
    global can_i_use_popup_is_showing
    if action.find("http") >= 0:
      webbrowser.open(action)
      return
    view = sublime.active_window().active_view()
    can_i_use_popup_is_showing = False
    view.hide_popup()
    if len(action.split(",")) > 1 and action.split(",")[1] == "main-menu" :
      view.run_command("can_i_use", args={"from": "main-menu"})
    else :  
      view.run_command("can_i_use")
  
  def show_pop_can_i_use(index):
    global can_i_use_file
    global items_found_can_i_use
    global can_i_use_popup_is_showing
    if index < 0:
      return
    item = items_found_can_i_use[index]
  
    browser_accepted = ["ie", "edge", "firefox", "chrome", "safari", "opera", "ios_saf", "op_mini", "android", "and_chr"]
    browser_name = [
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IE",
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;EDGE",
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Firefox", 
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Chrome", 
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Safari", 
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Opera", 
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;iOS Safari", 
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Opera Mini", 
      "&nbsp;&nbsp;&nbsp;Android Browser", 
      "Chrome for Android"
    ]
  
    html_browser = ""
  
    html_browser += "<div>"
    html_browser += "<h1 class=\"title\">"+cgi.escape(item["title"])+" <a href=\""+item["spec"].replace(" ", "%20")+"\"><span class=\"status "+item["status"]+"\"> - "+item["status"].upper()+"</span></a></h1>"
    html_browser += "<p class=\"description\">"+cgi.escape(item["description"])+"</p>"
    html_browser += "<p class=\"\"><span class=\"support\">Global Support: <span class=\"support-y\">"+str(item["usage_perc_y"])+"%</span>"+( " + <span class=\"support-a\">"+str(item["usage_perc_a"])+"%</span> = " if float(item["usage_perc_a"]) > 0 else "" )+( "<span class=\"support-total\">"+str( "{:10.2f}".format(float(item["usage_perc_y"]) + float(item["usage_perc_a"])) )+"%</span>" if float(item["usage_perc_a"]) > 0 else "" )+"</span> "+( " ".join(["<span class=\"category\">"+category+"</span>" for category in item["categories"]]) )+"</p>"
    html_browser += "</div>"
  
    html_browser += "<div class=\"container-browser-list\">"
    i = 0
    for browser in browser_accepted :
  
      browser_versions = can_i_use_file["agents"]
      stat = item["stats"].get(browser)
      stat_items_ordered = list()
      for k in stat.keys() :
        if k != "TP" : 
          stat_items_ordered.append(k)
  
      if len(stat_items_ordered) >= 1 and stat_items_ordered[0] != "all" :
        stat_items_ordered.sort(key=LooseVersion)
        stat_items_ordered = stat_items_ordered[::-1]
  
      html_p = "<p class=\"version-stat-item\"><span class=\"browser-name\">"+browser_name[i]+"</span> : "
      j = 0
      while j < len(stat_items_ordered) :
        if j == 7:
          break
        class_name = stat.get(stat_items_ordered[j])
        html_annotation_numbers = ""
        requires_prefix = ""
        can_be_enabled = ""
  
        if re.search(r"\bx\b", class_name) :
          requires_prefix = "x"
        if re.search(r"\bd\b", class_name) :
          can_be_enabled = "d"
  
        if class_name.find("#") >= 0 :
          numbers = class_name[class_name.find("#"):].strip().split(" ")
          for number in numbers :
            number = int(number.replace("#", ""))
            html_annotation_numbers += "<span class=\"annotation-number\">"+str(number)+"</span>"
  
        html_p += "<span class=\"version-stat "+stat.get(stat_items_ordered[j])+" \">"+( html_annotation_numbers if html_annotation_numbers else "" )+stat_items_ordered[j]+( "<span class=\"can-be-enabled\">&nbsp;</span>" if can_be_enabled else "" )+( "<span class=\"requires-prefix\">&nbsp;</span>" if requires_prefix else "" )+"</span> "
  
        j = j + 1
  
      html_p += "</p>"
      html_browser += html_p
      i = i + 1
  
    html_browser += "</div>"
  
    if item["notes_by_num"] :
      html_browser += "<div>"
      html_browser += "<h3>Notes</h3>"
      notes_by_num = item["notes_by_num"]
  
      notes_by_num_ordered = list()
      for k in notes_by_num.keys() :
        notes_by_num_ordered.append(k)
      notes_by_num_ordered.sort()
  
      i = 0
      while i < len(notes_by_num_ordered) :
        note = notes_by_num.get(notes_by_num_ordered[i])
        html_p = "<p class=\"note\"><span class=\"annotation-number\">"+str(notes_by_num_ordered[i])+"</span>"+cgi.escape(note)+"</p>"
        html_browser += html_p
        i = i + 1
      html_browser += "</div>"
  
    if item["links"] :
      html_browser += "<div>"
      html_browser += "<h3>Links</h3>"
      links = item["links"]
  
      for link in links :
        html_p = "<p class=\"link\"><a href=\""+link.get("url")+"\">"+cgi.escape(link.get("title"))+"</a></p>"
        html_browser += html_p
      html_browser += "</div>"
  
    view = sublime.active_window().active_view()
    
    can_i_use_popup_is_showing = True
    view.show_popup("""
      <html>
        <head></head>
        <body>
        """+can_i_use_css+"""
        <div class=\"container-back-button\">
          <a class=\"back-button\" href=\"back"""+( ",main-menu" if can_i_use_list_from_main_menu else "")+"""\">&lt; Back</a>
          <a class=\"view-on-site\" href=\"http://caniuse.com/#search="""+item["title"].replace(" ", "%20")+"""\"># View on \"Can I use\" site #</a>
        </div>
        <div class=\"content\">
          """+html_browser+"""
          <div class=\"legend\">
            <h3>Legend</h3>
            <div class=\"container-legend-items\">
              <span class=\"legend-item y\">&nbsp;</span> = Supported 
              <span class=\"legend-item n\">&nbsp;</span> = Not Supported 
              <span class=\"legend-item p a\">&nbsp;</span> = Partial support 
              <span class=\"legend-item u\">&nbsp;</span> = Support unknown 
              <span class=\"legend-item requires-prefix\">&nbsp;</span> = Requires Prefix 
              <span class=\"legend-item can-be-enabled\">&nbsp;</span> = Can Be Enabled 
            </div>
          </div>
        </div>
        </body>
      </html>""", sublime.COOPERATE_WITH_AUTO_COMPLETE, -1, 1250, 650, back_to_can_i_use_list)
  
  class can_i_useCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
  
      global items_found_can_i_use
      global can_i_use_file
      global can_i_use_list_from_main_menu
      can_i_use_data = can_i_use_file.get("data")
      if not can_i_use_data :
        return
  
      view = self.view
      selection = view.sel()[0]
      if args.get("from") != "main-menu" :
        can_i_use_list_from_main_menu = False
        word = view.substr(view.word(selection)).strip()
        items_found_can_i_use = find_in_can_i_use(word)
        sublime.active_window().show_quick_panel([item["title"] for item in items_found_can_i_use], show_pop_can_i_use)
      else :
        can_i_use_list_from_main_menu = True
        items_found_can_i_use = find_in_can_i_use("")
        sublime.active_window().show_quick_panel([item["title"] for item in items_found_can_i_use], show_pop_can_i_use)
    
    def is_enabled(self, **args):
      view = self.view
      if args.get("from") == "main-menu" or javascriptCompletions.get("enable_can_i_use_menu_option") :
        return True 
      return False
  
    def is_visible(self, **args):
      view = self.view
      if args.get("from") == "main-menu" :
        return True
      if javascriptCompletions.get("enable_can_i_use_menu_option") :
        if Util.split_string_and_find_on_multiple(view.scope_name(0), ["source.js", "text.html.basic", "source.css"]) < 0 :
          return False
        return True
      return False
      
  class can_i_use_hide_popupEventListener(sublime_plugin.EventListener):
    def on_selection_modified_async(self, view) :
      global can_i_use_popup_is_showing
      if can_i_use_popup_is_showing :
        view.hide_popup()
        can_i_use_popup_is_showing = False



import sublime, sublime_plugin
import os, shlex

def open_project_folder(project):
  
  subl(["--project", project])
  
def call_ui(client_file, host, port) :
  node = NodeJS()
  return Util.create_and_start_thread(node.execute, args=("electron", [client_file], True))

def is_javascript_project():
  project_file_name = sublime.active_window().project_file_name()
  project_dir_name = ""
  if project_file_name :
    project_dir_name = os.path.dirname(project_file_name)
    settings_dir_name = os.path.join(project_dir_name, ".jc-project-settings")
    return os.path.isdir(settings_dir_name)
  else :
    # try to look at window.folders()
    folder = sublime.active_window().folders()   
    if len(folder) > 0:
      folder = folder[0]
      settings_dir_name = os.path.join(folder, ".jc-project-settings")
      return os.path.isdir(settings_dir_name)
  return False

def is_type_javascript_project(type):
  settings = get_project_settings()
  return True if settings and type in settings["project_details"]["type"] else False

def is_project_view(view) :
  settings = get_project_settings()
  if settings :
    return view.file_name() and view.file_name().startswith(settings["project_dir_name"])
  return False

def get_project_settings(project_dir_name = ""):

  project_settings = dict()

  project_file_name = sublime.active_window().project_file_name() if not project_dir_name else ""
  settings_dir_name = ""

  if not project_dir_name :

    if project_file_name :
      project_dir_name = os.path.dirname(project_file_name)
    else :
      # try to look at window.folders()
      folder = sublime.active_window().folders()
      if len(folder) > 0:
        project_dir_name = folder[0]

  if not project_dir_name :
    return dict()

  if project_file_name :
    settings_dir_name = os.path.join(project_dir_name, ".jc-project-settings")
    if not os.path.isdir(settings_dir_name) :
      return dict()
  else :
    for file in os.listdir(project_dir_name) :
      if file.endswith(".sublime-project") :
        project_file_name = os.path.join(project_dir_name, file)
        break
    settings_dir_name = os.path.join(project_dir_name, ".jc-project-settings")
    if not os.path.isdir(settings_dir_name) :
      return dict()
        
  project_settings["project_file_name"] = project_file_name
  project_settings["project_dir_name"] = project_dir_name
  project_settings["settings_dir_name"] = settings_dir_name
  settings_file = ["project_details.json", "project_settings.json", "flow_settings.json"]
  for setting_file in settings_file :
    with open(os.path.join(settings_dir_name, setting_file), encoding="utf-8") as file :
      key = os.path.splitext(setting_file)[0]
      project_settings[key] = json.loads(file.read(), encoding="utf-8")
    if setting_file == "project_details.json" :
      for project_type in project_settings["project_details"]["type"]:
        with open(os.path.join(settings_dir_name, project_type+"_settings.json"), encoding="utf-8") as file :
          project_settings[project_type+"_settings"] = json.loads(file.read(), encoding="utf-8")

  return project_settings

def save_project_setting(setting_file, data):
  settings = get_project_settings()
  if settings :
    with open(os.path.join(settings["settings_dir_name"], setting_file), 'w+', encoding="utf-8") as file :
      file.write(json.dumps(data, indent=2))

def save_project_flowconfig(flow_settings):
  settings = get_project_settings()
  if settings :
    with open(os.path.join(settings["settings_dir_name"], "flow_settings.json"), 'w+', encoding="utf-8") as file :
      file.write(json.dumps(flow_settings, indent=2))
    with open(os.path.join(settings["project_dir_name"], ".flowconfig"), 'w+', encoding="utf-8") as file :
      include = "\n".join(flow_settings["include"])
      ignore = "\n".join(flow_settings["ignore"])
      libs = "\n".join(flow_settings["libs"])
      options = "\n".join(list(map(lambda item: item[0].strip()+"="+item[1].strip(), flow_settings["options"])))

      data = "[ignore]\n{ignore}\n[include]\n{include}\n[libs]\n{libs}\n[options]\n{options}".format(ignore=ignore, include=include, libs=libs, options=options)
      file.write(data.replace(':PACKAGE_PATH', PACKAGE_PATH))

import sublime, sublime_plugin
import os

manage_cli_window_command_processes = {}

class send_input_to_cliCommand(sublime_plugin.TextCommand):
  last_output_panel_name = None
  window = None
  def run(self, edit, **args):
    self.window = self.view.window()
    panel = self.window.active_panel()
    if panel :
      self.last_output_panel_name = panel.replace("output.", "")
    sublime.set_timeout_async(lambda : self.window.show_input_panel("Input: ", "", self.send_input, None, None))

  def send_input(self, input) :
    global manage_cli_window_command_processes
    settings = get_project_settings()
    if self.window and self.last_output_panel_name and settings and settings["project_dir_name"]+"_"+self.last_output_panel_name in manage_cli_window_command_processes :
      process = manage_cli_window_command_processes[settings["project_dir_name"]+"_"+self.last_output_panel_name]["process"]
      process.stdin.write("{}\n".format(input).encode("utf-8"))
      process.stdin.flush()
      self.window.run_command("show_panel", {"panel": "output."+self.last_output_panel_name})

  def is_enabled(self):
    global manage_cli_window_command_processes
    self.window = self.view.window()
    panel = self.window.active_panel()
    if panel :
      self.last_output_panel_name = panel.replace("output.", "")
    settings = get_project_settings()
    return True if ( self.window and self.last_output_panel_name and settings and settings["project_dir_name"]+"_"+self.last_output_panel_name in manage_cli_window_command_processes ) else False
  
  def is_visible(self):
    global manage_cli_window_command_processes
    self.window = self.view.window()
    panel = self.window.active_panel()
    if panel :
      self.last_output_panel_name = panel.replace("output.", "")
    settings = get_project_settings()
    return True if ( self.window and self.last_output_panel_name and settings and settings["project_dir_name"]+"_"+self.last_output_panel_name in manage_cli_window_command_processes ) else False


import signal

class stop_cli_commandCommand(sublime_plugin.TextCommand):
  last_output_panel_name = None
  window = None
  def run(self, edit, **args):
    self.window = self.view.window()
    panel = self.window.active_panel()
    if panel :
      self.last_output_panel_name = panel.replace("output.", "")
    sublime.set_timeout_async(self.stop_command)

  def stop_command(self) :
    global manage_cli_window_command_processes
    settings = get_project_settings()
    if self.window and self.last_output_panel_name and settings and settings["project_dir_name"]+"_"+self.last_output_panel_name in manage_cli_window_command_processes :
      process = manage_cli_window_command_processes[settings["project_dir_name"]+"_"+self.last_output_panel_name]["process"]
      if (process.poll() == None) :
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        del manage_cli_window_command_processes[settings["project_dir_name"]+"_"+self.last_output_panel_name]
      else :
        del manage_cli_window_command_processes[settings["project_dir_name"]+"_"+self.last_output_panel_name]

      panel = self.window.get_output_panel(self.last_output_panel_name)
      if panel :
        panel.run_command("print_panel_cli", {"line": "\n\nCommand Stopped\n\n"})
        panel.run_command("print_panel_cli", {"line": "OUTPUT-SUCCESS", "hide_panel_on_success": True, "wait_panel": 2000})

  def is_enabled(self):
    global manage_cli_window_command_processes
    self.window = self.view.window()
    panel = self.window.active_panel()
    if panel :
      self.last_output_panel_name = panel.replace("output.", "")
    settings = get_project_settings()
    return True if ( self.window and self.last_output_panel_name and settings and settings["project_dir_name"]+"_"+self.last_output_panel_name in manage_cli_window_command_processes ) else False
  
  def is_visible(self):
    global manage_cli_window_command_processes
    self.window = self.view.window()
    panel = self.window.active_panel()
    if panel :
      self.last_output_panel_name = panel.replace("output.", "")
    settings = get_project_settings()
    return True if ( self.window and self.last_output_panel_name and settings and settings["project_dir_name"]+"_"+self.last_output_panel_name in manage_cli_window_command_processes ) else False


class print_panel_cliCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):   
    line = args.get("line") or ""
    prefix = args.get("prefix") or ""
    postfix = args.get("postfix") or ""
    if line.strip() :
      if line == "OUTPUT-SUCCESS":
        if self.view.window() and args.get("hide_panel_on_success") :
          sublime.set_timeout_async(self.hide_window_panel, args.get("wait_panel") if "wait_panel" in args else 2000 )
        return
      elif line == "OUTPUT-ERROR" or line == "OUTPUT-DONE":
        return

      is_read_only = self.view.is_read_only()
      self.view.set_read_only(False)
      self.view.insert(edit, self.view.size(), prefix + line + postfix)
      self.view.set_read_only(is_read_only)
      self.view.show_at_center(self.view.size())
      self.view.add_regions(
        'output_cli',
        self.view.split_by_newlines(sublime.Region(0, self.view.size()))
      )

  def hide_window_panel(self):
    try :
      self.view.window().run_command("hide_panel")
    except AttributeError as e:
      pass

class enable_menu_project_typeEventListener(sublime_plugin.EventListener):
  project_type = ""
  path = ""
  path_disabled = ""

  def on_activated_async(self, view):
    if self.project_type and self.path and self.path_disabled:
      if is_type_javascript_project(self.project_type) :
        if os.path.isfile(self.path_disabled):
          os.rename(self.path_disabled, self.path)
      else :
        if os.path.isfile(self.path):
          os.rename(self.path, self.path_disabled)
    elif self.path and self.path_disabled:
      if is_javascript_project() :
        if os.path.isfile(self.path_disabled):
          os.rename(self.path_disabled, self.path)
      else :
        if os.path.isfile(self.path):
          os.rename(self.path, self.path_disabled)

  def on_new_async(self, view):
    self.on_activated_async(view)

  def on_load_async(self, view):
    self.on_activated_async(view)


import shlex

class manage_cliCommand(sublime_plugin.WindowCommand):
  cli = ""
  name_cli = ""
  bin_path = ""
  is_node = True
  is_npm = False
  panel = None
  output_panel_name = "output_panel_cli"
  panel_command = "print_panel_cli"
  line_prefix = ""
  line_postfix = ""
  status_message_before = ""
  status_message_after_on_success = ""
  status_message_after_on_error = ""
  settings = {}
  command_with_options = []
  show_panel = True
  placeholders = {}
  hide_panel_on_success = True
  process = None
  show_animation_loader = True
  animation_loader = AnimationLoader(["[=     ]", "[ =    ]", "[   =  ]", "[    = ]", "[     =]", "[    = ]", "[   =  ]", "[ =    ]"], 0.067, "Command is executing ")
  interval_animation = None
  syntax = os.path.join("Packages", PACKAGE_NAME,"javascript_enhancements.sublime-syntax")
  ask_custom_options = False
  wait_panel = 2000

  def run(self, **kwargs):
    self.settings = get_project_settings()
    if self.settings:

      self.callback_after_get_settings(**kwargs)

      self.cli = kwargs.get("cli") if "cli" in kwargs else self.cli
      if not self.cli and not self.is_npm  :
        raise Exception("'cli' field of the manage_cliCommand not defined.")

      self.command_with_options = self.substitute_placeholders( kwargs.get("command_with_options") if "command_with_options" in kwargs else self.command_with_options )
      # if not self.command_with_options or len(self.command_with_options) <= 0:
      #   raise Exception("'command_with_options' field of the manage_cliCommand not defined.")

      self.show_panel = kwargs.get("show_panel") if "show_panel" in kwargs != None else self.show_panel
      self.output_panel_name = self.substitute_placeholders( str(kwargs.get("output_panel_name") if "output_panel_name" in kwargs else self.output_panel_name) )
      self.status_message_before = self.substitute_placeholders( str(kwargs.get("status_message_before")) if "status_message_before" in kwargs else self.status_message_before )
      self.status_message_after_on_success = self.substitute_placeholders( str(kwargs.get("status_message_after_on_success")) if "status_message_after_on_success" in kwargs else self.status_message_after_on_success )
      self.status_message_after_on_error = self.substitute_placeholders( str(kwargs.get("status_message_after_on_error")) if "status_message_after_on_error" in kwargs else self.status_message_after_on_error )
      self.hide_panel_on_success = kwargs.get("hide_panel_on_success") if "hide_panel_on_success" in kwargs else self.hide_panel_on_success
      self.show_animation_loader = kwargs.get("show_animation_loader") if "show_animation_loader" in kwargs else self.show_animation_loader
      self.ask_custom_options = kwargs.get("ask_custom_options") if "ask_custom_options" in kwargs else self.ask_custom_options
      
      if self.settings["project_dir_name"]+"_"+self.output_panel_name in manage_cli_window_command_processes : 

        sublime.error_message("This command is already running! If you want execute it again, you must stop it first.")

        self.window.run_command("show_panel", {"panel": "output."+self.output_panel_name})

        return

      sublime.set_timeout_async(lambda: self.manage())

    else :

      sublime.error_message("Error: can't get project settings")

  def manage(self) :
    global manage_cli_window_command_processes

    if self.status_message_before :
      self.window.status_message(self.name_cli+": "+self.status_message_before)

    self.command_with_options = self.command_with_options + self.append_args_execute()

    if self.ask_custom_options :
      sublime.active_window().show_input_panel( 'Add custom options', '', lambda custom_options: self.execute(custom_options=shlex.split(custom_options)), None, self.execute )
      return

    self.execute()


  def execute(self, custom_options=[]) :

    if self.show_panel :
      self.panel = Util.create_and_show_panel(self.output_panel_name, window=self.window, syntax=self.syntax)
      self.panel.settings().set("is_output_cli_panel", True)

    self.before_execute()

    if ( self.can_execute() ) :

      if self.animation_loader and self.show_animation_loader :
        self.interval_animation = RepeatedTimer(self.animation_loader.sec, self.animation_loader.animate)

      if self.is_node :
        node = NodeJS(check_local = True)

        if self.bin_path :
          node.execute(self.cli, self.command_with_options + custom_options, is_from_bin=True, bin_path=self.bin_path, chdir=( self.settings[self.cli + "_settings"]["working_directory"] if self.cli + "_settings" in self.settings and "working_directory" in self.settings[self.cli + "_settings"] else self.settings["project_dir_name"] ), wait_terminate=False, func_stdout=self.print_panel)
        else :
          node.execute(self.cli, self.command_with_options + custom_options, is_from_bin=True, chdir=( self.settings[self.cli + "_settings"]["working_directory"] if self.cli + "_settings" in self.settings and "working_directory" in self.settings[self.cli + "_settings"] else self.settings["project_dir_name"] ), wait_terminate=False, func_stdout=self.print_panel)

      elif self.is_npm :
        npm = NPM(check_local = True)

        npm.execute(self.command_with_options[0], self.command_with_options[1:] + custom_options, chdir=( self.settings[self.cli + "_settings"]["working_directory"] if self.cli + "_settings" in self.settings and "working_directory" in self.settings[self.cli + "_settings"] else self.settings["project_dir_name"] ), wait_terminate=False, func_stdout=self.print_panel)

      else :
        Util.execute(self.cli, self.command_with_options + custom_options, chdir=( self.settings[self.cli + "_settings"]["working_directory"] if self.cli + "_settings" in self.settings and "working_directory" in self.settings[self.cli + "_settings"] else self.settings["project_dir_name"] ), wait_terminate=False, func_stdout=self.print_panel)

  def print_panel(self, line, process):
    global manage_cli_window_command_processes

    if not self.process :
      self.process = process

    self.process_communicate(line)

    if not self.settings["project_dir_name"]+"_"+self.output_panel_name in manage_cli_window_command_processes :
      manage_cli_window_command_processes[self.settings["project_dir_name"]+"_"+self.output_panel_name] = {
        "process": self.process
      }

    if line != None and self.show_panel:
      self.panel.run_command(self.panel_command, {"line": line, "prefix": self.line_prefix, "postfix": self.line_postfix, "hide_panel_on_success": self.hide_panel_on_success, "wait_panel": self.wait_panel})
  
    if line == "OUTPUT-SUCCESS" :
      if self.status_message_after_on_success :
        self.window.status_message(self.name_cli+": "+self.status_message_after_on_success)

      self.on_success()

    if line == "OUTPUT-ERROR" :
      if self.status_message_after_on_error :
        self.window.status_message(self.name_cli+": "+self.status_message_after_on_error)

      self.on_error()

    if line == "OUTPUT-DONE":
      self.process = None

      if self.settings["project_dir_name"]+"_"+self.output_panel_name in manage_cli_window_command_processes :
        del manage_cli_window_command_processes[self.settings["project_dir_name"]+"_"+self.output_panel_name]

      self.on_done()

      if self.animation_loader and self.interval_animation :
        self.animation_loader.on_complete()
        self.interval_animation.stop()

  def substitute_placeholders(self, variable):
    
    if isinstance(variable, list) :

      for index in range(len(variable)):
        for key, placeholder in self.placeholders.items():
          variable[index] = variable[index].replace(key, placeholder)

      return variable

    elif isinstance(variable, str) :

      for key, placeholder in self.placeholders.items():
        variable = variable.replace(key, placeholder)
        
      return variable

  def can_execute(self) :
    return True

  def before_execute(self) :
    return 

  def append_args_execute(self):
    return []

  def process_communicate(self, line):
    return
    
  def callback_after_get_settings(self, **kwargs):
    return

  def on_success(self):
    return

  def on_error(self):
    return

  def on_done(self):
    return


class open_live_terminalCommand(manage_cliCommand):
  cli = "/bin/bash" if sublime.platform() != 'windows' else "cmd.exe"
  name_cli = "Bash"
  is_node = False
  is_npm = False
  show_animation_loader = False
  hide_panel_on_success = True
  output_panel_name = "panel_terminal"
  line_prefix = "$ "
  syntax = "Packages/ShellScript/Shell-Unix-Generic.tmLanguage"
  wait_panel = 0

  def is_enabled(self) :

    return True if is_javascript_project() else False

  def is_visible(self) :

    return True if is_javascript_project() else False

class set_read_only_output_cliEventListener(sublime_plugin.EventListener) :

  def on_activated_async(self, view) :

    if not view.settings().get("is_output_cli_panel", False) :
      return 

    is_in = False
    for region in view.get_regions("output_cli"): 
      if region.contains(view.sel()[0]) or region.intersects(view.sel()[0]) :
        is_in = True
        view.set_read_only(True)
        break

    if not is_in :
      view.set_read_only(False)

  def on_selection_modified_async(self, view) :

    if not view.settings().get("is_output_cli_panel", False) :
      return 

    is_in = False
    for region in view.get_regions("output_cli"): 
      if region.contains(view.sel()[0]) or region.intersects(view.sel()[0]) :
        is_in = True
        view.set_read_only(True)
        break

    if not is_in :
      view.set_read_only(False)

  def on_modified_async(self, view) :

    if not view.settings().get("is_output_cli_panel", False) :
      return 

    is_in = False
    for region in view.get_regions("output_cli"): 
      if region.contains(view.sel()[0]) or region.intersects(view.sel()[0]) :
        is_in = True
        view.set_read_only(True)
        break

    if not is_in :
      view.set_read_only(False)

  def on_text_command(self, view, command_name, args) :

    if not view.settings().get("is_output_cli_panel", False) :
      return 

    is_in = False

    if command_name == "left_delete" :
      for region in view.get_regions("output_cli"): 
        if region.intersects(sublime.Region( view.sel()[0].begin() - 2, view.sel()[0].end() ) ):
          is_in = True
          view.set_read_only(True)
          break

    elif command_name == "insert" and "characters" in args and args["characters"] == '\n' :
      view.set_read_only(True)
      window = view.window()
      panel = window.active_panel()
      if panel :
        last_output_panel_name = panel.replace("output.", "")
        global manage_cli_window_command_processes
        settings = get_project_settings()
        if window and last_output_panel_name and settings and settings["project_dir_name"]+"_"+last_output_panel_name in manage_cli_window_command_processes :
          process = manage_cli_window_command_processes[settings["project_dir_name"]+"_"+last_output_panel_name]["process"]

          regions = view.lines(sublime.Region(0, view.size()))

          line = ""
          for i in range(1, len(regions)+1):
            line = view.substr(regions[-i]).strip()
            if line and not line.startswith("$ ") :
              break
            line = ""
            i = i + 1

          if line :

            view_settings = view.settings()
            view_settings.set("lines", view_settings.get("lines", []) + [line] )

            view.add_regions(
              'output_cli',
              view.split_by_newlines(sublime.Region(0, view.size()))
            )

            view_settings.set( "index_lines", len(view_settings.get("lines")) -1 )

            view.sel().clear()
            view.sel().add(sublime.Region(view.size(), view.size()))

            process.stdin.write("{}\n".format(line).replace("PROJECT_PATH", shlex.quote(settings["project_dir_name"])).encode("utf-8"))
            process.stdin.flush()

            window.run_command("show_panel", {"panel": "output."+last_output_panel_name})

    if not is_in :
      view.set_read_only(False)


class move_history_cliCommand(sublime_plugin.TextCommand) :

  def run(self, edit, **args):
    
    if "action" in args :
      view = self.view

      view_settings = view.settings()

      if not view_settings.has("index_lines") or not view.substr(view.line(view.size())).strip() :
        index_lines = len(view_settings.get("lines", [])) - 1

      else :
        if args.get("action") == "move_down" :
          index_lines = view_settings.get("index_lines", len(view_settings.get("lines", [])) ) + 1
        else :
          index_lines = view_settings.get("index_lines", len(view_settings.get("lines", [])) ) - 1

      if index_lines < 0 or index_lines >= len(view_settings.get("lines")) : 
        return

      if index_lines >= 0 :
        line = view_settings.get("lines")[index_lines]
        view.replace(edit, view.line(view.size()), '')
        view.insert(edit, view.size(), line)
        view.show_at_center(view.size())
        view_settings.set("index_lines", index_lines)

  def is_enabled(self) :

    view = self.view
    return True if view.settings().get("is_output_cli_panel", False) else False

  def is_visible(self) :
    
    view = self.view
    return True if view.settings().get("is_output_cli_panel", False) else False



## Npm ##
class enable_menu_npmEventListener(enable_menu_project_typeEventListener):
  path = os.path.join(PROJECT_FOLDER, "npm", "Main.sublime-menu")
  path_disabled = os.path.join(PROJECT_FOLDER, "npm", "Main_disabled.sublime-menu")

  def on_activated_async(self, view):
    super(enable_menu_npmEventListener, self).on_activated_async(view)

    default_value = [
      {
        "caption": "Tools",
        "id": "tools",
        "children": [
          {
            "caption": "Npm/Yarn",
            "id": "npm",
            "children":[
              {
                "caption": "Scripts",
                "id": "npm_scripts",
                "children": []
              },
              {
                "caption": "Install All",
                "command": "manage_npm_package",
                "args": {
                  "command_with_options": ["install", ":save-mode"],
                  "output_panel_name": "panel_install_all_npm_script",
                  "hide_panel_on_success": True
                }
              },
              {
                "caption": "Update All",
                "command": "manage_npm_package",
                "args": {
                  "command_with_options": ["update", ":save-mode"],
                  "output_panel_name": "panel_update_all_npm_script",
                  "hide_panel_on_success": True
                }
              },
              {
                "caption": "Install Package",
                "command": "manage_npm_package",
                "args": {
                  "command_with_options": ["install", ":save-mode", ":package"],
                  "status_message_before": "installing :package...",
                  "output_panel_name": "panel_install_package_npm_script",
                  "hide_panel_on_success": True
                }
              },
              {
                "caption": "Uninstall Package",
                "command": "manage_npm_package",
                "args": {
                  "command_with_options": ["uninstall", ":save-mode", ":package"],
                  "status_message_before": "uninstalling :package...",
                  "output_panel_name": "panel_uninstall_package_npm_script",
                  "hide_panel_on_success": True
                }
              },
              {
                "caption": "Update Package",
                "command": "manage_npm_package",
                "args": {
                  "command_with_options": ["update", ":save-mode", ":package"],
                  "status_message_before": "updating :package...",
                  "output_panel_name": "panel_update_package_npm_script",
                  "hide_panel_on_success": True
                }
              }
            ]
          }
        ]
      }
    ]

    if os.path.isfile(self.path) :
      with open(self.path, 'r+') as menu:
        content = menu.read()
        menu.seek(0)
        menu.write(json.dumps(default_value))
        menu.truncate()
        json_data = json.loads(content)
        npm_scripts = None
        for item in json_data :
          if item["id"] == "tools" :
            for item2 in item["children"] :
              if item2["id"] == "npm" :
                for item3 in item2["children"] :
                  if "id" in item3 and item3["id"] == "npm_scripts" :
                    item3["children"] = []
                    npm_scripts = item3["children"]
                break
            break
        if npm_scripts == None :
          return 
        try:
          npm = NPM(check_local=True)
          package_json = npm.getPackageJson()
          if package_json and "scripts" in package_json and len(package_json["scripts"].keys()) > 0 :
            for script in package_json["scripts"].keys():
              npm_scripts.append({
                "caption": script,
                "command": "manage_npm",
                "args": {
                  "command_with_options": ["run", script],
                  "output_panel_name": "panel_"+script+"_npm_script",
                  "hide_panel_on_success": True,
                  "ask_custom_options": True
                }
              })
            menu.seek(0)
            menu.write(json.dumps(json_data))
            menu.truncate()
        except Exception as e:
          print(traceback.format_exc())
          menu.seek(0)
          menu.write(json.dumps(default_value))
          menu.truncate()

    if os.path.isfile(self.path_disabled) :
      with open(self.path_disabled, 'w+') as menu:
        menu.write(json.dumps(default_value))

class manage_npmCommand(manage_cliCommand):
  is_node = False
  is_npm = True

  def is_enabled(self):
    settings = get_project_settings()
    return True if settings and os.path.isfile( os.path.join(settings["project_dir_name"], "package.json") ) else False

  def is_visible(self):
    settings = get_project_settings()
    return True if settings and os.path.isfile( os.path.join(settings["project_dir_name"], "package.json") ) else False

class manage_npm_packageCommand(manage_npmCommand):

  def run(self, **kwargs):
    if ":save-mode" in kwargs["command_with_options"]:
      self.window.show_input_panel("Save mode: ", "--save", lambda save_mode="": self.set_save_mode(save_mode.strip(), **kwargs), None, None)
    else :
      self.set_save_mode('', **kwargs)

  def set_save_mode(self, save_mode, **kwargs) :
    self.placeholders[":save-mode"] = save_mode
    if kwargs.get("command_with_options") :
      if ":package" in kwargs["command_with_options"]:
        self.window.show_input_panel("Package name: ", "", lambda package_name="": self.set_package_name(package_name.strip(), **kwargs), None, None)
        return
    super(manage_npm_packageCommand, self).run(**kwargs)

  def set_package_name(self, package_name, **kwargs):
    self.placeholders[":package"] = package_name
    super(manage_npm_packageCommand, self).run(**kwargs)

## Build Flow ##
class enable_menu_build_flowEventListener(enable_menu_project_typeEventListener):
  path = os.path.join(PROJECT_FOLDER, "build_flow", "Main.sublime-menu")
  path_disabled = os.path.join(PROJECT_FOLDER, "build_flow", "Main_disabled.sublime-menu")

class build_flowCommand(manage_cliCommand):
  cli = "flow-remove-types"
  name_cli = "Flow Remove Types"
  bin_path = ""

  def callback_after_get_settings(self, **kwargs):
    self.placeholders[":source_folder"] = self.settings["project_settings"]["build_flow"]["source_folder"]
    self.placeholders[":destination_folder"] = self.settings["project_settings"]["build_flow"]["destination_folder"]

  def append_args_execute(self) :
    custom_args = []
    custom_args = custom_args + self.settings["project_settings"]["build_flow"]["options"]

    return custom_args

  def is_enabled(self) :
    settings = get_project_settings()
    if settings and settings["project_settings"]["build_flow"]["source_folder"] and settings["project_settings"]["build_flow"]["destination_folder"] :
      return True
    return False

## Cordova ##
import sublime, sublime_plugin
import os, webbrowser, shlex

def create_cordova_project_process(line, process, panel, project_data, sublime_project_file_name, open_project) :

  if line != None and panel:
    panel.run_command("print_panel_cli", {"line": line, "hide_panel_on_success": True})

  if line == "OUTPUT-SUCCESS":
    Util.move_content_to_parent_folder(os.path.join(project_data["cordova_settings"]["working_directory"], "temp"))
    
    if open_project :
      open_project_folder(sublime_project_file_name)

def create_cordova_project(json_data):
  project_data = json_data["project_data"]
  project_details = project_data["project_details"]
  project_folder = project_data["cordova_settings"]["working_directory"]
  create_options = []

  if "create_options" in project_data and project_data["create_options"]:
    create_options = project_data["create_options"]
    
  panel = Util.create_and_show_panel("cordova_panel_installer_project")

  node = NodeJS()

  if "cordova_settings" in project_data and "package_json" in project_data["cordova_settings"] and "use_local_cli" in project_data["cordova_settings"] and project_data["cordova_settings"]["use_local_cli"] :
    node.execute('cordova', ["create", "temp"] + create_options, is_from_bin=True, bin_path=os.path.join(project_folder, ".jc-project-settings", "node_modules", ".bin"), chdir=project_folder, wait_terminate=False, func_stdout=create_cordova_project_process, args_func_stdout=[panel, project_data, (project_data['project_file_name'] if "sublime_project_file_name" not in json_data else json_data["sublime_project_file_name"]), (False if "sublime_project_file_name" not in json_data else True) ])
  else :  
    node.execute('cordova', ["create", "temp"] + create_options, is_from_bin=True, chdir=project_folder, wait_terminate=False, func_stdout=create_cordova_project_process, args_func_stdout=[panel, project_data, (project_data['project_file_name'] if "sublime_project_file_name" not in json_data else json_data["sublime_project_file_name"]), (False if "sublime_project_file_name" not in json_data else True) ])
    

  return json_data

Hook.add("cordova_create_new_project", create_cordova_project)

Hook.add("cordova_add_new_project_type", create_cordova_project)

class enable_menu_cordovaEventListener(enable_menu_project_typeEventListener):
  project_type = "cordova"
  path = os.path.join(PROJECT_FOLDER, "cordova", "Main.sublime-menu")
  path_disabled = os.path.join(PROJECT_FOLDER, "cordova", "Main_disabled.sublime-menu")

class cordova_baseCommand(manage_cliCommand):
  cli = "cordova"
  name_cli = "Cordova"
  bin_path = ""
  can_add_platform = False
  platform_list = []
  platform_list_on_success = None
  can_add_plugin = False
  plugin_list = []
  plugin_list_on_success = None

  def ask_platform(self, type, func):
    self.platform_list = []
    self.can_add_platform = False
    self.platform_list_on_success = func
    self.settings = get_project_settings()
    if self.settings :
      node = NodeJS()
      sublime.status_message(self.name_cli+": getting platform list...")
      node.execute(self.cli, ["platform", "list"], is_from_bin=True, chdir=self.settings["cordova_settings"]["working_directory"], wait_terminate=False, func_stdout=(self.get_list_installed_platform_window_panel if type == "installed" else self.get_list_available_platform_window_panel))
    else :
      sublime.error_message("Error: can't get project settings")

  def get_list_installed_platform_window_panel(self, line, process):

    self.get_platform_list("installed", line, process, True)

  def get_list_available_platform_window_panel(self, line, process):

    self.get_platform_list("available", line, process, True)

  def get_platform_list(self, type, line, process, show_panel = False):
    if line == "OUTPUT-DONE" or line == "OUTPUT-SUCCESS" or line == "OUTPUT-ERROR" :
      self.can_add_platform = False

    if type == "installed" :
      if line and line.strip().startswith("Available platforms") :
        self.can_add_platform = False

    elif type == "available" :  
      if line and line.strip().startswith("Installed platforms") :
        self.can_add_platform = False

    if line and self.can_add_platform and line.strip() :
      self.platform_list.append(line.strip().split(" ")[0])

    if type == "installed" :
      if line and line.strip().startswith("Installed platforms") :
        self.can_add_platform = True

    elif type == "available" :  
      if line and line.strip().startswith("Available platforms") :
        self.can_add_platform = True

    if line == "OUTPUT-DONE" :
      if self.platform_list :
        if show_panel :
          self.window.show_quick_panel([cordova_platform for cordova_platform in self.platform_list], self.platform_list_on_success)
        elif self.platform_list_on_success :
          self.platform_list_on_success()
      else :
        if type == "installed" :
          sublime.message_dialog(self.name_cli+": No platforms installed")
        elif type == "available" :  
          sublime.message_dialog(self.name_cli+": No more platforms available")

  def ask_plugin(self, func):
    self.plugin_list = []
    self.can_add_plugin = False
    self.plugin_list_on_success = func
    self.settings = get_project_settings()
    if self.settings :
      sublime.status_message(self.name_cli+": getting plugin list...")
      node = NodeJS()
      node.execute(self.cli, ["plugin", "list"], is_from_bin=True, chdir=self.settings["cordova_settings"]["working_directory"], wait_terminate=False, func_stdout=self.get_plugin_list_window_panel)
    else :
      sublime.error_message("Error: can't get project settings")

  def get_plugin_list_window_panel(self, line, process):
    self.get_plugin_list(line, process, True)

  def get_plugin_list(self, line, process, show_panel = False):
    if line == "OUTPUT-DONE" or line == "OUTPUT-SUCCESS" or line == "OUTPUT-ERROR" :
      self.can_add_plugin = False
    else :
      self.can_add_plugin = True

    if line and self.can_add_plugin and line.strip() :
      self.plugin_list.append(line.strip().split(" ")[0])
    if line == "OUTPUT-DONE" :
      if self.plugin_list:
        if show_panel :
          self.window.show_quick_panel([cordova_plugin for cordova_plugin in self.plugin_list], self.plugin_list_on_success)
        elif self.plugin_list_on_success :
          self.plugin_list_on_success()
      else :
        sublime.message_dialog(self.name_cli+": No plugins installed")

  def append_args_execute(self):
    custom_args = []
    custom_args = custom_args + self.settings["cordova_settings"]["cli_global_options"]
    command = self.command_with_options[0]

    if command == "serve" :
      custom_args = custom_args + [self.settings["cordova_settings"]["serve_port"]]

    elif command == "build" or command == "run" or command == "compile":
      mode = self.command_with_options[2][2:]
      platform = self.placeholders[":platform"]
      custom_args = custom_args + self.settings["cordova_settings"]["cli_"+command+"_options"]
      custom_args_platform = ""
      custom_args_platform = Util.getDictItemIfExists(self.settings["cordova_settings"]["platform_"+command+"_options"][mode], platform)
      if custom_args_platform :
        custom_args = custom_args + ["--"] + shlex.split(custom_args_platform)

    elif "cli_"+command+"_options" in self.settings["cordova_settings"] :
      custom_args = custom_args + self.settings["cordova_settings"]["cli_"+command+"_options"]
      
    return custom_args

  def before_execute(self):

    if self.settings["cordova_settings"]["cli_custom_path"] :
      self.bin_path = self.settings["cordova_settings"]["cli_custom_path"]
    elif self.settings["cordova_settings"]["use_local_cli"] :
      self.bin_path = os.path.join(self.settings["settings_dir_name"], "node_modules", ".bin")

  def is_enabled(self):
    return is_type_javascript_project("cordova")

  def is_visible(self):
    return is_type_javascript_project("cordova")

class manage_cordovaCommand(cordova_baseCommand):

  def run(self, **kwargs):
    flag = False

    if kwargs.get("ask_platform") and kwargs.get("ask_platform_type"):
      self.ask_platform(kwargs.get("ask_platform_type"), lambda index: self.set_platform(index, **kwargs))
      flag = True

    if kwargs.get("ask_plugin"):
      self.ask_plugin(lambda index: self.set_plugin(index, **kwargs))
      flag = True

    if not flag :
      super(manage_cordovaCommand, self).run(**kwargs)

  def set_platform(self, index, **kwargs):
    if index >= 0:
      self.placeholders[":platform"] = self.platform_list[index]
      super(manage_cordovaCommand, self).run(**kwargs)

  def set_plugin(self, index, **kwargs):
    if index >= 0:
      self.placeholders[":plugin"] = self.plugin_list[index]
      super(manage_cordovaCommand, self).run(**kwargs)

class manage_serve_cordovaCommand(cordova_baseCommand):

  def process_communicate(self, line):
    if line and line.strip().startswith("Static file server running on: "):
      line = line.strip()
      url = line.replace("Static file server running on: ", "")
      url = url.replace(" (CTRL + C to shut down)", "")
      url = url.strip()
      webbrowser.open(url) 

class manage_plugin_cordovaCommand(manage_cordovaCommand):

  def run(self, **kwargs):
    if kwargs.get("command_with_options") :
      if kwargs["command_with_options"][1] == "add" :
        self.window.show_input_panel("Plugin name: ", "", lambda plugin_name="": self.add_plugin(plugin_name.strip(), **kwargs), None, None)
        return
    super(manage_plugin_cordovaCommand, self).run(**kwargs)

  def add_plugin(self, plugin_name, **kwargs):
    self.placeholders[":plugin"] = plugin_name
    super(manage_plugin_cordovaCommand, self).run(**kwargs)

  def on_success(self):
    plugin_name = self.placeholders[":plugin"]
    plugin_lib_path = os.path.join(PACKAGE_PATH, "flow", "libs", "cordova", plugin_name+".js")
    plugin_lib_path_with_placeholder = os.path.join(":PACKAGE_PATH", "flow", "libs", "cordova", plugin_name+".js")
    if os.path.isfile(plugin_lib_path) :
      if self.command_with_options[1] == "add" :
        self.settings["flow_settings"]["libs"].append(plugin_lib_path_with_placeholder)
        save_project_flowconfig(self.settings["flow_settings"])
      elif self.command_with_options[1] == "remove" :
        Util.removeItemIfExists(self.settings["flow_settings"]["libs"], plugin_lib_path_with_placeholder)
        save_project_flowconfig(self.settings["flow_settings"])

class manage_add_platform_cordovaCommand(manage_cordovaCommand):

  def callback_after_get_settings(self, **kwargs):

    self.placeholders[":version"] = Util.getDictItemIfExists(self.settings["cordova_settings"]["platform_version_options"], self.placeholders[":platform"]) or ""

  def on_success(self):
    if not self.placeholders[":platform"] in self.settings["cordova_settings"]["installed_platform"] :
      self.settings["cordova_settings"]["installed_platform"].append(self.placeholders[":platform"])
    save_project_setting("cordova_settings.json", self.settings["cordova_settings"])

class manage_remove_platform_cordovaCommand(manage_cordovaCommand):

  def on_success(self):
    Util.removeItemIfExists(self.settings["cordova_settings"]["installed_platform"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["cordova_settings"]["platform_version_options"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["cordova_settings"]["platform_compile_options"]["debug"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["cordova_settings"]["platform_compile_options"]["release"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["cordova_settings"]["platform_build_options"]["debug"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["cordova_settings"]["platform_build_options"]["release"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["cordova_settings"]["platform_run_options"]["debug"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["cordova_settings"]["platform_run_options"]["release"], self.placeholders[":platform"])
    save_project_setting("cordova_settings.json", self.settings["cordova_settings"])

class sync_cordova_projectCommand(cordova_baseCommand):

  platform_list = []
  plugin_list = []

  def run(self, **kwargs):
    self.platform_list = []
    self.plugin_list = []
    self.settings = get_project_settings()

    if self.settings :
      sublime.status_message(self.name_cli+": synchronizing project...")
      node = NodeJS()
      node.execute(self.cli, ["platform", "list"], is_from_bin=True, chdir=self.settings["cordova_settings"]["working_directory"], wait_terminate=False, func_stdout=lambda line, process: self.get_platform_list("installed", line, process))
      node.execute(self.cli, ["plugin", "list"], is_from_bin=True, chdir=self.settings["cordova_settings"]["working_directory"], wait_terminate=False, func_stdout=self.get_plugin_list)
    else :
      sublime.error_message("Error: can't get project settings")

  def platform_list_on_success(self):
    self.settings["cordova_settings"]["installed_platform"] = []
    for platform_name in self.platform_list:
      self.settings["cordova_settings"]["installed_platform"].append(platform_name)

    save_project_setting("cordova_settings.json", self.settings["cordova_settings"])
    sublime.status_message(self.name_cli+": platforms synchronized")

  def plugin_list_on_success(self):
    plugin_list_to_remove = []
    for lib in self.settings["flow_settings"]["libs"]:
      if lib.startswith(":PACKAGE_PATH/flow/libs/cordova/") and lib != ":PACKAGE_PATH/flow/libs/cordova/cordova.js":
        plugin_list_to_remove.append(lib)
    for lib in plugin_list_to_remove:
      self.settings["flow_settings"]["libs"].remove(lib)

    for plugin_name in self.plugin_list:
      plugin_lib_path = os.path.join(PACKAGE_PATH, "flow", "libs", "cordova", plugin_name+".js")
      plugin_lib_path_with_placeholder = os.path.join(":PACKAGE_PATH", "flow", "libs", "cordova", plugin_name+".js")
      if os.path.isfile(plugin_lib_path) :
        self.settings["flow_settings"]["libs"].append(plugin_lib_path_with_placeholder)

    save_project_flowconfig(self.settings["flow_settings"])
    sublime.status_message(self.name_cli+": plugins synchronized")


## Ionic ##
import sublime, sublime_plugin
import os, webbrowser, shlex, json

def create_ionic_project_process(line, process, panel, project_data, sublime_project_file_name, open_project) :
  print(line)
  if line != None and panel:
    panel.run_command("print_panel_cli", {"line": line, "hide_panel_on_success": True})

  if line == "OUTPUT-SUCCESS":
    Util.move_content_to_parent_folder(os.path.join(project_data["ionic_settings"]["working_directory"], "temp"))

    if open_project :
      open_project_folder(sublime_project_file_name)

def create_ionic_project(json_data):
  project_data = json_data["project_data"]
  project_details = project_data["project_details"]
  project_folder = project_data["ionic_settings"]["working_directory"]
  create_options = []

  if "create_options" in project_data and project_data["create_options"]:
    create_options = project_data["create_options"]

  panel = Util.create_and_show_panel("ionic_panel_installer_project")

  node = NodeJS()

  if "ionic_settings" in project_data and "package_json" in project_data["ionic_settings"] and "use_local_cli" in project_data["ionic_settings"] and project_data["ionic_settings"]["use_local_cli"] :
    node.execute('ionic', ["start", "temp"] + create_options, is_from_bin=True, bin_path=os.path.join(project_folder, ".jc-project-settings", "node_modules", ".bin"), chdir=project_folder, wait_terminate=False, func_stdout=create_ionic_project_process, args_func_stdout=[panel, project_data, (project_data['project_file_name'] if "sublime_project_file_name" not in json_data else json_data["sublime_project_file_name"]), (False if "sublime_project_file_name" not in json_data else True) ])
  else :  
    node.execute('ionic', ["start", "temp"] + create_options, is_from_bin=True, chdir=project_folder, wait_terminate=False, func_stdout=create_ionic_project_process, args_func_stdout=[panel, project_data, (project_data['project_file_name'] if "sublime_project_file_name" not in json_data else json_data["sublime_project_file_name"]), (False if "sublime_project_file_name" not in json_data else True) ])

  return json_data

Hook.add("ionic_create_new_project", create_ionic_project)

Hook.add("ionic_add_new_project_type", create_ionic_project)

class enable_menu_ionicEventListener(enable_menu_project_typeEventListener):
  project_type = "ionic"
  path = os.path.join(PROJECT_FOLDER, "ionic", "Main.sublime-menu")
  path_disabled = os.path.join(PROJECT_FOLDER, "ionic", "Main_disabled.sublime-menu")

class ionic_baseCommand(manage_cliCommand):
  cli = "ionic"
  name_cli = "Ionic"
  bin_path = ""
  can_add_platform = False
  platform_list = []
  platform_list_on_success = None
  can_add_plugin = False
  plugin_list = []
  plugin_list_on_success = None

  def ask_platform(self, type, func):
    self.platform_list = []
    self.can_add_platform = False
    self.platform_list_on_success = func
    self.settings = get_project_settings()
    if self.settings :
      node = NodeJS()
      sublime.status_message(self.name_cli+": getting platform list...")
      node.execute(self.cli, ["platform", "list"], is_from_bin=True, chdir=self.settings["ionic_settings"]["working_directory"], wait_terminate=False, func_stdout=(self.get_list_installed_platform_window_panel if type == "installed" else self.get_list_available_platform_window_panel))
    else :
      sublime.error_message("Error: can't get project settings")

  def get_list_installed_platform_window_panel(self, line, process):

    self.get_platform_list("installed", line, process, True)

  def get_list_available_platform_window_panel(self, line, process):

    self.get_platform_list("available", line, process, True)

  def get_platform_list(self, type, line, process, show_panel = False):
    if line == "OUTPUT-DONE" or line == "OUTPUT-SUCCESS" or line == "OUTPUT-ERROR" :
      self.can_add_platform = False

    if type == "installed" :
      if line and line.strip().startswith("Available platforms") :
        self.can_add_platform = False

    elif type == "available" :  
      if line and line.strip().startswith("Installed platforms") :
        self.can_add_platform = False

    if line and self.can_add_platform and line.strip() :
      self.platform_list.append(line.strip().split(" ")[0])

    if type == "installed" :
      if line and line.strip().startswith("Installed platforms") :
        self.can_add_platform = True

    elif type == "available" :  
      if line and line.strip().startswith("Available platforms") :
        self.can_add_platform = True

    if line == "OUTPUT-DONE" :
      if self.platform_list :
        if show_panel :
          self.window.show_quick_panel([cordova_platform for cordova_platform in self.platform_list], self.platform_list_on_success)
        elif self.platform_list_on_success :
          self.platform_list_on_success()
      else :
        if type == "installed" :
          sublime.message_dialog(self.name_cli+": No platforms installed")
        elif type == "available" :  
          sublime.message_dialog(self.name_cli+": No more platforms available")

  def ask_plugin(self, func):
    self.plugin_list = []
    self.can_add_plugin = False
    self.plugin_list_on_success = func
    self.settings = get_project_settings()
    if self.settings :
      sublime.status_message(self.name_cli+": getting plugin list...")
      node = NodeJS()
      node.execute(self.cli, ["plugin", "list"], is_from_bin=True, chdir=self.settings["ionic_settings"]["working_directory"], wait_terminate=False, func_stdout=self.get_plugin_list_window_panel)
    else :
      sublime.error_message("Error: can't get project settings")

  def get_plugin_list_window_panel(self, line, process):
    self.get_plugin_list(line, process, True)

  def get_plugin_list(self, line, process, show_panel = False):
    if line == "OUTPUT-DONE" or line == "OUTPUT-SUCCESS" or line == "OUTPUT-ERROR" :
      self.can_add_plugin = False
    else :
      self.can_add_plugin = True

    if line and self.can_add_plugin and line.strip() :
      self.plugin_list.append(line.strip().split(" ")[0])
    if line == "OUTPUT-DONE" :
      if self.plugin_list:
        if show_panel :
          self.window.show_quick_panel([cordova_plugin for cordova_plugin in self.plugin_list], self.plugin_list_on_success)
        elif self.plugin_list_on_success :
          self.plugin_list_on_success()
      else :
        sublime.message_dialog(self.name_cli+": No plugins installed")

  def append_args_execute(self):
    custom_args = []
    custom_args = custom_args + self.settings["ionic_settings"]["cli_global_options"]
    command = self.command_with_options[0]

    if command == "platform" or command == "build" or command == "run" or command == "emulate" :
      custom_args = custom_args + self.settings["ionic_settings"]["cli_"+command+"_options"]
      if command == "emulate":
        mode = self.command_with_options[2][2:]
        platform = self.placeholders[":platform"]
        custom_args_platform = ""
        custom_args_platform = Util.getDictItemIfExists(self.settings["ionic_settings"]["platform_"+command+"_options"][mode], platform)
        if custom_args_platform :
          custom_args = custom_args + ["--"] + shlex.split(custom_args_platform)

    elif "cli_"+command+"_options" in self.settings["ionic_settings"] :
      custom_args = custom_args + self.settings["ionic_settings"]["cli_"+command+"_options"]
      
    return custom_args

  def before_execute(self):

    if self.settings["ionic_settings"]["cli_custom_path"] :
      self.bin_path = self.settings["ionic_settings"]["cli_custom_path"]
    elif self.settings["ionic_settings"]["use_local_cli"] :
      self.bin_path = os.path.join(self.settings["settings_dir_name"], "node_modules", ".bin")

    command = self.command_with_options[0]
    if command == "serve" :
      del self.command_with_options[1]

  def is_enabled(self):
    return is_type_javascript_project("ionic")

  def is_visible(self):
    return is_type_javascript_project("ionic")


class manage_ionicCommand(ionic_baseCommand):

  def run(self, **kwargs):
    flag = False

    if kwargs.get("ask_platform") and kwargs.get("ask_platform_type"):
      self.ask_platform(kwargs.get("ask_platform_type"), lambda index: self.set_platform(index, **kwargs))
      flag = True

    if kwargs.get("ask_plugin"):
      self.ask_plugin(lambda index: self.set_plugin(index, **kwargs))
      flag = True

    if not flag :
      super(manage_ionicCommand, self).run(**kwargs)

  def set_platform(self, index, **kwargs):
    if index >= 0:
      self.placeholders[":platform"] = self.platform_list[index]
      super(manage_ionicCommand, self).run(**kwargs)

  def set_plugin(self, index, **kwargs):
    if index >= 0:
      self.placeholders[":plugin"] = self.plugin_list[index]
      super(manage_ionicCommand, self).run(**kwargs)

class manage_serve_ionicCommand(ionic_baseCommand):

  def process_communicate(self, line):
    if line and line.strip().startswith("Static file server running on: "):
      line = line.strip()
      url = line.replace("Static file server running on: ", "")
      url = url.replace(" (CTRL + C to shut down)", "")
      url = url.strip()
      webbrowser.open(url) 


class manage_plugin_ionicCommand(manage_ionicCommand):

  def run(self, **kwargs):
    if kwargs.get("command_with_options") :
      if kwargs["command_with_options"][1] == "add" :
        self.window.show_input_panel("Plugin name: ", "", lambda plugin_name="": self.add_plugin(plugin_name.strip(), **kwargs), None, None)
        return
    super(manage_plugin_ionicCommand, self).run(**kwargs)

  def add_plugin(self, plugin_name, **kwargs):
    self.placeholders[":plugin"] = plugin_name
    super(manage_plugin_ionicCommand, self).run(**kwargs)

  def on_success(self):
    plugin_name = self.placeholders[":plugin"]
    plugin_lib_path = os.path.join(PACKAGE_PATH, "flow", "libs", "cordova", plugin_name+".js")
    plugin_lib_path_with_placeholder = os.path.join(":PACKAGE_PATH", "flow", "libs", "cordova", plugin_name+".js")
    if os.path.isfile(plugin_lib_path) :
      if self.command_with_options[1] == "add" :
        self.settings["flow_settings"]["libs"].append(plugin_lib_path_with_placeholder)
        save_project_flowconfig(self.settings["flow_settings"])
      elif self.command_with_options[1] == "remove" :
        Util.removeItemIfExists(self.settings["flow_settings"]["libs"], plugin_lib_path_with_placeholder)
        save_project_flowconfig(self.settings["flow_settings"])

class manage_add_platform_ionicCommand(manage_ionicCommand):

  def callback_after_get_settings(self, **kwargs):

    self.placeholders[":version"] = Util.getDictItemIfExists(self.settings["ionic_settings"]["platform_version_options"], self.placeholders[":platform"]) or ""

  def on_success(self):
    if not self.placeholders[":platform"] in self.settings["ionic_settings"]["installed_platform"] :
      self.settings["ionic_settings"]["installed_platform"].append(self.placeholders[":platform"])
    save_project_setting("ionic_settings.json", self.settings["ionic_settings"])

class manage_remove_platform_ionicCommand(manage_ionicCommand):

  def on_success(self):
    Util.removeItemIfExists(self.settings["ionic_settings"]["installed_platform"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["ionic_settings"]["platform_version_options"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["ionic_settings"]["platform_compile_options"]["debug"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["ionic_settings"]["platform_compile_options"]["release"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["ionic_settings"]["platform_build_options"]["debug"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["ionic_settings"]["platform_build_options"]["release"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["ionic_settings"]["platform_run_options"]["debug"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["ionic_settings"]["platform_run_options"]["release"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["ionic_settings"]["platform_emulate_options"]["debug"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["ionic_settings"]["platform_emulate_options"]["release"], self.placeholders[":platform"])
    save_project_setting("ionic_settings.json", self.settings["ionic_settings"])

class sync_ionic_projectCommand(ionic_baseCommand):

  platform_list = []
  plugin_list = []

  def run(self, **kwargs):
    self.platform_list = []
    self.plugin_list = []
    self.settings = get_project_settings()

    if self.settings :
      sublime.status_message(self.name_cli+": synchronizing project...")
      node = NodeJS()
      node.execute(self.cli, ["platform", "list"], is_from_bin=True, chdir=self.settings["ionic_settings"]["working_directory"], wait_terminate=False, func_stdout=lambda line, process: self.get_platform_list("installed", line, process))
      node.execute(self.cli, ["plugin", "list"], is_from_bin=True, chdir=self.settings["ionic_settings"]["working_directory"], wait_terminate=False, func_stdout=self.get_plugin_list)
    else :
      sublime.error_message("Error: can't get project settings")

  def platform_list_on_success(self):
    self.settings["ionic_settings"]["installed_platform"] = []
    for platform_name in self.platform_list:
      self.settings["ionic_settings"]["installed_platform"].append(platform_name)

    save_project_setting("ionic_settings.json", self.settings["ionic_settings"])
    sublime.status_message(self.name_cli+": platforms synchronized")

  def plugin_list_on_success(self):
    plugin_list_to_remove = []
    for lib in self.settings["flow_settings"]["libs"]:
      if lib.startswith(":PACKAGE_PATH/flow/libs/cordova/") and lib != ":PACKAGE_PATH/flow/libs/cordova/cordova.js":
        plugin_list_to_remove.append(lib)
    for lib in plugin_list_to_remove:
      self.settings["flow_settings"]["libs"].remove(lib)

    for plugin_name in self.plugin_list:
      plugin_lib_path = os.path.join(PACKAGE_PATH, "flow", "libs", "cordova", plugin_name+".js")
      plugin_lib_path_with_placeholder = os.path.join(":PACKAGE_PATH", "flow", "libs", "cordova", plugin_name+".js")
      if os.path.isfile(plugin_lib_path) :
        self.settings["flow_settings"]["libs"].append(plugin_lib_path_with_placeholder)

    save_project_flowconfig(self.settings["flow_settings"])
    sublime.status_message(self.name_cli+": plugins synchronized")


## React ##
import re, webbrowser

def create_react_project_process(line, process, panel, project_data, sublime_project_file_name, open_project) :

  if line != None and panel:
    panel.run_command("print_panel_cli", {"line": line, "hide_panel_on_success": True})

  if line == "OUTPUT-SUCCESS":
    Util.move_content_to_parent_folder(os.path.join(project_data["react_settings"]["working_directory"], "temp"))
    
    if open_project :
      open_project_folder(sublime_project_file_name)

def create_react_project(json_data):
  project_data = json_data["project_data"]
  project_details = project_data["project_details"]
  project_folder = project_data["react_settings"]["working_directory"]
  create_options = []

  if "create_options" in project_data and project_data["create_options"]:
    create_options = project_data["create_options"]
    
  panel = Util.create_and_show_panel("react_panel_installer_project")

  node = NodeJS()

  Util.execute('git', ["clone", "--progress", "--depth=1", "https://github.com/react-boilerplate/react-boilerplate.git", "temp"], chdir=project_folder, wait_terminate=False, func_stdout=create_cordova_project_process, args_func_stdout=[panel, project_data, (project_data['project_file_name'] if "sublime_project_file_name" not in json_data else json_data["sublime_project_file_name"]), (False if "sublime_project_file_name" not in json_data else True) ])
  #node.execute('create-react-app', ["temp"] + create_options, is_from_bin=True, chdir=project_folder, wait_terminate=False, func_stdout=create_cordova_project_process, args_func_stdout=[panel, project_data, (project_data['project_file_name'] if "sublime_project_file_name" not in json_data else json_data["sublime_project_file_name"]), (False if "sublime_project_file_name" not in json_data else True) ])
    
  return json_data

Hook.add("react_create_new_project", create_react_project)

Hook.add("react_add_new_project_type", create_react_project)

class enable_menu_reactEventListener(enable_menu_project_typeEventListener):
  project_type = "react"
  path = os.path.join(PROJECT_FOLDER, "react", "Main.sublime-menu")
  path_disabled = os.path.join(PROJECT_FOLDER, "react", "Main_disabled.sublime-menu")

class manage_serve_reactCommand(manage_cliCommand):
  cli = "serve"
  name_cli = "Serve React"

  def process_communicate(self, line) :

    if line and "http://localhost" in line :
      pattern = re.compile("http\:\/\/localhost\:([0-9]+)")
      match = pattern.search(line)
      if match :
        port = match.group(1)
        url = "http://localhost:"+port
        webbrowser.open(url) 

  def is_enabled(self) :
    settings = get_project_settings()
    if os.path.isdir(os.path.join( settings["project_dir_name"], "build" )) :
      return True
    return False

  def is_visible(self) :
    settings = get_project_settings()
    if os.path.isdir(os.path.join( settings["project_dir_name"], "build" )) :
      return True
    return False


import sublime, sublime_plugin
import subprocess, shutil, traceback

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

          if "type" in json_data["project_data"]["project_details"] :
            for project_type in json_data["project_data"]["project_details"]["type"]:
              json_data = Hook.apply(project_type+"_create_new_project", json_data)

          json_data = Hook.apply("after_create_new_project", json_data)

          data = dict()
          data["command"] = "close_window"
          data = json.dumps(data)
          socket_server_list["create_new_project"].socket.send_to(conn, addr, data)

        elif json_data["command"] == "try_flow_init":
          
          node = NodeJS()
          data = dict()
          data["command"] = "result_flow_init"
          data["result"] = node.execute("flow", ["init"], is_from_bin=True, chdir=json_data["project_data"]["path"])
          data["project_data"] = json_data["project_data"]
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


import sublime, sublime_plugin
import subprocess, shutil, traceback

socket_server_list["edit_project"] = SocketCallUI("edit_project", "localhost", 11112, os.path.join(PROJECT_FOLDER, "edit_project", "ui", "client.js"))

class edit_javascript_projectCommand(sublime_plugin.WindowCommand):
  def run(self, *args):
    global socket_server_list

    settings = get_project_settings()
    
    if not socket_server_list["edit_project"].is_socket_closed() :
      socket_server_list["edit_project"].socket.close_if_not_clients()

    if socket_server_list["edit_project"].is_socket_closed() :

      def recv(conn, addr, ip, port, client_data, client_fields):
        global socket_server_list

        json_data = json.loads(client_data)

        #print(json_data)
        #return
        if json_data["command"] == "add_project_type":
          
          json_data = Hook.apply("before_add_new_project", json_data)

          json_data = Hook.apply(json_data["project_data"]["type_added"]+"_add_new_project_type", json_data)

          json_data = Hook.apply("after_add_new_project", json_data)

          data = dict()
          data["command"] = "add_project_type_done"
          data = json.dumps(data)
          socket_server_list["edit_project"].socket.send_to(conn, addr, data)

        elif json_data["command"] == "ready":
          if settings :
            data = dict()
            data["command"] = "load_project_settings"
            data["settings"] = settings
            data = json.dumps(data)
            socket_server_list["edit_project"].socket.send_to(conn, addr, data) 

      def client_connected(conn, addr, ip, port, client_fields):
        global socket_server_list 
      
      def client_disconnected(conn, addr, ip, port):
        global socket_server_list  
        socket_server_list["edit_project"].socket.close_if_not_clients()

      socket_server_list["edit_project"].start(recv, client_connected, client_disconnected)
      
    else :
      socket_server_list["edit_project"].call_ui()

  def is_enabled(self):
    return is_javascript_project()

  def is_visible(self):
    return is_javascript_project()

import sublime, sublime_plugin
import os, time, signal

class close_all_servers_and_flowEventListener(sublime_plugin.EventListener):

  def on_pre_close(self, view) :

    node = NodeJS()

    global socket_server_list

    global manage_cli_window_command_processes

    if not sublime.windows() :
      
      sublime.status_message("flow server stopping")
      sublime.set_timeout_async(lambda: node.execute("flow", ["stop"], is_from_bin=True, chdir=os.path.join(PACKAGE_PATH, "flow")))

      for key in manage_cli_window_command_processes.keys() :
        process = manage_cli_window_command_processes[key]["process"]
        if (process.poll() == None) :
          os.killpg(os.getpgid(process.pid), signal.SIGTERM)

      for key, value in socket_server_list.items() :
        if not value["socket"].is_socket_closed() :
          sublime.status_message("socket server stopping")
          data = dict()
          data["command"] = "server_closing"
          data = json.dumps(data)
          value["socket"].send_all_clients(data)
          value["socket"].close()

    if is_javascript_project() and view.window() and len(view.window().views()) == 1 :
      settings = get_project_settings()
      sublime.status_message("flow server stopping")
      sublime.set_timeout_async(lambda: node.execute("flow", ["stop"], is_from_bin=True, chdir=os.path.join(settings["project_dir_name"])))



def plugin_loaded():
  global mainPlugin
  mainPlugin.init()


