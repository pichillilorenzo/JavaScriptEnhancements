import sublime, sublime_plugin

class RefactorConvertToArrowFunctionCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    selection = view.sel()[0]

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

      body = result[1]["body"]
      items = Util.nested_lookup("type", ["FunctionExpression"], body)
      for item in items:
        region = sublime.Region(int(item["range"][0]), int(item["range"][1]))
        if region.contains(selection):
          text = view.substr(region)
          
          if not text.startswith("function"):
            return

          text = text[8:].lstrip()
          block_statement_region = sublime.Region(int(item["body"]["range"][0]), int(item["body"]["range"][1]))
          block_statement = view.substr(block_statement_region)
          index = text.index(block_statement)

          while text[index - 1] == " ":
             text = text[0:index - 1] + text[index:]
             index = index - 1 

          text = text[0:index] + " => " + text[index:]
          view.replace(edit, region, text)

          break

    else:
      sublime.error_message("Cannot convert the function. Some problems occured.")

  def is_enabled(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    selection = view.sel()[0]

    scope = view.scope_name(selection.begin()).strip()
    if "meta.block.js" in scope:
      region_scope = Util.get_region_scope_last_match(view, scope, selection, "meta.block.js")
    else:
      region_scope = Util.get_region_scope_last_match(view, scope, selection, "meta.group.braces.curly.js")

    if not region_scope:
      return False

    return True

  def is_visible(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    selection = view.sel()[0]

    scope = view.scope_name(selection.begin()).strip()
    if "meta.block.js" in scope:
      region_scope = Util.get_region_scope_last_match(view, scope, selection, "meta.block.js")
    else:
      region_scope = Util.get_region_scope_last_match(view, scope, selection, "meta.group.braces.curly.js")

    if not region_scope:
      return False

    return True