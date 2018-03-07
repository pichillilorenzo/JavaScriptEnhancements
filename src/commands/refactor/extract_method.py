import sublime, sublime_plugin
import os
from ...libs import util
from ...libs import FlowCLI
from ...libs import window_view_manager

class JavascriptEnhancementsRefactorExtractMethodCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    selection = view.sel()[0]
    selection = util.trim_region(view, selection)
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

    flow_cli = FlowCLI(view)
    result = flow_cli.ast()

    if inputs["scope"] == "Class method":

      if result[0]:
        if "body" in result[1]:
          body = result[1]["body"]
          items = util.nested_lookup("type", ["ClassBody"], body)
          last_block_statement = None
          last_item = None
          region = None

          for item in items:
            region = sublime.Region(int(item["range"][0]), int(item["range"][1]))
            if region.contains(selection):
              prev_line_is_empty = util.prev_line_is_empty(view, sublime.Region(region.end(), region.end()))
              space = util.get_whitespace_from_line_begin(view, selection)
              space_before = ("\n\t" if not prev_line_is_empty else "\t")
              space_after = "\n\n"
              new_text = util.replace_with_tab(view, selection, space_before+function_name+" "+parameters+" {\n", "\n\t}" + space_after, add_to_each_line_before="\t", lstrip=True)
             
              view.insert(edit, region.end() - 1, new_text)
              view.erase(edit, selection)
              view.insert(edit, selection.begin(), "this." + function_name + parameters)

              break

    elif inputs["scope"] == "Current scope":

      if result[0]:
        if "body" in result[1]:
          body = result[1]["body"]
          items = util.nested_lookup("type", ["BlockStatement"], body)
          last_block_statement = None
          last_item = None
          region = None

          for item in items:
            r = sublime.Region(int(item["range"][0]), int(item["range"][1]))
            if r.contains(selection):
              last_block_statement = r
              last_item = item

          if last_block_statement:
            for item in last_item["body"]:
              r = sublime.Region(int(item["range"][0]), int(item["range"][1]))
              if r.contains(selection):
                region = r
                break

            if not region:
              region = last_block_statement

          else:
            for item in body:
              r = sublime.Region(int(item["range"][0]), int(item["range"][1]))
              if r.contains(selection) or r.intersects(selection):
                region = r
                break

          if region: 
            prev_line_is_empty = util.prev_line_is_empty(view, selection)
            space = util.get_whitespace_from_line_begin(view, selection)
            space_before = ("\n" + space if not prev_line_is_empty else ( space if view.substr(region).startswith("{") else ""))
            space_after = (( "\n" + space if not view.substr(region).startswith("{") else "\n") if not prev_line_is_empty else "\n" + space)
            new_text = util.replace_with_tab(view, selection, space_before+"function "+function_name+" "+parameters+" {\n"+space, "\n"+space+"}" + space_after)
            contains_this = util.region_contains_scope(view, selection, "variable.language.this.js")

            view.erase(edit, selection)
            if contains_this:
              view.insert(edit, selection.begin(), function_name+".call(this"+(", "+parameters[1:-1] if parameters[1:-1].strip() else "")+")" )
            else:
              view.insert(edit, selection.begin(), function_name+parameters)
            view.insert(edit, (view.full_line(region.begin()).end() if view.substr(region).startswith("{") else region.begin()), new_text)

    elif inputs["scope"] == "Global scope":

      if result[0]:
        if "body" in result[1]:
          body = result[1]["body"]
          items_sorted = sorted(body, key=lambda item: int(item["range"][0]))
          region = None

          for item in items_sorted:
            r = sublime.Region(int(item["range"][0]), int(item["range"][1]))
            if r.contains(selection) or r.intersects(selection):
              region = r
              break

          if region: 

            prev_line_is_empty = util.prev_line_is_empty(view, region)
            space_before = ("\n" if not prev_line_is_empty else "")
            new_text = util.replace_with_tab(view, selection, space_before+"function "+function_name+" "+parameters+" {\n", "\n}\n\n", lstrip=True)
            contains_this = util.region_contains_scope(view, selection, "variable.language.this.js")

            view.erase(edit, selection) 
            if contains_this:
              view.insert(edit, selection.begin(), function_name+".call(this"+(", "+parameters[1:-1] if parameters[1:-1].strip() else "")+")" )
            else:
              view.insert(edit, selection.begin(), function_name+parameters)
            view.insert(edit, region.begin(), new_text)

    window_view_manager.close(view.id())

  def is_enabled(self, **args) :
    view = self.view
    if not util.selection_in_js_scope(view) :
      return False
    selection = view.sel()[0]
    return selection.begin() != selection.end()

  def is_visible(self, **args) :
    view = self.view
    if not util.selection_in_js_scope(view) :
      return False
    selection = view.sel()[0]
    return selection.begin() != selection.end()
