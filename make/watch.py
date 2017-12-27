import os, subprocess, shlex
from datetime import datetime

PACKAGE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

class Monkey(object):
  def __init__(self):
    self.files = {}
    self.src = PACKAGE_PATH
    self.path_setup = os.path.join(PACKAGE_PATH, "make", "setup.py")

  def runrec(self,src):
    listdir = os.listdir(src)
    for x in listdir:   
      filename, extension = os.path.splitext(x)
      x = os.path.join(src, x)
      try:
        inode = os.stat(x).st_ino
        if not inode in self.files and not "_generated_" in x and os.path.isfile(x) and not "node_modules" in x and not "node_binaries" in x and not "vendor" in x and extension == ".py" and filename+extension != "setup.py" and filename+extension != "watch.py" :
          self.files[inode] = {
            "filename": x,
            "st_ctime_ns_cached": os.stat(x).st_ctime_ns,
            "st_mtime_ns_cached": os.stat(x).st_mtime_ns
          }
        if os.path.isdir(x):
          self.runrec(x)
      except FileNotFoundError as e:
        pass

  def check_change(self, file):
    try:
      st_ctime_ns = os.stat(file["filename"]).st_ctime_ns
      st_mtime_ns = os.stat(file["filename"]).st_mtime_ns  

      if st_ctime_ns != file["st_ctime_ns_cached"] or st_mtime_ns != file["st_mtime_ns_cached"]:
        print(str(datetime.now().strftime('%H:%M:%S')) + " " + file["filename"] + " changed")
        file["st_ctime_ns_cached"] = st_ctime_ns
        file["st_mtime_ns_cached"] = st_mtime_ns
        p = subprocess.Popen("python3 "+shlex.quote(self.path_setup), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        lines = ""
        for line in p.stderr.readlines():
          lines += codecs.decode(line, "utf-8", "ignore")
        if len(lines) > 0 :
          p.terminate()
          raise Exception(lines)
        p.terminate()

    except FileNotFoundError as e:
      pass

  def check_all(self):
    self.runrec(self.src)

    if len(self.files.items()) <= 0 :
      return

    for inode in self.files.keys():
      file = self.files[inode]
      self.check_change(file)

monkey = Monkey()

monkey.check_all()

while True:
  monkey.check_all()