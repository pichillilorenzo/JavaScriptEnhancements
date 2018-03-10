import sublime, sublime_plugin
import cgi, time, os
from ..libs import NodeJS
from ..libs import FlowCLI
from ..libs import flow
from ..libs import util
from ..libs.popup_manager import popup_manager
from .wait_modified_async import JavascriptEnhancementsWaitModifiedAsyncViewEventListener

show_flow_errors_css = ""
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "show_flow_errors.css"), encoding="utf-8") as css_file:
  show_flow_errors_css = "<style>"+css_file.read()+"</style>"

class JavascriptEnhancementsShowFlowErrorsViewEventListener(JavascriptEnhancementsWaitModifiedAsyncViewEventListener, sublime_plugin.ViewEventListener):

  description_by_row_column = {}
  diagnostics = {
    "error": [],
    "warning": []
  }
  diagnostic_regions = {
    "error": [],
    "warning": []
  }
  diagnostic_scope = {
    "error": "storage",
    "warning": "keyword"
  }
  callback_setted_use_flow_checker_on_current_view = False
  prefix_thread_name = "javascript_enhancements_show_flow_errors_view_event_listener"
  wait_time = .15
  modified = False

  def on_load_async(self):
    self.on_modified_async()

  def on_activated_async(self):
    self.on_modified_async()

  def on_modified(self):
    self.modified = True

  def on_modified_async(self):
    super(JavascriptEnhancementsShowFlowErrorsViewEventListener, self).on_modified_async()

  def on_selection_modified_async(self):
    view = self.view
    sel = view.sel()[0]

    if view.find_by_selector('source.js.embedded.html') and (self.diagnostics["error"] or self.diagnostics["warning"] or view.get_regions("javascript_enhancements_flow_error") or view.get_regions("javascript_enhancements_flow_warning")):
      pass

    elif not util.selection_in_js_scope(view) or not self.are_there_errors():
      flow.hide_errors(view)
      return

    for key, value in self.diagnostics.items():
      if not value and not view.get_regions("javascript_enhancements_flow_error"):
        flow.hide_errors(view, level=key)

    error_region = None
    error_level = ""

    for region in view.get_regions("javascript_enhancements_flow_error"):
      if region.contains(sel):
        error_region = region
        error_level = "error"
        break

    if not error_region:
      for region in view.get_regions("javascript_enhancements_flow_warning"):
        if region.contains(sel):
          error_region = region
          error_level = "warning"
          break

    if not self.can_check():
      return

    error_description = ""

    if error_region:
      row_region, col_region = view.rowcol(error_region.begin())
      end_row_region, endcol_region = view.rowcol(error_region.end())

      try :
        error_description = self.description_by_row_column[str(row_region)+":"+str(end_row_region)+":"+str(col_region)+":"+str(endcol_region)+":"+error_level]
      except KeyError as e:
        if str(row_region+1)+":"+str(row_region+1)+":0:0:"+error_level in self.description_by_row_column:
          error_description = self.description_by_row_column[str(row_region+1)+":"+str(row_region+1)+":0:0:"+error_level]


    for key, value in self.diagnostics.items():
      if value:
        error_count = len(value)
        error_count_text = 'Flow: {} {}{}'.format(
          error_count, key, '' if error_count is 1 else 's'
        )
        if error_level == key and error_region:
          view.set_status(
            'javascript_enhancements_flow_' + key, error_count_text + ': ' + error_description
          )
        else:
          view.set_status('javascript_enhancements_flow_' + key, error_count_text)

  def on_modified_async_with_thread(self, recheck=True):

    self.modified = False

    view = self.view

    if view.find_by_selector('source.js.embedded.html'):
      pass
    elif not util.selection_in_js_scope(view):
      flow.hide_errors(view)
      return

    if not self.can_check():
      return

    self.wait()  

    flow_cli = FlowCLI(view)
    result = flow_cli.check_contents()

    self.diagnostics = {
        "error": [],
        "warning": []
      }
    self.diagnostic_regions = {
        "error": [],
        "warning": []
     }
    self.description_by_row_column = {}

    if result[0] and len(result[1]['errors']) > 0:

      for error in result[1]['errors']:
        description = ''
        operation = error.get('operation')
        row = -1
        error_level = error['level']

        self.diagnostics[error_level].append(error)

        for i in range(len(error['message'])):
          message = error['message'][i]

          # check if the error path is the same file opened on the current view.
          # this check is done because sometimes flow put errors from other files (for example when defining new flow definitions)
          if message['path'] and message['path'] != view.file_name():
            continue

          if i == 0 :
            row = int(message['line']) - 1
            endrow = int(message['endline']) - 1
            col = int(message['start']) - 1
            endcol = int(message['end'])

            self.diagnostic_regions[error_level].append(util.rowcol_to_region(view, row, endrow, col, endcol))

            if operation:
              description += operation["descr"]

          if not description :
            description += "'"+message['descr']+"'"
          else :
            description += " " + message['descr']

        if row >= 0 :
          self.description_by_row_column[str(row)+":"+str(endrow)+":"+str(col)+":"+str(endcol)+":"+error_level] = description

    if not self.modified :

      need_update_sublime_status = False

      for key, value in self.diagnostic_regions.items():
        view.erase_regions('javascript_enhancements_flow_' + key)

        if value:

          view.add_regions( 'javascript_enhancements_flow_' + key, value, self.diagnostic_scope[key], 'dot', sublime.DRAW_SQUIGGLY_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE )

          if not need_update_sublime_status:
            need_update_sublime_status = True

        else:
          view.erase_status("javascript_enhancements_flow_" + key)

      if need_update_sublime_status:
        self.on_selection_modified_async()

    elif (recheck) :
      sublime.set_timeout_async(lambda: self.on_modified_async_with_thread(recheck=False))

  def on_hover(self, point, hover_zone) :
    view = self.view

    if view.find_by_selector('source.js.embedded.html') and (self.diagnostics["error"] or self.diagnostics["warning"] or view.get_regions("javascript_enhancements_flow_error") or view.get_regions("javascript_enhancements_flow_warning")):
      pass

    elif not util.selection_in_js_scope(view) or not self.are_there_errors():
      flow.hide_errors(view)
      return

    for key, value in self.diagnostics.items():
      if not value and not view.get_regions("javascript_enhancements_flow_error"):
        flow.hide_errors(view, level=key)

    if hover_zone != sublime.HOVER_TEXT :
      return

    sel = sublime.Region(point, point)

    is_hover_error = False
    region_hover_error = None
    error_level = ""

    for region in view.get_regions("javascript_enhancements_flow_error"):
      if region.contains(sel):
        region_hover_error = region
        is_hover_error = True
        error_level = "error"
        break

    if not is_hover_error:
      for region in view.get_regions("javascript_enhancements_flow_warning"):
        if region.contains(sel):
          region_hover_error = region
          is_hover_error = True
          error_level = "warning"
          break

    if not is_hover_error:
      return
    
    if not self.can_check():
      return

    row_region, col_region = view.rowcol(region_hover_error.begin())
    end_row_region, endcol_region = view.rowcol(region_hover_error.end())

    error = None

    try :
      error = self.description_by_row_column[str(row_region)+":"+str(end_row_region)+":"+str(col_region)+":"+str(endcol_region)+":"+error_level]
    except KeyError as e:
      if str(row_region+1)+":"+str(row_region+1)+":0:0:"+error_level in self.description_by_row_column:
        error = self.description_by_row_column[str(row_region+1)+":"+str(row_region+1)+":0:0:"+error_level]

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
      end_row_region, endcol_region = view.rowcol(region_hover_error.end())
      
      # here the css code for the <a> element is not working, so the style is inline.
      popup_manager.set_visible("javascript_enhancements_flow_" + error_level, True)
      view.show_popup("""
        <html>
          <body>
            """ + show_flow_errors_css + """
            """ + html + """
            <br>
            <a style="display: block; margin-top: 10px; color: #333;" class="copy-to-clipboard" href="copy_to_clipboard">Copy</a>
          </body>
        </html>""", sublime.HIDE_ON_MOUSE_MOVE_AWAY, point, 1150, 80, lambda action: sublime.set_clipboard(error) or view.hide_popup(), lambda: popup_manager.set_visible("javascript_enhancements_flow_" + error_level, False) )

  def can_check(self):
    view = self.view

    settings = util.get_project_settings()
    if settings :
      if not settings["project_settings"]["flow_checker_enabled"] or not util.is_project_view(view) :
        flow.hide_errors(view)
        return False
      elif settings["project_settings"]["flow_checker_enabled"] :
        comments = view.find_by_selector('source.js comment')
        flow_comment_found = False
        for comment in comments:
          if "@flow" in view.substr(comment) :
            flow_comment_found = True
            break
        if not flow_comment_found :
          flow.hide_errors(view)
          return False
    elif not view.settings().get("javascript_enhancements_use_flow_checker_on_current_view") :
      flow.hide_errors(view)
      return False 

    return True

  def are_there_errors(self):
    view = self.view
    return True if self.diagnostics["error"] or self.diagnostics["warning"] or view.get_regions("javascript_enhancements_flow_error") or view.get_regions("javascript_enhancements_flow_warning") else False