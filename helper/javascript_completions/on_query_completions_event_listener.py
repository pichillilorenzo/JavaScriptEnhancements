import sublime, sublime_plugin
import os, tempfile

# list of threads that are used to check if there are 
# multiple async completions tooltip queued (fix for tooltip stuttering)
javascript_completions_thread_list = []

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
  searching = False
  modified = False

  # Used for async completions.
  def run_auto_complete(self):
    sublime.active_window().active_view().run_command("auto_complete", {
      'disable_auto_insert': True,
      'api_completions_only': False,
      'next_completion_if_showing': False,
      'auto_complete_commit_on_tab': True
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

    # added "keyword.operator.accessor.js" for JavaScript (Babel) support
    if not prefix and not (scope.endswith(" punctuation.accessor.js") or scope.endswith(" keyword.operator.accessor.js")) :
      sublime.active_window().active_view().run_command(
        'hide_auto_complete'
      )
      return []

    if self.completions_ready and self.completions:
      self.completions_ready = False
      return self.completions

    if not self.searching:
      self.searching = True
      self.modified = False
    else: 
      return ([], sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

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
    
    flow_cli = "flow"
    is_from_bin = True
    chdir = ""
    use_node = True
    bin_path = ""

    settings = get_project_settings()
    if settings and settings["project_settings"]["flow_cli_custom_path"]:
      flow_cli = os.path.basename(settings["project_settings"]["flow_cli_custom_path"])
      bin_path = os.path.dirname(settings["project_settings"]["flow_cli_custom_path"])
      is_from_bin = False
      chdir = settings["project_dir_name"]
      use_node = False

    if self.modified == True:
      self.searching = False
      return

    node = NodeJS(check_local=True)
    
    result = node.execute_check_output(
      flow_cli,
      [
        'autocomplete',
        '--from', 'sublime_text',
        '--root', deps.project_root,
        '--json',
        deps.filename
      ],
      is_from_bin=is_from_bin,
      use_fp_temp=True, 
      fp_temp_contents=deps.contents, 
      is_output_json=True,
      chdir=chdir,
      bin_path=bin_path,
      use_node=use_node
    )

    if result[0]:

      if self.modified == True:
        self.searching = False
        return


          
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

      view = sublime.active_window().active_view()
      sel = view.sel()[0]

      if view.substr(view.word(sel)).strip() :

        if self.modified == True:
          self.searching = False
          return
        
        sublime.active_window().active_view().run_command(
          'hide_auto_complete'
        )
        self.run_auto_complete()

    self.searching = False

  def on_text_command(self, view, command_name, args):
    sel = view.sel()[0]
    if not view.match_selector(
        sel.begin(),
        'source.js - string - comment'
    ):
      return

    if command_name == "left_delete" :
      self.modified = True
      self.searching = False
      scope = view.scope_name(view.sel()[0].begin()-1).strip()
      if scope.endswith(" punctuation.accessor.js") or scope.endswith(" keyword.operator.accessor.js"):
        sublime.active_window().active_view().run_command(
          'hide_auto_complete'
        )

    elif command_name == "drag_select" :
      if view.sel()[0].begin() < view.word(view.sel()[0].begin()).end():
        self.modified = True
        self.searching = False

    elif command_name == "run_macro_file" and 'file' in args and args.get('file').endswith("Delete Left Right.sublime-macro"):
      scope = view.scope_name(view.sel()[0].begin()).strip()
      if popupManager.isVisible("hint_parameters") and ( scope.endswith(" punctuation.section.group.js") or scope.endswith(" meta.group.braces.round.function.arguments.js") ):
        view.hide_popup()

  def on_post_text_command(self, view, command_name, args):
    sel = view.sel()[0]
    if not view.match_selector(
        sel.begin(),
        'source.js - comment'
    ):
      return

    scope = view.scope_name(view.sel()[0].end()).strip()

    if command_name == "insert_snippet" and ( scope.endswith(" punctuation.section.group.js") or scope.endswith(" meta.group.braces.round.function.arguments.js") ):
      view.run_command("show_hint_parameters", args={"popup_position_on_point": True})

    elif ( command_name == "commit_completion" or command_name == "next_field" or command_name == "prev_field" ) and ( scope.endswith(" punctuation.section.group.js") or scope.endswith(" punctuation.separator.comma.js") or scope.endswith(" meta.group.braces.round.js") or scope.endswith(" meta.brace.round.end.js") ):
      view.run_command("show_hint_parameters", args={"popup_position_on_point": True})

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

    scope1 = view.scope_name(sel.begin()-1).strip()
    scope2 = view.scope_name(sel.begin()-2).strip()

    if (scope1.endswith(" punctuation.accessor.js") or scope1.endswith(" keyword.operator.accessor.js")) and not (scope2.endswith(" punctuation.accessor.js") or scope2.endswith(" keyword.operator.accessor.js")) and view.substr(sel.begin()-2).strip() :
      
      locations = list()
      locations.append(sel.begin())

      if not self.searching:
        self.searching = True
        self.modified = False
      else: 
        return 

      sublime.set_timeout_async(
        lambda: self.on_query_completions_async(
          view, "", locations
        )
      )
