import sublime, sublime_plugin
from ...libs import util
from ...libs import WindowView

class JavascriptEnhancementsRefactorCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    case = args.get("case")
    scope = view.scope_name(view.sel()[0].begin()).strip()

    if case == "safe_move" :
      window_view = WindowView(title="Refactor - Safe Move", restore_layout=True)
      window_view.add_title(text="Refactor - Safe Move")
      window_view.add(text="\n\n")
      window_view.add(text="NOTE: If you want this command checks all the imported/exported JavaScript dependencies and not just those with @flow, you need to add \"all=true\" into the .flowconfig [options]. See ")
      window_view.add_link(text="here", link="https://flow.org/en/docs/config/options/#toc-all-boolean", scope="flow-toc-all-boolean")
      window_view.add(text=".\n\n")
      window_view.add_input(value=view.file_name(), label="Move to: ", region_id="new_path")
      window_view.add_folder_explorer(start_path=view.file_name(), region_input_id="new_path", scope="javascriptenhancements.folder_explorer", only_dir=True)
      window_view.add(text="\n\n")
      window_view.add_button(text="PREVIEW", scope="javascriptenhancements.button_preview", callback=lambda view: self.view.run_command("javascript_enhancements_refactor_safe_move", args={"inputs": window_view.get_inputs(), "preview": True}))
      window_view.add(text="  ")
      window_view.add_button(text="MOVE", scope="javascriptenhancements.button_ok", callback=lambda view: self.view.run_command("javascript_enhancements_refactor_safe_move", args={"inputs": window_view.get_inputs(), "preview": False}))
      window_view.add(text="  ")
      window_view.add_close_button(text="CANCEL", scope="javascriptenhancements.button_cancel")
      window_view.add(text=" \n")

    elif case == "safe_copy" :
      window_view = WindowView(title="Refactor - Safe Copy", restore_layout=True)
      window_view.add_title(text="Refactor - Safe Copy")
      window_view.add(text="\n\n")
      window_view.add(text="NOTE: If you want this command checks all the imported/exported JavaScript dependencies and not just those with @flow, you need to add \"all=true\" into the .flowconfig [options]. See ")
      window_view.add_link(text="here", link="https://flow.org/en/docs/config/options/#toc-all-boolean", scope="flow-toc-all-boolean")
      window_view.add(text=".\n\n")
      window_view.add_input(value=view.file_name(), label="Copy to: ", region_id="new_path")
      window_view.add_folder_explorer(start_path=view.file_name(), region_input_id="new_path", scope="javascriptenhancements.folder_explorer", only_dir=True)
      window_view.add(text="\n\n")
      window_view.add_button(text="PREVIEW", scope="javascriptenhancements.button_preview", callback=lambda view: self.view.run_command("javascript_enhancements_refactor_safe_copy", args={"inputs": window_view.get_inputs(), "preview": True}))
      window_view.add(text="  ")
      window_view.add_button(text="COPY", scope="javascriptenhancements.button_ok", callback=lambda view: self.view.run_command("javascript_enhancements_refactor_safe_copy", args={"inputs": window_view.get_inputs(), "preview": False}))
      window_view.add(text="  ")
      window_view.add_close_button(text="CANCEL", scope="javascriptenhancements.button_cancel")
      window_view.add(text=" \n")

    if case == "safe_delete" :
      window_view = WindowView(title="Refactor - Safe Delete", restore_layout=True)
      window_view.add_title(text="Refactor - Safe Delete")
      window_view.add(text="\n\n")
      window_view.add(text="NOTE: If you want this command checks all the imported/exported JavaScript dependencies and not just those with @flow, you need to add \"all=true\" into the .flowconfig [options]. See ")
      window_view.add_link(text="here", link="https://flow.org/en/docs/config/options/#toc-all-boolean", scope="flow-toc-all-boolean")
      window_view.add(text=".\n\n")
      window_view.add(text="File to delete: " + str(view.file_name()))
      window_view.add(text="\n\n")
      window_view.add_button(text="PREVIEW", scope="javascriptenhancements.button_preview", callback=lambda view: self.view.run_command("javascript_enhancements_refactor_safe_delete", args={"preview": True}))
      window_view.add(text="  ")
      window_view.add_button(text="DELETE", scope="javascriptenhancements.button_ok", callback=lambda view: self.view.run_command("javascript_enhancements_refactor_safe_delete", args={"preview": False}))
      window_view.add(text="  ")
      window_view.add_close_button(text="CANCEL", scope="javascriptenhancements.button_cancel")
      window_view.add(text=" \n")

    elif case == "extract_method" :
      if view.sel()[0].begin() == view.sel()[0].end():
        return

      select_options = ['Global scope', 'Current scope', 'Class method']
      if not view.match_selector(view.sel()[0].begin(), 'meta.class.js'):
        select_options.remove('Class method')
        
      window_view = WindowView(title="Refactor - Extract Method", restore_layout=True)
      window_view.add_title(text="Refactor - Extract Method")
      window_view.add(text="\n\n")
      window_view.add_input(value="func", label="Function Name: ", region_id="function_name")
      window_view.add(text="\n")
      window_view.add_input(value="()", label="Parameters: ", region_id="parameters")
      window_view.add(text="\n")
      window_view.add_select(default_option=0, options=select_options, label="Scope: ", region_id="scope")
      window_view.add(text="\n\n")
      window_view.add_button(text="CREATE", scope="javascriptenhancements.button_ok", callback=lambda view: self.view.run_command("javascript_enhancements_refactor_extract_method", args={"inputs": window_view.get_inputs()}))
      window_view.add(text="        ")
      window_view.add_close_button(text="CANCEL", scope="javascriptenhancements.button_cancel")
      window_view.add(text=" \n")

    elif case == "extract_parameter" :
      if view.sel()[0].begin() == view.sel()[0].end():
        return

      self.view.run_command("javascript_enhancements_refactor_extract_parameter")

    elif case == "extract_variable" :
      if view.sel()[0].begin() == view.sel()[0].end():
        return

      self.view.run_command("javascript_enhancements_refactor_extract_variable")

    elif case == "extract_field" :
      if view.sel()[0].begin() == view.sel()[0].end() or not view.match_selector(view.sel()[0].begin(), 'meta.class.js'):
        return

      select_options = ["Current method", "Field declaration", "Class constructor"]

      window_view = WindowView(title="Refactor - Extract Field", restore_layout=True)
      window_view.add_title(text="Refactor - Extract Field")
      window_view.add(text="\n\n")
      window_view.add_input(value="new_field", label="Field Name: ", region_id="field_name")
      window_view.add(text="\n")
      window_view.add_select(default_option=0, options=select_options, label="Scope: ", region_id="scope")
      window_view.add(text="\n\n")
      window_view.add_close_button(text="CREATE", scope="javascriptenhancements.button_ok", callback=lambda view: self.view.run_command("javascript_enhancements_refactor_extract_field", args={"inputs": window_view.get_inputs()}))
      window_view.add(text="        ")
      window_view.add_close_button(text="CANCEL", scope="javascriptenhancements.button_cancel")
      window_view.add(text=" \n")

    elif case == "convert_to_arrow_function" :
      self.view.run_command("javascript_enhancements_refactor_convert_to_arrow_function")

    elif case == "export" :
      tp = args.get("type")

      window_view = WindowView(title="Refactor - Export " + tp.title(), restore_layout=True)
      window_view.add_title(text="Refactor - Export " + tp.title())
      window_view.add(text="\n\n")
      window_view.add_input(value=view.file_name(), label="Export " + tp.title() + " to: ", region_id="new_path")
      window_view.add_folder_explorer(start_path=view.file_name(), region_input_id="new_path", scope="javascriptenhancements.folder_explorer")
      window_view.add(text="\n\n")
      window_view.add_button(text="PREVIEW", scope="javascriptenhancements.button_preview", callback=lambda view: self.view.run_command("javascript_enhancements_refactor_export", args={"type": tp, "inputs": window_view.get_inputs(), "preview": True}))
      window_view.add(text="  ")
      window_view.add_button(text="EXPORT", scope="javascriptenhancements.button_ok", callback=lambda view: self.view.run_command("javascript_enhancements_refactor_export", args={"type": tp, "inputs": window_view.get_inputs(), "preview": False}))
      window_view.add(text="  ")
      window_view.add_close_button(text="CANCEL", scope="javascriptenhancements.button_cancel")
      window_view.add(text=" \n")

  def close_preview(self, preview_name):
    window = self.view.window()
    for v in window.views():
      if v.name() == preview_name:
        v.close()
        break

  def is_enabled(self, **args) :
    view = self.view
    return util.selection_in_js_scope(view)

  def is_visible(self, **args) :
    view = self.view
    return util.selection_in_js_scope(view)
