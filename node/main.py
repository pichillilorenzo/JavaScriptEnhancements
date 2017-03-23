import subprocess, threading
import sys, imp, codecs, shlex, os, json, traceback, tempfile
import node_variables

PACKAGE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

def check_thread_is_alive(thread_name) :
  for thread in threading.enumerate() :
    if thread.getName() == thread_name and thread.is_alive() :
      return True
  return False

def create_and_start_thread(target, thread_name="", args=[], daemon=True) :
  if not check_thread_is_alive(thread_name) :
    thread = threading.Thread(target=target, name=thread_name, args=args)
    thread.setDaemon(daemon)
    thread.start()
    return thread
  return None

def get_node_js_custom_path():
   with open(os.path.join(PACKAGE_PATH,  "JavaScript-Completions.sublime-settings")) as data_file:    
    return json.load(data_file).get("node_js_custom_path").strip()

def get_npm_custom_path():
   with open(os.path.join(PACKAGE_PATH,  "JavaScript-Completions.sublime-settings")) as data_file:    
    return json.load(data_file).get("npm_custom_path").strip()

class NodeJS(object):
  def eval(self, js, eval_type="eval", strict_mode=False):

    js = ("'use strict'; " if strict_mode else "") + js
    eval_type = "--eval" if eval_type == "eval" else "--print"

    args = ""

    if node_variables.NODE_JS_OS == 'win':
      args = [get_node_js_custom_path() or node_variables.NODE_JS_PATH_EXECUTABLE, eval_type, js]
    else :
      args = shlex.quote(get_node_js_custom_path() or node_variables.NODE_JS_PATH_EXECUTABLE)+" "+shlex.quote(eval_type)+" "+shlex.quote(js)

    p = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = ""

    # check for errors
    for line in p.stderr.readlines():
      lines += codecs.decode(line, "utf-8", "ignore")

    if len(lines) > 0 :
      p.terminate()
      raise Exception(lines)

    lines = ""
    for line in p.stdout.readlines():
      lines += codecs.decode(line, "utf-8", "ignore")
    p.terminate()
    
    return lines

  def getCurrentNodeJSVersion(self, checking_local = False) :

    args = ""

    if node_variables.NODE_JS_OS == 'win':
      args = [get_node_js_custom_path() or node_variables.NODE_JS_PATH_EXECUTABLE, "-v"]
    else :
      args = shlex.quote(get_node_js_custom_path() or node_variables.NODE_JS_PATH_EXECUTABLE if not checking_local else node_variables.NODE_JS_PATH_EXECUTABLE)+" -v"

    p = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = ""

    # check for errors
    for line in p.stderr.readlines():
      lines += codecs.decode(line, "utf-8", "ignore")

    if len(lines) > 0 :
      p.terminate()
      raise Exception(lines)

    lines = ""
    for line in p.stdout.readlines():
      lines += codecs.decode(line, "utf-8", "ignore")
    p.terminate()

    return lines.strip()

  def execute(self, command, command_args, is_from_bin=False, chdir="", wait_terminate=True, func_stdout=None) :

    if node_variables.NODE_JS_OS == 'win':
      if is_from_bin :
        args = [os.path.join(node_variables.NODE_MODULES_BIN_PATH, command+".cmd")] + command_args
      else :
        args = [get_node_js_custom_path() or node_variables.NODE_JS_PATH_EXECUTABLE, os.path.join(node_variables.NODE_MODULES_BIN_PATH, command)] + command_args
    else :
      command_args_list = list()
      for command_arg in command_args :
        command_args_list.append(shlex.quote(command_arg))
      command_args = " ".join(command_args_list)
      args = shlex.quote(get_node_js_custom_path() or node_variables.NODE_JS_PATH_EXECUTABLE)+" "+shlex.quote(os.path.join(node_variables.NODE_MODULES_BIN_PATH, command))+" "+command_args
 
    owd = os.getcwd()
    if chdir :
      os.chdir(chdir)

    p = None
    if wait_terminate :
      p = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif not wait_terminate and func_stdout :
      create_and_start_thread(self.wrapper_func_stdout, "", (args,func_stdout))

    if wait_terminate :
      lines = ""

      if chdir:
        os.chdir(owd)

      # check for errors
      for line in p.stderr.readlines():
        lines += codecs.decode(line, "utf-8", "ignore")

      if len(lines) > 0 :
        p.terminate()
        return [False, lines.strip()]

      lines = ""
      for line in p.stdout.readlines():
        lines += codecs.decode(line, "utf-8", "ignore")
      p.terminate()

      return [True, lines.strip()]

  def wrapper_func_stdout(self, *args):
    with subprocess.Popen(args[0], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1) as p:
      for line in p.stdout:
        line = codecs.decode(line, "utf-8", "ignore")
        args[1](line)
      flag_error = False
      for line in p.stderr:
        line = codecs.decode(line, "utf-8", "ignore")
        if not flag_error:
          flag_error = True
        args[1](line)
      if flag_error:
        args[1]("OUTPUT-ERROR")
      else :
        args[1]("OUTPUT-SUCCESS")
      args[1]("OUTPUT-DONE")

  def execute_check_output(self, command, command_args, is_from_bin=False, use_fp_temp=False, use_only_filename_view_flow=False, fp_temp_contents="", is_output_json=False, chdir="", clean_output_flow=False) :

    fp = None
    if use_fp_temp :
      
      fp = tempfile.NamedTemporaryFile()
      fp.write(str.encode(fp_temp_contents))
      fp.flush()

    if node_variables.NODE_JS_OS == 'win':
      if is_from_bin :
        args = [os.path.join(node_variables.NODE_MODULES_BIN_PATH, command+".cmd")] + command_args
      else :
        args = [get_node_js_custom_path() or node_variables.NODE_JS_PATH_EXECUTABLE, os.path.join(node_variables.NODE_MODULES_BIN_PATH, command)] + command_args
      if fp :
        args += ["<", fp.name]
    else :
      command_args_list = list()
      for command_arg in command_args :
        command_args_list.append(shlex.quote(command_arg))
      command_args = " ".join(command_args_list)
      args = shlex.quote(get_node_js_custom_path() or node_variables.NODE_JS_PATH_EXECUTABLE)+" "+shlex.quote(os.path.join(node_variables.NODE_MODULES_BIN_PATH, command))+" "+command_args+(" < "+shlex.quote(fp.name) if fp and not use_only_filename_view_flow else "")

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
        out = output.decode("utf-8", "ignore")
        out = out.split("\n")
        if len(out) > 1 and out[3:][0].startswith("Started a new flow server: -flow is still initializing; this can take some time. [processing] \\"):
          out = out[3:]
          out[0] = out[0].replace("Started a new flow server: -flow is still initializing; this can take some time. [processing] \\", "")
          out = "\n".join(out)
          result = json.loads(out) if is_output_json else out
        elif len(out) > 1 and out[3:][0].startswith("Started a new flow server: -"):
          out = out[3:]
          out[0] = out[0].replace("Started a new flow server: -", "")
          out = "\n".join(out)
          result = json.loads(out) if is_output_json else out
        else :
          result = json.loads(output.decode("utf-8", "ignore")) if is_output_json else output.decode("utf-8", "ignore")
      else :
        result = json.loads(output.decode("utf-8", "ignore")) if is_output_json else output.decode("utf-8", "ignore")

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

  def install_all(self) :

    args = ""

    if node_variables.NODE_JS_OS == 'win':
      args = ["npm", "install"]
    else :
      args = shlex.quote(get_node_js_custom_path() or node_variables.NODE_JS_PATH_EXECUTABLE)+" "+shlex.quote(get_npm_custom_path() or node_variables.NPM_PATH_EXECUTABLE)+" install"

    os.chdir(PACKAGE_PATH)

    p = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = ""

    # check for errors
    for line in p.stderr.readlines():
      lines += codecs.decode(line, "utf-8", "ignore")

    if len(lines) > 0 :
      p.terminate()
      raise Exception(lines)

    lines = ""
    for line in p.stdout.readlines():
      lines += codecs.decode(line, "utf-8", "ignore")
    p.terminate()

    return lines.strip()

  def update_all(self, save = False) :

    args = ""

    if node_variables.NODE_JS_OS == 'win':
      args = ["npm", "update", "--save"] if save else ["npm", "update"]
    else :
      args = shlex.quote(get_node_js_custom_path() or node_variables.NODE_JS_PATH_EXECUTABLE)+" "+shlex.quote(get_npm_custom_path() or node_variables.NPM_PATH_EXECUTABLE)+" update" + (" --save" if save else "")

    os.chdir(PACKAGE_PATH)

    p = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = ""

    # check for errors
    for line in p.stderr.readlines():
      lines += codecs.decode(line, "utf-8", "ignore")

    if len(lines) > 0 :
      p.terminate()
      raise Exception(lines)

    lines = ""
    for line in p.stdout.readlines():
      lines += codecs.decode(line, "utf-8", "ignore")
    p.terminate()

    return lines.strip()

  def install(self, package_name, save = False) :

    args = ""

    if node_variables.NODE_JS_OS == 'win':
      args = ["npm", "install", "--save", package_name] if save else ["npm", "install", package_name] 
    else :
      args = shlex.quote(get_node_js_custom_path() or node_variables.NODE_JS_PATH_EXECUTABLE)+" "+shlex.quote(get_npm_custom_path() or node_variables.NPM_PATH_EXECUTABLE)+" install" + (" --save" if save else "") + " " + shlex.quote(package_name)

    os.chdir(PACKAGE_PATH)

    p = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = ""

    # check for errors
    for line in p.stderr.readlines():
      lines += codecs.decode(line, "utf-8", "ignore")

    if len(lines) > 0 :
      p.terminate()
      raise Exception(lines)

    lines = ""
    for line in p.stdout.readlines():
      lines += codecs.decode(line, "utf-8", "ignore")
    p.terminate()

    return lines.strip()

  def update(self, package_name, save = False) :

    args = ""

    if node_variables.NODE_JS_OS == 'win':
      args = ["npm", "update", "--save", package_name] if save else ["npm", "update", package_name] 
    else :
      args = shlex.quote(get_node_js_custom_path() or node_variables.NODE_JS_PATH_EXECUTABLE)+" "+shlex.quote(get_npm_custom_path() or node_variables.NPM_PATH_EXECUTABLE)+" update" + (" --save" if save else "") + " " + shlex.quote(package_name)

    os.chdir(PACKAGE_PATH)
    
    p = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = ""

    # check for errors
    for line in p.stderr.readlines():
      lines += codecs.decode(line, "utf-8", "ignore")

    if len(lines) > 0 :
      p.terminate()
      raise Exception(lines)

    lines = ""
    for line in p.stdout.readlines():
      lines += codecs.decode(line, "utf-8", "ignore")
    p.terminate()

    return lines.strip()

  def getCurrentNPMVersion(self, checking_local = False) :

    args = ""

    if node_variables.NODE_JS_OS == 'win':
      args = ["npm", "-v"]
    else :
      args = shlex.quote(get_node_js_custom_path() or node_variables.NODE_JS_PATH_EXECUTABLE if not checking_local else node_variables.NODE_JS_PATH_EXECUTABLE)+" "+shlex.quote(get_npm_custom_path() or node_variables.NPM_PATH_EXECUTABLE if not checking_local else node_variables.NPM_PATH_EXECUTABLE)+" -v"

    p = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = ""

    # check for errors
    for line in p.stderr.readlines():
      lines += codecs.decode(line, "utf-8", "ignore")

    if len(lines) > 0 :
      p.terminate()
      raise Exception(lines)

    lines = ""
    for line in p.stdout.readlines():
      lines += codecs.decode(line, "utf-8", "ignore")
    p.terminate()

    return lines.strip()