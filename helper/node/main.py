import subprocess, threading
import sys, imp, codecs, shlex, os, json, traceback, tempfile

NODE_JS_EXEC = "node"
NPM_EXEC = "npm"
YARN_EXEC = "yarn"

NODE_MODULES_FOLDER_NAME = "node_modules"
NODE_MODULES_PATH = os.path.join(PACKAGE_PATH, NODE_MODULES_FOLDER_NAME)
NODE_MODULES_BIN_PATH = os.path.join(NODE_MODULES_PATH, ".bin")

class NodeJS(object):
  def __init__(self, check_local = False):
    self.check_local = check_local
    self.node_js_path = ""

    if self.check_local :
      settings = get_project_settings()
      if settings :
        self.node_js_path = settings["project_settings"]["node_js_custom_path"] or javascriptCompletions.get("node_js_custom_path") or NODE_JS_EXEC
      else :
        self.node_js_path = javascriptCompletions.get("node_js_custom_path") or NODE_JS_EXEC
    else :
      self.node_js_path = javascriptCompletions.get("node_js_custom_path") or NODE_JS_EXEC

  def eval(self, js, eval_type="eval", strict_mode=False):

    js = ("'use strict'; " if strict_mode else "") + js
    eval_type = "--eval" if eval_type == "eval" else "--print"

    args = [self.node_js_path, eval_type, js]

    result = Util.execute(args[0], args[1:])

    if result[0] :
      return result[1]

    raise Exception(result[1])

  def getCurrentNodeJSVersion(self) :

    args = [self.node_js_path, "-v"]

    result = Util.execute(args[0], args[1:])

    if result[0] :
      return result[1].strip()

    raise Exception(result[1])

  def execute(self, command, command_args, is_from_bin=False, chdir="", wait_terminate=True, func_stdout=None, args_func_stdout=[], bin_path="", use_node=True) :

    if sublime.platform() == 'windows':
      if is_from_bin :
        args = [os.path.join( (bin_path or NODE_MODULES_BIN_PATH), command+".cmd")] + command_args
      else :
        args = ([self.node_js_path] if use_node else []) + [os.path.join( (bin_path or NODE_MODULES_BIN_PATH), command)] + command_args
    else :
      args = ([self.node_js_path] if use_node else []) + [os.path.join( (bin_path or NODE_MODULES_BIN_PATH), command)] + command_args
    
    return Util.execute(args[0], args[1:], chdir=chdir, wait_terminate=wait_terminate, func_stdout=func_stdout, args_func_stdout=args_func_stdout)
    
  def execute_check_output(self, command, command_args, is_from_bin=False, use_fp_temp=False, use_only_filename_view_flow=False, fp_temp_contents="", is_output_json=False, chdir="", clean_output_flow=False, bin_path="", use_node=True) :

    fp = None
    args = ""

    if use_fp_temp :
      
      if sublime.platform() == "windows":
        fp = tempfile.NamedTemporaryFile(delete=False)
        fp.write(str.encode(fp_temp_contents))
        fp.close()
      else :
        fp = tempfile.NamedTemporaryFile()
        fp.write(str.encode(fp_temp_contents))
        fp.flush()

    command_args_list = list()
    for command_arg in command_args :
      if command_arg == ":temp_file":
        command_arg = fp.name
      command_args_list.append(shlex.quote(command_arg) if sublime.platform() != 'windows' else json.dumps(command_arg))
    command_args = " ".join(command_args_list)

    if sublime.platform() == 'windows':
      if is_from_bin :
        args = json.dumps(os.path.join((bin_path or NODE_MODULES_BIN_PATH), command)+'.cmd')+' '+command_args+(' < '+json.dumps(fp.name) if fp and not use_only_filename_view_flow else "")
      else :
        args = ( json.dumps(self.node_js_path)+" " if use_node else "")+json.dumps(os.path.join((bin_path or NODE_MODULES_BIN_PATH), command))+" "+command_args+(" < "+json.dumps(fp.name) if fp and not use_only_filename_view_flow else "")
    else:
      args = ( shlex.quote(self.node_js_path)+" " if use_node else "")+shlex.quote(os.path.join((bin_path or NODE_MODULES_BIN_PATH), command))+" "+command_args+(" < "+shlex.quote(fp.name) if fp and not use_only_filename_view_flow else "")

    #print(args)
      
    old_env = os.environ.copy()

    new_env = old_env.copy()
    new_env["PATH"] = new_env["PATH"] + javascriptCompletions.get("PATH")

    # update the PATH environment variable
    os.environ.update(new_env)
      
    try:
      output = None
      result = None

      owd = os.getcwd()
      if chdir :
        os.chdir(chdir)

      output = subprocess.check_output(
          args, shell=True, stderr=subprocess.STDOUT
      )

      if sublime.platform() == "windows" and use_fp_temp: 
        os.unlink(fp.name)

      # reset the PATH environment variable
      os.environ.update(old_env)

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
      print(traceback.format_exc())

      # reset the PATH environment variable
      os.environ.update(old_env)

      if sublime.platform() == "windows" and use_fp_temp: 
        os.unlink(fp.name)

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

      # reset the PATH environment variable
      os.environ.update(old_env)

      print(traceback.format_exc())

      if use_fp_temp :
        if sublime.platform() == "windows": 
          os.unlink(fp.name)
        else:
          fp.close()
      return [False, None]

class NPM(object):
  def __init__(self, check_local = False):
    self.check_local = check_local
    self.npm_path = ""
    self.yarn_path = ""
    self.cli_path = ""
    self.node_js_path = ""

    if self.check_local :
      settings = get_project_settings()
      if settings :
        self.node_js_path = settings["project_settings"]["node_js_custom_path"] or javascriptCompletions.get("node_js_custom_path") or NODE_JS_EXEC
        self.npm_path = settings["project_settings"]["npm_custom_path"] or javascriptCompletions.get("npm_custom_path") or NPM_EXEC
        self.yarn_path = settings["project_settings"]["yarn_custom_path"] or javascriptCompletions.get("yarn_custom_path") or YARN_EXEC

        if settings["project_settings"]["use_yarn"] and self.yarn_path :
          self.cli_path = self.yarn_path
        else :
          self.cli_path = self.npm_path

      else :
        self.node_js_path = javascriptCompletions.get("node_js_custom_path") or NODE_JS_EXEC
        self.npm_path = javascriptCompletions.get("npm_custom_path") or NPM_EXEC
        self.yarn_path = javascriptCompletions.get("yarn_custom_path") or YARN_EXEC

        self.cli_path = self.npm_path
    else :
      self.node_js_path = javascriptCompletions.get("node_js_custom_path") or NODE_JS_EXEC
      self.npm_path = javascriptCompletions.get("npm_custom_path") or NPM_EXEC
      self.yarn_path = javascriptCompletions.get("yarn_custom_path") or YARN_EXEC

      self.cli_path = self.npm_path

  def execute(self, command, command_args, chdir="", wait_terminate=True, func_stdout=None, args_func_stdout=[]) :

    args = []

    if sublime.platform() == 'windows':
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

    if sublime.platform() == 'windows':
      args = [self.cli_path, "-v"]
    else :
      args = [self.cli_path, "-v"]

    result = Util.execute(args[0], args[1:])

    if result[0] :
      return result[1].strip()

    raise Exception(result[1])
