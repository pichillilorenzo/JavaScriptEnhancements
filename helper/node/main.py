import subprocess, threading
import sys, imp, codecs, shlex, os, json, traceback, tempfile

${include node_variables.py}

def get_node_js_custom_path():
  json_file = Util.open_json(os.path.join(PACKAGE_PATH,  "settings.sublime-settings"))
  if json_file and "node_js_custom_path" in json_file :
    return json_file.get("node_js_custom_path").strip()
  return ""

def get_npm_custom_path():
  json_file = Util.open_json(os.path.join(PACKAGE_PATH,  "settings.sublime-settings"))
  if json_file and "npm_custom_path" in json_file :
    return json_file.get("npm_custom_path").strip()
  return ""

class NodeJS(object):
  def __init__(self, check_local = False):
    self.check_local = check_local

  def eval(self, js, eval_type="eval", strict_mode=False):

    node_js_path = ""

    if self.check_local :
      settings = get_project_settings()
      if settings :
        node_js_path = settings["project_settings"]["node_js_custom_path"] or get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
      else :
        node_js_path = get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
    else :
      node_js_path = NODE_JS_PATH_EXECUTABLE

    js = ("'use strict'; " if strict_mode else "") + js
    eval_type = "--eval" if eval_type == "eval" else "--print"

    args = ""

    if NODE_JS_OS == 'win':
      args = [node_js_path, eval_type, js]
    else :
      args = shlex.quote(node_js_path)+" "+shlex.quote(eval_type)+" "+shlex.quote(js)

    p = subprocess.Popen(args, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    lines_output = ""
    lines_error = ""

    for line in p.stdout.readlines():
      line = codecs.decode(line, "utf-8", "ignore").strip()
      if line :
        lines_output += line + ( b"\n" if type(line) is bytes else "\n" ) 

    for line in p.stderr.readlines():
      line = codecs.decode(line, "utf-8", "ignore").strip()
      if line :
        lines_error += line + ( b"\n" if type(line) is bytes else "\n" ) 

    if len(lines_error) > 0 :
      p.terminate()
      raise Exception(lines_error)

    lines = lines_output

    p.terminate()

    return lines

  def getCurrentNodeJSVersion(self) :

    node_js_path = ""

    if self.check_local :
      settings = get_project_settings()
      if settings :
        node_js_path = settings["project_settings"]["node_js_custom_path"] or get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
      else :
        node_js_path = get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
    else :
      node_js_path = NODE_JS_PATH_EXECUTABLE

    args = ""

    if NODE_JS_OS == 'win':
      args = [node_js_path, "-v"]
    else :
      args = shlex.quote(node_js_path)+" -v"

    p = subprocess.Popen(args, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    lines_output = ""
    lines_error = ""

    for line in p.stdout.readlines():
      line = codecs.decode(line, "utf-8", "ignore").strip()
      if line :
        lines_output += line + ( b"\n" if type(line) is bytes else "\n" ) 

    for line in p.stderr.readlines():
      line = codecs.decode(line, "utf-8", "ignore").strip()
      if line :
        lines_error += line + ( b"\n" if type(line) is bytes else "\n" ) 

    if len(lines_error) > 0 :
      p.terminate()
      raise Exception(lines_error)

    lines = lines_output.strip()

    p.terminate()

    return lines

  def execute(self, command, command_args, is_from_bin=False, chdir="", wait_terminate=True, func_stdout=None, args_func_stdout=[], bin_path="") :

    node_js_path = ""

    if self.check_local :
      settings = get_project_settings()
      if settings :
        node_js_path = settings["project_settings"]["node_js_custom_path"] or get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
      else :
        node_js_path = get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
    else :
      node_js_path = NODE_JS_PATH_EXECUTABLE

    if NODE_JS_OS == 'win':
      if is_from_bin :
        args = [os.path.join( (bin_path or NODE_MODULES_BIN_PATH), command+".cmd")] + command_args
      else :
        args = [node_js_path, os.path.join( (bin_path or NODE_MODULES_BIN_PATH), command)] + command_args
    else :
      command_args_list = list()
      for command_arg in command_args :
        command_args_list.append(shlex.quote(command_arg))
      command_args = " ".join(command_args_list)
      args = shlex.quote(node_js_path)+" "+shlex.quote(os.path.join( (bin_path or NODE_MODULES_BIN_PATH), command))+" "+command_args
    
    print(args)
    
    #owd = os.getcwd()
    if chdir :
      os.chdir(chdir)

    if wait_terminate :

      p = subprocess.Popen(args, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

      # if chdir:
      #   os.chdir(owd)

      lines_output = ""
      lines_error = ""
      no_error = True

      for line in p.stdout.readlines():
        line = codecs.decode(line, "utf-8", "ignore").strip()
        if line :
          lines_output += line + ( b"\n" if type(line) is bytes else "\n" ) 

      for line in p.stderr.readlines():
        line = codecs.decode(line, "utf-8", "ignore").strip()
        if line :
          lines_error += line + ( b"\n" if type(line) is bytes else "\n" ) 

      if len(lines_error) > 0 :
        no_error = False

      lines = lines_output + ( b"\n" if type(lines_output) is bytes else "\n" )  + lines_error

      p.terminate()

      return [no_error, lines]

    elif not wait_terminate and func_stdout :

      Util.create_and_start_thread(self.wrapper_func_stdout, "", (args, func_stdout, args_func_stdout))
      
  def wrapper_func_stdout(self, args, func_stdout, args_func_stdout=[]):
    with subprocess.Popen(args, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1) as p:

      func_stdout(None, p, *args_func_stdout)
      flag_error = False
      
      for line in p.stdout:
        line = codecs.decode(line, "utf-8", "ignore")
        func_stdout(line, p, *args_func_stdout)

      for line in p.stderr:
        line = codecs.decode(line, "utf-8", "ignore")
        if len(line.strip()) > 0 and not line.strip().startswith( b"npm WARN" if type(line) is bytes else "npm WARN" ) and not flag_error:
          flag_error = True  
        func_stdout(line, p, *args_func_stdout)

      if not flag_error:
        func_stdout("OUTPUT-SUCCESS", p, *args_func_stdout)
      else :
        func_stdout("OUTPUT-ERROR", p, *args_func_stdout)

      func_stdout("OUTPUT-DONE", p, *args_func_stdout)
      
  def execute_check_output(self, command, command_args, is_from_bin=False, use_fp_temp=False, use_only_filename_view_flow=False, fp_temp_contents="", is_output_json=False, chdir="", clean_output_flow=False) :

    node_js_path = ""

    if self.check_local :
      settings = get_project_settings()
      if settings :
        node_js_path = settings["project_settings"]["node_js_custom_path"] or get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
      else :
        node_js_path = get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
    else :
      node_js_path = NODE_JS_PATH_EXECUTABLE

    fp = None
    if use_fp_temp :
      
      fp = tempfile.NamedTemporaryFile()
      fp.write(str.encode(fp_temp_contents))
      fp.flush()

    if NODE_JS_OS == 'win':
      if is_from_bin :
        args = [os.path.join(NODE_MODULES_BIN_PATH, command+".cmd")] + command_args
      else :
        args = [node_js_path, os.path.join(NODE_MODULES_BIN_PATH, command)] + command_args
      if fp :
        args += ["<", fp.name]
    else :
      command_args_list = list()
      for command_arg in command_args :
        command_args_list.append(shlex.quote(command_arg))
      command_args = " ".join(command_args_list)
      args = shlex.quote(node_js_path)+" "+shlex.quote(os.path.join(NODE_MODULES_BIN_PATH, command))+" "+command_args+(" < "+shlex.quote(fp.name) if fp and not use_only_filename_view_flow else "")

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
          print(output.decode("utf-8", "ignore"))
          return [False, {}]

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
  def __init__(self, check_local = False):
    self.check_local = check_local

  def install_all(self, save = False, chdir="") :

    node_js_path = ""
    npm_path = ""

    if self.check_local :
      settings = get_project_settings()
      if settings :
        node_js_path = settings["project_settings"]["node_js_custom_path"] or get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
        npm_path = settings["project_settings"]["npm_custom_path"] or get_npm_custom_path() or NPM_PATH_EXECUTABLE
      else :
        node_js_path = get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
        npm_path = get_npm_custom_path() or NPM_PATH_EXECUTABLE
    else :
      node_js_path = NODE_JS_PATH_EXECUTABLE
      npm_path = NPM_PATH_EXECUTABLE

    args = ""

    if NODE_JS_OS == 'win':
      args = [npm_path, "install", "--save"] if save else [npm_path, "install"]
    else :
      args = shlex.quote(node_js_path)+" "+shlex.quote(npm_path)+" install" + (" --save" if save else "")

    if chdir :
      os.chdir(chdir)
    else :
      os.chdir(PACKAGE_PATH)

    p = subprocess.Popen(args, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    lines_output = ""
    lines_error = ""

    for line in p.stdout.readlines():
      line = codecs.decode(line, "utf-8", "ignore").strip()
      if line :
        lines_output += line + ( b"\n" if type(line) is bytes else "\n" ) 

    for line in p.stderr.readlines():
      line = codecs.decode(line, "utf-8", "ignore").strip()
      if line :
        if not line.startswith( b"npm WARN" if type(line) is bytes else "npm WARN" ) :
          lines_error += line + ( b"\n" if type(line) is bytes else "\n" ) 
        else :
          lines_output += line + ( b"\n" if type(line) is bytes else "\n" ) 

    if len(lines_error) > 0 :
      p.terminate()
      raise Exception(lines_error)

    lines = lines_output

    p.terminate()

    return lines

  def update_all(self, save = False, chdir="") :

    node_js_path = ""
    npm_path = ""

    if self.check_local :
      settings = get_project_settings()
      if settings :
        node_js_path = settings["project_settings"]["node_js_custom_path"] or get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
        npm_path = settings["project_settings"]["npm_custom_path"] or get_npm_custom_path() or NPM_PATH_EXECUTABLE
      else :
        node_js_path = get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
        npm_path = get_npm_custom_path() or NPM_PATH_EXECUTABLE
    else :
      node_js_path = NODE_JS_PATH_EXECUTABLE
      npm_path = NPM_PATH_EXECUTABLE

    args = ""

    if NODE_JS_OS == 'win':
      args = [npm_path, "update", "--save"] if save else [npm_path, "update"]
    else :
      args = shlex.quote(node_js_path)+" "+shlex.quote(npm_path)+" update" + (" --save" if save else "")

    if chdir :
      os.chdir(chdir)
    else :
      os.chdir(PACKAGE_PATH)

    p = subprocess.Popen(args, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    lines_output = ""
    lines_error = ""

    for line in p.stdout.readlines():
      line = codecs.decode(line, "utf-8", "ignore").strip()
      if line :
        lines_output += line + ( b"\n" if type(line) is bytes else "\n" ) 

    for line in p.stderr.readlines():
      line = codecs.decode(line, "utf-8", "ignore").strip()
      if line :
        if not line.startswith( b"npm WARN" if type(line) is bytes else "npm WARN" ) :
          lines_error += line + ( b"\n" if type(line) is bytes else "\n" ) 
        else :
          lines_output += line + ( b"\n" if type(line) is bytes else "\n" ) 

    if len(lines_error) > 0 :
      p.terminate()
      raise Exception(lines_error)

    lines = lines_output

    p.terminate()

    return lines

  def install(self, package_name, save = False, chdir="") :

    node_js_path = ""
    npm_path = ""

    if self.check_local :
      settings = get_project_settings()
      if settings :
        node_js_path = settings["project_settings"]["node_js_custom_path"] or get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
        npm_path = settings["project_settings"]["npm_custom_path"] or get_npm_custom_path() or NPM_PATH_EXECUTABLE
      else :
        node_js_path = get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
        npm_path = get_npm_custom_path() or NPM_PATH_EXECUTABLE
    else :
      node_js_path = NODE_JS_PATH_EXECUTABLE
      npm_path = NPM_PATH_EXECUTABLE

    args = ""

    if NODE_JS_OS == 'win':
      args = [npm_path, "install", "--save", package_name] if save else [npm_path, "install", package_name] 
    else :
      args = shlex.quote(node_js_path)+" "+shlex.quote(npm_path)+" install" + (" --save" if save else "") + " " + shlex.quote(package_name)

    if chdir :
      os.chdir(chdir)
    else :
      os.chdir(PACKAGE_PATH)

    p = subprocess.Popen(args, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    lines_output = ""
    lines_error = ""

    for line in p.stdout.readlines():
      line = codecs.decode(line, "utf-8", "ignore").strip()
      if line :
        lines_output += line + ( b"\n" if type(line) is bytes else "\n" ) 

    for line in p.stderr.readlines():
      line = codecs.decode(line, "utf-8", "ignore").strip()
      if line :
        if not line.startswith( b"npm WARN" if type(line) is bytes else "npm WARN" ) :
          lines_error += line + ( b"\n" if type(line) is bytes else "\n" ) 
        else :
          lines_output += line + ( b"\n" if type(line) is bytes else "\n" ) 

    if len(lines_error) > 0 :
      p.terminate()
      raise Exception(lines_error)

    lines = lines_output

    p.terminate()

    return lines

  def update(self, package_name, save = False, chdir="") :

    node_js_path = ""
    npm_path = ""

    if self.check_local :
      settings = get_project_settings()
      if settings :
        node_js_path = settings["project_settings"]["node_js_custom_path"] or get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
        npm_path = settings["project_settings"]["npm_custom_path"] or get_npm_custom_path() or NPM_PATH_EXECUTABLE
      else :
        node_js_path = get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
        npm_path = get_npm_custom_path() or NPM_PATH_EXECUTABLE
    else :
      node_js_path = NODE_JS_PATH_EXECUTABLE
      npm_path = NPM_PATH_EXECUTABLE

    args = ""

    if NODE_JS_OS == 'win':
      args = [npm_path, "update", "--save", package_name] if save else [npm_path, "update", package_name] 
    else :
      args = shlex.quote(node_js_path)+" "+shlex.quote(npm_path)+" update" + (" --save" if save else "") + " " + shlex.quote(package_name)

    if chdir :
      os.chdir(chdir)
    else :
      os.chdir(PACKAGE_PATH)
    
    p = subprocess.Popen(args, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    lines_output = ""
    lines_error = ""

    for line in p.stdout.readlines():
      line = codecs.decode(line, "utf-8", "ignore").strip()
      if line :
        lines_output += line + ( b"\n" if type(line) is bytes else "\n" ) 

    for line in p.stderr.readlines():
      line = codecs.decode(line, "utf-8", "ignore").strip()
      if line :
        if not line.startswith( b"npm WARN" if type(line) is bytes else "npm WARN" ) :
          lines_error += line + ( b"\n" if type(line) is bytes else "\n" ) 
        else :
          lines_output += line + ( b"\n" if type(line) is bytes else "\n" ) 

    if len(lines_error) > 0 :
      p.terminate()
      raise Exception(lines_error)

    lines = lines_output

    p.terminate()

    return lines

  def getCurrentNPMVersion(self) :

    node_js_path = ""
    npm_path = ""
    
    if self.check_local :
      settings = get_project_settings()
      if settings :
        node_js_path = settings["project_settings"]["node_js_custom_path"] or get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
        npm_path = settings["project_settings"]["npm_custom_path"] or get_npm_custom_path() or NPM_PATH_EXECUTABLE
      else :
        node_js_path = get_node_js_custom_path() or NODE_JS_PATH_EXECUTABLE
        npm_path = get_npm_custom_path() or NPM_PATH_EXECUTABLE
    else :
      node_js_path = NODE_JS_PATH_EXECUTABLE
      npm_path = NPM_PATH_EXECUTABLE

    args = ""

    if NODE_JS_OS == 'win':
      args = [npm_path, "-v"]
    else :
      args = shlex.quote(node_js_path)+" "+shlex.quote(npm_path)+" -v"

    p = subprocess.Popen(args, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    lines_output = ""
    lines_error = ""

    for line in p.stdout.readlines():
      line = codecs.decode(line, "utf-8", "ignore").strip()
      if line :
        lines_output += line + ( b"\n" if type(line) is bytes else "\n" ) 

    for line in p.stderr.readlines():
      line = codecs.decode(line, "utf-8", "ignore").strip()
      if line :
        if not line.startswith( b"npm WARN" if type(line) is bytes else "npm WARN" ) :
          lines_error += line + ( b"\n" if type(line) is bytes else "\n" )

    if len(lines_error) > 0 :
      p.terminate()
      raise Exception(lines_error)

    lines = lines_output.strip()

    p.terminate()

    return lines

${include NodeJSInstaller.py}