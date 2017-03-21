import cgi, time

class show_flow_errorsViewEventListener(sublime_plugin.ViewEventListener):

  description_by_row = {}
  errors = []
  callback_setted_use_flow_checker_on_current_view = False

  def on_activated_async(self) :

    view = self.view

    selections = view.sel()
 
    if len(selections) == 0:
      return
      
    sel = selections[0]
    if not view.match_selector(
        sel.begin(),
        'source.js'
    ) and not view.find_by_selector("source.js.embedded.html"):
      return

    settings = get_project_settings()
    if settings :
      if not settings["flow_settings"]["use_flow_checker"] or not is_project_view(view) :
        hide_flow_errors(view)
        return
    else :
      settings = view.settings()
      if not self.callback_setted_use_flow_checker_on_current_view :
        settings.clear_on_change("use_flow_checker_on_current_view")
        settings.add_on_change("use_flow_checker_on_current_view", lambda: sublime.set_timeout_async(lambda: self.on_modified_async()))
        self.callback_setted_use_flow_checker_on_current_view = True
      if not settings.get("use_flow_checker_on_current_view") :
        hide_flow_errors(view)
        return 

    sublime.set_timeout_async(lambda: self.on_modified_async())
    
  def on_modified_async(self) :

    view = self.view

    selections = view.sel()
 
    if len(selections) == 0:
      return
      
    sel = selections[0]
    if not view.match_selector(
        sel.begin(),
        'source.js'
    ) and not view.find_by_selector("source.js.embedded.html"):
      return

    settings = get_project_settings()
    if settings :
      if not settings["flow_settings"]["use_flow_checker"] or not is_project_view(view) :
        hide_flow_errors(view)
        return
    elif not view.settings().get("use_flow_checker_on_current_view") :
      hide_flow_errors(view)
      return 

    self.errors = []
    self.description_by_row = {}
    result = show_flow_errors(view)

    if result :
      self.errors = result["errors"]
      self.description_by_row = result["description_by_row"]

    sublime.set_timeout_async(lambda: self.on_selection_modified_async())

  def on_hover(self, point, hover_zone) :
    view = self.view
    view.erase_phantoms("flow_error")
    if hover_zone != sublime.HOVER_GUTTER :
      return

    sel = sublime.Region(point, point)
    if (not view.match_selector(
        sel.begin(),
        'source.js'
    ) and not view.find_by_selector("source.js.embedded.html")) or not self.errors or not view.get_regions("flow_error"):
      return
    
    settings = get_project_settings()
    if settings :
      if not settings["flow_settings"]["use_flow_checker"] or not is_project_view(view) :
        hide_flow_errors(view)
        return
    elif not view.settings().get("use_flow_checker_on_current_view") :
      hide_flow_errors(view)
      return 

    row, col = view.rowcol(sel.begin())

    error_for_row = self.description_by_row.get(row)
    
    if error_for_row:
      text = cgi.escape(error_for_row).split(" ")
      html = ""
      i = 0
      while i < len(text) - 1:
        html += text[i] + " " + text[i+1] + " "
        i += 2
        if i % 10 == 0 :
          html += " <br> "
      if len(text) % 2 != 0 :
        html += text[len(text) - 1]

      view.add_phantom("flow_error", sel, '<html style="padding: 0px; margin: 5px; background-color: rgba(255,255,255,0);"><body style="border-radius: 10px; padding: 10px; background-color: #F44336; margin: 0px;">'+html+"</body></html>", sublime.LAYOUT_BELOW)


  def on_selection_modified_async(self, *args) :

    view = self.view
    
    sel = view.sel()[0]
    if (not view.match_selector(
        sel.begin(),
        'source.js'
    ) and not view.find_by_selector("source.js.embedded.html")) or not self.errors or not view.get_regions("flow_error"):
      return
 
    view.erase_phantoms("flow_error")

    settings = get_project_settings()
    if settings :
      if not settings["flow_settings"]["use_flow_checker"] or not is_project_view(view) :
        hide_flow_errors(view)
        return
    elif not view.settings().get("use_flow_checker_on_current_view") :
      hide_flow_errors(view)
      return 

    row, col = view.rowcol(sel.begin())

    error_count = len(self.errors)
    error_count_text = 'Flow: {} error{}'.format(
      error_count, '' if error_count is 1 else 's'
    )
    error_for_row = self.description_by_row.get(row)
    if error_for_row:
      view.set_status(
        'flow_error', error_count_text + ': ' + error_for_row
      )
    else:
      view.set_status('flow_error', error_count_text)
