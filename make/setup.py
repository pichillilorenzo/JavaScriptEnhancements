import re, os, time, traceback

PACKAGE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

pattern = re.compile("^( *)\$\{include (\.\/)?(([\w\-]+\/)*)([\w\-]+\.[\w\-]+)\} *$", re.MULTILINE)
start_from = "make/_init.py"
code = ""
last_dir_name = ""
with open(os.path.join(PACKAGE_PATH, start_from), encoding="utf-8") as data_file :
  code = data_file.read()
  last_dir_name = os.path.abspath(os.path.dirname(os.path.join(PACKAGE_PATH, start_from)))

def compile_code(code, last_dir_name_ric, whitespace_ric) :
  lines = code.split("\n")
  code = ""
  for line in lines :
    matching = pattern.match(line)
    if matching :
      whitespace = whitespace_ric + matching.group(1)
      is_from_package_path = matching.group(2)
      path = matching.group(3)
      name = matching.group(5)
      full_path = ""
      if is_from_package_path :
        if path :
          full_path = os.path.join(PACKAGE_PATH, path[0:-1], name)
        else :
          full_path = os.path.join(PACKAGE_PATH, name)
      elif path :
        full_path = os.path.join(last_dir_name_ric, path[0:-1], name)
      else :
        full_path = os.path.join(last_dir_name_ric, name)
      
      new_last_dir_name = os.path.abspath(os.path.dirname(full_path))

      try :
        with open(full_path, encoding="utf-8") as file :
          file_code = file.read()
          code += compile_code(file_code, new_last_dir_name, whitespace)
      except Exception as e:
        print(matching.group(3))
        print(name)
        print("Line: "+line)
        print("File: "+full_path)
        print(traceback.format_exc())
    else :
      code += whitespace_ric+line+"\n" 
  return code

for x in os.listdir(PACKAGE_PATH):
  filename, extension = os.path.splitext(x)
  if extension == ".py" and filename.startswith("_generated_") :
    os.unlink(os.path.join(PACKAGE_PATH, x))
    break

file_name_compiled = "_generated_"+time.strftime("%Y_%m_%d_at_%H_%M_%S")+".py"
with open(os.path.join(PACKAGE_PATH, file_name_compiled), "w+", encoding="utf-8") as data_file :
  data_file.write(compile_code(code, last_dir_name, ""))
