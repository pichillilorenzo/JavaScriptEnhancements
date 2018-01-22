import sublime, sublime_plugin
import os, sys, imp, platform, json, traceback, threading, urllib, shutil, re, time
from shutil import copyfile
from threading import Timer

PLUGIN_VERSION = "0.13.13"

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

WINDOWS_BATCH_FOLDER = os.path.join(PACKAGE_PATH, 'windows_batch')

platform_switcher = {"osx": "OSX", "linux": "Linux", "windows": "Windows"}
os_switcher = {"osx": "darwin", "linux": "linux", "windows": "win"}
PLATFORM = platform_switcher.get(sublime.platform())
PLATFORM_ARCHITECTURE = "64bit" if platform.architecture()[0] == "64bit" else "32bit" 

PROJECT_TYPE_SUPPORTED = ['empty', 'angularv1', 'angularv2', 'cordova', 'express', 'ionicv1', 'ionicv2', 'react', 'react-native', 'yeoman']

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

  elif sublime.platform() == 'windows':
    executable_path = os.path.join(os.path.dirname(executable_path), "subl.exe")

  return executable_path

def subl(args):
  
  executable_path = sublime_executable_path()

  args_list = list()

  if sublime.platform() == 'windows' :
    args = [executable_path] + args
    for arg in args :
      args_list.append(json.dumps(arg))
    json.dumps(executable_path)
  else :
    for arg in args :
      args_list.append(shlex.quote(arg))
    shlex.quote(executable_path)
  
  args = executable_path + " " + " ".join(args_list)

  return subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def overwrite_default_javascript_snippet():
  if not os.path.isdir(os.path.join(SUBLIME_PACKAGES_PATH, "JavaScript")) :
    os.mkdir(os.path.join(SUBLIME_PACKAGES_PATH, "JavaScript"))
  if not os.path.isdir(os.path.join(SUBLIME_PACKAGES_PATH, "JavaScript", "Snippets")) :
    os.mkdir(os.path.join(SUBLIME_PACKAGES_PATH, "JavaScript", "Snippets"))
  for file_name in os.listdir(os.path.join(PACKAGE_PATH, "JavaScript-overwrite-default-snippet")) :
    if file_name.endswith(".sublime-snippet") and os.path.isfile(os.path.join(PACKAGE_PATH, "JavaScript-overwrite-default-snippet", file_name)) :
      shutil.copy(os.path.join(PACKAGE_PATH, "JavaScript-overwrite-default-snippet", file_name), os.path.join(SUBLIME_PACKAGES_PATH, "JavaScript", "Snippets", file_name))

class show_javascript_enhancements_versionCommand(sublime_plugin.WindowCommand):
  def run(self):
    if sublime.ok_cancel_dialog("JavaScript Enhancements plugin version: "+PLUGIN_VERSION, "Copy"):
      sublime.set_clipboard(PLUGIN_VERSION)

class startPlugin():
  def init(self):
 
    node_modules_path = os.path.join(PACKAGE_PATH, "node_modules")
    npm = NPM()
    if not os.path.exists(node_modules_path):
      sublime.active_window().status_message("JavaScript Enhancements - installing npm dependencies...")
      result = npm.install_all()
      if result[0]: 
        sublime.active_window().status_message("JavaScript Enhancements - npm dependencies installed correctly.")
      else:
        print(result)
        if os.path.exists(node_modules_path):
          shutil.rmtree(node_modules_path)
        sublime.error_message("Error during installation: can't install npm dependencies for JavaScript Enhancements plugin.\n\nThe error COULD be caused by the npm permission access (EACCES error), so in this case you need to repair/install node.js and npm in a way that doesn't require \"sudo\" command.\n\nFor example you could use a Node Version Manager, such as \"nvm\" or \"nodenv\".\n\nTry to run \"npm install\" inside the package of this plugin to see what you get.")
        return
    # else:
    #   result = npm.update_all()
    #   if not result[0]: 
    #     sublime.active_window().status_message("Error: JavaScript Enhancements - cannot update npm dependencies.")
    
    sublime.set_timeout_async(lambda: overwrite_default_javascript_snippet())

    window = sublime.active_window()
    view = window.active_view()

    sublime.set_timeout_async(lambda: show_flow_errorsViewEventListener(view).on_activated_async())

