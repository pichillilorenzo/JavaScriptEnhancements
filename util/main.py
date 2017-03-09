import sublime, sublime_plugin
import re, urllib, shutil, traceback, threading, time, os, hashlib

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

def check_thread_is_alive(thread_name) :
  for thread in threading.enumerate() :
    if thread.getName() == thread_name and thread.is_alive() :
      return True
  return False

def create_and_start_thread(target, thread_name="", args=[], daemon=True) :
  if not check_thread_is_alive(thread_name) :
    thread = threading.Thread(target=target, name=thread_name, args=args)
    thread.setDaemon(daemon)
    thread.start()
    return thread
  return None

def setTimeout(time, func):
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
  return indexOf(string_splitted, search_value) 

def split_string_and_find_on_multiple(string_to_split, search_values, split_delimiter=" ") :
  string_splitted = string_to_split.split(split_delimiter)
  for search_value in search_values :
    index = indexOf(string_splitted, search_value) 
    if index >= 0 :
      return index
  return -1

def split_string_and_findLast(string_to_split, search_value, split_delimiter=" ") :
  string_splitted = string_to_split.split(split_delimiter)
  return lastIndexOf(string_splitted, search_value) 

def indexOf(list_to_search, search_value) :
  index = -1
  try :
    index = list_to_search.index(search_value)
  except Exception as e:
    pass
  return index

def lastIndexOf(list_to_search, search_value) :
  index = -1
  list_to_search_reversed = reversed(list_to_search)
  list_length = len(list_to_search)
  try :
    index = next(i for i,v in zip(range(list_length-1, 0, -1), list_to_search_reversed) if v == search_value)
  except Exception as e:
    pass
  return index

def firstIndexOfMultiple(list_to_search, search_values) :
  index = -1
  string = ""
  for search_value in search_values :
    index_search = indexOf(list_to_search, search_value)
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
  index = indexOf(string, search_value)
  if index >= 0 :
    result = string[:index+len(search_value)]
  return result

def find_and_get_pre_string_and_matches(string, search_value) :
  result = None
  index = indexOf(string, search_value)
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

def get_region_scope_last_match(view, scope, selection, selector) :
  scope = find_and_get_pre_string_and_matches(scope, selector)
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

def find_regions_on_same_depth_level(view, scope, selection, selectors, depth_level, forward) :
  scope_splitted = scope.split(" ")
  regions = list()
  add_unit = 1 if forward else -1
  if len(scope_splitted) >= depth_level :  
    for selector in selectors :
      while indexOf(scope_splitted, selector) == -1 :
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

def get_specified_parent_region_scope(view, selection, parent) :
  scope = view.scope_name(selection.begin()).strip()
  scope = scope.split(" ")
  index_parent = lastIndexOf(scope, parent)
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

def cover_regions(regions) :
  first_region = regions[0]
  other_regions = regions[1:]
  for region in other_regions :
    first_region = first_region.cover(region)
  return first_region

def rowcol_to_region(view, row, col, endcol):
  start = view.text_point(row, col)
  end = view.text_point(row, endcol)
  return sublime.Region(start, end)
  
def trim_Region(view, region):
  new_region = sublime.Region(region.begin(), region.end())
  while(view.substr(new_region).startswith(" ") or view.substr(new_region).startswith("\n")):
    new_region.a = new_region.a + 1
  while(view.substr(new_region).endswith(" ") or view.substr(new_region).startswith("\n")):
    new_region.b = new_region.b - 1
  return new_region

def selection_in_js_scope(view, point = -1):
  sel_begin = view.sel()[0].begin() if point == -1 else point
  return view.match_selector(
    sel_begin,
    'source.js'
  ) or view.match_selector(
    sel_begin,
    'source.js.embedded.html'
  )
  
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

def get_whitespace_from_line_begin(view, region) :
  line = view.line(region)
  whitespace = ""
  count = line.begin()
  sel_begin = region.begin()
  while count != sel_begin :
    count = count + 1
    whitespace = whitespace + " "
  return whitespace

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
