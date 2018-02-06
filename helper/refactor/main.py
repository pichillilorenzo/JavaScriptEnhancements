import sublime, sublime_plugin

class RefactorCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    case = args.get("case")
    scope = view.scope_name(view.sel()[0].begin()).strip()

    if case == "safe_move" :
      windowView = WindowView(title="Refactor - Safe Move", use_compare_layout=True)
      windowView.addTitle(text="Refactor - Safe Move")
      windowView.add(text="\n\n")
      windowView.addInput(value=view.file_name(), label="Move to: ", region_id="new_path")
      windowView.add(text="\n\n")
      windowView.addButton(text="PREVIEW", scope="javascriptenhancements.button_preview", callback=lambda view: self.view.run_command("refactor_safe_move", args={"inputs": windowView.getInputs(), "preview": True}))
      windowView.add(text="  ")
      windowView.addButton(text="MOVE", scope="javascriptenhancements.button_ok", callback=lambda view: self.view.run_command("refactor_safe_move", args={"inputs": windowView.getInputs(), "preview": False, "view_id_caller": self.view.id()}))
      windowView.add(text="  ")
      windowView.addCloseButton(text="CANCEL", scope="javascriptenhancements.button_cancel", callback=lambda view: self.closePreview("Refactor - Safe Move Preview"))
      windowView.add(text=" \n")

    elif case == "safe_copy" :
      windowView = WindowView(title="Refactor - Safe Copy", use_compare_layout=True)
      windowView.addTitle(text="Refactor - Safe Copy")
      windowView.add(text="\n\n")
      windowView.addInput(value=view.file_name(), label="Copy to: ", region_id="new_path")
      windowView.add(text="\n\n")
      windowView.addButton(text="PREVIEW", scope="javascriptenhancements.button_preview", callback=lambda view: self.view.run_command("refactor_safe_copy", args={"inputs": windowView.getInputs(), "preview": True}))
      windowView.add(text="  ")
      windowView.addButton(text="COPY", scope="javascriptenhancements.button_ok", callback=lambda view: self.view.run_command("refactor_safe_copy", args={"inputs": windowView.getInputs(), "preview": False, "view_id_caller": self.view.id()}))
      windowView.add(text="  ")
      windowView.addCloseButton(text="CANCEL", scope="javascriptenhancements.button_cancel", callback=lambda view: self.closePreview("Refactor - Safe Copy Preview"))
      windowView.add(text=" \n")

    if case == "safe_delete" :
      windowView = WindowView(title="Refactor - Safe Delete", use_compare_layout=True)
      windowView.addTitle(text="Refactor - Safe Delete")
      windowView.add(text="\n\n")
      windowView.add(text="File to delete: " + view.file_name())
      windowView.add(text="\n\n")
      windowView.addButton(text="PREVIEW", scope="javascriptenhancements.button_preview", callback=lambda view: self.view.run_command("refactor_safe_delete", args={"preview": True}))
      windowView.add(text="  ")
      windowView.addButton(text="DELETE", scope="javascriptenhancements.button_ok", callback=lambda view: self.view.run_command("refactor_safe_delete", args={"preview": False, "view_id_caller": self.view.id()}))
      windowView.add(text="  ")
      windowView.addCloseButton(text="CANCEL", scope="javascriptenhancements.button_cancel", callback=lambda view: self.closePreview("Refactor - Safe Delete Preview"))
      windowView.add(text=" \n")

    elif case == "extract_method" :
      if view.sel()[0].begin() == view.sel()[0].end():
        return

      select_options = ['Global scope', 'Current scope', 'Class method']
      if not view.match_selector(view.sel()[0].begin(), 'meta.class.js'):
        select_options.remove('Class method')
      print(scope, len(scope.split(" ")))
      if len(scope.split(" ")) <= 2:
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
      windowView.addCloseButton(text="CREATE", scope="javascriptenhancements.button_ok", callback=lambda view: self.view.run_command("refactor_extract_method", args={"inputs": windowView.getInputs()}))
      windowView.add(text="        ")
      windowView.addCloseButton(text="CANCEL", scope="javascriptenhancements.button_cancel")
      windowView.add(text=" \n")

    elif case == "extract_parameter" :
      if view.sel()[0].begin() == view.sel()[0].end():
        return

      self.view.run_command("refactor_extract_parameter")

    elif case == "extract_variable" :
      if view.sel()[0].begin() == view.sel()[0].end():
        return

      self.view.run_command("refactor_extract_variable")

    elif case == "extract_field" :
      if view.sel()[0].begin() == view.sel()[0].end() or not view.match_selector(view.sel()[0].begin(), 'meta.class.js'):
        return

      select_options = ["Current method", "Field declaration", "Class constructor"]

      windowView = WindowView(title="Refactor - Extract Field", use_compare_layout=True)
      windowView.addTitle(text="Refactor - Extract Field")
      windowView.add(text="\n\n")
      windowView.addInput(value="new_field", label="Field Name: ", region_id="field_name")
      windowView.add(text="\n")
      windowView.addSelect(default_option=0, options=select_options, label="Scope: ", region_id="scope")
      windowView.add(text="\n\n")
      windowView.addCloseButton(text="CREATE", scope="javascriptenhancements.button_ok", callback=lambda view: self.view.run_command("refactor_extract_field", args={"inputs": windowView.getInputs()}))
      windowView.add(text="        ")
      windowView.addCloseButton(text="CANCEL", scope="javascriptenhancements.button_cancel")
      windowView.add(text=" \n")

    elif case == "convert_to_arrow_function" :
      self.view.run_command("refactor_convert_to_arrow_function")

  def closePreview(self, preview_name):
    window = self.view.window()
    for v in window.views():
      if v.name() == preview_name:
        v.close()
        break

  def is_enabled(self, **args) :
    view = self.view
    return Util.selection_in_js_scope(view)

  def is_visible(self, **args) :
    view = self.view
    return Util.selection_in_js_scope(view)

${include refactor_safe_move_command.py}

${include refactor_safe_copy_command.py}

${include refactor_safe_delete_command.py}

${include refactor_extract_method_command.py}

${include refactor_extract_parameter_command.py}

${include refactor_extract_variable_command.py}

${include refactor_extract_field_command.py}

${include refactor_convert_to_arrow_function_command.py}