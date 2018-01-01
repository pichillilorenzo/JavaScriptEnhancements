import cgi, time

class show_flow_errorsViewEventListener(wait_modified_asyncViewEventListener, sublime_plugin.ViewEventListener):

  description_by_row = {}
  errors = []
  callback_setted_use_flow_checker_on_current_view = False
  prefix_thread_name = "show_flow_errors_view_event_listener"
  wait_time = .35

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
      hide_flow_errors(view)
      return

    settings = get_project_settings()
    if settings :
      if not settings["project_settings"]["flow_checker_enabled"] or not is_project_view(view) :
        hide_flow_errors(view)
        return
      elif settings["project_settings"]["flow_checker_enabled"] :
        comments = view.find_by_selector('source.js comment')
        flow_comment_found = False
        for comment in comments:
          if "@flow" in view.substr(comment) :
            flow_comment_found = True
            break
        if not flow_comment_found :
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

  def on_modified_async(self):
    super(show_flow_errorsViewEventListener, self).on_modified_async()
    
  def on_modified_async_with_thread(self, recheck=True) : 
    view = self.view

    selections = view.sel()
 
    if len(selections) == 0:
      return
      
    sel = selections[0]
    if not view.match_selector(
        sel.begin(),
        'source.js'
    ) and not view.find_by_selector("source.js.embedded.html"):
      hide_flow_errors(view)
      return
    
    self.wait()  

    settings = get_project_settings()
    if settings :
      if not settings["project_settings"]["flow_checker_enabled"] or not is_project_view(view) :
        hide_flow_errors(view)
        return
      elif settings["project_settings"]["flow_checker_enabled"] :
        comments = view.find_by_selector('source.js comment')
        flow_comment_found = False
        for comment in comments:
          if "@flow" in view.substr(comment) :
            flow_comment_found = True
            break
        if not flow_comment_found :
          hide_flow_errors(view)
          return
    elif not view.settings().get("use_flow_checker_on_current_view") :
      hide_flow_errors(view)
      return 

    self.errors = []
    self.description_by_row = {}
    self.description_by_row_column = {}
    result = show_flow_errors(view)

    if result :
      self.errors = result["errors"]
      self.description_by_row = result["description_by_row"]
      self.description_by_row_column = result["description_by_row_column"]

    sublime.set_timeout_async(lambda: self.on_selection_modified_async())

    # recheck only first time to avoid error showing bug (because of async method)
    # while the code execution is here but the user is modifying content
    if (recheck) :
      sublime.set_timeout_async(lambda: self.on_modified_async_with_thread(recheck=False))


  def on_hover(self, point, hover_zone) :
    view = self.view

    if hover_zone != sublime.HOVER_TEXT :
      return

    sel = sublime.Region(point, point)

    if (not view.match_selector(
        sel.begin(),
        'source.js'
    ) and not view.find_by_selector("source.js.embedded.html")) or not self.errors or not view.get_regions("flow_error"):
      hide_flow_errors(view)
      return

    is_hover_error = False
    region_hover_error = None
    for region in view.get_regions("flow_error"):
      if region.contains(sel):
        region_hover_error = region
        is_hover_error = True
        break

    if not is_hover_error:
      return
    
    settings = get_project_settings()
    if settings :
      if not settings["project_settings"]["flow_checker_enabled"] or not is_project_view(view) :
        hide_flow_errors(view)
        return
      elif settings["project_settings"]["flow_checker_enabled"] :
        comments = view.find_by_selector('source.js comment')
        flow_comment_found = False
        for comment in comments:
          if "@flow" in view.substr(comment) :
            flow_comment_found = True
            break
        if not flow_comment_found :
          hide_flow_errors(view)
          return
    elif not view.settings().get("use_flow_checker_on_current_view") :
      hide_flow_errors(view)
      return 

    row_region, col_region = view.rowcol(region_hover_error.begin())
    row_region, endcol_region = view.rowcol(region_hover_error.end())

    error = self.description_by_row_column[str(row_region)+":"+str(col_region)+":"+str(endcol_region)]
    
    if error:
      text = cgi.escape(error).split(" ")
      html = ""
      i = 0
      while i < len(text) - 1:
        html += text[i] + " " + text[i+1] + " "
        i += 2
        if i % 10 == 0 :
          html += " <br> "
      if len(text) % 2 != 0 :
        html += text[len(text) - 1]

      row_region, col_region = view.rowcol(region_hover_error.begin())
      row_region, endcol_region = view.rowcol(region_hover_error.end())

      view.show_popup('<html style="padding: 0px; margin: 0px; background-color: rgba(255,255,255,1);"><body style="font-size: 0.75em; font-weight: bold; padding: 5px; background-color: #F44336; margin: 0px;">'+html+'<br><a style="margin-top: 10px; display: block; color: #000;" href="copy_to_clipboard">Copy</a></body></html>', sublime.COOPERATE_WITH_AUTO_COMPLETE | sublime.HIDE_ON_MOUSE_MOVE_AWAY, region_hover_error.begin(), 1150, 80, lambda action: sublime.set_clipboard(error) or view.hide_popup() )

  def on_selection_modified_async(self, *args) :

    view = self.view
    
    selections = view.sel()
 
    if len(selections) == 0:
      return
      
    sel = selections[0]
    if (not view.match_selector(
        sel.begin(),
        'source.js'
    ) and not view.find_by_selector("source.js.embedded.html")) or not self.errors or not view.get_regions("flow_error"):
      hide_flow_errors(view)
      return

    settings = get_project_settings()
    if settings :
      if not settings["project_settings"]["flow_checker_enabled"] or not is_project_view(view) :
        hide_flow_errors(view)
        return
      elif settings["project_settings"]["flow_checker_enabled"] :
        comments = view.find_by_selector('source.js comment')
        flow_comment_found = False
        for comment in comments:
          if "@flow" in view.substr(comment) :
            flow_comment_found = True
            break
        if not flow_comment_found :
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
        'flow_error', error_count_text + ': ' + error_for_row["description"]
      )
    else:
      view.set_status('flow_error', error_count_text)
  