mainPlugin = startPlugin()

${include ./flow/main.py}

${include ./project/main.py}

${include ./helper/main.py}

def start():

  global mainPlugin

  print("JavaScript Enhancements plugin version: "+PLUGIN_VERSION)

  if platform.architecture()[0] != "64bit":
    print(platform.architecture())
    sublime.error_message("Your architecture is not supported by this plugin. This plugin supports only 64bit architectures.")
    return

  if sublime.platform() != 'windows':
    try:
      sys.modules["TerminalView"]
    except Exception as err:
      response = sublime.yes_no_cancel_dialog("TerminalView plugin is missing. TerminalView is required to be able to use \"JavaScript Enhancements\" plugin.\n\nDo you want open the github repo of it?", "Yes, open it", "No")
      if response == sublime.DIALOG_YES:
        sublime.active_window().run_command("open_url", args={"url": "https://github.com/Wramberg/TerminalView"})
      return

  try:
    sys.modules["JavaScript Completions"]
    sublime.error_message("Please uninstall/disable my other plugin \"JavaScript Completions\". It could conflict with this one!")
    return
  except Exception as err:
    pass

  node = NodeJS(check_local=True)
  try:
    print("node.js version: " + str(node.getCurrentNodeJSVersion()))
  except Exception as err: 
    print(err)
    response = sublime.yes_no_cancel_dialog("Error during installation: \"node.js\" seems not installed on your system. Node.js and npm are required to be able to use JavaScript Enhancements plugin.\n\nIf you are using \"nvm\" or you have a different path for node.js and npm, please then change the path on:\n\nPreferences > Package Settings > JavaScript Enhancements > Settings\n\nand restart Sublime Text.\n\nIf this doesn't work then try also to add the path of their binaries in the PATH key-value on the same JavaScript Enhancements settings file. This variable will be used to add them in the $PATH environment variable, so put the symbol \":\" (instead \";\" for Windows) in front of your path.\n\nDo you want open the website of node.js?", "Yes, open it", "Or use nvm")
    if response == sublime.DIALOG_YES:
      sublime.active_window().run_command("open_url", args={"url": "https://nodejs.org"})
    elif response == sublime.DIALOG_NO:
      sublime.active_window().run_command("open_url", args={"url": "https://github.com/creationix/nvm"})
    return

  npm = NPM(check_local=True)
  try:
    print("npm version: " + str(npm.getCurrentNPMVersion()))
  except Exception as err: 
    print(err)
    response = sublime.yes_no_cancel_dialog("Error during installation: \"npm\" seems not installed on your system. Node.js and npm are required to be able to use JavaScript Enhancements plugin.\n\nIf you are using \"nvm\" or you have a different path for node.js and npm, please change their custom path on:\n\nPreferences > Package Settings > JavaScript Enhancements > Settings\n\nand restart Sublime Text.\n\nIf this doesn't work then try also to add the path of their binaries in the PATH key-value on the same JavaScript Enhancements settings file. This variable will be used to add them in the $PATH environment variable, so put the symbol \":\" (instead \";\" for Windows) in front of your path.\n\nDo you want open the website of node.js?", "Yes, open it", "Or use nvm")
    if response == sublime.DIALOG_YES:
      sublime.active_window().run_command("open_url", args={"url": "https://nodejs.org"})
    elif response == sublime.DIALOG_NO:
      sublime.active_window().run_command("open_url", args={"url": "https://github.com/creationix/nvm"})
    return

  mainPlugin.init()

def plugin_loaded():
  
  if int(sublime.version()) >= 3124 :
    sublime.set_timeout_async(start, 1000)
  else:
    response = sublime.yes_no_cancel_dialog("JavaScript Enhancements plugin requires Sublime Text 3 (build 3124 or newer). Your build is: " + sublime.version() + ". Do you want open the download page?", "Yes, open it", "No")
    if response == sublime.DIALOG_YES:
      sublime.active_window().run_command("open_url", args={"url": "https://www.sublimetext.com/3"})
