import sublime, sublime_plugin

class RefactorExtractMethodCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view

    inputs = args.get("inputs")
    scope = view.scope_name(view.sel()[0].begin())
    space = Util.get_whitespace_from_line_begin(view, view.sel()[0])
    function_name = inputs["function_name"].strip()
    parameters = inputs["parameters"].strip()
    if not parameters.startswith("("):
      parameters = "(" + parameters
    if not parameters.endswith(")"):
      parameters += ")"

    if inputs["scope"] == "Class method":

      view.replace(edit, view.sel()[0], "this."+function_name+parameters)
      region_class = Util.get_region_scope_first_match(view, scope, view.sel()[0], 'meta.class.js')["region"]
      new_text = Util.replace_with_tab(view, view.sel()[0], ("\t\n" if not Util.prev_line_is_empty(view, sublime.Region(region_class.end(), region_class.end())) else "")+"\t"+function_name+" "+parameters+" {\n\t", "\n\t}\n")

      view.insert(edit, region_class.end()-1, new_text)

    elif inputs["scope"] == "Current Scope":

      new_text = Util.replace_with_tab(view, view.sel()[0], "function "+function_name+" "+parameters+" {\n"+space, "\n"+space+"}\n"+space)

      if Util.region_contains_scope(view, view.sel()[0], "variable.language.this.js"):
        view.replace(edit, view.sel()[0], function_name+".call(this"+(", "+parameters[1:-1] if parameters[1:-1].strip() else "")+")" )
      else:
        view.replace(edit, view.sel()[0], function_name+parameters)
      view.insert(edit, view.sel()[0].begin(), new_text)

    elif inputs["scope"] == "Global scope":

      region_class = Util.get_region_scope_first_match(view, scope, view.sel()[0], scope.split(" ")[1])["region"]
      space = Util.get_whitespace_from_line_begin(view, region_class)
      new_text = Util.replace_with_tab(view, view.sel()[0], "function "+function_name+" "+parameters+" {\n"+space, "\n"+space+"}\n\n"+space)

      if Util.region_contains_scope(view, view.sel()[0], "variable.language.this.js"):
        view.replace(edit, view.sel()[0], function_name+".call(this"+(", "+parameters[1:-1] if parameters[1:-1].strip() else "")+")" )
      else:
        view.replace(edit, view.sel()[0], function_name+parameters)
      view.insert(edit, region_class.begin(), new_text)

  def is_enabled(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    selection = view.sel()[0]
    return selection.begin() != selection.end()

  def is_visible(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    selection = view.sel()[0]
    return selection.begin() != selection.end()
