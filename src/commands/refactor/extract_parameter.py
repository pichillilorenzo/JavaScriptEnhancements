import sublime, sublime_plugin
import os
from ...libs import util
from ...libs import FlowCLI

class JavascriptEnhancementsRefactorExtractParameterCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    selection = view.sel()[0]
    contents = view.substr(selection).strip()
    contents = contents[:-1] if contents[-1] == ";" else contents
    scope = view.scope_name(selection.begin()).strip()
    region_scope = None
    is_babel = False

    if "meta.block.js" in scope:
      region_scope = util.get_region_scope_last_match(view, scope, selection, "meta.block.js")
    else:
      is_babel = True
      region_scope = util.get_region_scope_last_match(view, scope, selection, "meta.group.braces.curly.js")

    if not region_scope:
      return

    flow_cli = FlowCLI(view)
    result = flow_cli.ast(contents=contents)

    if result[0] and not result[1]["errors"] and result[1]["body"] and "type" in result[1]["body"][0] and result[1]["body"][0]["type"] == "ExpressionStatement":

      region = region_scope["region"]
      point = region.begin()
      is_arrow_function = False
      variable_need_brackets = ""

      while not ( 
        view.scope_name(point).strip().endswith("punctuation.section.group.end.js") if not is_babel else view.scope_name(point).strip().endswith("punctuation.definition.parameters.end.js") 
        ) and point >= 0:

        point_scope = view.scope_name(point).strip()
        if point_scope == "source.js":
          return

        # support for arrow_function
        if not is_arrow_function:
          if point_scope.endswith("storage.type.function.arrow.js"):
            is_arrow_function = True
        elif point_scope.endswith("variable.parameter.function.js"):
          variable_need_brackets = view.substr(view.word(point))
          point = view.word(point).begin()
          break

        point -= 1

      if point >= 0:

        first_parameter = True
        point_begin = point
        while point_begin >= 0:
          word = view.word(point_begin)
          str_word = view.substr(view.word(point_begin)).strip()
          if str_word == "" or str_word == ")":
            pass
          elif str_word.startswith("("):
            break
          else:
            first_parameter = False
            break
          point_begin = word.begin()

        variable_name = "new_var"
        str_parameter = (", " if not first_parameter else "") + variable_name + " = " + contents

        view.erase(edit, selection)
        view.insert(edit, selection.begin(), variable_name)

        if variable_need_brackets:
          str_parameter = "(" + variable_need_brackets + str_parameter + ")"
          view.erase(edit, sublime.Region(point, point+len(variable_need_brackets)))
        view.insert(edit, point, str_parameter)

        view.sel().clear()
        view.sel().add_all([

          sublime.Region(
            selection.begin()+len(str_parameter)-len(variable_need_brackets), 
            selection.begin()+len(str_parameter)+len(variable_name)-len(variable_need_brackets)
          ),

          # +2 is for the ", " string at the begin of str_parameter, +1 is for "(" in case of variable_need_brackets
          sublime.Region(
            point + (2 if not first_parameter else 0) + (len(variable_need_brackets)+1 if variable_need_brackets else 0),
            point + (2 if not first_parameter else 0) + len(variable_name) + (len(variable_need_brackets)+1 if variable_need_brackets else 0)
          )

        ])

    else:
      sublime.error_message("Cannot introduce parameter. Selection does not form an ExpressionStatement.")

  def is_enabled(self, **args) :
    view = self.view
    if not util.selection_in_js_scope(view) :
      return False
    selection = view.sel()[0]

    if selection.begin() == selection.end():
      return False

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

    if selection.begin() == selection.end():
      return False

    scope = view.scope_name(selection.begin()).strip()
    if "meta.block.js" in scope:
      region_scope = util.get_region_scope_last_match(view, scope, selection, "meta.block.js")
    else:
      region_scope = util.get_region_scope_last_match(view, scope, selection, "meta.group.braces.curly.js")

    if not region_scope:
      return False

    return True