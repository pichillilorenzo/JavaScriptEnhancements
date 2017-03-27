import sublime, sublime_plugin
import os, sys, imp, platform, json, traceback, threading, urllib, shutil, re
from shutil import copyfile
from threading import Timer

PACKAGE_PATH = os.path.abspath(os.path.dirname(__file__))
PACKAGE_NAME = os.path.basename(PACKAGE_PATH)
SUBLIME_PACKAGES_PATH = os.path.dirname(PACKAGE_PATH)

JC_SETTINGS_FOLDER_NAME = "javascript_completions"
JC_SETTINGS_FOLDER = os.path.join(PACKAGE_PATH, "helper", JC_SETTINGS_FOLDER_NAME)

PROJECT_FOLDER_NAME = "project"
PROJECT_FOLDER = os.path.join(PACKAGE_PATH, PROJECT_FOLDER_NAME)
socket_server_list = dict()

BOOKMARKS_FOLDER = os.path.join(PACKAGE_PATH, 'helper', 'bookmarks')
 
sys.path += [PACKAGE_PATH] + [os.path.join(PACKAGE_PATH, f) for f in ['node', 'util', 'my_socket']]

if 'reloader' in sys.modules:
  imp.reload(sys.modules['reloader'])
import reloader

platform_switcher = {"osx": "OSX", "linux": "Linux", "windows": "Windows"}
PLATFORM = platform_switcher.get(sublime.platform())
PLATFORM_ARCHITECTURE = "64bit" if platform.architecture()[0] == "64bit" else "32bit" 

def subl(args):
  
  executable_path = sublime.executable_path()
  if sublime.platform() == 'osx':
    app_path = executable_path[:executable_path.rfind(".app/") + 5]
    executable_path = app_path + "Contents/SharedSupport/bin/subl"

  if sublime.platform() == 'windows' :
    args = [executable_path] + args
  else :
    args_list = list()
    for arg in args :
      args_list.append(shlex.quote(arg))
    args = shlex.quote(executable_path) + " " + " ".join(args_list)

  return subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def overwrite_default_javascript_snippet():
  if not os.path.isdir(os.path.join(SUBLIME_PACKAGES_PATH, "JavaScript")) :
    os.mkdir(os.path.join(SUBLIME_PACKAGES_PATH, "JavaScript"))
  if not os.path.isdir(os.path.join(SUBLIME_PACKAGES_PATH, "JavaScript", "Snippets")) :
    os.mkdir(os.path.join(SUBLIME_PACKAGES_PATH, "JavaScript", "Snippets"))
  for file_name in os.listdir(os.path.join(PACKAGE_PATH, "JavaScript-overwrite-default-snippet")) :
    if file_name.endswith(".sublime-snippet") and os.path.isfile(os.path.join(PACKAGE_PATH, "JavaScript-overwrite-default-snippet", file_name)) :
      shutil.copy(os.path.join(PACKAGE_PATH, "JavaScript-overwrite-default-snippet", file_name), os.path.join(SUBLIME_PACKAGES_PATH, "JavaScript", "Snippets", file_name))

class startPlugin():
  def init(self):
    import node.node_variables as node_variables
    import node.installer as installer
    from node.main import NodeJS
    node = NodeJS()
    
    sublime.set_timeout_async(lambda: overwrite_default_javascript_snippet())

    sublime.set_timeout_async(lambda: installer.install(node_variables.NODE_JS_VERSION))

    window = sublime.active_window()
    view = window.active_view()

    sublime.set_timeout_async(lambda: show_flow_errorsViewEventListener(view).on_activated_async())
    sublime.set_timeout_async(lambda: load_bookmarks_viewViewEventListener(view).on_load_async())

mainPlugin = startPlugin()

import sublime, sublime_plugin
import os
from collections import namedtuple
import util.main as Util

flowCLIRequirements = namedtuple('flowCLIRequirements', [
    'filename', 'project_root', 'contents', 'cursor_pos', 'row', 'col', 'row_offset'
])

FLOW_DEFAULT_CONFIG_PATH = os.path.join(PACKAGE_PATH, "flow", ".flowconfig")

def find_flow_config(filename):
  if not filename or filename is '/':
    return FLOW_DEFAULT_CONFIG_PATH

  potential_root = os.path.dirname(filename)
  if os.path.isfile(os.path.join(potential_root, '.flowconfig')):
    return potential_root

  return find_flow_config(potential_root)

def flow_parse_cli_dependencies(view, **kwargs):
  filename = view.file_name()
  contextual_keys = sublime.active_window().extract_variables()
  folder_path = contextual_keys.get("folder")
  if folder_path and os.path.isdir(folder_path) and os.path.isfile(os.path.join(folder_path, '.flowconfig')) :    
    project_root = folder_path
  else :
    project_root = find_flow_config(filename)

  cursor_pos = 0
  if kwargs.get('cursor_pos') :
    cursor_pos = kwargs.get('cursor_pos')
  else :
    if len(view.sel()) > 0 :
      cursor_pos = view.sel()[0].begin()
    
  row, col = view.rowcol(cursor_pos)

  if kwargs.get('check_all_source_js_embedded'):
    embedded_regions = view.find_by_selector("source.js.embedded.html")
    if not embedded_regions :
      return flowCLIRequirements(
        filename=None,
        project_root=None,
        contents="",
        cursor_pos=None,
        row=None, col=None,
        row_offset=0
      )
    flowCLIRequirements_list = list()
    for region in embedded_regions:
      current_contents = view.substr(region)
      row_scope, col_scope = view.rowcol(region.begin())
      row_offset = row_scope
      row_scope = row - row_scope

      flowCLIRequirements_list.append(flowCLIRequirements(
        filename=filename,
        project_root=project_root,
        contents=current_contents,
        cursor_pos=cursor_pos,
        row=row, col=col,
        row_offset=row_offset
      ))
    return flowCLIRequirements_list
  else :
    scope_region = None
    if view.match_selector(
        cursor_pos,
        'source.js'
    ) and view.substr(sublime.Region(0, view.size()) ) == "" :
      scope_region = sublime.Region(0, 0)
    else :
      scope = view.scope_name(cursor_pos)
      result = Util.get_region_scope_first_match(view, scope, sublime.Region(cursor_pos, cursor_pos), "source.js")
      if not result:
        result = Util.get_region_scope_first_match(view, scope, sublime.Region(cursor_pos, cursor_pos), "source.js.embedded.html")
        if not result:
          return flowCLIRequirements(
            filename=None,
            project_root=None,
            contents="",
            cursor_pos=None,
            row=None, col=None,
            row_offset=0
          )
      scope_region = result["region"]
    current_contents = view.substr(scope_region)
    row_scope, col_scope = view.rowcol(scope_region.begin())
    row_offset = row_scope
    row_scope = row - row_scope
    """
    current_contents = view.substr(
      sublime.Region(0, view.size())
    )
    """
    
    if kwargs.get('add_magic_token'):
      current_lines = current_contents.splitlines()
      try :
        current_line = current_lines[row_scope]
      except IndexError as e:
        return flowCLIRequirements(
            filename=None,
            project_root=None,
            contents="",
            cursor_pos=None,
            row=None, col=None,
            row_offset=0
          )
      tokenized_line = ""
      if not kwargs.get('not_add_last_part_tokenized_line') :
        tokenized_line = current_line[0:col] + 'AUTO332' + current_line[col:-1]
      else :
        tokenized_line = current_line[0:col] + 'AUTO332'
      current_lines[row_scope] = tokenized_line
      current_contents = '\n'.join(current_lines)

    return flowCLIRequirements(
      filename=filename,
      project_root=project_root,
      contents=current_contents,
      cursor_pos=cursor_pos,
      row=row, col=col,
      row_offset=row_offset
    )


import sublime, sublime_plugin
import json, os, re, webbrowser, cgi, threading, shutil
import util.main as Util
from util.animation_loader import AnimationLoader
from util.repeated_timer import RepeatedTimer
from distutils.version import LooseVersion

HELPER_FOLDER_NAME = "helper"
HELPER_FOLDER = os.path.join(PACKAGE_PATH, HELPER_FOLDER_NAME)

import os, time
from my_socket.main import mySocketServer 
import util.main as Util

class SocketCallUI(object):

  def __init__(self, name, host, port, client_ui_file, wait_for_new_changes=1):
    super(SocketCallUI, self).__init__()
    self.name = name
    self.host = host
    self.port = port
    self.client_thread = None
    self.client_ui_file = client_ui_file
    self.socket = None
    self.current_selected_view = None
    self.last_modified = None
    self.wait_for_new_changes = wait_for_new_changes

  def init(self):
    if not os.path.isfile(self.client_ui_file):
      raise Exception("Client UI file \""+self.client_ui_file+"\" not found.")
    self.last_modified = time.time()

  def start(self, handle_recv, handle_client_connection, handle_client_disconnection):
    self.init()
    self.listen(handle_recv, handle_client_connection, handle_client_disconnection)
    self.client_thread = call_ui(self.client_ui_file , self.host, self.port)

  def listen(self, handle_recv, handle_client_connection, handle_client_disconnection):
    self.socket = mySocketServer(self.name) 
    self.socket.bind(self.host, self.port)
    self.socket.handle_recv(handle_recv)
    self.socket.handle_client_connection(handle_client_connection)
    self.socket.handle_client_disconnection(handle_client_disconnection)
    self.socket.listen()

  def update_time(self):
    self.last_modified = time.time()

  def handle_new_changes(self, fun, thread_name, *args):
    args = (fun,) + args
    return Util.create_and_start_thread(self.check_changes, args=args, thread_name=thread_name)

  def check_changes(self, fun, *args):
    while True:
      time.sleep(.1)
      now = time.time()
      if now - self.last_modified >= self.wait_for_new_changes :
        break
    fun(*args)
    
  def get_file_name(self):
    return self.current_selected_view.file_name()


