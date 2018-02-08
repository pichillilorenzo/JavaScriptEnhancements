import sublime, sublime_plugin

class surround_withCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    selections = view.sel()
    case = args.get("case")
    if case == "if_else_statement" :
      if len(selections) != 2 :
        return

      sel_1 = Util.trim_Region(view, selections[0])
      prev_line_is_empty = Util.prev_line_is_empty(view, sel_1)
      space_1 = Util.get_whitespace_from_line_begin(view, sel_1)
      space_before = (space_1 + "\n" + space_1 if not prev_line_is_empty else "")
      new_text = Util.replace_with_tab(view, sel_1, space_before + "if (bool) {\n" + space_1, "\n" + space_1 + "} ")
      view.replace(edit, sel_1, new_text)

      sel_2 = Util.trim_Region(view, selections[1])
      next_line_is_empty = Util.next_line_is_empty(view, sel_2)
      space_2 = Util.get_whitespace_from_line_begin(view, sel_2)
      space_after = ("\n" + space_2 if not next_line_is_empty else "")
      new_text = Util.replace_with_tab(view, sel_2, " else {\n" + space_2, "\n" + space_2 + "}" + space_after)
      view.replace(edit, sel_2, new_text)

      new_selection = sublime.Region(sel_1.begin() + len(space_before+"if ("), sel_1.begin() + len(space_before+"if (bool"))
      view.sel().clear()
      view.sel().add(new_selection)
      
    else :
      for selection in selections :
        selection = Util.trim_Region(view, selection)
        if view.substr(selection).strip() == "" :
          continue

        prev_line_is_empty = Util.prev_line_is_empty(view, selection)
        next_line_is_empty = Util.next_line_is_empty(view, selection)
        space = Util.get_whitespace_from_line_begin(view, selection)
        space_before = (space + "\n" + space if not prev_line_is_empty else "")
        space_after = ("\n" + space if not next_line_is_empty else "")
        new_text = ""
        new_selection = None

        if case == "if_statement" :
          new_text = Util.replace_with_tab(view, selection, space_before+"if (bool) {\n"+space, "\n"+space+"}" + space_after)
          new_selection = sublime.Region(selection.begin() + len(space_before+"if ("), selection.begin() + len(space_before+"if (bool"))

        elif case == "while_statement" :
          new_text = Util.replace_with_tab(view, selection, space_before+"while (bool) {\n"+space, "\n"+space+"}" + space_after)
          new_selection = sublime.Region(selection.begin() + len(space_before+"while ("), selection.begin() + len(space_before+"while (bool"))

        elif case == "do_while_statement" :
          new_text = Util.replace_with_tab(view, selection, space_before+"do {\n"+space, "\n"+space+"} while (bool)" + space_after)
          new_selection = sublime.Region(selection.begin() + len(new_text) - len("ool)"), selection.begin() + len(new_text))

        elif case == "for_statement" :
          new_text = Util.replace_with_tab(view, selection, space_before+"for ( ; bool ; ) {\n"+space, "\n"+space+"}" + space_after)
          new_selection = sublime.Region(selection.begin() + len(space_before+"for ( ; "), selection.begin() + len(space_before+"for ( ; bool"))

        elif case == "try_catch_statement" :
          new_text = Util.replace_with_tab(view, selection, space_before+"try {\n"+space, "\n"+space+"} catch (e) {\n"+space+"\n"+space+"}" + space_after)
          new_selection = sublime.Region(selection.begin() + len(new_text) - len(") {\n"+space+"\n"+space+"}" + space_after), selection.begin() + len(new_text) - len(" {\n"+space+"\n"+space+"}" + space_after))

        elif case == "try_finally_statement" :
          new_text = Util.replace_with_tab(view, selection, space_before+"try {\n"+space, "\n"+space+"} finally {\n"+space+"\n"+space+"}" + space_after)
          new_selection = sublime.Region(selection.begin() + len(space_before+"try {"), selection.begin() + len(space_before+"try {"))

        elif case == "try_catch_finally_statement" :
          new_text = Util.replace_with_tab(view, selection, space_before+"try {\n"+space, "\n"+space+"} catch (e) {\n"+space+"\n"+space+"} finally {\n"+space+"\n"+space+"}" + space_after)
          new_selection = sublime.Region(selection.begin() + len(new_text) - len(") {\n"+space+"\n"+space+"} finally {\n"+space+"\n"+space+"}" + space_after + space_after), selection.begin() + len(new_text) - len(" {\n"+space+"\n"+space+"} finally {\n"+space+"\n"+space+"}" + space_after + space_after))

        elif case == "function" :
          new_text = Util.replace_with_tab(view, selection, space_before+"function func_name () {\n"+space, "\n"+space+"}" + space_after)
          new_selection = sublime.Region(selection.begin() + len(space_before+"function "), selection.begin() + len(space_before+"function func_name"))

        elif case == "anonymous_function" :
          new_text = Util.replace_with_tab(view, selection, space_before+"function () {\n"+space, "\n"+space+"}" + space_after)
          new_selection = sublime.Region(selection.begin() + len(space_before+"function () {"), selection.begin() + len(space_before+"function () {"))

        elif case == "arrow_function" :
          new_text = Util.replace_with_tab(view, selection, space_before+"() => {\n"+space, "\n"+space+"}" + space_after)
          new_selection = sublime.Region(selection.begin() + len(space_before+"() => {"), selection.begin() + len(space_before+"() => {"))

        elif case == "async_function" :
          new_text = Util.replace_with_tab(view, selection, space_before+"async function func_name () {\n"+space, "\n"+space+"}" + space_after)
          new_selection = sublime.Region(selection.begin() + len(space_before+"async function "), selection.begin() + len(space_before+"async function func_name"))

        elif case == "iife_function" :
          new_text = Util.replace_with_tab(view, selection, space_before+"(function () {\n"+space, "\n"+space+"})()" + space_after)
          new_selection = sublime.Region(selection.begin() + len(space_before+"(function () {"), selection.begin() + len(space_before+"(function () {"))

        elif case == "generator_function" :
          new_text = Util.replace_with_tab(view, selection, space_before+"function* func_name () {\n"+space, "\n"+space+"}" + space_after)
          new_selection = sublime.Region(selection.begin() + len(space_before+"function* "), selection.begin() + len(space_before+"function* func_name"))

        elif case == "block" :
          new_text = Util.replace_with_tab(view, selection, space_before+"{\n"+space, "\n"+space+"}" + space_after)
          new_selection = sublime.Region(selection.begin() + len(space_before+"{"), selection.begin() + len(space_before+"{"))

        view.erase(edit, selection)
        view.insert(edit, selection.begin(), new_text)
        view.sel().clear()
        view.sel().add(new_selection)
          
  def is_enabled(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    selections = view.sel()
    for selection in selections :
      if view.substr(selection).strip() != "" :
        return True
    return False

  def is_visible(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    selections = view.sel()
    for selection in selections :
      if view.substr(selection).strip() != "" :
        return True
    return False