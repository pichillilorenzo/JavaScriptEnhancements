import sublime, sublime_plugin
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
          str(deps.row + 1), str(deps.col + 1)
        ],
        is_from_bin=True,
        use_fp_temp=True, 
        fp_temp_contents=deps.contents, 
        is_output_json=True
      )
      if result[0] :
        row = result[1]["line"]-1
        col = result[1]["start"]-1
        if result[1]["path"] != "-" :
          view = sublime.active_window().open_file(result[1]["path"])     
        sublime.set_timeout_async(lambda: self.go_to_def_at_center(view, row, col))

  def go_to_def_at_center(self, view, row, col):
    while view.is_loading() :
      time.sleep(.1)
    point = view.text_point(row, col)
    view.sel().clear()
    view.sel().add(point)
    view.show_at_center(point)

  def is_enabled(self):
    view = self.view
    sel = view.sel()[0]
    if not view.match_selector(
        sel.begin(),
        'source.js - string - comment'
    ):
      return False
    return True

  def is_visible(self):
    view = self.view
    sel = view.sel()[0]
    if not view.match_selector(
        sel.begin(),
        'source.js - string - comment'
    ):
      return False
    return True