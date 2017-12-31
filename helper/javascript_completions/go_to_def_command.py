import sublime, sublime_plugin
import os



class go_to_defCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    if args and "point" in args :
      point = args["point"]
    else :
      point = view.sel()[0].begin()
    point = view.word(point).begin()
    self.go_to_def(view, point)

  def go_to_def(self, view, point):
    view = sublime.active_window().active_view()
    view.sel().clear()
    #sublime.active_window().run_command("goto_definition")

    #if view.sel()[0].begin() == point :
    # try flow get-def
    sublime.set_timeout_async(lambda : self.find_def(view, point))

  def find_def(self, view, point) :
    view.sel().add(point)

    deps = flow_parse_cli_dependencies(view)
    
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
        'get-def',
        '--from', 'sublime_text',
        '--root', deps.project_root,
        '--json',
        ':temp_file',
        str(deps.row + 1), str(deps.col + 1)
      ],
      is_from_bin=is_from_bin,
      use_fp_temp=True, 
      fp_temp_contents=deps.contents, 
      is_output_json=True,
      use_only_filename_view_flow=True,
      chdir=chdir,
      bin_path=bin_path,
      use_node=use_node
    )

    if result[0] :
      row = result[1]["line"]-1
      col = result[1]["start"]-1
      if result[1]["path"] != "-" and os.path.isfile(result[1]["path"]) :
        view = sublime.active_window().open_file(result[1]["path"])     
      Util.go_to_centered(view, row, col)

  def is_enabled(self):
    view = self.view
    if not Util.selection_in_js_scope(view):
      return False
    return True

  def is_visible(self):
    view = self.view
    if not Util.selection_in_js_scope(view, -1, "- string - comment"):
      return False
    return True