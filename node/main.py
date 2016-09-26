import subprocess
import sys, imp, codecs, shlex, os
import node_variables

PACKAGE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

class NodeJS(object):
  def eval(self, js, eval_type="eval", strict_mode=False):

    js = ("'use strict'; " if strict_mode else "") + js
    eval_type = "--eval" if eval_type == "eval" else "--print"

    args = ""

    if node_variables.NODE_JS_OS == 'win':
      args = [node_variables.NODE_JS_PATH_EXECUTABLE, eval_type, js]
    else :
      args = shlex.quote(node_variables.NODE_JS_PATH_EXECUTABLE)+" "+shlex.quote(eval_type)+" "+shlex.quote(js)

    p = subprocess.Popen(args,  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

  def getCurrentNodeJSVersion(self) :

    args = ""

    if node_variables.NODE_JS_OS == 'win':
      args = [node_variables.NODE_JS_PATH_EXECUTABLE, "-v"]
    else :
      args = shlex.quote(node_variables.NODE_JS_PATH_EXECUTABLE)+" -v"

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
        args = [node_variables.NODE_JS_PATH_EXECUTABLE, os.path.join(node_variables.NODE_MODULES_BIN_PATH, command)] + command_args
    else :
      command_args_list = list()
      for command_arg in command_args :
        command_args_list.append(shlex.quote(command_arg))
      command_args = " ".join(command_args_list)
      args = shlex.quote(node_variables.NODE_JS_PATH_EXECUTABLE)+" "+shlex.quote(os.path.join(node_variables.NODE_MODULES_BIN_PATH, command))+" "+command_args

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
      args = shlex.quote(node_variables.NODE_JS_PATH_EXECUTABLE)+" "+shlex.quote(node_variables.NPM_PATH_EXECUTABLE)+" install"

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

  def update_all(self) :

    args = ""

    if node_variables.NODE_JS_OS == 'win':
      args = ["npm", "update", "--save"]
    else :
      args = shlex.quote(node_variables.NODE_JS_PATH_EXECUTABLE)+" "+shlex.quote(node_variables.NPM_PATH_EXECUTABLE)+" update --save"

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

  def install(self, package_name) :

    args = ""

    if node_variables.NODE_JS_OS == 'win':
      args = ["npm", "install", "--save", package_name]
    else :
      args = shlex.quote(node_variables.NODE_JS_PATH_EXECUTABLE)+" "+shlex.quote(node_variables.NPM_PATH_EXECUTABLE)+" install --save "+shlex.quote(package_name)

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

  def update(self, package_name) :

    args = ""

    if node_variables.NODE_JS_OS == 'win':
      args = ["npm", "update", "--save", package_name]
    else :
      args = shlex.quote(node_variables.NODE_JS_PATH_EXECUTABLE)+" "+shlex.quote(node_variables.NPM_PATH_EXECUTABLE)+" update --save "+shlex.quote(package_name)

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

  def getCurrentNPMVersion(self) :

    args = ""

    if node_variables.NODE_JS_OS == 'win':
      args = ["npm", "-v"]
    else :
      args = shlex.quote(node_variables.NODE_JS_PATH_EXECUTABLE)+" "+shlex.quote(node_variables.NPM_PATH_EXECUTABLE)+" -v"

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