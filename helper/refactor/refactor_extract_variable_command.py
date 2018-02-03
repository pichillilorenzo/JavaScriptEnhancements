import sublime, sublime_plugin

class RefactorExtractVariableCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    selection = view.sel()[0]
    content = view.substr(selection).strip()
    content = content[:-1] if content[-1] == ";" else content
    variable_name = "new_var"

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
      fp_temp_contents=content, 
      is_output_json=True,
      chdir=chdir,
      bin_path=bin_path,
      use_node=use_node
    )

    if result[0] and not result[1]["errors"] and result[1]["body"] and "type" in result[1]["body"][0] and result[1]["body"][0]["type"] == "ExpressionStatement":

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
              if r.contains(selection):
                region = r
                break
            
          if region: 
            prev_line_is_empty = Util.prev_line_is_empty(view, region)

            space = Util.get_whitespace_from_line_begin(view, region)
            str_assignement = ("\n" + space if not prev_line_is_empty else "") + "let " + variable_name + " = " + content + "\n" + space

            view.erase(edit, selection)
            view.insert(edit, selection.begin(), variable_name)
            view.insert(edit, region.begin(), str_assignement)

            view.sel().clear()
            view.sel().add_all([

              sublime.Region(
                selection.begin()+len(str_assignement), 
                selection.begin()+len(str_assignement)+len(variable_name)
              ),

              sublime.Region(
                region.begin() + len(("\n" + space if not prev_line_is_empty else "") + "let "), region.begin() + len(("\n" + space if not prev_line_is_empty else "") + "let ") + len(variable_name)
              )

            ])

      else:
        sublime.error_message("Cannot introduce variable. Some problems occured.")

    else:
      sublime.error_message("Cannot introduce variable. Selection does not form an ExpressionStatement.")

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
