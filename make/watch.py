import os, subprocess, shlex

PACKAGE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

class Monkey(object):
  def __init__(self):
    self.files = []
    self.src = PACKAGE_PATH
    self.path_setup = os.path.join(PACKAGE_PATH, "make", "setup.py")

  def runrec(self,src):
    for x in os.listdir(src):
      filename, extension = os.path.splitext(x)
      x = os.path.join(src, x)
      if os.path.isfile(x) and extension == ".py" and filename+extension != "setup.py" and filename+extension != "watch.py" :
        self.files.append({
          "filename": x,
          "st_ctime_ns_cached": os.stat(x).st_ctime_ns,
          "st_mtime_ns_cached": os.stat(x).st_mtime_ns
        })
      if os.path.isdir(x):
        self.runrec(x)

  def check_change(self, index):
    if len(self.files) <= 0 :
      return

    file = self.files[index]
    st_ctime_ns = os.stat(file["filename"]).st_ctime_ns
    st_mtime_ns = os.stat(file["filename"]).st_mtime_ns
    if st_ctime_ns != file["st_ctime_ns_cached"] or st_mtime_ns != file["st_mtime_ns_cached"]:
      print(file["filename"] + " changed")
      p = subprocess.Popen("python3 "+shlex.quote(self.path_setup), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      lines = ""
      for line in p.stderr.readlines():
        lines += codecs.decode(line, "utf-8", "ignore")
      if len(lines) > 0 :
        p.terminate()
        raise Exception(lines)
      p.terminate()

  def check_all(self):
    self.files = []
    self.runrec(self.src)
    for index, file in enumerate(self.files):
      self.check_change(index)

monkey = Monkey()

while True:
  monkey.check_all()