import sublime, sublime_plugin
import re, urllib, shutil, traceback, threading, time, os, hashlib, json, multiprocessing, shlex

class Util(object) :

  multiprocessing_list = []

  @staticmethod
  def download_and_save(url, where_to_save) :
    if where_to_save :
      try :
        request = urllib.request.Request(url)
        request.add_header('User-agent', r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1')
        with urllib.request.urlopen(request) as response :
          with open(where_to_save, 'wb+') as out_file :
            shutil.copyfileobj(response, out_file)
            return True
      except Exception as e:
        traceback.print_exc()
    return False

  @staticmethod
  def open_json(path):
    with open(path) as json_file :    
      try :
        return json.load(json_file)
      except Exception as e :
        print("Error: "+traceback.format_exc())
    return None

  @staticmethod
  def check_thread_is_alive(thread_name) :
    for thread in threading.enumerate() :
      if thread.getName() == thread_name and thread.is_alive() :
        return True
    return False

  @staticmethod
  def create_and_start_thread(target, thread_name="", args=[], kwargs={}, daemon=True) :
    if not Util.check_thread_is_alive(thread_name) :
      thread = threading.Thread(target=target, name=thread_name, args=args, kwargs=kwargs, daemon=daemon)
      thread.start()
      return thread
    return None

  @staticmethod
  def check_process_is_alive(process_name) :
    Util.multiprocessing_list
    for process in Util.multiprocessing_list :
      if process.name == process_name :
        if process.is_alive() :
          return True
        else :
          Util.multiprocessing_list.remove(process)
    return False

  @staticmethod
  def create_and_start_process(target, process_name="", args=[], kwargs={}, daemon=True) :
    Util.multiprocessing_list
    if not Util.check_process_is_alive(process_name) :
      process = multiprocessing.Process(target=target, name=process_name, args=args, kwargs=kwargs, daemon=daemon)
      process.start()
      Util.multiprocessing_list.append(process)
      return process
    return None

  @staticmethod
  def setTimeout(time, func):
    timer = threading.Timer(time, func)
    timer.start()
    return timer

  @staticmethod
  def checksum_sha1(fname):
    hash_sha1 = hashlib.sha1()
    with open(fname, "rb") as f:
      for chunk in iter(lambda: f.read(4096), b""):
        hash_sha1.update(chunk)
    return hash_sha1.hexdigest()

  @staticmethod
  def checksum_sha1_equalcompare(fname1, fname2):
    return Util.checksum_sha1(fname1) == Util.checksum_sha1(fname2)

  @staticmethod
  def split_string_and_find(string_to_split, search_value, split_delimiter=" ") :
    string_splitted = string_to_split.split(split_delimiter)
    return Util.indexOf(string_splitted, search_value) 

  @staticmethod
  def split_string_and_find_on_multiple(string_to_split, search_values, split_delimiter=" ") :
    string_splitted = string_to_split.split(split_delimiter)
    for search_value in search_values :
      index = Util.indexOf(string_splitted, search_value) 
      if index >= 0 :
        return index
    return -1

  @staticmethod
  def split_string_and_findLast(string_to_split, search_value, split_delimiter=" ") :
    string_splitted = string_to_split.split(split_delimiter)
    return Util.lastIndexOf(string_splitted, search_value) 

  @staticmethod
  def indexOf(list_to_search, search_value) :
    index = -1
    try :
      index = list_to_search.index(search_value)
    except Exception as e:
      pass
    return index

  @staticmethod
  def lastIndexOf(list_to_search, search_value) :
    index = -1
    list_to_search_reversed = reversed(list_to_search)
    list_length = len(list_to_search)
    try :
      index = next(i for i,v in zip(range(list_length-1, 0, -1), list_to_search_reversed) if v == search_value)
    except Exception as e:
      pass
    return index

  @staticmethod
  def firstIndexOfMultiple(list_to_search, search_values) :
    index = -1
    string = ""
    for search_value in search_values :
      index_search = Util.indexOf(list_to_search, search_value)
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

  @staticmethod
  def find_and_get_pre_string_and_first_match(string, search_value) :
    result = None
    index = Util.indexOf(string, search_value)
    if index >= 0 :
      result = string[:index+len(search_value)]
    return result

  @staticmethod
  def find_and_get_pre_string_and_matches(string, search_value) :
    result = None
    index = Util.indexOf(string, search_value)
    if index >= 0 :
      result = string[:index+len(search_value)]
      string = string[index+len(search_value):]
      count_occ = string.count(search_value)
      i = 0
      while i < count_occ :
        result += " "+search_value
        i = i + 1
    return result

  @staticmethod
  def get_region_scope_first_match(view, scope, selection, selector) :
    scope = Util.find_and_get_pre_string_and_first_match(scope, selector)
    if scope :
      for region in view.find_by_selector(scope) :
        if region.contains(selection):
          selection.a = region.begin()
          selection.b = selection.a
          return {
            "scope": scope,
            "region": region,
            "region_string": view.substr(region),
            "region_string_stripped": view.substr(region).strip(),
            "selection": selection
          }
    return None

  @staticmethod
  def get_region_scope_last_match(view, scope, selection, selector) :
    scope = Util.find_and_get_pre_string_and_matches(scope, selector)
    if scope :
      for region in view.find_by_selector(scope) :
        if region.contains(selection):
          selection.a = region.begin()
          selection.b = selection.a
          return {
            "scope": scope,
            "region": region,
            "region_string": view.substr(region),
            "region_string_stripped": view.substr(region).strip(),
            "selection": selection
          }
    return None

  @staticmethod
  def find_regions_on_same_depth_level(view, scope, selection, selectors, depth_level, forward) :
    scope_splitted = scope.split(" ")
    regions = list()
    add_unit = 1 if forward else -1
    if len(scope_splitted) >= depth_level :  
      for selector in selectors :
        while Util.indexOf(scope_splitted, selector) == -1 :
          if selection.a == 0 or len(scope_splitted) < depth_level :
            return list()
          selection.a = selection.a + add_unit
          selection.b = selection.a 
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

  @staticmethod
  def get_current_region_scope(view, selection) :
    scope = view.scope_name(selection.begin()).strip()
    for region in view.find_by_selector(scope) :
      if region.contains(selection):
        selection.a = region.begin()
        selection.b = selection.a
        return {
          "scope": scope,
          "region": region,
          "region_string": view.substr(region),
          "region_string_stripped": view.substr(region).strip(),
          "selection": selection
        }
    return None

  @staticmethod
  def get_parent_region_scope(view, selection) :
    scope = view.scope_name(selection.begin()).strip()
    scope = " ".join(scope.split(" ")[:-1])
    for region in view.find_by_selector(scope) :
      if region.contains(selection):
        selection.a = region.begin()
        selection.b = selection.a
        return {
          "scope": scope,
          "region": region,
          "region_string": view.substr(region),
          "region_string_stripped": view.substr(region).strip(),
          "selection": selection
        }
    return None

  @staticmethod
  def get_specified_parent_region_scope(view, selection, parent) :
    scope = view.scope_name(selection.begin()).strip()
    scope = scope.split(" ")
    index_parent = Util.lastIndexOf(scope, parent)
    scope = " ".join(scope[:index_parent+1])
    for region in view.find_by_selector(scope) :
      if region.contains(selection):
        selection.a = region.begin()
        selection.b = selection.a
        return {
          "scope": scope,
          "region": region,
          "region_string": view.substr(region),
          "region_string_stripped": view.substr(region).strip(),
          "selection": selection
        }
    return None

  @staticmethod
  def cover_regions(regions) :
    first_region = regions[0]
    other_regions = regions[1:]
    for region in other_regions :
      first_region = first_region.cover(region)
    return first_region

  @staticmethod
  def rowcol_to_region(view, row, col, endcol):
    start = view.text_point(row, col)
    end = view.text_point(row, endcol)
    return sublime.Region(start, end)
  
  @staticmethod
  def trim_Region(view, region):
    new_region = sublime.Region(region.begin(), region.end())
    while(view.substr(new_region).startswith(" ") or view.substr(new_region).startswith("\n")):
      new_region.a = new_region.a + 1
    while(view.substr(new_region).endswith(" ") or view.substr(new_region).startswith("\n")):
      new_region.b = new_region.b - 1
    return new_region

  @staticmethod
  def selection_in_js_scope(view, point = -1, except_for = ""):
    sel_begin = view.sel()[0].begin() if point == -1 else point
    return view.match_selector(
      sel_begin,
      'source.js ' + except_for
    ) or view.match_selector(
      sel_begin,
      'source.js.embedded.html ' + except_for
    )
  
  @staticmethod
  def replace_with_tab(view, region, pre="", after="", add_to_each_line_before="", add_to_each_line_after="") :
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
      line = "\t"+add_to_each_line_before+line+add_to_each_line_after
      body.append(line)
    if body[len(body)-1].strip() == "" :
      del body[len(body)-1]
    body = "\n".join(body)
    return pre+body+after

  @staticmethod
  def replace_without_tab(view, region, pre="", after="", add_to_each_line_before="", add_to_each_line_after="") :
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
      body.append(add_to_each_line_before+line+add_to_each_line_after)
    if body[len(body)-1].strip() == "" :
      del body[len(body)-1]
    body = "\n".join(body)
    return pre+body+after

  @staticmethod
  def get_whitespace_from_line_begin(view, region) :
    line = view.line(region)
    whitespace = ""
    count = line.begin()
    sel_begin = region.begin()
    while count != sel_begin :
      count = count + 1
      whitespace = whitespace + " "
    return whitespace

  @staticmethod
  def add_whitespace_indentation(view, region, string, replace="\t", add_whitespace_end=True) :
    whitespace = Util.get_whitespace_from_line_begin(view, region)
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

  @staticmethod
  def go_to_centered(view, row, col):
    while view.is_loading() :
      time.sleep(.1)
    point = view.text_point(row, col)
    view.sel().clear()
    view.sel().add(point)
    view.show_at_center(point)

  @staticmethod
  def wait_view(view, fun):
    while view.is_loading() :
      time.sleep(.1)
    fun()

  @staticmethod
  def move_content_to_parent_folder(path):
    for filename in os.listdir(path):
      shutil.move(os.path.join(path, filename), os.path.dirname(path)) 
    os.rmdir(path)

  @staticmethod
  def merge_dicts(*dict_args):
      result = {}
      for dictionary in dict_args:
          result.update(dictionary)
      return result

  @staticmethod
  def removeItemIfExists(arr, item):
    if item in arr: arr.remove(item)

  @staticmethod
  def getListItemIfExists(arr, item):
    if item in arr : 
      return item
    return None

  @staticmethod
  def delItemIfExists(obj, key):
    try :
      del obj[key]
    except KeyError as e:
      pass

  @staticmethod
  def getDictItemIfExists(obj, key):
    try :
      return obj[key]
    except KeyError as e:
      pass
    return None

  @staticmethod
  def create_and_show_panel(output_panel_name, window = None):
    window = sublime.active_window() if not window else window
    panel = window.create_output_panel(output_panel_name, False)
    panel.set_read_only(True)
    panel.set_syntax_file(os.path.join("Packages", PACKAGE_NAME, "javascript_enhancements.sublime-syntax"))
    window.run_command("show_panel", {"panel": "output."+output_panel_name})
    return panel

  