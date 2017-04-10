result_js = ""
region_selected = None
popup_is_showing = False
ej_css = """
<style>
html{
  margin: 0;
  padding: 0;
}
body{
  color: #fff;
  margin: 0;
  padding: 0;
}
.container{
  background-color: #202A31;
  padding: 10px;
}
a{
  color: #fff;
  display: block;
  margin: 10px 0;
}
</style>
"""

def action_result(action):
  global result_js
  global region_selected

  view = sublime.active_window().active_view()
  sel = region_selected
  str_selected = view.substr(sel).strip()

  if action == "copy_to_clipboard" :
    sublime.set_clipboard(result_js)

  elif action == "replace_text" :
    view.run_command("replace_text")

  elif action == "view_result_formatted":
    view.run_command("view_result_formatted")

  view.hide_popup()
  result_js = ""

class view_result_formattedCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    global result_js
    global region_selected

    sublime.active_window().show_input_panel("Result", result_js, back_to_popup, back_to_popup, back_to_popup)

class replace_textCommand(sublime_plugin.TextCommand):

  def run(self, edit):
    global result_js
    global region_selected

    view = self.view
    sel = Util.trim_Region(view, region_selected)
    view.replace(edit, sel, result_js)
    if region_selected.a < region_selected.b :
      region_selected.b = region_selected.a+len(result_js)
    else :
      region_selected.a = region_selected.b+len(result_js)

class ej_hide_popupEventListener(sublime_plugin.EventListener):
  def on_modified_async(self, view) :
    global popup_is_showing
    if popup_is_showing :
      view.hide_popup()
      popup_is_showing = False

class evaluate_javascriptCommand(sublime_plugin.TextCommand):

  def run(self, edit, is_line=False, eval_type="eval"):
    global result_js
    global region_selected
    global popup_is_showing

    view = self.view
    sel = view.sel()[0]
    popup_is_showing = False
    str_selected = view.substr(sel).strip()

    if is_line:
      lines = view.lines(sel)
      region_selected = lines[0]
      str_selected = view.substr(region_selected)
    else: 
      if not str_selected and region_selected : 
        region = get_start_end_code_highlights_eval()
        region_selected = sublime.Region(region[0], region[1])
        lines = view.lines(region_selected)
        str_selected = ""
        for line in lines:
          str_selected += view.substr(view.full_line(line))
      elif str_selected:
        lines = view.lines(sel)
        region_selected = sublime.Region if not region_selected else region_selected
        region_selected = sublime.Region(lines[0].begin(), lines[-1:][0].end())
      elif not str_selected :
        return
    
    if not region_selected :
      return

    view.run_command("show_start_end_dot_eval")

    try:
      node = NodeJS(check_local=True)
      result_js = node.eval(str_selected, eval_type=eval_type, strict_mode=True)
      popup_is_showing = True
      view.show_popup("<html><head></head><body>"+ej_css+"""<div class=\"container\">
        <p class="result">Result: """+result_js+"""</p>
        <div><a href="view_result_formatted">View result with all spaces(\\t,\\n,...)</a></div>
        <div><a href="copy_to_clipboard">Copy result to clipboard</a></div>
        <div><a href="replace_text">Replace text with result</a></div>
        </div>
      </body></html>""", sublime.COOPERATE_WITH_AUTO_COMPLETE, -1, 400, 400, action_result)
    except Exception as e:
      #sublime.error_message("Error: "+traceback.format_exc())
      sublime.active_window().show_input_panel("Result", "Error: "+traceback.format_exc(), lambda x: "" , lambda x: "", lambda : "")

  def is_enabled(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True

  def is_visible(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True

class show_start_end_dot_evalCommand(sublime_plugin.TextCommand) :
  def run(self, edit) :
    global region_selected
    view = self.view
    lines = view.lines(region_selected)
    view.add_regions("region-dot", [lines[0], lines[-1:][0]],  "code", "dot", sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE)
    #view.add_regions("region-body", [region_selected],  "code", "", sublime.DRAW_NO_FILL)
  
  def is_enabled(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True

  def is_visible(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True

class hide_start_end_dot_evalCommand(sublime_plugin.TextCommand) :
  def run(self, edit) :
    view = self.view
    view.erase_regions("region-dot")
    #view.erase_regions("region-body")
  
  def is_enabled(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True

  def is_visible(self, **args) :
    view = self.view
    if not Util.selection_in_js_scope(view) :
      return False
    return True

def get_start_end_code_highlights_eval() :
  view = sublime.active_window().active_view()
  return [view.line(view.get_regions("region-dot")[0]).begin(), view.line(view.get_regions("region-dot")[1]).end()]

def back_to_popup(*str_arg):
  view = sublime.active_window().active_view()
  view.run_command("evaluate_javascript")
  return
