import subprocess
import sys, imp, codecs, shlex, os, json
import node_variables

PACKAGE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

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

  def execute(self, command, command_args, is_from_bin=False) :

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

    p = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = ""

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

  def update(self, package_name, save) :

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