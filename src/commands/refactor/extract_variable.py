import sublime, sublime_plugin
import os
from ...libs import util
from ...libs import FlowCLI

class JavascriptEnhancementsRefactorExtractVariableCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    selection = view.sel()[0]
    contents = view.substr(selection).strip()
    contents = contents[:-1] if contents[-1] == ";" else contents
    variable_name = "new_var"

    flow_cli = FlowCLI(view)
    result = flow_cli.ast(contents=contents)

    if result[0] and not result[1]["errors"] and result[1]["body"] and "type" in result[1]["body"][0] and result[1]["body"][0]["type"] == "ExpressionStatement":

      result = flow_cli.ast()

      if result[0]:
        if "body" in result[1]:
          body = result[1]["body"]
          items = util.nested_lookup("type", ["BlockStatement"], body)
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
            prev_line_is_empty = util.prev_line_is_empty(view, region)

            space = util.get_whitespace_from_line_begin(view, region)
            str_assignement = ("\n" + space if not prev_line_is_empty else "") + "let " + variable_name + " = " + contents + "\n" + space

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

            variable_kind = ["let", "const", "var"]
            whitespace_length = len("\n" + space if not prev_line_is_empty else "")
            view.window().show_quick_panel(variable_kind, None, 0, 0, lambda index: self.view.run_command("javascript_enhancements_replace_text_view", args={"start": region.begin() + whitespace_length, "end": region.begin() + whitespace_length + len(view.substr(view.word(region.begin() + whitespace_length))) , "text": variable_kind[index]}))

      else:
        sublime.error_message("Cannot introduce variable. Some problems occured.")

    else:
      sublime.error_message("Cannot introduce variable. Selection does not form an ExpressionStatement.")

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
