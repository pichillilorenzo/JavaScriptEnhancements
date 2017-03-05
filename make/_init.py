import sublime, sublime_plugin
import os, sys, imp, platform, json, traceback, threading, urllib, shutil, re
from shutil import copyfile
from threading import Timer

PACKAGE_PATH = os.path.abspath(os.path.dirname(__file__))
PACKAGE_NAME = os.path.basename(PACKAGE_PATH)
SUBLIME_PACKAGES_PATH = os.path.dirname(PACKAGE_PATH)
 
sys.path += [PACKAGE_PATH] + [os.path.join(PACKAGE_PATH, f) for f in ['node', 'util']]

sublime_version = int(sublime.version())

if 'reloader' in sys.modules:
  imp.reload(sys.modules['reloader'])
import reloader

# platform
platform_switcher = {"osx": "OSX", "linux": "Linux", "windows": "Windows"}
PLATFORM = platform_switcher.get(sublime.platform())
PLATFORM_ARCHITECTURE = "64bit" if platform.architecture()[0] == "64bit" else "32bit" 

def setTimeout(time, func):
  timer = Timer(time, func)
  timer.start()

# class handle_settingCommand(sublime_plugin.WindowCommand) :
#   def run(self, folder_from_package, file_name, extension) :
#     open_setting(folder_from_package, file_name, extension)

#   def is_visible(self, folder_from_package, file_name, extension) :
#     if file_name.find(" (") >= 0 and file_name.find(" ("+PLATFORM+")") >= 0 :
#       return True
#     elif file_name.find(" (") >= 0 and file_name.find(" ("+PLATFORM+")") < 0 :
#       return False
#     return True
    
# def enable_setting(folder_from_package, file_name, extension) :
#   path = os.path.join(PACKAGE_PATH, folder_from_package)
#   file_name_enabled = file_name + "." + extension
#   file_name_disabled = file_name + "_disabled" + "." + extension
#   path_file_enabled = os.path.join(path, file_name_enabled)
#   path_file_disabled = os.path.join(path, file_name_disabled)
#   try :
#     if os.path.isfile(path_file_disabled) :
#       os.rename(path_file_disabled, path_file_enabled)
#   except Exception as e :
#     print("Error: "+traceback.format_exc())

# def disable_setting(folder_from_package, file_name, extension) :
#   path = os.path.join(PACKAGE_PATH, folder_from_package)
#   file_name_enabled = file_name + "." + extension
#   file_name_disabled = file_name + "_disabled" + "." + extension
#   path_file_enabled = os.path.join(path, file_name_enabled)
#   path_file_disabled = os.path.join(path, file_name_disabled)
#   try :
#     if os.path.isfile(path_file_enabled) :
#       os.rename(path_file_enabled, path_file_disabled)
#   except Exception as e :
#     print("Error: "+traceback.format_exc())

# def is_setting_enabled(folder_from_package, file_name, extension) :
#   path = os.path.join(PACKAGE_PATH, folder_from_package)
#   file_name_enabled = file_name + "." + extension
#   path_file_enabled = os.path.join(path, file_name_enabled)
#   return os.path.isfile(path_file_enabled)
      
# def open_setting(folder_from_package, file_name, extension) :
#   path = os.path.join(PACKAGE_PATH, folder_from_package)
#   file_name_enabled = file_name + "." + extension
#   file_name_disabled = file_name + "_disabled" + "." + extension
#   path_file_enabled = os.path.join(path, file_name_enabled)
#   path_file_disabled = os.path.join(path, file_name_disabled)

#   if os.path.isfile(path_file_enabled) :
#     sublime.active_window().open_file(path_file_enabled)
#   elif os.path.isfile(path_file_disabled) :
#     sublime.active_window().open_file(path_file_disabled)

class startPlugin():
  def init(self):
    import node.node_variables as node_variables
    import node.installer as installer

    if int(sublime.version()) >= 3000 :
    
      installer.install(node_variables.NODE_JS_VERSION)

mainPlugin = startPlugin()

${include ./javascript_completions/javascript_completions_class.py}
javascriptCompletions = JavaScriptCompletions()

${include ./evaluate_javascript/evaluate_javascript_class.py}

${include ./helper/helper_class.py}

${include ./javascript_completions/main.py}

${include ./evaluate_javascript/main.py}

${include ./helper/main.py}

if int(sublime.version()) < 3000 :
  mainPlugin.init()
  javascriptCompletions.init()
else :
  def plugin_loaded():
    global mainPlugin
    mainPlugin.init()
    global javascriptCompletions
    javascriptCompletions.init()
