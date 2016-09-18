import subprocess
import sys, imp, codecs, shlex
import node_variables

class NodeJS(object):
  def eval(self, js, eval_type="eval", strict_mode=False):

    js = ("'use strict'; " if strict_mode else "") + js
    eval_type = "--eval" if eval_type == "eval" else "--print"

    p = subprocess.Popen(shlex.quote(node_variables.NODE_JS_PATH_EXECUTABLE)+" "+shlex.quote(eval_type)+" "+shlex.quote(js), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = ""

    # check for errors
    for line in p.stderr.readlines():
      lines += codecs.decode(line)

    if len(lines) > 0 :
      p.terminate()
      raise Exception(lines)

    lines = ""
    for line in p.stdout.readlines():
      lines += codecs.decode(line)
    p.terminate()
    
    return lines

  def getCurrentNodeJSVersion(self) :

    p = subprocess.Popen(shlex.quote(node_variables.NODE_JS_PATH_EXECUTABLE)+" -v", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = ""

    # check for errors
    for line in p.stderr.readlines():
      lines += codecs.decode(line)

    if len(lines) > 0 :
      p.terminate()
      raise Exception(lines)

    lines = ""
    for line in p.stdout.readlines():
      lines += codecs.decode(line)
    p.terminate()
    
    return lines.strip()