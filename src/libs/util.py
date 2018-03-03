import sublime, sublime_plugin
import re, urllib, shutil, traceback, threading, time, os, hashlib, json, multiprocessing, shlex, subprocess, codecs, collections
from .global_vars import *
from .javascript_enhancements_settings import *

multiprocessing_list = []

def download_and_save(url, destination_path) :
  if destination_path :
    try :
      request = urllib.request.Request(url)
      request.add_header('User-agent', r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1')
      with urllib.request.urlopen(request) as response :
        with open(destination_path, 'wb+') as out_file :
          shutil.copyfileobj(response, out_file)
          return True
    except Exception as e:
      traceback.print_exc()
  return False

def open_json(path):
  with open(path, encoding="utf-8") as json_file :    
    try :
      return json.load(json_file)
    except Exception as e :
      print("Error: "+traceback.format_exc())
  return None

def check_thread_is_alive(thread_name) :
  for thread in threading.enumerate() :
    if thread.getName() == thread_name and thread.is_alive() :
      return True
  return False

def create_and_start_thread(target, thread_name="", args=[], kwargs={}, daemon=True) :
  if not check_thread_is_alive(thread_name) :
    thread = threading.Thread(target=target, name=thread_name, args=args, kwargs=kwargs, daemon=daemon)
    thread.start()
    return thread
  return None

def check_process_is_alive(process_name) :
  global multiprocessing_list
  for process in multiprocessing_list :
    if process.name == process_name :
      if process.is_alive() :
        return True
      else :
        multiprocessing_list.remove(process)
  return False

def create_and_start_process(target, process_name="", args=[], kwargs={}, daemon=True) :
  global multiprocessing_list
  if not check_process_is_alive(process_name) :
    process = multiprocessing.Process(target=target, name=process_name, args=args, kwargs=kwargs, daemon=daemon)
    process.start()
    multiprocessing_list.append(process)
    return process
  return None

def set_timeout(time, func):
  timer = threading.Timer(time, func)
  timer.start()
  return timer

def checksum_sha1(fname):
  hash_sha1 = hashlib.sha1()
  with open(fname, "rb") as f:
    for chunk in iter(lambda: f.read(4096), b""):
      hash_sha1.update(chunk)
  return hash_sha1.hexdigest()

def checksum_sha1_equalcompare(fname1, fname2):
  return checksum_sha1(fname1) == checksum_sha1(fname2)

def split_string_and_find(string_to_split, search_value, split_delimiter=" ") :
  string_splitted = string_to_split.split(split_delimiter)
  return index_of(string_splitted, search_value) 

def split_string_and_find_on_multiple(string_to_split, search_values, split_delimiter=" ") :
  string_splitted = string_to_split.split(split_delimiter)
  for search_value in search_values :
    index = index_of(string_splitted, search_value) 
    if index >= 0 :
      return index
  return -1

def split_string_and_findLast(string_to_split, search_value, split_delimiter=" ") :
  string_splitted = string_to_split.split(split_delimiter)
  return last_index_of(string_splitted, search_value) 

def index_of(list_to_search, search_value) :
  index = -1
  try :
    index = list_to_search.index(search_value)
  except Exception as e:
    pass
  return index

def last_index_of(list_to_search, search_value) :
  index = -1
  list_to_search_reversed = reversed(list_to_search)
  list_length = len(list_to_search)
  try :
    index = next(i for i,v in zip(range(list_length-1, 0, -1), list_to_search_reversed) if v == search_value)
  except Exception as e:
    pass
  return index

def first_index_of_multiple(list_to_search, search_values) :
  index = -1
  string = ""
  for search_value in search_values :
    index_search = index_of(list_to_search, search_value)
    if index_search >= 0 and index == -1 :
      index = index_search
      string = search_value
    elif index_search >= 0 :
      index = min(index, index_search)
      string = search_value
  return {
    "index": index,
    "string": string
  }

def find_and_get_pre_string_and_first_match(string, search_value) :
  result = None
  index = index_of(string, search_value)
  if index >= 0 :
    result = string[:index+len(search_value)]
  return result

def find_and_get_pre_string_and_matches(string, search_value) :
  result = None
  index = index_of(string, search_value)
  if index >= 0 :
    result = string[:index+len(search_value)]
    string = string[index+len(search_value):]
    count_occ = string.count(search_value)
    i = 0
    while i < count_occ :
      result += " "+search_value
      i = i + 1
  return result

def get_region_scope_first_match(view, scope, selection, selector) :
  scope = find_and_get_pre_string_and_first_match(scope, selector)
  if scope :
    for region in view.find_by_selector(scope) :
      if region.contains(selection) or region.intersects(selection):
        sel = sublime.Region(region.begin(), region.begin())
        return {
          "scope": scope,
          "region": region,
          "region_string": view.substr(region),
          "region_string_stripped": view.substr(region).strip(),
          "selection": sel
        }
  return None

def get_region_scope_last_match(view, scope, selection, selector) :
  scope = find_and_get_pre_string_and_matches(scope, selector)
  if scope :
    for region in view.find_by_selector(scope) :
      if region.contains(selection) or region.intersects(selection):
        sel = sublime.Region(region.begin(), region.begin())
        return {
          "scope": scope,
          "region": region,
          "region_string": view.substr(region),
          "region_string_stripped": view.substr(region).strip(),
          "selection": sel
        }
  return None

def find_regions_on_same_depth_level(view, scope, selection, selectors, depth_level, forward) :
  scope_splitted = scope.split(" ")
  regions = list()
  add_unit = 1 if forward else -1
  if len(scope_splitted) >= depth_level :  
    for selector in selectors :
      while index_of(scope_splitted, selector) == -1 :
        if selection.a == 0 or len(scope_splitted) < depth_level:
          return list()
        selection = sublime.Region(selection.a + add_unit, selection.a + add_unit )
        scope = view.scope_name(selection.begin()).strip()
        scope_splitted = scope.split(" ")
      region = view.extract_scope(selection.begin())
      regions.append({
        "scope": scope,
        "region": region,
        "region_string": view.substr(region),
        "region_string_stripped": view.substr(region).strip(),
        "selection": selection
      })
  return regions

def get_current_region_scope(view, selection) :
  scope = view.scope_name(selection.begin()).strip()
  for region in view.find_by_selector(scope) :
    if region.contains(selection):
        sel = sublime.Region(region.begin(), region.begin())
        return {
          "scope": scope,
          "region": region,
          "region_string": view.substr(region),
          "region_string_stripped": view.substr(region).strip(),
          "selection": sel
        }
  return None

def get_parent_region_scope(view, selection) :
  scope = view.scope_name(selection.begin()).strip()
  scope = " ".join(scope.split(" ")[:-1])
  for region in view.find_by_selector(scope) :
    if region.contains(selection):
        sel = sublime.Region(region.begin(), region.begin())
        return {
          "scope": scope,
          "region": region,
          "region_string": view.substr(region),
          "region_string_stripped": view.substr(region).strip(),
          "selection": sel
        }
  return None

def get_specified_parent_region_scope(view, selection, parent) :
  scope = view.scope_name(selection.begin()).strip()
  scope = scope.split(" ")
  index_parent = last_index_of(scope, parent)
  scope = " ".join(scope[:index_parent+1])
  for region in view.find_by_selector(scope) :
    if region.contains(selection):
        sel = sublime.Region(region.begin(), region.begin())
        return {
          "scope": scope,
          "region": region,
          "region_string": view.substr(region),
          "region_string_stripped": view.substr(region).strip(),
          "selection": sel
        }
  return None

def region_contains_scope(view, region, scope) :
  for region_scope in view.find_by_selector(scope) :
    if region.contains(region_scope):
      return True
  return False

def cover_regions(regions) :
  first_region = regions[0]
  other_regions = regions[1:]
  for region in other_regions :
    first_region = first_region.cover(region)
  return first_region

def rowcol_to_region(view, row, endrow, col, endcol):
  start = view.text_point(row, col)
  end = view.text_point(endrow, endcol)
  return sublime.Region(start, end)

def trim_region(view, region):
  new_region = sublime.Region(region.begin(), region.end())
  while(view.substr(new_region).startswith(" ") or view.substr(new_region).startswith("\n")):
    new_region.a = new_region.a + 1
  while(view.substr(new_region).endswith(" ") or view.substr(new_region).startswith("\n")):
    new_region.b = new_region.b - 1
  return new_region

def prev_line_is_empty(view, region):
  return view.substr(view.line(view.line(region.begin()).begin()-1)).strip() == ""

def next_line_is_empty(view, region):
  return view.substr(view.line(view.line(region.end()).end()+1)).strip() == ""

def selection_in_js_scope(view, point = -1, except_for = ""):
  try :

    sel_begin = view.sel()[0].begin() if point == -1 else point

    return view.match_selector(
      sel_begin,
      'source.js ' + except_for
    ) or view.match_selector(
      sel_begin,
      'source.js.embedded.html ' + except_for
    )

  except IndexError as e:
    return False   

def replace_with_tab(view, region, pre="", after="", add_to_each_line_before="", add_to_each_line_after="", lstrip=False) :
  lines = view.substr(region).splitlines()
  body = list()
  empty_line = 0
  for line in lines :
    if line.strip() == "" :
      empty_line = empty_line + 1
      if empty_line == 2 :
        empty_line = 1 # leave at least one empty line
        continue
    else :
      empty_line = 0
    line = "\t" + add_to_each_line_before + (line.lstrip() if lstrip else line) + add_to_each_line_after
    body.append(line)
  if body[len(body)-1].strip() == "" :
    del body[len(body)-1]
  body = "\n".join(body)
  return pre+body+after

def replace_without_tab(view, region, pre="", after="", add_to_each_line_before="", add_to_each_line_after="", lstrip=False) :
  lines = view.substr(region).split("\n")
  body = list()
  empty_line = 0
  for line in lines :
    if line.strip() == "" :
      empty_line = empty_line + 1
      if empty_line == 2 :
        empty_line = 1 # leave at least one empty line
        continue
    else :
      empty_line = 0
    body.append(add_to_each_line_before + (line.lstrip() if lstrip else line) + add_to_each_line_after)
  if body[len(body)-1].strip() == "" :
    del body[len(body)-1]
  body = "\n".join(body)
  return pre+body+after

def get_whitespace_from_line_begin(view, region) :
  n_space = len(view.substr(view.line(region.begin()))) - len(view.substr(view.line(region.begin())).lstrip())
  return " " * n_space

def add_whitespace_indentation(view, region, string, replace="\t", add_whitespace_end=True) :
  whitespace = get_whitespace_from_line_begin(view, region)
  if replace == "\n" :
    lines = string.split("\n")
    lines = [whitespace+line for line in lines]
    lines[0] = lines[0].lstrip()
    string = "\n".join(lines)
    return string
  if add_whitespace_end :
    lines = string.split("\n")
    lines[len(lines)-1] = whitespace + lines[-1:][0]
  string = "\n".join(lines)
  string = re.sub("(["+replace+"]+)", whitespace+r"\1", string)
  return string

def convert_tabs_using_tab_size(view, string):
  tab_size = view.settings().get("tab_size")
  
  if tab_size:
    return string.replace("\t", " "*tab_size)

  return string.replace("\t", " ")

def go_to_centered(view, row, col):
  while view.is_loading() :
    time.sleep(.1)
  point = view.text_point(row, col)
  view.sel().clear()
  view.sel().add(point)
  view.show_at_center(point)

def wait_view(view, fun):
  while view.is_loading() :
    time.sleep(.1)
  fun()

def move_content_to_parent_folder(path):
  for filename in os.listdir(path):
    shutil.move(os.path.join(path, filename), os.path.dirname(path)) 
  os.rmdir(path)

def merge_dicts(*dict_args):
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def removeItemIfExists(arr, item):
  if item in arr: arr.remove(item)

def getListItemIfExists(arr, item):
  if item in arr : 
    return item
  return None

def delItemIfExists(obj, key):
  try :
    del obj[key]
  except KeyError as e:
    pass

def getDictItemIfExists(obj, key):
  try :
    return obj[key]
  except KeyError as e:
    pass
  return None

def create_and_show_panel(output_panel_name, window=None, syntax="", read_only=False, return_if_exists=False, unlisted=False):
  window = sublime.active_window() if not window else window
  panel = None

  if return_if_exists:
    panel = window.find_output_panel(output_panel_name)

  if not panel:
    panel = window.create_output_panel(output_panel_name, unlisted)
    panel.set_read_only(read_only)
    if syntax :
      panel.set_syntax_file(syntax)
    window.run_command("show_panel", {"panel": "output."+output_panel_name})

  return panel

def split_path(path):
  return os.path.normpath(path).split(os.path.sep)

def convert_path_to_unix(path):
  return "/".join(split_path(path))

def execute(command, command_args, chdir="", wait_terminate=True, func_stdout=None, args_func_stdout=[]) :

  debug_mode = javaScriptEnhancements.get("debug_mode")
  
  if sublime.platform() == 'windows':
    args = [command] + command_args
  else :
    command_args_list = list()
    for command_arg in command_args :
      command_args_list.append(shlex.quote(command_arg))
    command_args = " ".join(command_args_list)
    args = shlex.quote(command)+" "+command_args
  
  if debug_mode:
    print(args)

  if wait_terminate :

    env = os.environ.copy()
    env["PATH"] = env["PATH"] + javaScriptEnhancements.get("PATH")
    shell = None if sublime.platform() == 'windows' else '/bin/bash'

    with subprocess.Popen(args, shell=True, executable=shell, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=(None if not chdir else chdir)) as p:

      lines_output = []
      lines_error = []

      thread_output = create_and_start_thread(_wrapper_func_stdout_listen_output, "", (p, None, [], lines_output))

      thread_error = create_and_start_thread(_wrapper_func_stdout_listen_error, "", (p, None, [], lines_error))

      if thread_output:
        thread_output.join()

      if thread_error:
        thread_error.join()

      lines = "\n".join(lines_output) + "\n" + "\n".join(lines_error)

      return [True if p.wait() == 0 else False, lines]

  elif not wait_terminate and func_stdout :

    return create_and_start_thread(_wrapper_func_stdout, "", (args, func_stdout, args_func_stdout, chdir))

def _wrapper_func_stdout(args, func_stdout, args_func_stdout=[], chdir=""):

  env = os.environ.copy()
  env["PATH"] = env["PATH"] + javaScriptEnhancements.get("PATH")
  shell = None if sublime.platform() == 'windows' else '/bin/bash'

  with subprocess.Popen(args, shell=True, executable=shell, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, preexec_fn=os.setsid, cwd=(None if not chdir else chdir)) as p:

    func_stdout(None, p, *args_func_stdout)
    
    thread_output = create_and_start_thread(_wrapper_func_stdout_listen_output, "", (p, func_stdout, args_func_stdout))

    thread_error = create_and_start_thread(_wrapper_func_stdout_listen_error, "", (p, func_stdout, args_func_stdout))

    if thread_output:
      thread_output.join()
      
    if thread_error:
      thread_error.join()

    if p.wait() == 0:
      func_stdout("OUTPUT-SUCCESS", p, *args_func_stdout)
    else :
      func_stdout("OUTPUT-ERROR", p, *args_func_stdout)

    func_stdout("OUTPUT-DONE", p, *args_func_stdout)

def _wrapper_func_stdout_listen_output(process, func_stdout=None, args_func_stdout=[], lines_output=[]):

  char = b""
  line = b""

  while True :
    char = process.stdout.read(1)
    if not char :
      break
    if not char.endswith(b'\n') :
      line = line + char
    else :
      line = line + char
      line = codecs.decode(line, "utf-8", "ignore").strip()
      line = re.sub(r'\x1b(\[.*?[@-~]|\].*?(\x07|\x1b\\))', '', line)
      line = re.sub(r'[\n\r]', '\n', line)
      lines_output.append(line)
      line = line + ( b"\n" if type(line) is bytes else "\n" ) 
      if func_stdout :
        func_stdout(line, process, *args_func_stdout)
      line = b""
    char = b""

def _wrapper_func_stdout_listen_error(process, func_stdout=None, args_func_stdout=[], lines_error=[]):

  char = b""
  line = b""

  while True :
    char = process.stderr.read(1)
    if not char :
      break
    if not char.endswith(b'\n') :
      line = line + char
    else :
      line = line + char
      line = codecs.decode(line, "utf-8", "ignore").strip()
      line = re.sub(r'\x1b(\[.*?[@-~]|\].*?(\x07|\x1b\\))', '', line)
      line = re.sub(r'[\n\r]', '\n', line)
      lines_error.append(line)
      line = line + ( b"\n" if type(line) is bytes else "\n" ) 
      if func_stdout :
        func_stdout(line, process, *args_func_stdout)
      line = b""
    char = b""

def nested_lookup(key, values, document, wild=False, return_parent=False):
    """Lookup a key in a nested document, return a list of values"""
    return list(_nested_lookup(key, values, document, wild=wild, return_parent=return_parent))

def _nested_lookup(key, values, document, wild=False, return_parent=False):
    """Lookup a key in a nested document, yield a value"""
    if isinstance(document, list):
        for d in document:
          for result in _nested_lookup(key, values, d, wild=wild, return_parent=(document if return_parent else False)):
            yield result

    if isinstance(document, dict):
        for k, v in document.items():
          if values and v in values and (key == k or (wild and key.lower() in k.lower())):
            yield (document if not return_parent else return_parent)
          elif not values and key == k or (wild and key.lower() in k.lower()):
            yield (document if not return_parent else return_parent)
          elif isinstance(v, dict):
            for result in _nested_lookup(key, values, v, wild=wild, return_parent=(document if return_parent else False)):
              yield result
          elif isinstance(v, list):
            for d in v:
              for result in _nested_lookup(key, values, d, wild=wild, return_parent=(document if return_parent else False)):
                yield result

def sublime_executable_path():
  executable_path = sublime.executable_path()

  if sublime.platform() == 'osx':
    app_path = executable_path[:executable_path.rfind(".app/") + 5]
    executable_path = app_path + "Contents/SharedSupport/bin/subl"

  elif sublime.platform() == 'windows':
    executable_path = os.path.join(os.path.dirname(executable_path), "subl.exe")

  return executable_path

def subl(args):
  
  executable_path = sublime_executable_path()
  args = [executable_path] + args
  args_list = list()

  if sublime.platform() == 'windows' :
    for arg in args :
      args_list.append(json.dumps(arg, ensure_ascii=False))
  else :
    for arg in args :
      args_list.append(shlex.quote(arg))
  
  args = " ".join(args_list)

  return subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def overwrite_default_javascript_snippet():
  if not os.path.isdir(os.path.join(SUBLIME_PACKAGES_PATH, "JavaScript")) :
    os.mkdir(os.path.join(SUBLIME_PACKAGES_PATH, "JavaScript"))
  if not os.path.isdir(os.path.join(SUBLIME_PACKAGES_PATH, "JavaScript", "Snippets")) :
    os.mkdir(os.path.join(SUBLIME_PACKAGES_PATH, "JavaScript", "Snippets"))
  for file_name in os.listdir(os.path.join(PACKAGE_PATH, "JavaScript-overwrite-default-snippet")) :
    if file_name.endswith(".sublime-snippet") and os.path.isfile(os.path.join(PACKAGE_PATH, "JavaScript-overwrite-default-snippet", file_name)) :
      shutil.copy(os.path.join(PACKAGE_PATH, "JavaScript-overwrite-default-snippet", file_name), os.path.join(SUBLIME_PACKAGES_PATH, "JavaScript", "Snippets", file_name))

def open_project_folder(project):
  
  if not is_project_open(project) :
    subl(["--project", project])

def is_project_open(project): 

  project_folder_to_find = os.path.dirname(project)

  windows = sublime.windows()

  for window in windows :

    project_file_name = sublime.active_window().project_file_name()

    if project_file_name :
      project_folder = os.path.dirname(project_file_name)

      return True if project_folder == project_folder_to_find else False

    else :
      # try to look at window.folders()
      folders = window.folders()   
      if len(folders) > 0:

        project_folder = folders[0]

        return True if project_folder == project_folder_to_find else False

  return False
  
def is_javascript_project():
  project_file_name = sublime.active_window().project_file_name()
  project_dir_name = ""
  if project_file_name :
    project_dir_name = os.path.dirname(project_file_name)
    settings_dir_name = os.path.join(project_dir_name, PROJECT_SETTINGS_FOLDER_NAME)
    return os.path.isdir(settings_dir_name)
  else :
    # try to look at window.folders()
    folders = sublime.active_window().folders()   
    if len(folders) > 0:
      folders = folders[0]
      settings_dir_name = os.path.join(folders, PROJECT_SETTINGS_FOLDER_NAME)
      return os.path.isdir(settings_dir_name)
  return False

def is_type_javascript_project(type):
  settings = get_project_settings()
  return True if settings and os.path.exists(os.path.join(settings["settings_dir_name"], type+"_settings.json")) else False

def is_project_view(view) :
  settings = get_project_settings()
  if settings :
    # added view.file_name() == None because of new files without a name
    return ( view.file_name() and view.file_name().startswith(settings["project_dir_name"]) ) or view.file_name() == None
  return False

def get_project_settings(project_dir_name = ""):

  project_settings = dict()

  project_file_name = sublime.active_window().project_file_name() if not project_dir_name else ""
  settings_dir_name = ""

  if not project_dir_name :

    if project_file_name :
      project_dir_name = os.path.dirname(project_file_name)
    else :
      # try to look at window.folders()
      folders = sublime.active_window().folders()
      if len(folders) > 0:
        project_dir_name = folders[0]

  if not project_dir_name :
    return dict()

  if project_file_name :
    settings_dir_name = os.path.join(project_dir_name, PROJECT_SETTINGS_FOLDER_NAME)
    if not os.path.isdir(settings_dir_name) :
      return dict()
  else :
    for file in os.listdir(project_dir_name) :
      if file.endswith(".sublime-project") :
        project_file_name = os.path.join(project_dir_name, file)
        break
    settings_dir_name = os.path.join(project_dir_name, PROJECT_SETTINGS_FOLDER_NAME)
    if not os.path.isdir(settings_dir_name) :
      return dict()
        
  project_settings["project_file_name"] = project_file_name
  project_settings["project_dir_name"] = project_dir_name
  project_settings["settings_dir_name"] = settings_dir_name
  settings_file = ["project_details.json", "project_settings.json"]
  for setting_file in os.listdir(project_settings["settings_dir_name"]) :
    with open(os.path.join(settings_dir_name, setting_file), encoding="utf-8") as file :
      key = os.path.splitext(setting_file)[0]
      project_settings[key] = json.loads(file.read(), encoding="utf-8", object_pairs_hook=collections.OrderedDict)
  
  return project_settings

def save_project_setting(setting_file, data):
  settings = get_project_settings()
  if settings :
    with open(os.path.join(settings["settings_dir_name"], setting_file), 'w+', encoding="utf-8") as file :
      file.write(json.dumps(data, indent=2))

def word_with_dollar_char(view, region_or_point):
  user_setting_word_separators = view.settings().get("word_separators")
  view.settings().set("word_separators", "./\\()\"'-:,.;<>~!@#%^&*|+=[]{}`~?")
  word = view.word(region_or_point)
  view.settings().set("word_separators", user_setting_word_separators)
  return word

