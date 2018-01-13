import sublime, sublime_plugin

def hide_flow_errors(view) :
  view.erase_regions('flow_error')
  view.erase_status('flow_error')

class handle_flow_errorsCommand(sublime_plugin.TextCommand):

  def run(self, edit, **args):
    view = self.view

    if args :
      if args["type"] == "show" :
        sublime.set_timeout_async(lambda: show_flow_errorsViewEventListener(view).on_activated_async())
      elif args["type"] == "hide" :
        hide_flow_errors(view)

  def is_enabled(self):
    view = self.view
    return Util.selection_in_js_scope(view)

  def is_visible(self):
    view = self.view
    return Util.selection_in_js_scope(view)
