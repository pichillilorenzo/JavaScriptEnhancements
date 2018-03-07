import sublime, sublime_plugin
import os, traceback
from ...libs import util
from ...libs import FlowCLI

class JavascriptEnhancementsRefactorConvertToArrowFunctionCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    selection = view.sel()[0]

    flow_cli = FlowCLI(view)
    result = flow_cli.ast()

    if result[0]:

      body = result[1]["body"]
      items = util.nested_lookup("type", ["FunctionExpression"], body)
      for item in items:
        region = sublime.Region(int(item["range"][0]), int(item["range"][1]))
        if region.contains(selection):
          text = view.substr(region)

          if not text.startswith("function"):
            return

          index_begin_parameter = 8
          text = text[index_begin_parameter:].lstrip()
          while text[0] != "(" and len(text) > 0:
            text = text[1:].lstrip()

          block_statement_region = sublime.Region(int(item["body"]["range"][0]), int(item["body"]["range"][1]))
          block_statement = view.substr(block_statement_region)
          index = text.index(block_statement)

          while text[index - 1] == " " and index - 1 >= 0:
             text = text[0:index - 1] + text[index:]
             index = index - 1 

          text = text[0:index] + " => " + text[index:]
          view.replace(edit, region, text)

          break

    else:
      sublime.error_message("Cannot convert the function. Some problems occured.")

  def is_enabled(self, **args) :
    view = self.view
    if not util.selection_in_js_scope(view) :
      return False
    selection = view.sel()[0]

    scope = view.scope_name(selection.begin()).strip()
    if "meta.block.js" in scope:
      region_scope = util.get_region_scope_last_match(view, scope, selection, "meta.block.js")
    else:
      region_scope = util.get_region_scope_last_match(view, scope, selection, "meta.group.braces.curly.js")

    if not region_scope:
      return False

    return True

  def is_visible(self, **args) :
    view = self.view
    if not util.selection_in_js_scope(view) :
      return False
    selection = view.sel()[0]

    scope = view.scope_name(selection.begin()).strip()
    if "meta.block.js" in scope:
      region_scope = util.get_region_scope_last_match(view, scope, selection, "meta.block.js")
    else:
      region_scope = util.get_region_scope_last_match(view, scope, selection, "meta.group.braces.curly.js")

    if not region_scope:
      return False

    return True