class surround_withCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    selections = view.sel()
    region = None
    sub = None
    case = args.get("case")
    if case == "if_else_statement" :
      if len(selections) != 2 :
        return

      sel_1 = Util.trim_Region(view, selections[0])
      space_1 = Util.get_whitespace_from_line_begin(view, sel_1)
      new_text = Util.replace_with_tab(view, sel_1, space_1+"\n"+space_1+"if (bool) {\n"+space_1, "\n"+space_1+"} ")
      view.replace(edit, sel_1, new_text.strip())

      sel_2 = Util.trim_Region(view, selections[1])
      space_2 = Util.get_whitespace_from_line_begin(view, sel_2)
      new_text = Util.replace_with_tab(view, sel_2, " else {\n"+space_2, "\n"+space_2+"}\n"+space_2)
      view.replace(edit, sel_2, new_text.strip())
    else :
      for selection in selections :
        selection = Util.trim_Region(view, selection)
        if view.substr(selection).strip() == "" :
          continue
        space = Util.get_whitespace_from_line_begin(view, selection)

        if case == "if_statement" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"if (bool) {\n"+space, "\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "while_statement" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"while (bool) {\n"+space, "\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "do_while_statement" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"do {\n"+space, "\n"+space+"} while (bool);\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "for_statement" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"for ( ; bool ; ) {\n"+space, "\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "try_catch_statement" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"try {\n"+space, "\n"+space+"} catch (e) {\n"+space+"\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "try_catch_finally_statement" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"try {\n"+space, "\n"+space+"} catch (e) {\n"+space+"\n"+space+"} finally {\n"+space+"\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)
          
  def is_enabled(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    selections = view.sel()
    for selection in selections :
      if view.substr(selection).strip() != "" :
        return True
    return False

  def is_visible(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    selections = view.sel()
    for selection in selections :
      if view.substr(selection).strip() != "" :
        return True
    return False

class delete_surroundedCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    selections = view.sel()
    case = args.get("case")
    for selection in selections :
      scope = view.scope_name(selection.begin()).strip()
      scope_splitted = scope.split(" ")
      if case == "strip_quoted_string" :
        result = Util.firstIndexOfMultiple(scope_splitted, ("string.quoted.double.js", "string.quoted.single.js", "string.template.js"))
        selector = result.get("string")
        item = Util.get_region_scope_first_match(view, scope, selection, selector)
        if item :
          region_scope = item.get("region")
          new_str = item.get("region_string")
          new_str = new_str[1:-1]
          view.replace(edit, region_scope, new_str)

  def is_enabled(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True
    
  def is_visible(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True

class sort_arrayCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    from node.main import NodeJS
    node = NodeJS()
    view = self.view
    selections = view.sel()
    for selection in selections :
      scope = view.scope_name(selection.begin()).strip()
      result = Util.get_region_scope_first_match(view, scope, selection, "meta.brackets.js")
      if result :
        region = result.get("region")
        array_string = result.get("region_string_stripped")
        from node.main import NodeJS
        node = NodeJS()
        case = args.get("case")
        sort_func = ""
        if case == "compare_func_desc" :
          sort_func = "function(x,y){return y-x;}"
        elif case == "compare_func_asc" :
          sort_func = "function(x,y){return x-y;}"
        elif case == "alpha_asc" :
          sort_func = ""
        elif case == "alpha_desc" :
          sort_func = ""
        sort_result = node.eval("var array = "+array_string+"; console.log(array.sort("+sort_func+")"+( ".reverse()" if case == "alpha_desc" else "" )+")").strip()
        view.replace(edit, region, sort_result)

  def is_enabled(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    selections = view.sel()
    for selection in selections :
      scope = view.scope_name(selection.begin()).strip()
      index = Util.split_string_and_find(scope, "meta.brackets.js")
      if index < 0 :
        return False
    return True

  def is_visible(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    selections = view.sel()
    for selection in selections :
      scope = view.scope_name(selection.begin()).strip()
      index = Util.split_string_and_find(scope, "meta.brackets.js")
      if index < 0 :
        return False
    return True

class create_class_from_object_literalCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    selections = view.sel()
    for selection in selections :
      scope = view.scope_name(selection.begin()).strip()
      depth_level = Util.split_string_and_find(scope, "meta.object-literal.js")
      item_object_literal = Util.get_region_scope_first_match(view, scope, selection, "meta.object-literal.js")

      if item_object_literal :

        scope = item_object_literal.get("scope")
        object_literal_region = item_object_literal.get("region")
        selection = item_object_literal.get("selection")
        object_literal = item_object_literal.get("region_string_stripped")
        from node.main import NodeJS
        node = NodeJS()
        object_literal = json.loads(node.eval("JSON.stringify("+object_literal+")", "print"))
        object_literal = [(key, json.dumps(value)) for key, value in object_literal.items()]

        list_ordered = ("keyword.operator.assignment.js", "variable.other.readwrite.js", "storage.type.js")
        items = Util.find_regions_on_same_depth_level(view, scope, selection, list_ordered, depth_level, False)
        if items :
          last_selection = items[-1:][0].get("selection")
          class_name = items[1].get("region_string_stripped")
          regions = [(item.get("region")) for item in items]
          regions.append(object_literal_region)
          regions = Util.cover_regions(regions)
          parameters = list()
          constructor_body = list()
          get_set = list()
          for parameter in object_literal: 
            parameters.append( parameter[0] + ( "="+parameter[1] if json.loads(parameter[1]) != "required" else "") )
            constructor_body.append( "\t\tthis."+parameter[0]+" = "+parameter[0]+";" )
            get_set.append("\tget "+parameter[0]+"() {\n\t\treturn this."+parameter[0]+";\n\t}")
            get_set.append("\tset "+parameter[0]+"("+parameter[0]+") {\n\t\tthis."+parameter[0]+" = "+parameter[0]+";\n\t}")
          parameters = ", ".join(parameters)
          constructor_body = '\n'.join(constructor_body)
          get_set = '\n\n'.join(get_set)
          js_syntax  = "class "+class_name+" {\n"
          js_syntax += "\n\tconstructor ("+parameters+") {\n"
          js_syntax += constructor_body
          js_syntax += "\n\t}\n\n"
          js_syntax += get_set
          js_syntax += "\n}"
          js_syntax = Util.add_whitespace_indentation(view, regions, js_syntax)
          view.replace(edit, regions, js_syntax)

  def is_enabled(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    selection = view.sel()[0]
    scope = view.scope_name(selection.begin()).strip()
    index = Util.split_string_and_find(scope, "meta.object-literal.js")
    if index < 0 :
      return False
    return True

  def is_visible(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    selection = view.sel()[0]
    scope = view.scope_name(selection.begin()).strip()
    index = Util.split_string_and_find(scope, "meta.object-literal.js")
    if index < 0 :
      return False
    return True
      
class split_string_lines_to_variableCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    selections = view.sel()
    for selection in selections :
      scope = view.scope_name(selection.begin()).strip()
      scope_splitted = scope.split(" ")
      case = args.get("case")
      if case == "split" :
        result = Util.firstIndexOfMultiple(scope_splitted, ("string.quoted.double.js", "string.quoted.single.js", "string.template.js"))
        scope_string = scope_splitted[result.get("index")]
        selector = result.get("string")
        item = Util.get_region_scope_first_match(view, scope, selection, selector)
        if item :
          lines = item.get("region_string_stripped")[1:-1].split("\n")
          str_splitted = list()
          str_splitted.append("var str = \"\"")
          for line in lines :
            line = line if scope_string == "string.template.js" else line.strip()[0:-1]
            line = line.strip()
            if line :
              str_splitted.append( "str += "+"%r"%line )
          str_splitted = "\n".join(str_splitted)
          str_splitted = Util.add_whitespace_indentation(view, selection, str_splitted, "\n")
          view.replace(edit, item.get("region"), str_splitted)
          
  def is_visible(self, **args) :
    view = self.view
    if Util.split_string_and_find(view.scope_name(0), "source.js") < 0 :
      return False
    selection = view.sel()[0]
    scope = view.scope_name(selection.begin()).strip()
    scope_splitted = scope.split(" ")
    result = Util.firstIndexOfMultiple(scope_splitted, ("string.quoted.double.js", "string.quoted.single.js", "string.template.js"))
    if result.get("index") < 0 :
      return False
    return True

add_type_any_parameter_list = []
class add_type_any_parameterCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    global add_type_any_parameter_list
    view = self.view
    params = []
    if not "recall" in args :
      params = view.find_by_selector("variable.parameter.function.js")
      add_type_any_parameter_list = params
    else :
      params = add_type_any_parameter_list

    if "recall" in args and args["recall"] >= 0 :
      args["recall"] = args["recall"] + 1

    if params :
      view.insert(edit, params[0].end() + ( args["recall"]*len("/* : any */") if "recall" in args else 0 ) , "/* : any */")
      del params[0]
      if not "recall" in args :
        view.run_command("add_type_any_parameter", {"recall" : 0})
      else :
        view.run_command("add_type_any_parameter", {"recall": args["recall"]})

import sublime, sublime_plugin
import sys, imp, os, webbrowser, re, cgi
import util.main as Util

class JavaScriptCompletions():

  def get(self, key):
    return sublime.load_settings('JavaScript-Completions.sublime-settings').get(key)

javascriptCompletions = JavaScriptCompletions()

import sublime, sublime_plugin
import os
from node.main import NodeJS
import util.main as Util

node = NodeJS()

def build_type_from_func_details(comp_details):
  if comp_details :

    paramText = ""
    for param in comp_details["params"]:
      if not paramText:
        paramText += param['name'] + (": " + param['type'] if param['type'] else "")
      else:
        paramText += ", " + param['name'] + (": " + param['type'] if param['type'] else "")

    return ("("+paramText+")" if paramText else "()") + " => " + comp_details["return_type"]

  return ""

def build_completion_snippet(name, params):
  snippet = name + '({})'
  paramText = ''

  count = 1
  for param in params:
    if not paramText:
      paramText += "${" + str(count) + ":" + param['name'] + "}"
    else:
      paramText += ', ' + "${" + str(count) + ":" + param['name'] + "}"
    count = count + 1

  return snippet.format(paramText)

def create_completion(comp_name, comp_type, comp_details) :
  t = tuple()
  t += (comp_name + '\t' + comp_type, )
  t += (build_completion_snippet(
      comp_name,
      comp_details["params"]
    )
    if comp_details else comp_name, )
  return t

class javascript_completionsEventListener(sublime_plugin.EventListener):
  completions = None
  completions_ready = False

  # Used for async completions.
  def run_auto_complete(self):
    sublime.active_window().active_view().run_command("auto_complete", {
      'disable_auto_insert': True,
      'api_completions_only': False,
      'next_completion_if_showing': False,
      'auto_complete_commit_on_tab': True,
    })

  def on_query_completions(self, view, prefix, locations):
    # Return the pending completions and clear them

    if not view.match_selector(
        locations[0],
        'source.js - string - comment'
    ):
      return

    view = sublime.active_window().active_view()

    scope = view.scope_name(view.sel()[0].begin()-1).strip()

    if not prefix and not scope.endswith(" punctuation.accessor.js") :
      sublime.active_window().active_view().run_command(
        'hide_auto_complete'
      )
      return []

    if self.completions_ready and self.completions:
      self.completions_ready = False
      return self.completions

    sublime.set_timeout_async(
      lambda: self.on_query_completions_async(
        view, prefix, locations
      )
    )

    if not self.completions_ready or not self.completions:
      return ([], sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

  def on_query_completions_async(self, view, prefix, locations):
    self.completions = None

    if not view.match_selector(
        locations[0],
        'source.js - string - comment'
    ):
      return

    deps = flow_parse_cli_dependencies(view, add_magic_token=True, cursor_pos=locations[0])

    if deps.project_root is '/':
      return

    result = node.execute_check_output(
      "flow",
      [
        'autocomplete',
        '--from', 'sublime_text',
        '--root', deps.project_root,
        '--json',
        deps.filename
      ],
      is_from_bin=True,
      use_fp_temp=True, 
      fp_temp_contents=deps.contents, 
      is_output_json=True
    )

    if result[0]:
      result = result[1]
      self.completions = list()
      for match in result['result'] :

        comp_name = match['name']
        comp_type = match['type'] if match['type'] else build_type_from_func_details(match.get('func_details'))

        if comp_type.startswith("((") or comp_type.find("&") >= 0 :
          sub_completions = comp_type.split("&")
          for sub_comp in sub_completions :
            sub_comp = sub_comp.strip()
            sub_type = sub_comp[1:-1] if comp_type.startswith("((") else sub_comp
            
            if not match.get('func_details') :
              text_params = sub_type[ : sub_type.rfind(" => ") if sub_type.rfind(" => ") >= 0 else None ]
              text_params = text_params.strip()
              match["func_details"] = dict()
              match["func_details"]["params"] = list()
              start = 1 if sub_type.find("(") == 0 else sub_type.find("(")+1
              end = text_params.rfind(")")
              params = text_params[start:end].split(",")
              for param in params :
                param_dict = dict()
                param_info = param.split(":")
                param_dict["name"] = param_info[0].strip()
                match['func_details']["params"].append(param_dict)

            completion = create_completion(comp_name, sub_type, match.get('func_details'))
            self.completions.append(completion)
        else :
          completion = create_completion(comp_name, comp_type, match.get('func_details'))
          self.completions.append(completion)

      self.completions += load_default_autocomplete(view, self.completions, prefix, locations[0])
      self.completions = (self.completions, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)
      self.completions_ready = True

      sublime.active_window().active_view().run_command(
        'hide_auto_complete'
      )
      
      view = sublime.active_window().active_view()
      sel = view.sel()[0]
      if view.substr(view.word(sel)).strip() :
        self.run_auto_complete()

  def on_text_command(self, view, command_name, args):
    sel = view.sel()[0]
    if not view.match_selector(
        sel.begin(),
        'source.js - string - comment'
    ):
      return

    if command_name == "left_delete" :
      scope = view.scope_name(view.sel()[0].begin()-1).strip()
      if scope.endswith(" punctuation.accessor.js") :
        sublime.active_window().active_view().run_command(
          'hide_auto_complete'
        )

  def on_selection_modified_async(self, view) :

    selections = view.sel()
    if len(selections) == 0:
      return
      
    sel = selections[0]
    if not view.match_selector(
        sel.begin(),
        'source.js - string - comment'
    ):
      return

    scope1 = view.scope_name(selections[0].begin()-1).strip()
    scope2 = view.scope_name(selections[0].begin()-2).strip()

    if scope1.endswith(" punctuation.accessor.js") and not scope2.endswith(" punctuation.accessor.js") and view.substr(selections[0].begin()-2).strip() :
    
      locations = list()
      locations.append(selections[0].begin())

      sublime.set_timeout_async(
        lambda: self.on_query_completions_async(
          view, "", locations
        )
      )


import sublime, sublime_plugin
import os
from node.main import NodeJS

node = NodeJS()

class go_to_defCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    if args and "point" in args :
      point = args["point"]
    else :
      point = view.sel()[0].begin()
    self.go_to_def(view, point)

  def go_to_def(self, view, point):
    view = sublime.active_window().active_view()
    view.sel().clear()
    view.sel().add(point)
    sublime.active_window().run_command("goto_definition")
    if view.sel()[0].begin() == point :
      # try flow get-def
      sublime.status_message("")
      deps = flow_parse_cli_dependencies(view)
      result = node.execute_check_output(
        "flow",
        [
          'get-def',
          '--from', 'sublime_text',
          '--root', deps.project_root,
          '--json',
          view.file_name(),
          str(deps.row + 1), str(deps.col + 1)
        ],
        is_from_bin=True,
        use_fp_temp=True, 
        fp_temp_contents=deps.contents, 
        is_output_json=True,
        use_only_filename_view_flow=True
      )
      if result[0] :
        row = result[1]["line"]-1
        col = result[1]["start"]-1
        if result[1]["path"] != "-" and os.path.isfile(result[1]["path"]) :
          view = sublime.active_window().open_file(result[1]["path"])     
        sublime.set_timeout_async(lambda: Util.go_to_centered(view, row, col))

  def is_enabled(self):
    view = self.view
    if not Util.selection_in_js_scope(view, -1, "- string - comment"):
      return False
    return True

  def is_visible(self):
    view = self.view
    if not Util.selection_in_js_scope(view, -1, "- string - comment"):
      return False
    return True

js_css = ""
with open(os.path.join(JC_SETTINGS_FOLDER, "style.css")) as css_file:
  js_css = "<style>"+css_file.read()+"</style>"

if int(sublime.version()) >= 3124 :

  default_completions = Util.open_json(os.path.join(PACKAGE_PATH, 'default_autocomplete.json')).get('completions')

  def load_default_autocomplete(view, comps_to_campare, prefix, location, isHover = False):

    if not prefix :
      return []
    
    scope = view.scope_name(location-(len(prefix)+1)).strip()

    if scope.endswith(" punctuation.accessor.js") :
      return []

    prefix = prefix.lower()
    completions = default_completions
    completions_to_add = []
    for completion in completions: 
      c = completion[0].lower()
      if not isHover:
        if c.startswith(prefix):
          completions_to_add.append((completion[0], completion[1]))
      else :
        if len(completion) == 3 and c.startswith(prefix) :
          completions_to_add.append(completion[2])
    final_completions = []
    for completion in completions_to_add:
      flag = False
      for c_to_campare in comps_to_campare:
        if not isHover and completion[0].split("\t")[0] == c_to_campare[0].split("\t")[0] :
          flag = True
          break
        elif isHover and completion["name"] == c_to_campare["name"] :
          flag = True
          break
      if not flag :
        final_completions.append(completion)

    return final_completions

  import sublime, sublime_plugin
  import util.main as Util
  from node.main import NodeJS
  
  node = NodeJS()
  
  def description_details_html(description):
    description_name = "<span class=\"name\">" + cgi.escape(description['name']) + "</span>"
    description_return_type = ""
  
    text_pre_params = ""
  
    parameters_html = ""
    if description['func_details'] :
  
      if not description['type'].startswith("(") :
        text_pre_params = description['type'][ : description['type'].rfind(" => ") if description['type'].rfind(" => ") >= 0 else None ]
        text_pre_params = "<span class=\"text-pre-params\">" + cgi.escape(text_pre_params[:text_pre_params.find("(")]) + "</span>"
  
      for param in description['func_details']["params"]:
        is_optional = True if param['name'].find("?") >= 0 else False
        param['name'] = cgi.escape(param['name'].replace("?", ""))
        param['type'] = cgi.escape(param['type']) if param.get('type') else None
        if not parameters_html:
          parameters_html += "<span class=\"parameter-name\">" + param['name'] + "</span>" + ( "<span class=\"parameter-is-optional\">?</span>" if is_optional else "" ) + ( ": <span class=\"parameter-type\">" + param['type'] + "</span>" if param['type'] else "" )
        else:
          parameters_html += ', ' + "<span class=\"parameter-name\">" + param['name'] + "</span>" + ( "<span class=\"parameter-is-optional\">?</span>" if is_optional else "" ) + ( ": <span class=\"parameter-type\">" + param['type'] + "</span>" if param['type'] else "" )
      parameters_html = "("+parameters_html+")"
  
      description_return_type = cgi.escape(description['func_details']["return_type"]) if description['func_details']["return_type"] else ""
    elif description['type'] :
      description_return_type = cgi.escape(description['type'])
    if description_return_type :
      description_return_type = " => <span class=\"return-type\">"+description_return_type+"</span>"
  
    html = """ 
    <div class=\"container-description\">
      <div>"""+description_name+text_pre_params+parameters_html+description_return_type+"""</div>
      <div class=\"container-go-to-def\"><a href="go_to_def" class="go-to-def">Go to definition</a></div>
    </div>
    """
    return html
  
  class on_hover_descriptionEventListener(sublime_plugin.EventListener):
  
    def on_hover(self, view, point, hover_zone) :
      sublime.set_timeout_async(lambda: on_hover_description_async(view, point, hover_zone, point))
  
  def on_hover_description_async(view, point, hover_zone, popup_position) :
    if not view.match_selector(
        point,
        'source.js - comment'
    ):
      return
  
    if hover_zone != sublime.HOVER_TEXT :
      return
  
    region = view.word(point)
    word = view.substr(region)
    if not word.strip() :
      return
      
    cursor_pos = region.end()
  
    deps = flow_parse_cli_dependencies(view, cursor_pos=cursor_pos, add_magic_token=True, not_add_last_part_tokenized_line=True)
  
    if deps.project_root is '/':
      return
  
    result = node.execute_check_output(
      "flow",
      [
        'autocomplete',
        '--from', 'sublime_text',
        '--root', deps.project_root,
        '--json',
        deps.filename
      ],
      is_from_bin=True,
      use_fp_temp=True, 
      fp_temp_contents=deps.contents, 
      is_output_json=True
    )
  
    html = ""
  
    if result[0]:
      descriptions = result[1]["result"] + load_default_autocomplete(view, result[1]["result"], word, region.begin(), True)
  
      for description in descriptions :
        if description['name'] == word :
  
          if description['type'].startswith("((") or description['type'].find("&") >= 0 :
            sub_completions = description['type'].split("&")
            for sub_comp in sub_completions :
  
              sub_comp = sub_comp.strip()
              sub_type = sub_comp[1:-1] if description['type'].startswith("((") else sub_comp
                         
              text_params = sub_type[ : sub_type.rfind(" => ") if sub_type.rfind(" => ") >= 0 else None ]
              text_params = text_params.strip()
              description["func_details"] = dict()
              description["func_details"]["params"] = list()
              description["func_details"]["return_type"] = ""
              if sub_type.rfind(" => ") >= 0 :
                description["func_details"]["return_type"] = sub_type[sub_type.rfind(" => ")+4:].strip()
              start = 1 if sub_type.find("(") == 0 else sub_type.find("(")+1
              end = text_params.rfind(")")
              params = text_params[start:end].split(",")
              for param in params :
                param_dict = dict()
                param_info = param.split(":")
                param_dict["name"] = param_info[0].strip()
                if len(param_info) > 1 :
                  param_dict["type"] = param_info[1].strip()
                description['func_details']["params"].append(param_dict)
  
              html += description_details_html(description)
          else :
  
            html += description_details_html(description)
  
    if not html :
      deps = flow_parse_cli_dependencies(view)
      if deps.project_root is '/':
        return
      row, col = view.rowcol(point)
      result = node.execute_check_output(
        "flow",
        [
          'type-at-pos',
          '--from', 'sublime_text',
          '--root', deps.project_root,
          '--path', deps.filename,
          '--json',
          str(row - deps.row_offset + 1), str(col + 1)
        ],
        is_from_bin=True,
        use_fp_temp=True, 
        fp_temp_contents=deps.contents, 
        is_output_json=True
      )
  
      if result[0] and result[1].get("type") and result[1]["type"] != "(unknown)":
        description = dict()
        description["name"] = ""
        description['func_details'] = dict()
        description['func_details']["params"] = list()
        description['func_details']["return_type"] = ""
        is_function = False
        matches = re.match("^([a-zA-Z_]\w+)", result[1]["type"])
        if matches :
          description["name"] = matches.group()
        if result[1]["type"].find(" => ") >= 0 :
          description['func_details']["return_type"] = cgi.escape(result[1]["type"][result[1]["type"].find(" => ")+4:])
        else :
          description['func_details']["return_type"] = cgi.escape(result[1]["type"])
        if result[1]["type"].find("(") == 0:
          is_function = True
          start = 1
          end = result[1]["type"].find(")")
          params = result[1]["type"][start:end].split(",")
          description['func_details']["params"] = list()
          for param in params :
            param_dict = dict()
            param_info = param.split(":")
            param_dict["name"] = cgi.escape(param_info[0].strip())
            if len(param_info) == 2 :
              param_dict["type"] = cgi.escape(param_info[1].strip())
            else :
              param_dict["type"] = None
            description['func_details']["params"].append(param_dict)
  
        description_name = "<span class=\"name\">" + cgi.escape(description['name']) + "</span>"
        description_return_type = ""
  
        parameters_html = ""
        if description['func_details'] :
  
          for param in description['func_details']["params"]:
            is_optional = True if param['name'].find("?") >= 0 else False
            param['name'] = param['name'].replace("?", "")
            if not parameters_html:
              parameters_html += "<span class=\"parameter-name\">" + param['name'] + "</span>" + ( "<span class=\"parameter-is-optional\">?</span>" if is_optional else "" ) + ( ": <span class=\"parameter-type\">" + param['type'] + "</span>" if param['type'] else "" )
            else:
              parameters_html += ', ' + "<span class=\"parameter-name\">" + param['name'] + "</span>" + ( "<span class=\"parameter-is-optional\">?</span>" if is_optional else "" ) + ( ": <span class=\"parameter-type\">" + param['type'] + "</span>" if param['type'] else "" )
          parameters_html = "("+parameters_html+")" if is_function else ""
  
          description_return_type = description['func_details']["return_type"]
        elif description['type'] :
          description_return_type = description['type']
        if description_return_type :
          description_return_type = (" => " if description['name'] or is_function else "") + "<span class=\"return-type\">"+description_return_type+"</span>"
  
        html += """ 
        <div class=\"container-description\">
          <div>"""+description_name+parameters_html+description_return_type+"""</div>
          <div class=\"container-go-to-def\"><a href="go_to_def" class="go-to-def">Go to definition</a></div>
        </div>
        """
  
    func_action = lambda x: view.run_command("go_to_def", args={"point": point}) if x == "go_to_def" else ""
  
    if html :
        view.show_popup("""
        <html><head></head><body>
        """+js_css+"""
          <div class=\"container-hint-popup\">
            """ + html + """    
          </div>
        </body></html>""", sublime.COOPERATE_WITH_AUTO_COMPLETE | sublime.HIDE_ON_MOUSE_MOVE_AWAY, popup_position, 1150, 60, func_action )
    

  import sublime, sublime_plugin
  import util.main as Util
  
  class show_hint_parametersCommand(sublime_plugin.TextCommand):
    
    def run(self, edit, **args):
      view = self.view
  
      scope = view.scope_name(view.sel()[0].begin()).strip()
  
      meta_fun_call = "meta.function-call.method.js"
      result = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call+" meta.group.js")
  
      if not result :
        meta_fun_call = "meta.function-call.js"
        result = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call+" meta.group.js")
  
      if result :
        point = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call)["region"].begin()
        sublime.set_timeout_async(lambda: on_hover_description_async(view, point, sublime.HOVER_TEXT, view.sel()[0].begin()))
  
    def is_enabled(self) :
      view = self.view
      sel = view.sel()[0]
      if not view.match_selector(
          sel.begin(),
          'source.js - comment'
      ):
        return False
  
      scope = view.scope_name(view.sel()[0].begin()).strip()
      
      meta_fun_call = "meta.function-call.method.js"
      result = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call+" meta.group.js")
  
      if not result :
        meta_fun_call = "meta.function-call.js"
        result = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call+" meta.group.js")
  
      if result :
        point = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call)["region"].begin()
        scope_splitted = scope.split(" ")
        find_and_get_scope = Util.find_and_get_pre_string_and_matches(scope, meta_fun_call+" meta.group.js")
        find_and_get_scope_splitted = find_and_get_scope.split(" ")
        if (
            (
              len(scope_splitted) == len(find_and_get_scope_splitted) + 1 
              or scope == find_and_get_scope 
              or (
                  len(scope_splitted) == len(find_and_get_scope_splitted) + 2 
                  and ( Util.get_parent_region_scope(view, view.sel()[0])["scope"].split(" ")[-1] == "string.quoted.double.js"
                      or Util.get_parent_region_scope(view, view.sel()[0])["scope"].split(" ")[-1] == "string.quoted.single.js"
                      or Util.get_parent_region_scope(view, view.sel()[0])["scope"].split(" ")[-1] == "string.template.js"
                    ) 
                ) 
            ) 
            and not scope.endswith("meta.block.js") 
            and not scope.endswith("meta.object-literal.js")
          ) :
          return True
      return False
  
    def is_visible(self) :
      view = self.view
      sel = view.sel()[0]
      if not view.match_selector(
          sel.begin(),
          'source.js - comment'
      ):
        return False
  
      scope = view.scope_name(view.sel()[0].begin()).strip()
      
      meta_fun_call = "meta.function-call.method.js"
      result = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call+" meta.group.js")
  
      if not result :
        meta_fun_call = "meta.function-call.js"
        result = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call+" meta.group.js")
  
      if result :
        point = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call)["region"].begin()
        scope_splitted = scope.split(" ")
        find_and_get_scope = Util.find_and_get_pre_string_and_matches(scope, meta_fun_call+" meta.group.js")
        find_and_get_scope_splitted = find_and_get_scope.split(" ")
        if (
            (
              len(scope_splitted) == len(find_and_get_scope_splitted) + 1 
              or scope == find_and_get_scope 
              or (
                  len(scope_splitted) == len(find_and_get_scope_splitted) + 2 
                  and ( Util.get_parent_region_scope(view, view.sel()[0])["scope"].split(" ")[-1] == "string.quoted.double.js"
                      or Util.get_parent_region_scope(view, view.sel()[0])["scope"].split(" ")[-1] == "string.quoted.single.js"
                      or Util.get_parent_region_scope(view, view.sel()[0])["scope"].split(" ")[-1] == "string.template.js"
                    ) 
                ) 
            ) 
            and not scope.endswith("meta.block.js") 
            and not scope.endswith("meta.object-literal.js")
          ) :
          return True
      return False

  def show_flow_errors(view) :
  
    view_settings = view.settings()
    sel = view.sel()[0]
    if not view.match_selector(
        sel.begin(),
        'source.js'
    ) and not view.find_by_selector("source.js.embedded.html") :
      return None
  
    deps_list = list()
    if view.find_by_selector("source.js.embedded.html") :
      deps_list = flow_parse_cli_dependencies(view, check_all_source_js_embedded=True)
    else :
      deps_list = [flow_parse_cli_dependencies(view)]
  
    errors = []
    description_by_row = {}
    regions = []
    for deps in deps_list:
      if deps.project_root is '/':
        return None
  
      """
      if (
        '// @flow' not in deps.contents and
        '/* @flow */' not in deps.contents
      ):
        return view.erase_regions('flow_error')
      """
  
      if view_settings.get("flow_weak_mode") :
        deps = deps._replace(contents = "/* @flow weak */" + deps.contents)
  
      result = node.execute_check_output(
        "flow",
        [
          'check-contents',
          '--from', 'sublime_text',
          '--root', deps.project_root,
          '--json',
          deps.filename
        ],
        is_from_bin=True,
        use_fp_temp=True, 
        fp_temp_contents=deps.contents, 
        is_output_json=True,
        clean_output_flow=True
      )
  
      if result[0]:
  
        if result[1]['passed']:
          continue
  
        for error in result[1]['errors']:
          description = ''
          operation = error.get('operation')
          row = -1
          for i in range(len(error['message'])):
            message = error['message'][i]
            if i == 0 :
              row = int(message['line']) + deps.row_offset - 1
              col = int(message['start']) - 1
              endcol = int(message['end'])
  
              if row == 0 and view_settings.get("flow_weak_mode") : #fix when error start at the first line with @flow weak mode
                col = col - len("/* @flow weak */")
                endcol = endcol - len("/* @flow weak */")
  
              regions.append(Util.rowcol_to_region(view, row, col, endcol))
  
              if operation:
                description += operation["descr"]
  
            if not description :
              description += message['descr']
            else :
              description += ". " + message['descr']
  
          if row >= 0 :
            row_description = description_by_row.get(row)
            if not row_description:
              description_by_row[row] = description
            if row_description and description not in row_description:
              description_by_row[row] += '; ' + description
              
        errors = result[1]['errors']
  
    if errors :
      view.add_regions(
        'flow_error', regions, 'scope.js', 'dot',
        sublime.DRAW_SQUIGGLY_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
      )
      return {"errors": errors, "description_by_row": description_by_row}
    
    view.erase_regions('flow_error')
    view.set_status('flow_error', 'Flow: no errors')
    return None
  
  def hide_flow_errors(view) :
    view.erase_regions('flow_error')
    view.erase_status('flow_error')
  
  class handle_flow_errorsCommand(sublime_plugin.TextCommand):
  
    def run(self, edit, **args):
      if args :
        if args["type"] == "show" :
          show_flow_errors(self.view)
        elif args["type"] == "hide" :
          hide_flow_errors(self.view)
  

  import cgi, time
  
  class show_flow_errorsViewEventListener(Util.wait_modified_asyncViewEventListener, sublime_plugin.ViewEventListener):
  
    description_by_row = {}
    errors = []
    callback_setted_use_flow_checker_on_current_view = False
    prefix_thread_name = "show_flow_errors_view_event_listener"
    wait_time = .5
  
    def on_activated_async(self) :
      
      view = self.view
  
      selections = view.sel()
   
      if len(selections) == 0:
        return
        
      sel = selections[0]
      if not view.match_selector(
          sel.begin(),
          'source.js'
      ) and not view.find_by_selector("source.js.embedded.html"):
        hide_flow_errors(view)
        return
  
      settings = get_project_settings()
      if settings :
        if not settings["flow_settings"]["use_flow_checker"] or not is_project_view(view) :
          hide_flow_errors(view)
          return
      else :
        settings = view.settings()
        if not self.callback_setted_use_flow_checker_on_current_view :
          settings.clear_on_change("use_flow_checker_on_current_view")
          settings.add_on_change("use_flow_checker_on_current_view", lambda: sublime.set_timeout_async(lambda: self.on_modified_async()))
          self.callback_setted_use_flow_checker_on_current_view = True
        if not settings.get("use_flow_checker_on_current_view") :
          hide_flow_errors(view)
          return 
  
      sublime.set_timeout_async(lambda: self.on_modified_async())
  
    def on_modified_async(self):
      super(show_flow_errorsViewEventListener, self).on_modified_async()
      
    def on_modified_async_with_thread(self) : 
      view = self.view
  
      selections = view.sel()
   
      if len(selections) == 0:
        return
        
      sel = selections[0]
      if not view.match_selector(
          sel.begin(),
          'source.js'
      ) and not view.find_by_selector("source.js.embedded.html"):
        hide_flow_errors(view)
        return
      
      self.wait()  
  
      settings = get_project_settings()
      if settings :
        if not settings["flow_settings"]["use_flow_checker"] or not is_project_view(view) :
          hide_flow_errors(view)
          return
      elif not view.settings().get("use_flow_checker_on_current_view") :
        hide_flow_errors(view)
        return 
  
      self.errors = []
      self.description_by_row = {}
      result = show_flow_errors(view)
  
      if result :
        self.errors = result["errors"]
        self.description_by_row = result["description_by_row"]
  
      sublime.set_timeout_async(lambda: self.on_selection_modified_async())
  
    def on_hover(self, point, hover_zone) :
      view = self.view
      view.erase_phantoms("flow_error")
      if hover_zone != sublime.HOVER_GUTTER :
        return
  
      sel = sublime.Region(point, point)
      if (not view.match_selector(
          sel.begin(),
          'source.js'
      ) and not view.find_by_selector("source.js.embedded.html")) or not self.errors or not view.get_regions("flow_error"):
        hide_flow_errors(view)
        return
      
      settings = get_project_settings()
      if settings :
        if not settings["flow_settings"]["use_flow_checker"] or not is_project_view(view) :
          hide_flow_errors(view)
          return
      elif not view.settings().get("use_flow_checker_on_current_view") :
        hide_flow_errors(view)
        return 
  
      row, col = view.rowcol(sel.begin())
  
      error_for_row = self.description_by_row.get(row)
      
      if error_for_row:
        text = cgi.escape(error_for_row).split(" ")
        html = ""
        i = 0
        while i < len(text) - 1:
          html += text[i] + " " + text[i+1] + " "
          i += 2
          if i % 10 == 0 :
            html += " <br> "
        if len(text) % 2 != 0 :
          html += text[len(text) - 1]
  
        view.add_phantom("flow_error", sel, '<html style="padding: 0px; margin: 5px; background-color: rgba(255,255,255,0);"><body style="border-radius: 10px; padding: 10px; background-color: #F44336; margin: 0px;">'+html+"</body></html>", sublime.LAYOUT_BELOW)
  
  
    def on_selection_modified_async(self, *args) :
  
      view = self.view
      
      selections = view.sel()
   
      if len(selections) == 0:
        return
        
      sel = selections[0]
      if (not view.match_selector(
          sel.begin(),
          'source.js'
      ) and not view.find_by_selector("source.js.embedded.html")) or not self.errors or not view.get_regions("flow_error"):
        hide_flow_errors(view)
        return
   
      view.erase_phantoms("flow_error")
  
      settings = get_project_settings()
      if settings :
        if not settings["flow_settings"]["use_flow_checker"] or not is_project_view(view) :
          hide_flow_errors(view)
          return
      elif not view.settings().get("use_flow_checker_on_current_view") :
        hide_flow_errors(view)
        return 
  
      row, col = view.rowcol(sel.begin())
  
      error_count = len(self.errors)
      error_count_text = 'Flow: {} error{}'.format(
        error_count, '' if error_count is 1 else 's'
      )
      error_for_row = self.description_by_row.get(row)
      if error_for_row:
        view.set_status(
          'flow_error', error_count_text + ': ' + error_for_row
        )
      else:
        view.set_status('flow_error', error_count_text)
  

  import sublime, sublime_plugin
  
  class navigate_flow_errorsCommand(sublime_plugin.TextCommand):
  
    def run(self, edit, **args) :
      
      view = self.view
  
      regions = view.get_regions("flow_error")
      if not regions:
        return
  
      move_type = args.get("type")
  
      if move_type == "next" :
  
        r_next = self.find_next(regions)
        if r_next :
          row, col = view.rowcol(r_next.begin())
  
          Util.go_to_centered(view, row, col)
  
      elif move_type == "previous" :
  
        r_prev = self.find_prev(regions)
        if r_prev :
          row, col = view.rowcol(r_prev.begin())
  
          Util.go_to_centered(view, row, col)
  
    def find_next(self, regions):
      view = self.view
  
      sel = view.sel()[0]
  
      for region in regions :
        if region.begin() > sel.begin() :
          return region
  
      if(len(regions) > 0) :
        return regions[0]
  
      return None
  
    def find_prev(self, regions):
      view = self.view
  
      sel = view.sel()[0]
  
      previous_regions = []
      for region in regions :
        if region.begin() < sel.begin() :
          previous_regions.append(region)
  
      if not previous_regions and len(regions) > 0:
        previous_regions.append(regions[len(regions)-1])
  
      return previous_regions[len(previous_regions)-1] if len(previous_regions) > 0 else None
  

import sublime, sublime_plugin
import traceback, os, json, io, sys, imp
import util.main as Util

result_js = ""
region_selected = None
popup_is_showing = False
ej_css = """
<style>
html{
  margin: 0;
  padding: 0;
}
body{
  color: #fff;
  margin: 0;
  padding: 0;
}
.container{
  background-color: #202A31;
  padding: 10px;
}
a{
  color: #fff;
  display: block;
  margin: 10px 0;
}
</style>
"""

def action_result(action):
  global result_js
  global region_selected

  view = sublime.active_window().active_view()
  sel = region_selected
  str_selected = view.substr(sel).strip()

  if action == "copy_to_clipboard" :
    sublime.set_clipboard(result_js)

  elif action == "replace_text" :
    view.run_command("replace_text")

  elif action == "view_result_formatted":
    view.run_command("view_result_formatted")

  view.hide_popup()
  result_js = ""

class view_result_formattedCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    global result_js
    global region_selected

    sublime.active_window().show_input_panel("Result", result_js, back_to_popup, back_to_popup, back_to_popup)

class replace_textCommand(sublime_plugin.TextCommand):

  def run(self, edit):
    global result_js
    global region_selected

    view = self.view
    sel = Util.trim_Region(view, region_selected)
    view.replace(edit, sel, result_js)
    if region_selected.a < region_selected.b :
      region_selected.b = region_selected.a+len(result_js)
    else :
      region_selected.a = region_selected.b+len(result_js)

class ej_hide_popupEventListener(sublime_plugin.EventListener):
  def on_modified_async(self, view) :
    global popup_is_showing
    if popup_is_showing :
      view.hide_popup()
      popup_is_showing = False

class evaluate_javascriptCommand(sublime_plugin.TextCommand):

  def run(self, edit, is_line=False, eval_type="eval"):
    global result_js
    global region_selected
    global popup_is_showing

    view = self.view
    sel = view.sel()[0]
    popup_is_showing = False
    str_selected = view.substr(sel).strip()

    if is_line:
      lines = view.lines(sel)
      region_selected = lines[0]
      str_selected = view.substr(region_selected)
    else: 
      if not str_selected and region_selected : 
        region = get_start_end_code_highlights_eval()
        region_selected = sublime.Region(region[0], region[1])
        lines = view.lines(region_selected)
        str_selected = ""
        for line in lines:
          str_selected += view.substr(view.full_line(line))
      elif str_selected:
        lines = view.lines(sel)
        region_selected = sublime.Region if not region_selected else region_selected
        region_selected = sublime.Region(lines[0].begin(), lines[-1:][0].end())
      elif not str_selected :
        return
    
    if not region_selected :
      return

    view.run_command("show_start_end_dot_eval")

    try:
      from node.main import NodeJS
      node = NodeJS()
      result_js = node.eval(str_selected, eval_type, True)
      popup_is_showing = True
      view.show_popup("<html><head></head><body>"+ej_css+"""<div class=\"container\">
        <p class="result">Result: """+result_js+"""</p>
        <div><a href="view_result_formatted">View result with all spaces(\\t,\\n,...)</a></div>
        <div><a href="copy_to_clipboard">Copy result to clipboard</a></div>
        <div><a href="replace_text">Replace text with result</a></div>
        </div>
      </body></html>""", sublime.COOPERATE_WITH_AUTO_COMPLETE, -1, 400, 400, action_result)
    except Exception as e:
      #sublime.error_message("Error: "+traceback.format_exc())
      sublime.active_window().show_input_panel("Result", "Error: "+traceback.format_exc(), lambda x: "" , lambda x: "", lambda : "")

  def is_enabled(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True

  def is_visible(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True

class show_start_end_dot_evalCommand(sublime_plugin.TextCommand) :
  def run(self, edit) :
    global region_selected
    view = self.view
    lines = view.lines(region_selected)
    view.add_regions("region-dot", [lines[0], lines[-1:][0]],  "code", "dot", sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE)
    #view.add_regions("region-body", [region_selected],  "code", "", sublime.DRAW_NO_FILL)
  
  def is_enabled(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True

  def is_visible(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True

class hide_start_end_dot_evalCommand(sublime_plugin.TextCommand) :
  def run(self, edit) :
    view = self.view
    view.erase_regions("region-dot")
    #view.erase_regions("region-body")
  
  def is_enabled(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True

  def is_visible(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True

def get_start_end_code_highlights_eval() :
  view = sublime.active_window().active_view()
  return [view.line(view.get_regions("region-dot")[0]).begin(), view.line(view.get_regions("region-dot")[1]).end()]

def back_to_popup(*str_arg):
  view = sublime.active_window().active_view()
  view.run_command("evaluate_javascript")
  return



import sublime, sublime_plugin
import subprocess, time
from my_socket.main import mySocketServer  
from node.main import NodeJS
import util.main as Util
node = NodeJS()

socket_server_list["structure_javascript"] = SocketCallUI("structure_javascript", "localhost", 11113, os.path.join(HELPER_FOLDER, "structure_javascript", "ui", "client.js"), 1)

def update_structure_javascript(view, filename, clients=[]):
  global socket_server_list 

  deps = flow_parse_cli_dependencies(view)

  output = node.execute_check_output(
    "flow",
    [
      'ast',
      '--from', 'sublime_text'
    ],
    is_from_bin=True,
    use_fp_temp=True, 
    fp_temp_contents=deps.contents,
    is_output_json=True
  )
  
  if output[0] :
    errors = node.execute_check_output(
      "flow",
      [
        'check-contents',
        '--from', 'sublime_text',
        '--root', deps.project_root,
        '--json',
        deps.filename
      ],
      is_from_bin=True,
      use_fp_temp=True, 
      fp_temp_contents=deps.contents,
      is_output_json=True
    )

    output[1]["command"] = "show_structure_javascript"
    output[1]["filename"] = filename
    output[1]["file_content"] = deps.contents
    output[1]["errors"] = errors[1]["errors"] if errors[0] else None

    data = json.dumps(output[1])

    for client in clients :
      socket_server_list["structure_javascript"].socket.send_to(client["socket"], client["addr"], data)
  else :
    output[1] = dict()
    output[1]["command"] = "show_structure_javascript"
    output[1]["filename"] = "Error during loading structure"
    output[1]["file_content"] = ""
    output[1]["errors"] = None
    data = json.dumps(output[1])
    socket_server_list["structure_javascript"].socket.send_to(conn, addr, data)

class update_structure_javascriptViewEventListener(sublime_plugin.ViewEventListener):
  def on_modified_async(self) :
    global socket_server_list 
  
    if socket_server_list["structure_javascript"].socket :
      
      filename = self.view.file_name()
      filename = filename if filename else ""

      clients = socket_server_list["structure_javascript"].socket.find_clients_by_field("filename", filename)
      
      if clients:
        socket_server_list["structure_javascript"].update_time()
        socket_server_list["structure_javascript"].handle_new_changes(update_structure_javascript, "update_structure_javascript"+filename, self.view, filename, clients)

class view_structure_javascriptCommand(sublime_plugin.TextCommand):
  def run(self, edit, *args):
    global socket_server_list

    if socket_server_list["structure_javascript"].socket and socket_server_list["structure_javascript"].socket.close_if_not_clients():
      socket_server_list["structure_javascript"].socket = None
      
    if socket_server_list["structure_javascript"].socket == None :
      
      socket_server_list["structure_javascript"].current_selected_view = self.view

      def recv(conn, addr, ip, port, client_data, client_fields):
        global socket_server_list
        json_data = json.loads(client_data)

        if json_data["command"] == "ready":
          filename = socket_server_list["structure_javascript"].get_file_name()
          filename = filename if filename else ""

          update_structure_javascript(socket_server_list["structure_javascript"].current_selected_view, filename, [{"socket": conn, "addr": addr}])

        elif json_data["command"] == "set_dot_line" and os.path.isfile(client_fields["filename"]):
          other_view = sublime.active_window().open_file(client_fields["filename"])
          sublime.set_timeout_async(lambda: self.set_dot_line(other_view, json_data["line"]))    

      def client_connected(conn, addr, ip, port, client_fields):
        global socket_server_list   
        filename = socket_server_list["structure_javascript"].get_file_name()
        filename = filename if filename else ""
        client_fields["filename"] = filename

      def client_disconnected(conn, addr, ip, port):
        socket_server_list["structure_javascript"].client_thread = None
        if socket_server_list["structure_javascript"].socket.close_if_not_clients() :
            socket_server_list["structure_javascript"].socket = None

      socket_server_list["structure_javascript"].start(recv, client_connected, client_disconnected)

  def set_dot_line(self, view, line) :

    while view.is_loading() :
      time.sleep(.1)

    line = int(line)-1
    point = view.text_point(line, 0)
    view.show_at_center(point)
    view.sel().clear()
    view.sel().add(point)
    view.add_regions("structure-javascript-dot", [view.sel()[0]],  "code", "dot", sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE)
    sublime.set_timeout_async(lambda: view.erase_regions("structure-javascript-dot"), 500)

  def is_enabled(self):
    view = self.view
    if Util.split_string_and_find(view.scope_name(0), "source.js") < 0 :
      return False
    return True

  def is_visible(self):
    view = self.view
    if Util.split_string_and_find(view.scope_name(0), "source.js") < 0 :
      return False
    return True


import sublime, sublime_plugin
import json, time
import util.main as Util

bookmarks = []
latest_bookmarks_view = dict()

def set_bookmarks(is_project = False, set_dot = False):
  global bookmarks
  view = sublime.active_window().active_view()

  if is_project and ( not is_project_view(view) or not is_javascript_project() ) :
    sublime.error_message("Can't recognize JavaScript Project.")
    return
  elif is_project and is_project_view(view) and is_javascript_project() :
    project_settings = get_project_settings()
    bookmarks = Util.open_json(os.path.join(project_settings["settings_dir_name"], 'bookmarks.json')) or []
  else :
    bookmarks = Util.open_json(os.path.join(BOOKMARKS_FOLDER, 'bookmarks.json')) or []

  view.erase_regions("region-dot-bookmarks")
  if set_dot :
    lines = []
    lines = [view.line(view.text_point(bookmark["line"], 0)) for bookmark in search_bookmarks_by_view(view, is_project, is_from_set = True)]
    view.add_regions("region-dot-bookmarks", lines,  "code", "bookmark", sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE)

def update_bookmarks(is_project = False, set_dot = False):
  global bookmarks
  path = ""
  view = sublime.active_window().active_view()

  if is_project and ( not is_project_view(view) or not is_javascript_project() ) :
    sublime.error_message("Can't recognize JavaScript Project.")
    return
  elif is_project and is_project_view(view) and is_javascript_project() :
    project_settings = get_project_settings()
    path = os.path.join(project_settings["settings_dir_name"], 'bookmarks.json')
  else :
    path = os.path.join(BOOKMARKS_FOLDER, 'bookmarks.json')

  with open(path, 'w+') as bookmarks_json:
    bookmarks_json.write(json.dumps(bookmarks))

  view.erase_regions("region-dot-bookmarks")
  if set_dot :
    lines = []
    lines = [view.line(view.text_point(bookmark["line"], 0)) for bookmark in search_bookmarks_by_view(view, is_project)]

    view.add_regions("region-dot-bookmarks", lines,  "code", "bookmark", sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE)

def add_bookmark(view, line, name = "", is_project = False) :
  if not view.file_name() or line < 0:
    return False

  global bookmarks

  if is_project :
    set_bookmarks(True, True)
  else :
    set_bookmarks(False, True)

  bookmark = {
    "file_name": view.file_name(),
    "line": line,
    "name": name.strip()
  }

  if get_index_bookmark(bookmark) == -1:

    bookmarks.append(bookmark)
    update_bookmarks(is_project, True)

def remove_bookmark(bookmark, is_project = False) :

  if not bookmark["file_name"] or bookmark["line"] < 0:
    return False

  if is_project :
    set_bookmarks(True, True)
  else :
    set_bookmarks(False, True)

  global bookmarks

  if bookmark in bookmarks :
    bookmarks.remove(bookmark)
    update_bookmarks(is_project, True)

def search_bookmarks_by_view(view, is_project = False, is_from_set = False):
  if not view.file_name():
    return []

  global bookmarks

  if not is_from_set :
    if is_project :
      set_bookmarks(True, True)
    else :
      set_bookmarks(False, True)

  view_bookmarks = []

  for bookmark in bookmarks:
    if bookmark['file_name'] == view.file_name() :
      view_bookmarks.append(bookmark)

  return view_bookmarks

def delete_bookmarks_by_view(view, is_project = False):
  if not view.file_name():
    return False

  global bookmarks

  if is_project :
    set_bookmarks(True, True)
  else :
    set_bookmarks(False, True)

  new_bookmarks = []

  for bookmark in bookmarks:
    if bookmark['file_name'] != view.file_name() :
      new_bookmarks.append(bookmark)

  bookmarks = new_bookmarks
  update_bookmarks(is_project, True)

def get_index_bookmark(bookmark) :
  global bookmarks

  if bookmark in bookmarks :
    return bookmarks.index(bookmark)

  return -1

def open_bookmarks_and_show(index, bookmarks_view = []) :

  if index < 0 :
    return

  global bookmarks
  global latest_bookmarks_view

  if len(bookmarks_view) > 0 :
    bookmark = bookmarks_view[index]
  else :
    bookmark = bookmarks[index]

  latest_bookmarks_view = {"index": index, "bookmarks": bookmarks_view} if bookmarks_view else dict()

  view = sublime.active_window().open_file(bookmark["file_name"])

  sublime.set_timeout_async(lambda: Util.go_to_centered(view, bookmark["line"]-1, 0))

def set_multiple_bookmarks_names(view, index, selections, is_project = False):

  if len(selections) <= 0:
    return

  row = selections[0].begin()

  new_selections = []

  for index, sel in enumerate(selections):
    if index == 0:
      continue
    new_selections.append(sel)

  sublime.active_window().show_input_panel("Bookmark Name "+str(index+1)+": ", "",
    lambda name: add_bookmark(view, view.rowcol(row)[0], name, is_project) or set_multiple_bookmarks_names(view, index+1, new_selections),
    None,
    None
  )

class add_global_bookmark_hereCommand(sublime_plugin.TextCommand) :

  def run(self, edit):

    view = self.view

    selections = view.sel()

    set_multiple_bookmarks_names(view, 0, selections, False)
      
class add_project_bookmark_hereCommand(sublime_plugin.TextCommand) :

  def run(self, edit):

    if not is_javascript_project() :
      sublime.error_message("Can't recognize JavaScript Project.")
      return 

    view = self.view

    selections = view.sel()

    set_multiple_bookmarks_names(view, 0, selections, True)


class show_bookmarksCommand(sublime_plugin.TextCommand):

  def run(self, edit, **args) :
    global bookmarks
    global latest_bookmarks_view

    window = sublime.active_window()
    view = self.view

    show_type = args.get("type")

    if show_type == "global" or show_type == "view" :
      set_bookmarks(False, True)
    else :
      set_bookmarks(True, True)

    if len(bookmarks) <= 0:
      return 

    if show_type == "global" or show_type == "global_project" :

      items = [ ( bookmark['name'] + ", line: " + str(bookmark["line"]) ) if bookmark['name'] else ( bookmark['file_name'] + ", line: " + str(bookmark["line"]) ) for bookmark in bookmarks]

      window.show_quick_panel(items, lambda index: open_bookmarks_and_show(index))

    elif show_type == "view" or show_type == "view_project" : 

      bookmarks_view = search_bookmarks_by_view(view, False if show_type == "view" else True)

      latest_bookmarks_view = {"index": 0, "bookmarks": bookmarks_view} if bookmarks_view else dict()

      items = [ ( bookmark['name'] + ", line: " + str(bookmark["line"]) ) if bookmark['name'] else ( "line: " + str(bookmark["line"]) ) for bookmark in bookmarks_view]
      
      window.show_quick_panel(items, lambda index: open_bookmarks_and_show(index, bookmarks_view))

class delete_bookmarksCommand(sublime_plugin.TextCommand):

  def run(self, edit, **args) :
    global bookmarks

    window = sublime.active_window()
    view = self.view

    show_type = args.get("type")

    if show_type == "global" or show_type == "global_project" :

      bookmarks = []
      update_bookmarks(False if show_type == "global" else True, True)

    elif show_type == "view" or show_type == "view_project" : 

      delete_bookmarks_by_view(view, False if show_type == "view" else True)

    elif show_type == "single_global" or show_type == "single_global_project" : 

      items = [ ( bookmark['name'] + ", line: " + str(bookmark["line"]) ) if bookmark['name'] else ( bookmark['file_name'] + ", line: " + str(bookmark["line"]) ) for bookmark in bookmarks]

      window.show_quick_panel(items, lambda index: remove_bookmark(bookmarks[index], False if show_type == "single_global" else True))

class navigate_bookmarksCommand(sublime_plugin.TextCommand):

  def run(self, edit, **args) :

    window = sublime.active_window()
    view = self.view

    move_type = args.get("type")

    regions = view.get_regions("region-dot-bookmarks")

    if move_type == "next" :

      r_next = self.find_next(regions)
      if r_next :
        row, col = view.rowcol(r_next.begin())

        Util.go_to_centered(view, row, col)

    elif move_type == "previous" :

      r_prev = self.find_prev(regions)
      if r_prev :
        row, col = view.rowcol(r_prev.begin())

        Util.go_to_centered(view, row, col)

  def find_next(self, regions):
    view = self.view

    sel = view.sel()[0]

    for region in regions :
      if region.begin() > sel.begin() :
        return region

    if(len(regions) > 0) :
      return regions[0]

    return None

  def find_prev(self, regions):
    view = self.view

    sel = view.sel()[0]

    previous_regions = []
    for region in regions :
      if region.begin() < sel.begin() :
        previous_regions.append(region)

    if not previous_regions and len(regions) > 0:
      previous_regions.append(regions[len(regions)-1])

    return previous_regions[len(previous_regions)-1] if len(previous_regions) > 0 else None
      
class load_bookmarks_viewViewEventListener(sublime_plugin.ViewEventListener):

  def on_load_async(self) :

    view = self.view

    view.erase_regions("region-dot-bookmarks")
    lines = []
    lines = [view.line(view.text_point(bookmark["line"], 0)) for bookmark in search_bookmarks_by_view(view, ( True if is_project_view(view) and is_javascript_project() else False ))]
    view.add_regions("region-dot-bookmarks", lines,  "code", "bookmark", sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE)

import sublime, sublime_plugin
import re

class expand_modelCommand(sublime_plugin.TextCommand):

  def run(self, edit, *args) :

    view = self.view

    for sel in view.sel():

      row, col = view.rowcol(sel.begin())

      string = view.substr(sel).strip()

      index = string.rfind("*")

      n_times = int(string[index+1:])

      string = string[:index]

      final_string =  ""
      string_pieces = re.split(r"\$+", string)
      delimeters = re.findall(r"(\$+)", string)

      for x in range(1, n_times+1):
        for y in range(len(string_pieces)):
          if y < len(string_pieces) - 1:
            final_string += string_pieces[y] + str(x).zfill(len(delimeters[y]))
          else :
            final_string += string_pieces[y] + "\n" + ( " " * col)

      view.replace(edit, sel, final_string)

  def is_enabled(self) :

    view = self.view

    sel = view.sel()[0]
    string = view.substr(sel).strip()
    index = string.rfind("*")
    if index >= 0 :
      try :
        int(string[index+1:])
        return True
      except ValueError as e:
        pass

    return False

  def is_visible(self) :

    view = self.view

    sel = view.sel()[0]
    string = view.substr(sel).strip()
    index = string.rfind("*")
    if index >= 0 :
      try :
        int(string[index+1:])
        return True
      except ValueError as e:
        pass

    return False

if int(sublime.version()) >= 3124 :

  items_found_can_i_use = None
  can_i_use_file = None
  can_i_use_popup_is_showing = False
  can_i_use_list_from_main_menu = False
  path_to_can_i_use_data = os.path.join(HELPER_FOLDER, "can_i_use", "can_i_use_data.json")
  path_to_test_can_i_use_data = os.path.join(HELPER_FOLDER, "can_i_use", "can_i_use_data2.json")
  url_can_i_use_json_data = "https://raw.githubusercontent.com/Fyrd/caniuse/master/data.json"
  
  can_i_use_css = ""
  with open(os.path.join(HELPER_FOLDER, "can_i_use", "style.css")) as css_file:
    can_i_use_css = "<style>"+css_file.read()+"</style>"
  
  def donwload_can_i_use_json_data() :
    global can_i_use_file
  
    if os.path.isfile(path_to_can_i_use_data) :
      with open(path_to_can_i_use_data) as json_file:    
        try :
          can_i_use_file = json.load(json_file)
        except Exception as e :
          print("Error: "+traceback.format_exc())
          sublime.active_window().status_message("Can't use \"Can I use\" json data from: https://raw.githubusercontent.com/Fyrd/caniuse/master/data.json")
  
    if Util.download_and_save(url_can_i_use_json_data, path_to_test_can_i_use_data) :
      if os.path.isfile(path_to_can_i_use_data) :
        if not Util.checksum_sha1_equalcompare(path_to_can_i_use_data, path_to_test_can_i_use_data) :
          with open(path_to_test_can_i_use_data) as json_file:    
            try :
              can_i_use_file = json.load(json_file)
              if os.path.isfile(path_to_can_i_use_data) :
                os.remove(path_to_can_i_use_data)
              os.rename(path_to_test_can_i_use_data, path_to_can_i_use_data)
            except Exception as e :
              print("Error: "+traceback.format_exc())
              sublime.active_window().status_message("Can't use new \"Can I use\" json data from: https://raw.githubusercontent.com/Fyrd/caniuse/master/data.json")
        if os.path.isfile(path_to_test_can_i_use_data) :
          os.remove(path_to_test_can_i_use_data)
      else :
        os.rename(path_to_test_can_i_use_data, path_to_can_i_use_data)
        with open(path_to_can_i_use_data) as json_file :    
          try :
            can_i_use_file = json.load(json_file)
          except Exception as e :
            print("Error: "+traceback.format_exc())
            sublime.active_window().status_message("Can't use \"Can I use\" json data from: https://raw.githubusercontent.com/Fyrd/caniuse/master/data.json")
  
  Util.create_and_start_thread(donwload_can_i_use_json_data, "DownloadCanIuseJsonData")
  
  def find_in_can_i_use(word) :
    global can_i_use_file
    can_i_use_data = can_i_use_file.get("data")
    word = word.lower()
    return [value for key, value in can_i_use_data.items() if value["title"].lower().find(word) >= 0]
  
  def back_to_can_i_use_list(action):
    global can_i_use_popup_is_showing
    if action.find("http") >= 0:
      webbrowser.open(action)
      return
    view = sublime.active_window().active_view()
    can_i_use_popup_is_showing = False
    view.hide_popup()
    if len(action.split(",")) > 1 and action.split(",")[1] == "main-menu" :
      view.run_command("can_i_use", args={"from": "main-menu"})
    else :  
      view.run_command("can_i_use")
  
  def show_pop_can_i_use(index):
    global can_i_use_file
    global items_found_can_i_use
    global can_i_use_popup_is_showing
    if index < 0:
      return
    item = items_found_can_i_use[index]
  
    browser_accepted = ["ie", "edge", "firefox", "chrome", "safari", "opera", "ios_saf", "op_mini", "android", "and_chr"]
    browser_name = [
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IE",
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;EDGE",
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Firefox", 
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Chrome", 
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Safari", 
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Opera", 
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;iOS Safari", 
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Opera Mini", 
      "&nbsp;&nbsp;&nbsp;Android Browser", 
      "Chrome for Android"
    ]
  
    html_browser = ""
  
    html_browser += "<div>"
    html_browser += "<h1 class=\"title\">"+cgi.escape(item["title"])+" <a href=\""+item["spec"].replace(" ", "%20")+"\"><span class=\"status "+item["status"]+"\"> - "+item["status"].upper()+"</span></a></h1>"
    html_browser += "<p class=\"description\">"+cgi.escape(item["description"])+"</p>"
    html_browser += "<p class=\"\"><span class=\"support\">Global Support: <span class=\"support-y\">"+str(item["usage_perc_y"])+"%</span>"+( " + <span class=\"support-a\">"+str(item["usage_perc_a"])+"%</span> = " if float(item["usage_perc_a"]) > 0 else "" )+( "<span class=\"support-total\">"+str( "{:10.2f}".format(float(item["usage_perc_y"]) + float(item["usage_perc_a"])) )+"%</span>" if float(item["usage_perc_a"]) > 0 else "" )+"</span> "+( " ".join(["<span class=\"category\">"+category+"</span>" for category in item["categories"]]) )+"</p>"
    html_browser += "</div>"
  
    html_browser += "<div class=\"container-browser-list\">"
    i = 0
    for browser in browser_accepted :
  
      browser_versions = can_i_use_file["agents"]
      stat = item["stats"].get(browser)
      stat_items_ordered = list()
      for k in stat.keys() :
        if k != "TP" : 
          stat_items_ordered.append(k)
  
      if len(stat_items_ordered) >= 1 and stat_items_ordered[0] != "all" :
        stat_items_ordered.sort(key=LooseVersion)
        stat_items_ordered = stat_items_ordered[::-1]
  
      html_p = "<p class=\"version-stat-item\"><span class=\"browser-name\">"+browser_name[i]+"</span> : "
      j = 0
      while j < len(stat_items_ordered) :
        if j == 7:
          break
        class_name = stat.get(stat_items_ordered[j])
        html_annotation_numbers = ""
        requires_prefix = ""
        can_be_enabled = ""
  
        if re.search(r"\bx\b", class_name) :
          requires_prefix = "x"
        if re.search(r"\bd\b", class_name) :
          can_be_enabled = "d"
  
        if class_name.find("#") >= 0 :
          numbers = class_name[class_name.find("#"):].strip().split(" ")
          for number in numbers :
            number = int(number.replace("#", ""))
            html_annotation_numbers += "<span class=\"annotation-number\">"+str(number)+"</span>"
  
        html_p += "<span class=\"version-stat "+stat.get(stat_items_ordered[j])+" \">"+( html_annotation_numbers if html_annotation_numbers else "" )+stat_items_ordered[j]+( "<span class=\"can-be-enabled\">&nbsp;</span>" if can_be_enabled else "" )+( "<span class=\"requires-prefix\">&nbsp;</span>" if requires_prefix else "" )+"</span> "
  
        j = j + 1
  
      html_p += "</p>"
      html_browser += html_p
      i = i + 1
  
    html_browser += "</div>"
  
    if item["notes_by_num"] :
      html_browser += "<div>"
      html_browser += "<h3>Notes</h3>"
      notes_by_num = item["notes_by_num"]
  
      notes_by_num_ordered = list()
      for k in notes_by_num.keys() :
        notes_by_num_ordered.append(k)
      notes_by_num_ordered.sort()
  
      i = 0
      while i < len(notes_by_num_ordered) :
        note = notes_by_num.get(notes_by_num_ordered[i])
        html_p = "<p class=\"note\"><span class=\"annotation-number\">"+str(notes_by_num_ordered[i])+"</span>"+cgi.escape(note)+"</p>"
        html_browser += html_p
        i = i + 1
      html_browser += "</div>"
  
    if item["links"] :
      html_browser += "<div>"
      html_browser += "<h3>Links</h3>"
      links = item["links"]
  
      for link in links :
        html_p = "<p class=\"link\"><a href=\""+link.get("url")+"\">"+cgi.escape(link.get("title"))+"</a></p>"
        html_browser += html_p
      html_browser += "</div>"
  
    view = sublime.active_window().active_view()
    
    can_i_use_popup_is_showing = True
    view.show_popup("""
      <html>
        <head></head>
        <body>
        """+can_i_use_css+"""
        <div class=\"container-back-button\">
          <a class=\"back-button\" href=\"back"""+( ",main-menu" if can_i_use_list_from_main_menu else "")+"""\">&lt; Back</a>
          <a class=\"view-on-site\" href=\"http://caniuse.com/#search="""+item["title"].replace(" ", "%20")+"""\"># View on \"Can I use\" site #</a>
        </div>
        <div class=\"content\">
          """+html_browser+"""
          <div class=\"legend\">
            <h3>Legend</h3>
            <div class=\"container-legend-items\">
              <span class=\"legend-item y\">&nbsp;</span> = Supported 
              <span class=\"legend-item n\">&nbsp;</span> = Not Supported 
              <span class=\"legend-item p a\">&nbsp;</span> = Partial support 
              <span class=\"legend-item u\">&nbsp;</span> = Support unknown 
              <span class=\"legend-item requires-prefix\">&nbsp;</span> = Requires Prefix 
              <span class=\"legend-item can-be-enabled\">&nbsp;</span> = Can Be Enabled 
            </div>
          </div>
        </div>
        </body>
      </html>""", sublime.COOPERATE_WITH_AUTO_COMPLETE, -1, 1250, 650, back_to_can_i_use_list)
  
  class can_i_useCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
  
      global items_found_can_i_use
      global can_i_use_file
      global can_i_use_list_from_main_menu
      can_i_use_data = can_i_use_file.get("data")
      if not can_i_use_data :
        return
  
      view = self.view
      selection = view.sel()[0]
      if args.get("from") != "main-menu" :
        can_i_use_list_from_main_menu = False
        word = view.substr(view.word(selection)).strip()
        items_found_can_i_use = find_in_can_i_use(word)
        sublime.active_window().show_quick_panel([item["title"] for item in items_found_can_i_use], show_pop_can_i_use)
      else :
        can_i_use_list_from_main_menu = True
        items_found_can_i_use = find_in_can_i_use("")
        sublime.active_window().show_quick_panel([item["title"] for item in items_found_can_i_use], show_pop_can_i_use)
    
    def is_enabled(self, **args):
      view = self.view
      if args.get("from") == "main-menu" or javascriptCompletions.get("enable_can_i_use_menu_option") :
        return True 
      return False
  
    def is_visible(self, **args):
      view = self.view
      if args.get("from") == "main-menu" :
        return True
      if javascriptCompletions.get("enable_can_i_use_menu_option") :
        if Util.split_string_and_find_on_multiple(view.scope_name(0), ["source.js", "text.html.basic", "source.css"]) < 0 :
          return False
        return True
      return False
      
  class can_i_use_hide_popupEventListener(sublime_plugin.EventListener):
    def on_selection_modified_async(self, view) :
      global can_i_use_popup_is_showing
      if can_i_use_popup_is_showing :
        view.hide_popup()
        can_i_use_popup_is_showing = False



import sublime, sublime_plugin
import os, shlex

def call_ui(client_file, host, port) :
  from node.main import NodeJS
  node = NodeJS()
  return Util.create_and_start_thread(node.execute, client_file, ("electron", [client_file], True))

def is_javascript_project():
  project_file_name = sublime.active_window().project_file_name()
  project_dir_name = ""
  if project_file_name :
    project_dir_name = os.path.dirname(project_file_name)
    settings_dir_name = os.path.join(project_dir_name, ".jc-project-settings")
    return os.path.isdir(settings_dir_name)
  else :
    # try to look at window.folders()
    folder = sublime.active_window().folders()   
    if len(folder) > 0:
      folder = folder[0]
      settings_dir_name = os.path.join(folder, ".jc-project-settings")
      return os.path.isdir(settings_dir_name)
  return False

def is_type_javascript_project(type):
  settings = get_project_settings()
  return True if settings and type in settings["project_details"]["type"] else False

def is_project_view(view) :
  settings = get_project_settings()
  if settings :
    return view.file_name() and view.file_name().startswith(settings["project_dir_name"])
  return False

def get_project_settings():

  project_settings = dict()

  project_file_name = sublime.active_window().project_file_name()
  project_dir_name = ""
  settings_dir_name = ""
  if project_file_name :
    project_dir_name = os.path.dirname(project_file_name)
    settings_dir_name = os.path.join(project_dir_name, ".jc-project-settings")
    if not os.path.isdir(settings_dir_name) :
      return dict()
  else :
    # try to look at window.folders()
    folder = sublime.active_window().folders()
    if len(folder) > 0:
      project_dir_name = folder[0]
      for file in os.listdir(project_dir_name) :
        if file.endswith(".sublime-project") :
          project_file_name = os.path.join(project_dir_name, file)
          break
      settings_dir_name = os.path.join(project_dir_name, ".jc-project-settings")
      if not os.path.isdir(settings_dir_name) :
        return dict()
    else :
      return dict()
        
  project_settings["project_file_name"] = project_file_name
  project_settings["project_dir_name"] = project_dir_name
  project_settings["settings_dir_name"] = settings_dir_name
  settings_file = ["project_details.json", "flow_settings.json"]
  for setting_file in settings_file :
    with open(os.path.join(settings_dir_name, setting_file), encoding="utf-8") as file :
      key = os.path.splitext(setting_file)[0]
      project_settings[key] = json.loads(file.read(), encoding="utf-8")
    if setting_file == "project_details.json" :
      for project_type in project_settings["project_details"]["type"]:
        with open(os.path.join(settings_dir_name, project_type+"_settings.json"), encoding="utf-8") as file :
          project_settings[project_type+"_settings"] = json.loads(file.read(), encoding="utf-8")

  return project_settings

def save_project_setting(setting_file, data):
  settings = get_project_settings()
  if settings :
    with open(os.path.join(settings["settings_dir_name"], setting_file), 'w+', encoding="utf-8") as file :
      file.write(json.dumps(data, indent=2))

def save_project_flowconfig(flow_settings):
  settings = get_project_settings()
  if settings :
    with open(os.path.join(settings["settings_dir_name"], "flow_settings.json"), 'w+', encoding="utf-8") as file :
      file.write(json.dumps(flow_settings, indent=2))
    with open(os.path.join(settings["project_dir_name"], ".flowconfig"), 'w+', encoding="utf-8") as file :
      include = "\n".join(flow_settings["include"])
      ignore = "\n".join(flow_settings["ignore"])
      libs = "\n".join(flow_settings["libs"])
      options = "\n".join(list(map(lambda item: item[0].strip()+"="+item[1].strip(), flow_settings["options"])))

      data = "[ignore]\n{ignore}\n[include]\n{include}\n[libs]\n{libs}\n[options]\n{options}".format(ignore=ignore, include=include, libs=libs, options=options)
      file.write(data.replace(':PACKAGE_PATH', PACKAGE_PATH))

import sublime, sublime_plugin
import subprocess, shutil, traceback
from my_socket.main import mySocketServer  
from node.main import NodeJS
node = NodeJS()

socket_server_list["create_new_project"] = SocketCallUI("create_new_project", "localhost", 11111, os.path.join(PROJECT_FOLDER, "create_new_project", "ui", "client.js"))

def open_project_folder(project):
  
  subl(["--project", project])

class create_new_projectCommand(sublime_plugin.WindowCommand):
  def run(self, *args):
    global socket_server_list

    if socket_server_list["create_new_project"].socket and socket_server_list["create_new_project"].socket.close_if_not_clients():
      socket_server_list["create_new_project"].socket = None

    if socket_server_list["create_new_project"].socket == None :

      def recv(conn, addr, ip, port, client_data, client_fields):
        global socket_server_list

        json_data = json.loads(client_data)

        if json_data["command"] == "open_project":

          if json_data.get("type") :
            project_folder = os.path.dirname(json_data["project"])
            if "cordova" in json_data["type"]:
              node.execute('cordova', ["create", "temp"], is_from_bin=True, chdir=project_folder)
              Util.move_content_to_parent_folder(os.path.join(project_folder, "temp"))

          open_project_folder(json_data["project"])
          data = dict()
          data["command"] = "close_window"
          data = json.dumps(data)
          socket_server_list["create_new_project"].socket.send_to(conn, addr, data)

        elif json_data["command"] == "try_flow_init":
          
          data = dict()
          data["command"] = "result_flow_init"
          data["result"] = node.execute("flow", ["init"], is_from_bin=True, chdir=json_data["project"]["path"])
          data["project"] = json_data["project"]
          data = json.dumps(data)

          socket_server_list["create_new_project"].socket.send_to(conn, addr, data)

      def client_connected(conn, addr, ip, port, client_fields):
        global socket_server_list   

      def client_disconnected(conn, addr, ip, port):
        socket_server_list["create_new_project"].client_thread = None
        if socket_server_list["create_new_project"].socket.close_if_not_clients() :
          socket_server_list["create_new_project"].socket = None

      socket_server_list["create_new_project"].start(recv, client_connected, client_disconnected)


import sublime, sublime_plugin
import subprocess, shutil, traceback
from my_socket.main import mySocketServer  

socket_server_list["edit_project"] = SocketCallUI("edit_project", "localhost", 11112, os.path.join(PROJECT_FOLDER, "edit_project", "ui", "client.js"))

class edit_javascript_projectCommand(sublime_plugin.WindowCommand):
  def run(self, *args):
    global socket_server_list

    if socket_server_list["edit_project"].socket and socket_server_list["edit_project"].socket.close_if_not_clients():
      socket_server_list["edit_project"].socket = None

    if socket_server_list["edit_project"].socket == None :

      def recv(conn, addr, ip, port, client_data, client_fields):
        global socket_server_list

        json_data = json.loads(client_data)

        if json_data["command"] == "ready":
          settings = get_project_settings()
          if settings :
            data = dict()
            data["command"] = "load_project_settings"
            data["settings"] = settings
            data = json.dumps(data)
            socket_server_list["edit_project"].socket.send_to(conn, addr, data) 

      def client_connected(conn, addr, ip, port, client_fields):
        global socket_server_list 
        

      def client_disconnected(conn, addr, ip, port):
        socket_server_list["edit_project"].client_thread = None
        if socket_server_list["edit_project"].socket.close_if_not_clients() :
          socket_server_list["edit_project"].socket = None

      socket_server_list["edit_project"].start(recv, client_connected, client_disconnected)

  def is_enabled(self):
    return is_javascript_project()

  def is_visible(self):
    return is_javascript_project()

import sublime, sublime_plugin
import os, time

class close_all_servers_and_flowEventListener(sublime_plugin.EventListener):

  def on_pre_close(self, view) :

    from node.main import NodeJS
    node = NodeJS()

    global socket_server_list

    if not sublime.windows() :
      
      sublime.status_message("flow server stopping")
      sublime.set_timeout_async(lambda: node.execute("flow", ["stop"], True, os.path.join(PACKAGE_PATH, "flow")))

      for key, value in socket_server_list.items() :
        if value["socket"] != None :
          sublime.status_message("socket server stopping")
          data = dict()
          data["command"] = "server_closing"
          data = json.dumps(data)
          value["socket"].send_all_clients(data)
          value["socket"].close()

    if is_javascript_project() and view.window() and len(view.window().views()) == 1 :
      settings = get_project_settings()
      sublime.status_message("flow server stopping")
      sublime.set_timeout_async(lambda: node.execute("flow", ["stop"], True, os.path.join(settings["project_dir_name"])))


class print_panel_cliCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):   
    line = args.get("line")
    if line == "OUTPUT-SUCCESS":
      if self.view.window() and args.get("hide_panel_on_success") :
        sublime.set_timeout_async(lambda: self.view.window().run_command("hide_panel"), args.get("wait_panel") if args.get("wait_panel") else 1000 )
      return
    elif line == "OUTPUT-ERROR" or line == "OUTPUT-DONE":
      return
    self.view.set_read_only(False)
    self.view.insert(edit, self.view.size(), line)
    self.view.show_at_center(self.view.size())
    self.view.set_read_only(True)

class enable_menu_cliViewEventListener(sublime_plugin.ViewEventListener):

  def on_activated_async(self, **kwargs):
    cli = kwargs.get("cli")
    path = kwargs.get("path")
    path_disabled = kwargs.get("path_disabled")
    if cli and path and path_disabled:
      if is_type_javascript_project(cli) :
        if os.path.isfile(path_disabled):
          os.rename(path_disabled, path)
      else :
        if os.path.isfile(path):
          os.rename(path, path_disabled)

class manage_cliCommand(sublime_plugin.WindowCommand):
  cli = ""
  panel = None
  output_panel_name = "output_panel_cli"
  panel_command = "print_panel_cli"
  status_message_before = ""
  status_message_after_on_success = ""
  status_message_after_on_error = ""
  settings = {}
  command_with_options = []
  show_panel = True
  placeholders = {}
  hide_panel_on_success = True
  process = None
  is_stoppable = False
  stop_now = None
  command_stopped_text = "\n\nCommand Stopped\n\n"

  def run(self, **kwargs):
    if self.is_stoppable and self.stop_process():
      return
    self.settings = get_project_settings()
    if self.settings:
      self.callback_after_get_settings(**kwargs)
      self.cli = kwargs.get("cli") if kwargs.get("cli") else self.cli
      if not self.cli:
        raise Exception("'cli' field of the manage_cliCommand not defined.")

      self.command_with_options = self.substitute_placeholders(kwargs.get("command_with_options"))
      if not self.command_with_options or len(self.command_with_options) <= 0:
        raise Exception("'command_with_options' field of the manage_cliCommand not defined.")

      self.show_panel = kwargs.get("show_panel") if kwargs.get("show_panel") != None else self.show_panel
      self.output_panel_name = self.substitute_placeholders( self.output_panel_name if not kwargs.get("output_panel_name") else str(kwargs.get("output_panel_name")) )
      self.status_message_before = self.substitute_placeholders( self.status_message_before if not kwargs.get("status_message_before") else str(kwargs.get("status_message_before")) )
      self.status_message_after_on_success = self.substitute_placeholders( self.status_message_after_on_success if not kwargs.get("status_message_after_on_success") else str(kwargs.get("status_message_after_on_success")) )
      self.status_message_after_on_error = self.substitute_placeholders( self.status_message_after_on_error if not kwargs.get("status_message_after_on_error") else str(kwargs.get("status_message_after_on_error")) )
      self.hide_panel_on_success = True if kwargs.get("hide_panel_on_success") else False

      sublime.set_timeout_async(lambda: self.manage())
    else :
      sublime.error_message("Error: can't get project settings")

  def manage(self) :
    if self.status_message_before :
      self.window.status_message("Cordova: "+self.status_message_before)
    node = NodeJS()
    if self.show_panel :
      self.panel = self.window.create_output_panel(self.output_panel_name, False)
      self.window.run_command("show_panel", {"panel": "output."+self.output_panel_name})
    self.command_with_options = self.command_with_options + self.append_args_execute()
    node.execute(self.cli, self.command_with_options, is_from_bin=True, chdir=self.settings["project_dir_name"], wait_terminate=False, func_stdout=self.print_panel)
    
  def print_panel(self, line, process):
    if not self.process :
      self.process = process

    self.process_communicate(line)
    if line != None and self.show_panel:
      self.panel.run_command(self.panel_command, {"line": line, "hide_panel_on_success": self.hide_panel_on_success})
  
    if line == "OUTPUT-SUCCESS" and self.status_message_after_on_success :
      self.window.status_message("Cordova: "+self.status_message_after_on_success)

    if line == "OUTPUT-ERROR" and self.status_message_after_on_error :
      self.window.status_message("Cordova: "+self.status_message_after_on_error)

    if line == "OUTPUT-SUCCESS" :
      self.on_success()

    if line == "OUTPUT-ERROR" :
      self.on_error()

    if line == "OUTPUT-DONE":
      self.process = None
      self.on_done()

  def stop_process(self):
    if self.stop_now == None:
      self.stop_now = False
    elif self.stop_now == False and self.process != None:
      self.stop_now = True

    if self.stop_now:
      self.process.terminate()
      self.process = None
      self.stop_now = None
      self.panel.run_command(self.panel_command, {"line": self.command_stopped_text})
      self.panel.run_command(self.panel_command, {"line": "OUTPUT-SUCCESS", "hide_panel_on_success": True, "wait_panel": 3000})
      return True

    return False

  def substitute_placeholders(self, variable):
    if isinstance(variable, list) :
      for index in range(len(variable)):
        for key, placeholder in self.placeholders.items():
          variable[index] = variable[index].replace(key, placeholder)
      return variable
    elif isinstance(variable, str) :
      for key, placeholder in self.placeholders.items():
        variable = variable.replace(key, placeholder)
      return variable

  def append_args_execute(self):
    return []

  def process_communicate(self, line):
    return
    
  def callback_after_get_settings(self, **kwargs):
    return

  def on_success(self):
    return

  def on_error(self):
    return

  def on_done(self):
    return

## Cordova ##
import sublime, sublime_plugin
import os, webbrowser, shlex
from node.main import NodeJS

class enable_menu_cordovaViewEventListener(enable_menu_cliViewEventListener):
  def __init__(self, *args, **kwargs):  
    self.cli = "cordova"
    self.path = os.path.join(PACKAGE_PATH, "project", "cordova", "Main.sublime-menu")
    self.path_disabled = os.path.join(PACKAGE_PATH, "project", "cordova", "Main_disabled.sublime-menu")
    super(enable_menu_cliViewEventListener, self).__init__(*args, **kwargs)

  def on_activated_async(self, **kwargs):
    kwargs["cli"] = self.cli
    kwargs["path"] = self.path
    kwargs["path_disabled"] = self.path_disabled
    sublime.set_timeout_async(lambda: enable_menu_cliViewEventListener.on_activated_async(self, **kwargs))

class cordova_baseCommand(manage_cliCommand):
  cli = "cordova"
  can_add_platform = False
  platform_list = []
  platform_list_on_success = None
  can_add_plugin = False
  plugin_list = []
  plugin_list_on_success = None

  def ask_platform(self, type, func):
    self.platform_list = []
    self.can_add_platform = False
    self.platform_list_on_success = func
    self.settings = get_project_settings()
    if self.settings :
      sublime.status_message("Cordova: getting platform list...")
      node.execute(self.cli, ["platform", "list"], is_from_bin=True, chdir=self.settings["project_dir_name"], wait_terminate=False, func_stdout=(self.get_list_installed_platform_window_panel if type == "installed" else self.get_list_available_platform_window_panel))
    else :
      sublime.error_message("Error: can't get project settings")

  def get_list_installed_platform_window_panel(self, line, process):

    self.get_platform_list("installed", line, process, True)

  def get_list_available_platform_window_panel(self, line, process):

    self.get_platform_list("available", line, process, True)

  def get_platform_list(self, type, line, process, show_panel = False):
    if line == "OUTPUT-DONE" or line == "OUTPUT-SUCCESS" or line == "OUTPUT-ERROR" :
      self.can_add_platform = False

    if type == "installed" :
      if line and line.strip().startswith("Available platforms") :
        self.can_add_platform = False

    elif type == "available" :  
      if line and line.strip().startswith("Installed platforms") :
        self.can_add_platform = False

    if line and self.can_add_platform and line.strip() :
      self.platform_list.append(line.strip().split(" ")[0])

    if type == "installed" :
      if line and line.strip().startswith("Installed platforms") :
        self.can_add_platform = True

    elif type == "available" :  
      if line and line.strip().startswith("Available platforms") :
        self.can_add_platform = True

    if line == "OUTPUT-DONE" :
      if self.platform_list :
        if show_panel :
          self.window.show_quick_panel([cordova_platform for cordova_platform in self.platform_list], self.platform_list_on_success)
        elif self.platform_list_on_success :
          self.platform_list_on_success()
      else :
        if type == "installed" :
          sublime.message_dialog("Cordova: No platforms installed")
        elif type == "available" :  
          sublime.message_dialog("Cordova: No more platforms available")

  def ask_plugin(self, func):
    self.plugin_list = []
    self.can_add_plugin = False
    self.plugin_list_on_success = func
    self.settings = get_project_settings()
    if self.settings :
      sublime.status_message("Cordova: getting plugin list...")
      node.execute(self.cli, ["plugin", "list"], is_from_bin=True, chdir=self.settings["project_dir_name"], wait_terminate=False, func_stdout=self.get_plugin_list_window_panel)
    else :
      sublime.error_message("Error: can't get project settings")

  def get_plugin_list_window_panel(self, line, process):
    self.get_plugin_list(line, process, True)

  def get_plugin_list(self, line, process, show_panel = False):
    if line == "OUTPUT-DONE" or line == "OUTPUT-SUCCESS" or line == "OUTPUT-ERROR" :
      self.can_add_plugin = False
    else :
      self.can_add_plugin = True

    if line and self.can_add_plugin and line.strip() :
      self.plugin_list.append(line.strip().split(" ")[0])
    if line == "OUTPUT-DONE" :
      if self.plugin_list:
        if show_panel :
          self.window.show_quick_panel([cordova_plugin for cordova_plugin in self.plugin_list], self.plugin_list_on_success)
        elif self.plugin_list_on_success :
          self.plugin_list_on_success()
      else :
        sublime.message_dialog("Cordova: No plugins installed")

  def append_args_execute(self):
    custom_args = []
    custom_args = custom_args + self.settings["cordova_settings"]["cli_global_options"]
    command = self.command_with_options[0]
    mode = ""
    if command == "build" or command == "compile": 
      mode = self.command_with_options[2][2:]
    if command == "build" or command == "run" or command == "compile":
      platform = self.placeholders[":platform"]
      custom_args = custom_args + self.settings["cordova_settings"]["cli_"+command+"_options"]
      custom_args_platform = ""
      if mode :
        custom_args_platform = Util.getDictItemIfExists(self.settings["cordova_settings"]["platform_"+command+"_options"][mode], platform)
      else :
        custom_args_platform = Util.getDictItemIfExists(self.settings["cordova_settings"]["platform_"+command+"_options"], platform)
      if custom_args_platform :
        custom_args = custom_args + ["--"] + shlex.split(custom_args_platform)
    return custom_args

  def is_enabled(self):
    return is_type_javascript_project("cordova")

  def is_visible(self):
    return is_type_javascript_project("cordova")

class manage_cordovaCommand(cordova_baseCommand):

  def run(self, **kwargs):
    flag = False

    if kwargs.get("ask_platform") and kwargs.get("ask_platform_type"):
      self.ask_platform(kwargs.get("ask_platform_type"), lambda index: self.set_platform(index, **kwargs))
      flag = True

    if kwargs.get("ask_plugin"):
      self.ask_plugin(lambda index: self.set_plugin(index, **kwargs))
      flag = True

    if not flag :
      super(manage_cordovaCommand, self).run(**kwargs)

  def set_platform(self, index, **kwargs):
    if index >= 0:
      self.placeholders[":platform"] = self.platform_list[index]
      super(manage_cordovaCommand, self).run(**kwargs)

  def set_plugin(self, index, **kwargs):
    if index >= 0:
      self.placeholders[":plugin"] = self.plugin_list[index]
      super(manage_cordovaCommand, self).run(**kwargs)

class manage_serve_cordovaCommand(cordova_baseCommand):

  is_stoppable = True

  def process_communicate(self, line):
    if line and line.strip().startswith("Static file server running on: "):
      line = line.strip()
      url = line.replace("Static file server running on: ", "")
      url = url.replace(" (CTRL + C to shut down)", "")
      url = url.strip()
      webbrowser.open(url)

class manage_plugin_cordovaCommand(manage_cordovaCommand):

  def run(self, **kwargs):
    if kwargs.get("command_with_options") :
      if kwargs["command_with_options"][1] == "add" :
        self.window.show_input_panel("Plugin name: ", "", lambda plugin_name="": self.add_plugin(plugin_name.strip(), **kwargs), None, None)
        return
    super(manage_plugin_cordovaCommand, self).run(**kwargs)

  def add_plugin(self, plugin_name, **kwargs):
    self.placeholders[":plugin"] = plugin_name
    super(manage_plugin_cordovaCommand, self).run(**kwargs)

  def on_success(self):
    plugin_name = self.placeholders[":plugin"]
    plugin_lib_path = os.path.join(PACKAGE_PATH, "flow", "libs", "cordova", plugin_name+".js")
    plugin_lib_path_with_placeholder = os.path.join(":PACKAGE_PATH", "flow", "libs", "cordova", plugin_name+".js")
    if os.path.isfile(plugin_lib_path) :
      if self.command_with_options[1] == "add" :
        self.settings["flow_settings"]["libs"].append(plugin_lib_path_with_placeholder)
        save_project_flowconfig(self.settings["flow_settings"])
      elif self.command_with_options[1] == "remove" :
        Util.removeItemIfExists(self.settings["flow_settings"]["libs"], plugin_lib_path_with_placeholder)
        save_project_flowconfig(self.settings["flow_settings"])

class manage_add_platform_cordovaCommand(manage_cordovaCommand):

  def callback_after_get_settings(self, **kwargs):

    self.placeholders[":version"] = Util.getDictItemIfExists(self.settings["cordova_settings"]["platform_version_options"], self.placeholders[":platform"]) or ""

  def on_success(self):
    if not self.placeholders[":platform"] in self.settings["cordova_settings"]["installed_platform"] :
      self.settings["cordova_settings"]["installed_platform"].append(self.placeholders[":platform"])
    save_project_setting("cordova_settings.json", self.settings["cordova_settings"])

class manage_remove_platform_cordovaCommand(manage_cordovaCommand):

  def on_success(self):
    Util.removeItemIfExists(self.settings["cordova_settings"]["installed_platform"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["cordova_settings"]["platform_version_options"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["cordova_settings"]["platform_compile_options"]["debug"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["cordova_settings"]["platform_compile_options"]["release"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["cordova_settings"]["platform_build_options"]["debug"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["cordova_settings"]["platform_build_options"]["release"], self.placeholders[":platform"])
    Util.delItemIfExists(self.settings["cordova_settings"]["platform_run_options"], self.placeholders[":platform"])
    save_project_setting("cordova_settings.json", self.settings["cordova_settings"])

class sync_cordova_projectCommand(cordova_baseCommand):

  platform_list = []
  plugin_list = []

  def run(self, **kwargs):
    self.platform_list = []
    self.plugin_list = []
    self.settings = get_project_settings()
    if self.settings :
      sublime.status_message("Cordova: synchronizing project...")
      node.execute(self.cli, ["platform", "list"], is_from_bin=True, chdir=self.settings["project_dir_name"], wait_terminate=False, func_stdout=lambda line, process: self.get_platform_list("installed", line, process))
      node.execute(self.cli, ["plugin", "list"], is_from_bin=True, chdir=self.settings["project_dir_name"], wait_terminate=False, func_stdout=self.get_plugin_list)
    else :
      sublime.error_message("Error: can't get project settings")

  def platform_list_on_success(self):
    self.settings["cordova_settings"]["installed_platform"] = []
    for platform_name in self.platform_list:
      self.settings["cordova_settings"]["installed_platform"].append(platform_name)

    save_project_setting("cordova_settings.json", self.settings["cordova_settings"])
    sublime.status_message("Cordova: platforms synchronized")

  def plugin_list_on_success(self):
    plugin_list_to_remove = []
    for lib in self.settings["flow_settings"]["libs"]:
      if lib.startswith(":PACKAGE_PATH/flow/libs/cordova/") and lib != ":PACKAGE_PATH/flow/libs/cordova/cordova.js":
        plugin_list_to_remove.append(lib)
    for lib in plugin_list_to_remove:
      self.settings["flow_settings"]["libs"].remove(lib)

    for plugin_name in self.plugin_list:
      plugin_lib_path = os.path.join(PACKAGE_PATH, "flow", "libs", "cordova", plugin_name+".js")
      plugin_lib_path_with_placeholder = os.path.join(":PACKAGE_PATH", "flow", "libs", "cordova", plugin_name+".js")
      if os.path.isfile(plugin_lib_path) :
        self.settings["flow_settings"]["libs"].append(plugin_lib_path_with_placeholder)

    save_project_flowconfig(self.settings["flow_settings"])
    sublime.status_message("Cordova: plugins synchronized")


def plugin_loaded():
  global mainPlugin
  mainPlugin.init()


