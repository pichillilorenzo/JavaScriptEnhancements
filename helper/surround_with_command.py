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
      space_1 = Util.get_whitespace_from_line_begin(view, sel_1)
      new_text = Util.replace_with_tab(view, sel_1, space_1+"\n"+space_1+"if (bool) {\n"+space_1, "\n"+space_1+"} ")
      view.replace(edit, sel_1, new_text.strip())

      sel_2 = Util.trim_Region(view, selections[1])
      space_2 = Util.get_whitespace_from_line_begin(view, sel_2)
      new_text = Util.replace_with_tab(view, sel_2, " else {\n"+space_2, "\n"+space_2+"}\n"+space_2)
      view.replace(edit, sel_2, new_text.strip())
    else :
      for selection in selections :
        selection = Util.trim_Region(view, selection)
        if view.substr(selection).strip() == "" :
          continue
        space = Util.get_whitespace_from_line_begin(view, selection)

        if case == "if_statement" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"if (bool) {\n"+space, "\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "while_statement" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"while (bool) {\n"+space, "\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "do_while_statement" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"do {\n"+space, "\n"+space+"} while (bool);\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "for_statement" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"for ( ; bool ; ) {\n"+space, "\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "try_catch_statement" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"try {\n"+space, "\n"+space+"} catch (e) {\n"+space+"\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "try_finally_statement" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"try {\n"+space, "\n"+space+"} finally {\n"+space+"\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "try_catch_finally_statement" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"try {\n"+space, "\n"+space+"} catch (e) {\n"+space+"\n"+space+"} finally {\n"+space+"\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "function" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"function func_name () {\n"+space, "\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "anonymous_function" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"function () {\n"+space, "\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "arrow_function" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"() => {\n"+space, "\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "async_function" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"async function func_name () {\n"+space, "\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "iife_function" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"(function () {\n"+space, "\n"+space+"})()\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "block" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"{\n"+space, "\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)
          
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