import sublime, sublime_plugin
import os, sys, imp, platform, json, traceback, threading, urllib, shutil, re
from shutil import copyfile
from threading import Timer

PACKAGE_PATH = os.path.abspath(os.path.dirname(__file__))
PACKAGE_NAME = os.path.basename(PACKAGE_PATH)
SUBLIME_PACKAGES_PATH = os.path.dirname(PACKAGE_PATH)
 
sys.path += [PACKAGE_PATH] + [os.path.join(PACKAGE_PATH, f) for f in ['node', 'util', 'my_socket']]

if 'reloader' in sys.modules:
  imp.reload(sys.modules['reloader'])
import reloader

platform_switcher = {"osx": "OSX", "linux": "Linux", "windows": "Windows"}
PLATFORM = platform_switcher.get(sublime.platform())
PLATFORM_ARCHITECTURE = "64bit" if platform.architecture()[0] == "64bit" else "32bit" 

main_settings_json = dict()
if os.path.isfile(os.path.join(PACKAGE_PATH, "main.sublime-settings")) :
  with open(os.path.join(PACKAGE_PATH, "main.sublime-settings")) as main_settings_file:    
    main_settings_json = json.load(main_settings_file)

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
    import node.node_variables as node_variables
    import node.installer as installer
    from node.main import NodeJS
    node = NodeJS()

    overwrite_default_javascript_snippet()

    installer.install(node_variables.NODE_JS_VERSION)

mainPlugin = startPlugin()

${include ./flow/main.py}

${include ./javascript_completions/main.py}

${include ./evaluate_javascript/main.py}

${include ./project/main.py}

${include ./helper/main.py}

if int(sublime.version()) < 3000 :
  mainPlugin.init()
else :
  def plugin_loaded():
    global mainPlugin
    mainPlugin.init()
    if not test_python() :
      sublime.error_message("You must install Python 3 and set the absolute path in the main settings to use some features!")
