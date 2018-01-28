import sublime, sublime_plugin
import os, sys, imp, platform, json, traceback, threading, urllib, shutil, re, time
from shutil import copyfile
from threading import Timer
from os import environ
from subprocess import Popen, PIPE

PLUGIN_VERSION = "0.13.18"

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
${include ./helper/PopupManager.py}

KEYMAP_COMMANDS = []
keymaps = Util.open_json(os.path.join(PACKAGE_PATH, 'Default.sublime-keymap'))
for keymap in keymaps:
  if keymap["command"] != "window_view_keypress":
    KEYMAP_COMMANDS += [keymap["command"]]

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

    if os.path.exists(node_modules_path) and not os.path.exists(os.path.join(node_modules_path, ".bin")):
      if sublime.platform() == "windows":
        os.system("taskkill /f /im flow.exe")
      shutil.rmtree(node_modules_path)

    if not os.path.exists(node_modules_path):
      animation_npm_installer = AnimationLoader(["[=     ]", "[ =    ]", "[   =  ]", "[    = ]", "[     =]", "[    = ]", "[   =  ]", "[ =    ]"], 0.067, "JavaScript Enhancements - installing npm dependencies ")
      interval_animation = RepeatedTimer(animation_npm_installer.sec, animation_npm_installer.animate)

      result = npm.install_all()
      if result[0]: 
        animation_npm_installer.on_complete()
        interval_animation.stop()
        sublime.active_window().status_message("JavaScript Enhancements - npm dependencies installed correctly.")
      else:
        animation_npm_installer.on_complete()
        interval_animation.stop()
        print(result)
        if os.path.exists(node_modules_path):
          shutil.rmtree(node_modules_path)
        sublime.error_message("Error during installation: can't install npm dependencies for JavaScript Enhancements plugin.\n\nThe error COULD be caused by the npm permission access (EACCES error), so in this case you need to repair/install node.js and npm in a way that doesn't require \"sudo\" command.\n\nFor example you could use a Node Version Manager, such as \"nvm\" or \"nodenv\".\n\nTry to run \"npm install\" inside the package of this plugin to see what you get.")
        return
    
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
    response = sublime.yes_no_cancel_dialog("Error during installation: \"node.js\" seems not installed on your system. Node.js and npm are required to be able to use JavaScript Enhancements plugin.\n\nIf you are using \"nvm\" or you have a different path for node.js and npm, please then change the path on:\n\nPreferences > Package Settings > JavaScript Enhancements > Settings\n\nand restart Sublime Text. If you don't know the path of it, use \"which node\" (for Linux-based OS) or \"where node.exe\" (for Windows OS) to get it.\n\nIf this doesn't work then try also to add the path of their binaries in the PATH key-value on the same JavaScript Enhancements settings file. This variable will be used to add them in the $PATH environment variable, so put the symbol \":\" (instead \";\" for Windows) in front of your path.\n\nDo you want open the website of node.js?", "Yes, open it", "Or use nvm")
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
    response = sublime.yes_no_cancel_dialog("Error during installation: \"npm\" seems not installed on your system. Node.js and npm are required to be able to use JavaScript Enhancements plugin.\n\nIf you are using \"nvm\" or you have a different path for node.js and npm, please change their custom path on:\n\nPreferences > Package Settings > JavaScript Enhancements > Settings\n\nand restart Sublime Text. If you don't know the path of it, use \"which npm\" (for Linux-based OS) or \"where npm\" (for Windows OS) to get it.\n\nIf this doesn't work then try also to add the path of their binaries in the PATH key-value on the same JavaScript Enhancements settings file. This variable will be used to add them in the $PATH environment variable, so put the symbol \":\" (instead \";\" for Windows) in front of your path.\n\nDo you want open the website of node.js?", "Yes, open it", "Or use nvm")
    if response == sublime.DIALOG_YES:
      sublime.active_window().run_command("open_url", args={"url": "https://nodejs.org"})
    elif response == sublime.DIALOG_NO:
      sublime.active_window().run_command("open_url", args={"url": "https://github.com/creationix/nvm"})
    return

  mainPlugin.init()

##
## start - Fix Mac Path plugin code with some fixes
##

fixPathSettings = None
fixPathOriginalEnv = {}

def getSysPath():
  command = ""
  if platform.system() == "Darwin":
    command = "TERM=ansi CLICOLOR=\"\" SUBLIME=1 /usr/bin/login -fqpl $USER $SHELL -l -c 'TERM=ansi CLICOLOR=\"\" SUBLIME=1 printf \"%s\" \"$PATH\"'"
  elif platform.system() == "Linux":
    command = "TERM=ansi CLICOLOR=\"\" SUBLIME=1 $SHELL --login -c 'TERM=ansi CLICOLOR=\"\" printf \"%s\" $PATH'"
  else:
    return ""

  # Execute command with original environ. Otherwise, our changes to the PATH propogate down to
  # the shell we spawn, which re-adds the system path & returns it, leading to duplicate values.
  sysPath = Popen(command, stdout=PIPE, shell=True, env=fixPathOriginalEnv).stdout.read()

  sysPathString = sysPath.decode("utf-8")
  # Remove ANSI control characters (see: http://www.commandlinefu.com/commands/view/3584/remove-color-codes-special-characters-with-sed )
  sysPathString = re.sub(r'\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]', '', sysPathString)
  sysPathString = sysPathString.strip().rstrip(':')

  # Decode the byte array into a string, remove trailing whitespace, remove trailing ':'
  return sysPathString

def fixPath():
  currSysPath = getSysPath()
  # Basic sanity check to make sure our new path is not empty
  if len(currSysPath) < 1:
    return False

  environ['PATH'] = currSysPath

  for pathItem in fixPathSettings.get("additional_path_items", []):
    environ['PATH'] = pathItem + ':' + environ['PATH']

  return True


def plugin_unloaded():
  if platform.system() == "Darwin" or platform.system() == "Linux":
    # When we unload, reset PATH to original value. Otherwise, reloads of this plugin will cause
    # the PATH to be duplicated.
    environ['PATH'] = fixPathOriginalEnv['PATH']

    global fixPathSettings
    fixPathSettings.clear_on_change('fixpath-reload')

  node = NodeJS(check_local=True)
  sublime.set_timeout_async(lambda: node.execute("flow", ["stop"], is_from_bin=True, chdir=os.path.join(PACKAGE_PATH, "flow")))

##
## end - Fix Mac Path plugin code
##

def plugin_loaded():
  
  if int(sublime.version()) >= 3124 :

    if platform.system() == "Darwin" or platform.system() == "Linux":
      global fixPathSettings
      fixPathSettings = sublime.load_settings("Preferences.sublime-settings")
      fixPathSettings.clear_on_change('fixpath-reload')
      fixPathSettings.add_on_change('fixpath-reload', fixPath)

      # Save the original environ (particularly the original PATH) to restore later
      global fixPathOriginalEnv
      for key in environ:
        fixPathOriginalEnv[key] = environ[key]

      fixPath()

    sublime.set_timeout_async(start, 1000)

  else:
    response = sublime.yes_no_cancel_dialog("JavaScript Enhancements plugin requires Sublime Text 3 (build 3124 or newer). Your build is: " + sublime.version() + ". Do you want open the download page?", "Yes, open it", "No")
    if response == sublime.DIALOG_YES:
      sublime.active_window().run_command("open_url", args={"url": "https://www.sublimetext.com/3"})
