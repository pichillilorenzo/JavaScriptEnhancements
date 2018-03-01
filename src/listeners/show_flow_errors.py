import sublime, sublime_plugin
import cgi, time, os
from ..libs import NodeJS
from ..libs import flow
from ..libs import util
from ..libs.popup_manager import popup_manager
from .wait_modified_async import JavascriptEnhancementsWaitModifiedAsyncViewEventListener

show_flow_errors_css = ""
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "show_flow_errors.css"), encoding="utf-8") as css_file:
  show_flow_errors_css = "<style>"+css_file.read()+"</style>"

class JavascriptEnhancementsShowFlowErrorsViewEventListener(JavascriptEnhancementsWaitModifiedAsyncViewEventListener, sublime_plugin.ViewEventListener):

  description_by_row = {}
  errors = []
  errorRegions = []
  callback_setted_use_flow_checker_on_current_view = False
  prefix_thread_name = "show_flow_errors_view_event_listener"
  wait_time = .15
  modified = False

  def on_activated_async(self):
    self.on_modified_async()

  def on_modified(self):
    self.modified = True

  def on_modified_async(self):
    super(JavascriptEnhancementsShowFlowErrorsViewEventListener, self).on_modified_async()

  def on_selection_modified_async(self):
    view = self.view

    if view.find_by_selector('source.js.embedded.html') and (self.errors or view.get_regions("javascript_enhancements_flow_error")):
      pass

    elif not util.selection_in_js_scope(view) or not self.errors or not view.get_regions("javascript_enhancements_flow_error"):
      flow.hide_errors(view)
      return

    settings = util.get_project_settings()
    if settings :
      if not settings["project_settings"]["flow_checker_enabled"] or not util.is_project_view(view) :
        flow.hide_errors(view)
        return
      elif settings["project_settings"]["flow_checker_enabled"] :
        comments = view.find_by_selector('source.js comment')
        flow_comment_found = False
        for comment in comments:
          if "@flow" in view.substr(comment) :
            flow_comment_found = True
            break
        if not flow_comment_found :
          flow.hide_errors(view)
          return
    elif not view.settings().get("javascript_enhancements_use_flow_checker_on_current_view") :
      flow.hide_errors(view)
      return 

    row, col = view.rowcol(view.sel()[0].begin())

    if self.errors:
      error_count = len(self.errors)
      error_count_text = 'Flow: {} error{}'.format(
        error_count, '' if error_count is 1 else 's'
      )
      error_for_row = self.description_by_row.get(row)
      if error_for_row:
        view.set_status(
          'javascript_enhancements_flow_error', error_count_text + ': ' + error_for_row["description"]
        )
      else:
        view.set_status('javascript_enhancements_flow_error', error_count_text)

  def on_modified_async_with_thread(self, recheck=True):

    self.modified = False

    view = self.view

    if view.find_by_selector('source.js.embedded.html'):
      pass
    elif not util.selection_in_js_scope(view):
      flow.hide_errors(view)
      return

    settings = util.get_project_settings()

    if settings :
      if not settings["project_settings"]["flow_checker_enabled"] or not util.is_project_view(view) :
        flow.hide_errors(view)
        return
      elif settings["project_settings"]["flow_checker_enabled"] :
        comments = view.find_by_selector('source.js comment')
        flow_comment_found = False
        for comment in comments:
          if "@flow" in view.substr(comment) :
            flow_comment_found = True
            break
        if not flow_comment_found :
          flow.hide_errors(view)
          return
    elif not view.settings().get("javascript_enhancements_use_flow_checker_on_current_view") :
      flow.hide_errors(view)
      return 

    self.wait()  

    deps = flow.parse_cli_dependencies(view)

    flow_cli = "flow"
    is_from_bin = True
    chdir = ""
    use_node = True
    bin_path = ""

    settings = util.get_project_settings()
    if settings and settings["project_settings"]["flow_cli_custom_path"]:
      flow_cli = os.path.basename(settings["project_settings"]["flow_cli_custom_path"])
      bin_path = os.path.dirname(settings["project_settings"]["flow_cli_custom_path"])
      is_from_bin = False
      chdir = settings["project_dir_name"]
      use_node = False
      
    node = NodeJS(check_local=True)
    
    result = node.execute_check_output(
      flow_cli,
      [
        'check-contents',
        '--from', 'sublime_text',
        '--root', deps.project_root,
        '--json',
        deps.filename
      ],
      is_from_bin=is_from_bin,
      use_fp_temp=True, 
      fp_temp_contents=deps.contents, 
      is_output_json=True,
      clean_output_flow=True,
      chdir=chdir,
      bin_path=bin_path,
      use_node=use_node
    )

    self.errors = []
    self.description_by_row = {}
    self.description_by_row_column = {}
    self.errorRegions = []

    if result[0] and not result[1]['passed']:

      for error in result[1]['errors']:
        description = ''
        operation = error.get('operation')
        row = -1
        for i in range(len(error['message'])):
          message = error['message'][i]
          if i == 0 :
            row = int(message['line']) - 1
            endrow = int(message['endline']) - 1
            col = int(message['start']) - 1
            endcol = int(message['end'])

            self.errorRegions.append(util.rowcol_to_region(view, row, endrow, col, endcol))

            if operation:
              description += operation["descr"]

          if not description :
            description += "'"+message['descr']+"'"
          else :
            description += " " + message['descr']

        if row >= 0 :
          row_description = self.description_by_row.get(row)
          if not row_description:
            self.description_by_row[row] = {
              "col": col,
              "description": description
            }
          if row_description and description not in row_description:
            self.description_by_row[row]["description"] += '; ' + description

          self.description_by_row_column[str(row)+":"+str(endrow)+":"+str(col)+":"+str(endcol)] = description
            
      self.errors += result[1]['errors']

    if not self.modified :
      view.erase_regions('javascript_enhancements_flow_error')
      if self.errorRegions:
        view.add_regions( 'javascript_enhancements_flow_error', self.errorRegions, 'keyword', 'dot', sublime.DRAW_SQUIGGLY_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE )
      else:
        view.erase_status("javascript_enhancements_flow_error")
    elif (recheck) :
      sublime.set_timeout_async(lambda: self.on_modified_async_with_thread(recheck=False))

  def on_hover(self, point, hover_zone) :
    view = self.view

    if view.find_by_selector('source.js.embedded.html') and (self.errors or view.get_regions("javascript_enhancements_flow_error")):
      pass

    elif not util.selection_in_js_scope(view) or not self.errors or not view.get_regions("javascript_enhancements_flow_error"):
      flow.hide_errors(view)
      return

    if hover_zone != sublime.HOVER_TEXT :
      return

    sel = sublime.Region(point, point)

    is_hover_error = False
    region_hover_error = None
    for region in view.get_regions("javascript_enhancements_flow_error"):
      if region.contains(sel):
        region_hover_error = region
        is_hover_error = True
        break

    if not is_hover_error:
      return
    
    settings = util.get_project_settings()
    if settings :
      if not settings["project_settings"]["flow_checker_enabled"] or not util.is_project_view(view) :
        flow.hide_errors(view)
        return
      elif settings["project_settings"]["flow_checker_enabled"] :
        comments = view.find_by_selector('source.js comment')
        flow_comment_found = False
        for comment in comments:
          if "@flow" in view.substr(comment) :
            flow_comment_found = True
            break
        if not flow_comment_found :
          flow.hide_errors(view)
          return
    elif not view.settings().get("javascript_enhancements_use_flow_checker_on_current_view") :
      flow.hide_errors(view)
      return 

    row_region, col_region = view.rowcol(region_hover_error.begin())
    end_row_region, endcol_region = view.rowcol(region_hover_error.end())

    error = None

    try :
      error = self.description_by_row_column[str(row_region)+":"+str(end_row_region)+":"+str(col_region)+":"+str(endcol_region)]
    except KeyError as e:
      if str(row_region+1)+":"+str(row_region+1)+":0:0" in self.description_by_row_column:
        error = self.description_by_row_column[str(row_region+1)+":"+str(row_region+1)+":0:0"]

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
      popup_manager.set_visible("javascript_enhancements_flow_error", True)
      view.show_popup("""
        <html>
          <body>
            """ + show_flow_errors_css + """
            """ + html + """
            <br>
            <a style="display: block; margin-top: 10px; color: #333;" class="copy-to-clipboard" href="copy_to_clipboard">Copy</a>
          </body>
        </html>""", sublime.HIDE_ON_MOUSE_MOVE_AWAY, point, 1150, 80, lambda action: sublime.set_clipboard(error) or view.hide_popup(), lambda: popup_manager.set_visible("javascript_enhancements_flow_error", False) )
