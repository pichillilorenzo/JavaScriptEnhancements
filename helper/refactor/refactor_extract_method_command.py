import sublime, sublime_plugin

class refactorExtractMethodCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    inputs = args.get("inputs")
    scope = view.scope_name(view.sel()[0].begin())
    space = Util.get_whitespace_from_line_begin(view, view.sel()[0])

    if inputs["scope"] == "Class method":

      new_text = Util.replace_with_tab(view, view.sel()[0], "\t\n\t"+inputs["function_name"]+" "+inputs["parameters"]+" {\n\t", "\n\t}\n")

      view.replace(edit, view.sel()[0], "this."+inputs["function_name"]+inputs["parameters"])
      region_class = Util.get_region_scope_first_match(view, scope, view.sel()[0], 'meta.class.js')["region"]
      view.insert(edit, region_class.end()-1, new_text)

    elif inputs["scope"] == "Current Scope":

      new_text = Util.replace_with_tab(view, view.sel()[0], "function "+inputs["function_name"]+" "+inputs["parameters"]+" {\n"+space, "\n"+space+"}\n"+space)

      if Util.region_contains_scope(view, view.sel()[0], "variable.language.this.js"):
        view.replace(edit, view.sel()[0], inputs["function_name"]+".call(this"+(", "+inputs["parameters"][1:-1] if inputs["parameters"][1:-1].strip() else "")+")" )
      else:
        view.replace(edit, view.sel()[0], inputs["function_name"]+inputs["parameters"])
      view.insert(edit, view.sel()[0].begin(), new_text)

    elif inputs["scope"] == "Global scope":

      region_class = Util.get_region_scope_first_match(view, scope, view.sel()[0], scope.split(" ")[1])["region"]
      space = Util.get_whitespace_from_line_begin(view, region_class)
      new_text = Util.replace_with_tab(view, view.sel()[0], "function "+inputs["function_name"]+" "+inputs["parameters"]+" {\n"+space, "\n"+space+"}\n\n"+space)

      if Util.region_contains_scope(view, view.sel()[0], "variable.language.this.js"):
        view.replace(edit, view.sel()[0], inputs["function_name"]+".call(this"+(", "+inputs["parameters"][1:-1] if inputs["parameters"][1:-1].strip() else "")+")" )
      else:
        view.replace(edit, view.sel()[0], inputs["function_name"]+inputs["parameters"])
      view.insert(edit, region_class.begin(), new_text)

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
