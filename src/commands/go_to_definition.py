import sublime, sublime_plugin
import os
from ..libs import NodeJS
from ..libs import util
from ..libs import FlowCLI

class JavascriptEnhancementsGoToDefinitionCommand(sublime_plugin.TextCommand):
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

    flow_cli = FlowCLI(view)
    result = flow_cli.get_def()

    if result[0] :
      row = result[1]["line"] - 1
      col = result[1]["start"] - 1
      if row >= 0:
        if result[1]["path"] != "-" and os.path.isfile(result[1]["path"]) :
          view = sublime.active_window().open_file(result[1]["path"])     
        util.go_to_centered(view, row, col)

  def is_enabled(self, **args):
    view = self.view

    if args and "point" in args :
      point = args["point"]
    else :
      point = view.sel()[0].begin()
    point = view.word(point).begin()

    if not util.selection_in_js_scope(view, point):
      return False
    return True

  def is_visible(self, **args):
    view = self.view

    if args and "point" in args :
      point = args["point"]
    else :
      point = view.sel()[0].begin()
    point = view.word(point).begin()

    if not util.selection_in_js_scope(view, point, "- string - comment"):
      return False
    return True