import sys, imp, codecs, shlex, os, json, traceback, tempfile, subprocess, threading

from . import util
from .global_vars import *
from .javascript_enhancements_settings import *

class NPM():
  def __init__(self, check_local = False):
    self.check_local = check_local
    self.npm_path = ""
    self.yarn_path = ""
    self.cli_path = ""
    self.node_js_path = ""

    if self.check_local :
      settings = util.get_project_settings()
      if settings :
        self.node_js_path = settings["project_settings"]["node_js_custom_path"] or javaScriptEnhancements.get("node_js_custom_path") or NODE_JS_EXEC
        self.npm_path = settings["project_settings"]["npm_custom_path"] or javaScriptEnhancements.get("npm_custom_path") or NPM_EXEC
        self.yarn_path = settings["project_settings"]["yarn_custom_path"] or javaScriptEnhancements.get("yarn_custom_path") or YARN_EXEC

        if settings["project_settings"]["use_yarn"] and self.yarn_path :
          self.cli_path = self.yarn_path
        else :
          self.cli_path = self.npm_path

      else :
        self.node_js_path = javaScriptEnhancements.get("node_js_custom_path") or NODE_JS_EXEC
        self.npm_path = javaScriptEnhancements.get("npm_custom_path") or NPM_EXEC
        self.yarn_path = javaScriptEnhancements.get("yarn_custom_path") or YARN_EXEC

        self.cli_path = self.npm_path
    else :
      self.node_js_path = javaScriptEnhancements.get("node_js_custom_path") or NODE_JS_EXEC
      self.npm_path = javaScriptEnhancements.get("npm_custom_path") or NPM_EXEC
      self.yarn_path = javaScriptEnhancements.get("yarn_custom_path") or YARN_EXEC

      self.cli_path = self.npm_path

  def execute(self, command, command_args, chdir="", wait_terminate=True, func_stdout=None, args_func_stdout=[]) :

    args = []

    if sublime.platform() == 'windows':
      args = [self.cli_path, command] + command_args
    else :
      args = [self.cli_path, command] + command_args
    
    return util.execute(args[0], args[1:], chdir=chdir, wait_terminate=wait_terminate, func_stdout=func_stdout, args_func_stdout=args_func_stdout)

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
    settings = util.get_project_settings()

    if self.check_local and settings and os.path.isfile( os.path.join(settings["project_dir_name"], "package.json") ) :
      package_json_path = os.path.join(settings["project_dir_name"], "package.json")
    elif self.check_local and (not settings or not os.path.isfile( os.path.join(settings["project_dir_name"], "package.json") ) ) :
      return None
    else :
      package_json_path = os.path.join(PACKAGE_PATH, "package.json")

    return util.open_json(package_json_path)

  def getCurrentNPMVersion(self) :

    if sublime.platform() == 'windows':
      args = [self.cli_path, "-v"]
    else :
      args = [self.cli_path, "-v"]

    result = util.execute(args[0], args[1:])

    if result[0] :
      return result[1].strip()

    raise Exception(result[1])
