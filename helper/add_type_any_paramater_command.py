add_type_any_parameter_list = []
class add_type_any_parameterCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    global add_type_any_parameter_list
    view = self.view
    params = []
    if not "recall" in args :
      params = view.find_by_selector("variable.parameter.function.js")
      add_type_any_parameter_list = params
    else :
      params = add_type_any_parameter_list

    if "recall" in args and args["recall"] >= 0 :
      args["recall"] = args["recall"] + 1

    if params :
      view.insert(edit, params[0].end() + ( args["recall"]*len("/* : any */") if "recall" in args else 0 ) , "/* : any */")
      del params[0]
      if not "recall" in args :
        view.run_command("add_type_any_parameter", {"recall" : 0})
      else :
        view.run_command("add_type_any_parameter", {"recall": args["recall"]})