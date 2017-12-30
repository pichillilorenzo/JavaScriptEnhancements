import sublime, sublime_plugin
import os, sys, imp, platform, json, traceback, threading, urllib, shutil, re, time
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

PROJECT_TYPE_SUPPORTED = ['empty', 'angularv1', 'angularv2', 'cordova', 'express', 'ionicv1', 'ionicv2', 'react', 'yeoman']

${include ./helper/Hook.py}

${include ./helper/AnimationLoader.py}
${include ./helper/RepeatedTimer.py}
${include ./helper/node/main.py}
${include ./helper/util/main.py}
${include ./helper/my_socket/main.py}

def sublime_executable_path():
  executable_path = sublime.executable_path()
  if sublime.platform() == 'osx':
    app_path = executable_path[:executable_path.rfind(".app/") + 5]
    executable_path = app_path + "Contents/SharedSupport/bin/subl"

  return executable_path

def subl(args):
  
  executable_path = sublime_executable_path()

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
 
    node_modules_path = os.path.join(PACKAGE_PATH, "node_modules")
    npm = NPM()
    if not os.path.exists(node_modules_path):
      result = npm.install_all()
      if result[0]: 
        sublime.active_window().status_message("JavaScript Enhancements - npm dependencies installed correctly.")
      else:
        if os.path.exists(node_modules_path):
          shutil.rmtree(node_modules_path)
        sublime.error_message("Error during installation: can not install the npm dependencies for JavaScript Enhancements.")
    # else:
    #   result = npm.update_all()
    #   if not result[0]: 
    #     sublime.active_window().status_message("Error: JavaScript Enhancements - cannot update npm dependencies.")
    
    sublime.set_timeout_async(lambda: overwrite_default_javascript_snippet())

    window = sublime.active_window()
    view = window.active_view()

    sublime.set_timeout_async(lambda: show_flow_errorsViewEventListener(view).on_activated_async())
    sublime.set_timeout_async(lambda: load_bookmarks_viewViewEventListener(view).on_load_async())

mainPlugin = startPlugin()

${include ./flow/main.py}

${include ./project/main.py}

${include ./helper/main.py}

def start():

  global mainPlugin

  try:
    sys.modules["TerminalView"]
  except Exception as err:
    sublime.error_message("TerminalView plugin is missing. TerminalView is required to be able to use this plugin.")
    return

  try:
    sys.modules["JavaScript Completions"]
    sublime.error_message("Please uninstall/disable JavaScript Completions plugin.")
    return
  except Exception as err:
    pass

  node = NodeJS()
  try:
    node.getCurrentNodeJSVersion()
  except Exception as err: 
    sublime.error_message("Error during installation: node.js is not installed on your system.")
    return

  # test
  
  # result = node.execute("flow-typed", command_args=["search", "express"])
  # flow_typed_searched_items = []
  # if result[0]:
  #   lines = result[1].encode('ascii', errors='ignore').decode("utf-8").strip().split("\n")
  #   linesNotDecoded = result[1].strip().split("\n")
  #   found_definations_flag = False
  #   for i in range(0, len(lines)):
  #     line = lines[i].strip()
  #     lineNotDecoded = linesNotDecoded[i].strip()

  #     if found_definations_flag and line:
 
  #       item = lineNotDecoded.split(b'\xe2\x94\x82'.decode("utf-8"))
  #       for j in range(0, len(item)):
  #         item[j] = item[j].encode('ascii', errors='ignore').decode("utf-8").strip()

  #       flow_typed_searched_items += [item]

  #     elif line.startswith("Name") and line.endswith("Flow Version"):
  #       found_definations_flag = True
      
  # print(flow_typed_searched_items)


  mainPlugin.init()

def plugin_loaded():
  
  if int(sublime.version()) >= 3124 :
    sublime.set_timeout_async(start, 1000)
  else:
    sublime.error_message("JavaScript Enhancements plugin requires Sublime Text 3 (build 3124 or newer). Your version build is: " + sublime.version())

