import sublime, sublime_plugin

class RefactorCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    case = args.get("case")
    scope = view.scope_name(view.sel()[0].begin())

    if case == "move" :
      windowView = WindowView(title="Refactor - Move", use_compare_layout=True)
      windowView.addTitle(text="Refactor - Move")
      windowView.add(text="\n\n")
      windowView.addInput(value=view.file_name(), label="Move to: ", region_id="new_path")
      windowView.add(text="\n\n")
      windowView.addButton(text="PREVIEW", scope="javascriptenhancements.button_preview", callback=lambda view: self.view.run_command("refactor_move", args={"inputs": windowView.getInputs(), "preview": True}))
      windowView.add(text="  ")
      windowView.addButton(text="MOVE", scope="javascriptenhancements.button_ok", callback=lambda view: self.view.run_command("refactor_move", args={"inputs": windowView.getInputs(), "preview": False, "view_id_caller": self.view.id()}))
      windowView.add(text="  ")
      windowView.addCloseButton(text="CANCEL", scope="javascriptenhancements.button_cancel")
      windowView.add(text=" \n")

    elif case == "copy" :
      self.view.run_command("refactor_copy")

    elif case == "extract_method" :

      if view.sel()[0].begin() == view.sel()[0].end():
        return

      select_options = ['Global scope', 'Current Scope', 'Class method']
      if not view.match_selector(view.sel()[0].begin(), 'meta.class.js'):
        select_options.remove('Class method')
      if len(scope.split(" ")) < 2:
        select_options.remove('Global scope')
        
      windowView = WindowView(title="Refactor - Extract Method", use_compare_layout=True)
      windowView.addTitle(text="Refactor - Extract Method")
      windowView.add(text="\n\n")
      windowView.addInput(value="func", label="Function Name: ", region_id="function_name")
      windowView.add(text="\n")
      windowView.addInput(value="()", label="Parameters: ", region_id="parameters")
      windowView.add(text="\n")
      windowView.addSelect(default_option=0, options=select_options, label="Scope: ", region_id="scope")
      windowView.add(text="\n\n")
      windowView.addCloseButton(text="OK", scope="javascriptenhancements.button_ok", callback=lambda view: self.view.run_command("refactor_extract_method", args={"inputs": windowView.getInputs()}))
      windowView.add(text="        ")
      windowView.addCloseButton(text="CANCEL", scope="javascriptenhancements.button_cancel")
      windowView.add(text=" \n")

    elif case == "extract_parameter" :
      self.view.run_command("refactor_extract_parameter")

    elif case == "extract_variable" :
      self.view.run_command("refactor_extract_variable")

  def is_enabled(self, **args) :

    view = self.view
    return Util.selection_in_js_scope(view)

  def is_visible(self, **args) :
    view = self.view
    return Util.selection_in_js_scope(view)

${include refactor_move_command.py}

${include refactor_copy_command.py}

${include refactor_extract_method_command.py}

${include refactor_extract_parameter_command.py}

${include refactor_extract_variable_command.py}