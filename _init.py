import sublime, sublime_plugin
import os, sys, imp, platform, json, traceback
from shutil import copyfile
from threading import Timer

PACKAGE_PATH = os.path.abspath(os.path.dirname(__file__))
PACKAGE_NAME = os.path.basename(PACKAGE_PATH)
SUBLIME_PACKAGES_PATH = os.path.dirname(PACKAGE_PATH)
 
sys.path += [PACKAGE_PATH] + [os.path.join(PACKAGE_PATH, f) for f in ['node', 'evaluate_javascript', 'javascript_completions']]

sublime_version = int(sublime.version())

if 'reloader' in sys.modules:
  imp.reload(sys.modules['reloader'])
import reloader

# platform
platform_switcher = {"osx": "OSX", "linux": "Linux", "windows": "Windows"}
PLATFORM = platform_switcher.get(sublime.platform())
PLATFORM_ARCHITECTURE = "64bit" if platform.architecture()[0] == "64bit" else "32bit" 

_plugins = ["javascript_completions", "evaluate_javascript"]


class handle_settingCommand(sublime_plugin.WindowCommand) :
  def run(self, folder_from_package, file_name, extension) :
    open_setting(folder_from_package, file_name, extension)

  def is_visible(self, folder_from_package, file_name, extension) :
    if file_name.find(" (") >= 0 and file_name.find(" ("+PLATFORM+")") >= 0 :
      return True
    elif file_name.find(" (") >= 0 and file_name.find(" ("+PLATFORM+")") < 0 :
      return False
    return True
def setTimeout(time, func):
  timer = Timer(time, func)
  timer.start()

def enable_setting(folder_from_package, file_name, extension) :
  path = os.path.join(PACKAGE_PATH, folder_from_package)
  file_name_enabled = file_name + "." + extension
  file_name_disabled = file_name + "_disabled" + "." + extension
  path_file_enabled = os.path.join(path, file_name_enabled)
  path_file_disabled = os.path.join(path, file_name_disabled)
  path_load_resource = os.path.join(PACKAGE_NAME, path, file_name_enabled)
  try :
    if os.path.isfile(path_file_disabled) :
      os.rename(path_file_disabled, path_file_enabled)
  except Exception as e :
    print("Error: "+traceback.format_exc())

def disable_setting(folder_from_package, file_name, extension) :
  path = os.path.join(PACKAGE_PATH, folder_from_package)
  file_name_enabled = file_name + "." + extension
  file_name_disabled = file_name + "_disabled" + "." + extension
  path_file_enabled = os.path.join(path, file_name_enabled)
  path_file_disabled = os.path.join(path, file_name_disabled)
  path_load_resource = os.path.join(PACKAGE_NAME, path, file_name_enabled)
  try :
    if os.path.isfile(path_file_enabled) :
      os.rename(path_file_enabled, path_file_disabled)
  except Exception as e :
    print("Error: "+traceback.format_exc())

def open_setting(folder_from_package, file_name, extension) :
  path = os.path.join(PACKAGE_PATH, folder_from_package)
  file_name_enabled = file_name + "." + extension
  file_name_disabled = file_name + "_disabled" + "." + extension
  path_file_enabled = os.path.join(path, file_name_enabled)
  path_file_disabled = os.path.join(path, file_name_disabled)
  path_load_resource = os.path.join(PACKAGE_NAME, path, file_name_enabled)

  if os.path.isfile(path_file_enabled) :
    sublime.active_window().open_file(path_file_enabled)
  elif os.path.isfile(path_file_disabled) :
    sublime.active_window().open_file(path_file_disabled)

class startPlugin():
  def init(self):
    import node.node_variables as node_variables
    import node.installer as installer

    if int(sublime.version()) >= 3000 :
      eval_js_json = None
      if os.path.isfile(os.path.join(PACKAGE_PATH, "evaluate_javascript", "Evaluate-JavaScript.sublime-settings")) :
        with open(os.path.join(PACKAGE_PATH, "evaluate_javascript", "Evaluate-JavaScript.sublime-settings")) as data_file:    
          eval_js_json = json.load(data_file)

      node_js_version = sublime.load_settings('Evaluate-JavaScript.sublime-settings').get("node_js_version") or eval_js_json.get("node_js_version") or node_variables.NODE_JS_VERSION
      
      installer.install(node_js_version)

    self.handle_plugins()

  def load_plugins(self):
    global _plugins
    for _plugin in _plugins :
      copyfile(os.path.join(PACKAGE_PATH, _plugin, "main.py"), os.path.join(PACKAGE_PATH, "_created_"+_plugin+".py"))

  def delete_plugins(self):
    global _plugins
    for _plugin in _plugins :
      if os.path.isfile(os.path.join(PACKAGE_PATH, "_created_"+_plugin+".py")) : 
        os.remove(os.path.join(PACKAGE_PATH, "_created_"+_plugin+".py"))
    setTimeout(1, self.load_plugins)

  def handle_plugins(self):
    setTimeout(0, self.delete_plugins)

mainPlugin = startPlugin()

if int(sublime.version()) < 3000 :
  mainPlugin.init()
else :
  def plugin_loaded():
    global mainPlugin
    mainPlugin.init()
