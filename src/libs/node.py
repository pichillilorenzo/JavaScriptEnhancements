import sys, imp, codecs, shlex, os, json, traceback, tempfile, subprocess, threading

from . import util
from .global_vars import *
from .javascript_enhancements_settings import *

class NodeJS():
  def __init__(self, check_local = False):

    self.check_local = check_local
    self.node_js_path = ""

    if self.check_local :
      settings = util.get_project_settings()
      if settings :
        self.node_js_path = settings["project_settings"]["node_js_custom_path"] or javaScriptEnhancements.get("node_js_custom_path") or NODE_JS_EXEC
      else :
        self.node_js_path = javaScriptEnhancements.get("node_js_custom_path") or NODE_JS_EXEC
    else :
      self.node_js_path = javaScriptEnhancements.get("node_js_custom_path") or NODE_JS_EXEC

  def eval(self, js, eval_type="eval", strict_mode=False):

    js = ("'use strict'; " if strict_mode else "") + js
    eval_type = "--eval" if eval_type == "eval" else "--print"

    args = [self.node_js_path, eval_type, js]

    result = util.execute(args[0], args[1:])

    if result[0] :
      return result[1]

    raise Exception(result[1])

  def getCurrentNodeJSVersion(self) :

    args = [self.node_js_path, "-v"]

    result = util.execute(args[0], args[1:])

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

    return util.execute(args[0], args[1:], chdir=chdir, wait_terminate=wait_terminate, func_stdout=func_stdout, args_func_stdout=args_func_stdout)
    
  def execute_check_output(self, command, command_args, is_from_bin=False, use_fp_temp=False, use_only_filename_view_flow=False, fp_temp_contents="", is_output_json=False, chdir="", clean_output_flow=False, bin_path="", use_node=True, command_arg_escape=True) :
    
    debug_mode = javaScriptEnhancements.get("debug_mode")

    fp = None
    args = ""

    if use_fp_temp :
      
      if sublime.platform() == "windows":
        fp = tempfile.NamedTemporaryFile(prefix="javascript_enhancements_", delete=False)
        fp.write(str.encode(fp_temp_contents))
        fp.close()
      else :
        fp = tempfile.NamedTemporaryFile(prefix="javascript_enhancements_")
        fp.write(str.encode(fp_temp_contents))
        fp.flush()

    command_args_list = list()
    for command_arg in command_args :
      if command_arg == ":temp_file":
        command_arg = fp.name
      command_args_list.append( (shlex.quote(command_arg) if sublime.platform() != 'windows' else json.dumps(command_arg, ensure_ascii=False)) if command_arg_escape else command_arg )
    command_args = " ".join(command_args_list)

    if sublime.platform() == 'windows':
      if is_from_bin :
        args = json.dumps(os.path.join((bin_path or NODE_MODULES_BIN_PATH), command)+'.cmd', ensure_ascii=False)+' '+command_args+(' < '+json.dumps(fp.name, ensure_ascii=False) if fp and not use_only_filename_view_flow else "")
      else :
        args = ( json.dumps(self.node_js_path, ensure_ascii=False)+" " if use_node else "")+json.dumps(os.path.join((bin_path or NODE_MODULES_BIN_PATH), command), ensure_ascii=False)+" "+command_args+(" < "+json.dumps(fp.name, ensure_ascii=False) if fp and not use_only_filename_view_flow else "")
    else:
      args = ( shlex.quote(self.node_js_path)+" " if use_node else "")+shlex.quote(os.path.join((bin_path or NODE_MODULES_BIN_PATH), command))+" "+command_args+(" < "+shlex.quote(fp.name) if fp and not use_only_filename_view_flow else "")

    if debug_mode:
      print(args)

    old_env = os.environ.copy()

    new_env = old_env.copy()
    new_env["PATH"] = new_env["PATH"] + javaScriptEnhancements.get("PATH")

    # update the PATH environment variable
    os.environ.update(new_env)

    try:
      output = None
      result = None

      owd = os.getcwd()
      if chdir :
        os.chdir(chdir)

      output = subprocess.check_output(
          args, shell=True, stderr=subprocess.STDOUT, timeout=10
      )
      #print(output)

      if sublime.platform() == "windows" and use_fp_temp: 
        try:
          os.remove(fp.name)
        except PermissionError as e:
          pass

      # reset the PATH environment variable
      os.environ.update(old_env)

      if chdir:
        os.chdir(owd)

      if clean_output_flow :
        out = output.decode("utf-8", "ignore").strip()
        out = out.split("\n")
        out = out[-1]
        if '{"flowVersion":"' in out :
          index = out.index('{"flowVersion":"')
          out = out[index:]
          result = json.loads(out) if is_output_json else out
        else :
          try:
            result = json.loads(out) if is_output_json else out
          except ValueError as e:
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

      if e.output:
        print(e.output)
        output_error_message = e.output.decode("utf-8", "ignore").strip()
        output_error_message = output_error_message.split("\n")
        final_message = ""
        flag = False

        for msg in output_error_message:
          msg = msg.strip()
          if msg.startswith("{\"flowVersion\":"):
            flag = True
            break
          else:
            final_message += msg + " "

        if flag:
          sublime.active_window().status_message("Flow CLI Error: " + final_message)

      # reset the PATH environment variable
      os.environ.update(old_env)

      if sublime.platform() == "windows" and use_fp_temp: 
        os.remove(fp.name)

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

    except subprocess.TimeoutExpired as e:
      # reset the PATH environment variable
      os.environ.update(old_env)

      #print(traceback.format_exc())

      if use_fp_temp :
        if sublime.platform() == "windows": 
          os.remove(fp.name)
        else:
          fp.close()
      return [False, None]

    except Exception as e:

      # reset the PATH environment variable
      os.environ.update(old_env)

      print(traceback.format_exc())

      if use_fp_temp :
        if sublime.platform() == "windows": 
          os.remove(fp.name)
        else:
          fp.close()
      return [False, None]
