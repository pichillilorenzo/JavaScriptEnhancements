import sublime, sublime_plugin

class RefactorExtractMethodCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    selection = view.sel()[0]
    selection = Util.trim_Region(view, selection)
    inputs = args.get("inputs")
    scope = view.scope_name(selection.begin()).strip()
    function_name = inputs["function_name"].strip()
    parameters = inputs["parameters"].strip()
    if not parameters.startswith("("):
      parameters = "(" + parameters
    if not parameters.endswith(")"):
      parameters += ")"

    if not function_name:
      sublime.error_message("Cannot create function. Function name is empty.")
      return 

    if inputs["scope"] == "Class method":

      view.replace(edit, selection, "this."+function_name+parameters)
      region_class = Util.get_region_scope_first_match(view, scope, selection, 'meta.class.js')["region"]
      new_text = Util.replace_with_tab(view, selection, ("\t\n" if not Util.prev_line_is_empty(view, sublime.Region(region_class.end(), region_class.end())) else "")+"\t"+function_name+" "+parameters+" {\n\t", "\n\t}\n")

      view.insert(edit, region_class.end()-1, new_text)

    elif inputs["scope"] == "Current scope":

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

      node = NodeJS(check_local=True)
      
      result = node.execute_check_output(
        flow_cli,
        [
          'ast',
          '--from', 'sublime_text'
        ],
        is_from_bin=is_from_bin,
        use_fp_temp=True, 
        fp_temp_contents=view.substr(sublime.Region(0, view.size())), 
        is_output_json=True,
        chdir=chdir,
        bin_path=bin_path,
        use_node=use_node
      )

      if result[0]:
        if "body" in result[1]:
          body = result[1]["body"]
          items = Util.nested_lookup("type", ["BlockStatement"], body)
          last_block_statement = None
          last_item = None
          region = None

          for item in items:
            region = sublime.Region(int(item["range"][0]), int(item["range"][1]))
            if region.contains(selection):
              last_block_statement = region
              last_item = item

          if last_block_statement:
            for item in last_item["body"]:
              r = sublime.Region(int(item["range"][0]), int(item["range"][1]))
              if r.contains(selection):
                region = r
                break
          else:
            for item in body:
              r = sublime.Region(int(item["range"][0]), int(item["range"][1]))
              if r.contains(selection) or r.intersects(selection):
                region = r
                break

          if region: 
            prev_line_is_empty = Util.prev_line_is_empty(view, selection)
            next_line_is_empty = Util.next_line_is_empty(view, selection)
            space = Util.get_whitespace_from_line_begin(view, selection)
            space_before = ("\n" + space if not prev_line_is_empty else "")
            space_after = "\n" + space
            new_text = Util.replace_with_tab(view, selection, space_before+"function "+function_name+" "+parameters+" {\n"+space, "\n"+space+"}" + space_after)

            view.erase(edit, selection)
            if Util.region_contains_scope(view, selection, "variable.language.this.js"):
              view.insert(edit, selection.begin(), function_name+".call(this"+(", "+parameters[1:-1] if parameters[1:-1].strip() else "")+")" )
            else:
              view.insert(edit, selection.begin(), function_name+parameters)
            view.insert(edit, region.begin() + (1 if view.substr(region.begin()) == "{" else 0), new_text)

    elif inputs["scope"] == "Global scope":

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

      node = NodeJS(check_local=True)
      
      result = node.execute_check_output(
        flow_cli,
        [
          'ast',
          '--from', 'sublime_text'
        ],
        is_from_bin=is_from_bin,
        use_fp_temp=True, 
        fp_temp_contents=view.substr(sublime.Region(0, view.size())), 
        is_output_json=True,
        chdir=chdir,
        bin_path=bin_path,
        use_node=use_node
      )

      if result[0]:
        if "body" in result[1]:
          body = result[1]["body"]
          items = Util.nested_lookup("type", ["BlockStatement"], body, return_parent=True)[::-1]
          region = None

          for item in items:
            r = sublime.Region(int(item["range"][0]), int(item["range"][1]))
            if r.contains(selection):
              region = r
              break
          else:
            for item in body:
              r = sublime.Region(int(item["range"][0]), int(item["range"][1]))
              if r.contains(selection) or r.intersects(selection):
                region = r
                break

          if region: 

            prev_line_is_empty = Util.prev_line_is_empty(view, region)
            next_line_is_empty = Util.next_line_is_empty(view, region)
            space_before = ("\n" if not prev_line_is_empty else "")

            new_text = Util.replace_with_tab(view, selection, space_before+"function "+function_name+" "+parameters+" {\n", "\n}\n\n", lstrip=True)

            view.erase(edit, selection)
            view.insert(edit, region.begin(), new_text)
            if Util.region_contains_scope(view, selection, "variable.language.this.js"):
              view.insert(edit, selection.begin() + len(Util.convert_tabs_using_tab_size(view, new_text)), function_name+".call(this"+(", "+parameters[1:-1] if parameters[1:-1].strip() else "")+")" )
            else:
              view.insert(edit, selection.begin() + len(Util.convert_tabs_using_tab_size(view, new_text)), function_name+parameters)

    windowViewManager.close(view.id())

  def is_enabled(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    selection = view.sel()[0]
    return selection.begin() != selection.end()

  def is_visible(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    selection = view.sel()[0]
    return selection.begin() != selection.end()
