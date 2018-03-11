import sublime, sublime_plugin
import os, json, subprocess, threading
from ..libs import NodeJS
from ..libs.global_vars import *
from ..libs.popup_manager import popup_manager
from ..libs import util
from ..libs import Hook
from ..libs import FlowCLI
from ..libs import flow_ide_clients

default_completions = util.open_json(os.path.join(PACKAGE_PATH, 'default_autocomplete.json')).get('completions')

def load_default_autocomplete(view, comps_to_campare, prefix, location, isHover = False):

  if not prefix :
    return []
  
  scope = view.scope_name(location-(len(prefix)+1)).strip()

  if scope.endswith(" punctuation.accessor.js") or scope.endswith(" keyword.operator.accessor.js") :
    return []

  prefix = prefix.lower()
  completions = default_completions
  completions_to_add = []
  for completion in completions: 
    c = completion[0].lower()
    if not isHover:
      if prefix in c:
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

class JavascriptEnhancementsCompletionsEventListener(sublime_plugin.EventListener):
  completions = list()
  completions_ready = False
  searching = False
  modified = False
  prefix = ""
  locations = []

  # Used for async completions.
  def run_auto_complete(self):
    sublime.active_window().active_view().run_command("auto_complete", {
      'disable_auto_insert': True,
      'api_completions_only': False,
      'next_completion_if_showing': False,
      'auto_complete_commit_on_tab': True,
      'auto_complete_delay': 0
    })

  def on_query_completions(self, view, prefix, locations):

    if not view.match_selector(
        locations[0],
        'source.js - string - comment'
    ):
      return []

    scope = view.scope_name(view.sel()[0].begin()-1).strip()

    # added "keyword.operator.accessor.js" for JavaScript (Babel) support
    # added "punctuation.dollar.js" and startswith("$") for completions that starts with "$" char
    # because Sublime Text 3 doesn't recognize it
    # 
    # force prefix in case of presence of "$" char
    if scope.endswith(" punctuation.dollar.js"):
      prefix = "$"
    elif view.substr(util.word_with_dollar_char(view, view.sel()[0])).startswith("$"): 
      prefix = view.substr(util.word_with_dollar_char(view, view.sel()[0]))

    self.prefix = prefix
    self.locations = locations

    if not prefix and not (scope.endswith(" punctuation.accessor.js") or scope.endswith(" punctuation.dollar.js") or view.substr(util.word_with_dollar_char(view, view.sel()[0].begin()-1)).startswith("$") or scope.endswith(" keyword.operator.accessor.js")) :
      sublime.active_window().active_view().run_command(
        'hide_auto_complete'
      )
      return []

    if self.completions_ready and self.completions:
      self.completions_ready = False
      # Return the pending completions
      return self.completions

    if not self.searching:
      self.searching = True
      self.modified = False
    else: 
      return ([], sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

    sublime.set_timeout_async(
      lambda: self.on_query_completions_async(view)
    )

    if not self.completions_ready or not self.completions:
      return ([], sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)
      
  def on_query_completions_async(self, view):
    self.completions = None

    if not view.match_selector(
        self.locations[0],
        'source.js - string - comment'
    ):
      return

    deps = FlowCLI.parse_cli_dependencies(view, add_magic_token=True, cursor_pos=self.locations[0])

    if not deps.project_root in flow_ide_clients:
      return
      
    params = [
      (deps.filename if deps.filename else ""), 
      deps.row + 1, 
      deps.col + 1, 
      deps.contents
    ]

    if not Hook.check_exists("flow_ide_server.autocomplete"):
      Hook.add("flow_ide_server.autocomplete", self.generate_completions)
      
    flow_ide_clients[deps.project_root].autocomplete(params)

  def build_type_from_func_details(self, comp_details):
    if comp_details :

      paramText = ""
      for param in comp_details["params"]:
        if not paramText:
          paramText += param['name'] + (": " + param['type'] if param['type'] else "")
        else:
          paramText += ", " + param['name'] + (": " + param['type'] if param['type'] else "")

      return ("("+paramText+")" if paramText else "()") + " => " + comp_details["return_type"]

    return ""

  def build_completion_snippet(self, name, params):
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

  def create_completion(self, comp_name, comp_type, comp_details) :
    t = tuple()
    t += (comp_name + '\t' + comp_type, )
    t += (self.build_completion_snippet(
        comp_name.replace("$", "\\$"),
        comp_details["params"]
      )
      if comp_details else comp_name.replace("$", "\\$"), )
    return t

  def generate_completions(self, result):
    
    view = sublime.active_window().active_view()

    if self.modified == True:
      self.searching = False
      return

    self.completions = list()

    scope = view.scope_name(view.sel()[0].begin()-1).strip()
    dollar_prefix = view.substr(util.word_with_dollar_char(view, view.sel()[0]))
    is_prefix_dollar = (scope.endswith(" punctuation.dollar.js") or scope.endswith(" variable.other.dollar.js") or dollar_prefix.startswith("$"))

    for match in result['result'] :

      comp_name = match['name']

      if (is_prefix_dollar and not comp_name.startswith(dollar_prefix)) or "AUTO332" in comp_name:
        continue

      comp_type = match['type'] if match['type'] else self.build_type_from_func_details(match.get('func_details'))

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

          completion = self.create_completion(comp_name, sub_type, match.get('func_details'))
          self.completions.append(completion)
      else :
        completion = self.create_completion(comp_name, comp_type, match.get('func_details'))
        self.completions.append(completion)

    self.completions += load_default_autocomplete(view, self.completions, self.prefix, self.locations[0])
    self.completions = (self.completions, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)
    self.completions_ready = True

    view = sublime.active_window().active_view()
    sel = view.sel()[0]

    if view.substr(util.word_with_dollar_char(view, sel)).strip() :

      if self.modified == True:
        self.searching = False
        return
      
      sublime.active_window().active_view().run_command(
        'hide_auto_complete'
      )

      self.run_auto_complete()

    self.searching = False

  def on_text_command(self, view, command_name, args):

    selections = view.sel()
    sel = None
    try:
      sel = selections[0]
    except IndexError as e:
      return

    if not view.match_selector(
        sel.begin(),
        'source.js - string - comment'
    ):
      return

    if command_name == "left_delete" :
      self.modified = True
      self.searching = False
      scope = view.scope_name(view.sel()[0].begin()-1).strip()
      if scope.endswith(" punctuation.accessor.js") or scope.endswith(" punctuation.dollar.js") or view.substr(view.word(view.sel()[0].begin()-1)) == " $" or view.substr(view.word(view.sel()[0].begin()-1)) == "\n$" or scope.endswith(" keyword.operator.accessor.js"):
        sublime.active_window().active_view().run_command(
          'hide_auto_complete'
        )

    elif command_name == "drag_select" :
      if view.sel()[0].begin() < view.word(view.sel()[0].begin()).end():
        self.modified = True
        self.searching = False

    elif command_name == "run_macro_file" and 'file' in args and args.get('file').endswith("Delete Left Right.sublime-macro"):
      scope = view.scope_name(view.sel()[0].begin()).strip()
      if popup_manager.is_visible("javascript_enhancements_hint_parameters") and ( scope.endswith(" punctuation.section.group.js") or scope.endswith(" meta.group.braces.round.function.arguments.js") ):
        view.hide_popup()

  def on_post_text_command(self, view, command_name, args):

    selections = view.sel()
    sel = None
    try:
      sel = selections[0]
    except IndexError as e:
      return

    if not view.match_selector(
        sel.begin(),
        'source.js - comment'
    ):
      return

    scope = view.scope_name(view.sel()[0].end()).strip()

    if command_name == "insert_snippet" and ( scope.endswith(" punctuation.section.group.js") or scope.endswith(" meta.group.braces.round.function.arguments.js") ):
      view.run_command("javascript_enhancements_show_hint_parameters", args={"popup_position_on_point": True})

    elif (( command_name == "commit_completion" or (
             ( command_name == "next_field" or command_name == "prev_field" ) and sel.begin() != sel.end()
            )
          )
          and (
            scope.endswith(" punctuation.section.group.js") or 
            scope.endswith(" punctuation.separator.comma.js") or 
            scope.endswith(" meta.group.braces.round.js") or 
            scope.endswith(" meta.brace.round.end.js") 
          )) :
      view.run_command("javascript_enhancements_show_hint_parameters", args={"popup_position_on_point": True})

  def on_modified(self, view):
    # on_modified method added because Sublime Text 3
    # doesn't call on_query_completions with "$" char at the begin.
    # In this way I don't need to overwrite user's settings about word_separators option
    selections = view.sel()
    sel = None
    try:
      sel = selections[0]
    except IndexError as e:
      return
      
    if not view.match_selector(
        sel.begin(),
        'source.js - string - comment'
    ):
      return

    scope = view.scope_name(sel.begin()-1).strip()

    if scope.endswith(" punctuation.dollar.js") or view.substr(view.word(sel.begin()-1)) == " $" or view.substr(view.word(sel.begin()-1)) == "\n$":
      self.run_auto_complete()

  def on_selection_modified_async(self, view) :

    selections = view.sel()
    sel = None
    try:
      sel = selections[0]
    except IndexError as e:
      return
      
    if not view.match_selector(
        sel.begin(),
        'source.js - string - comment'
    ):
      return

    scope1 = view.scope_name(sel.begin()-1).strip()
    scope2 = view.scope_name(sel.begin()-2).strip()

    if ((
          scope1.endswith(" punctuation.accessor.js") or 
          scope1.endswith(" keyword.operator.accessor.js") 
        ) and 
        not ( 
          scope2.endswith(" punctuation.accessor.js") or 
          scope2.endswith(" keyword.operator.accessor.js") 
        ) and 
        view.substr(sel.begin()-2).strip() 
      ) :
      
      locations = list()
      locations.append(sel.begin())

      if not self.searching:
        self.searching = True
        self.modified = False
      else: 
        return 

      self.locations = locations
      self.prefix = ""

      sublime.set_timeout_async(
        lambda: self.on_query_completions_async(view)
      )
