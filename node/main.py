import subprocess
import sys, imp, codecs, shlex
import node_variables

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
