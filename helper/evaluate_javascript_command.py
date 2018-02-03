import sublime, sublime_plugin
import traceback, os, json, io, sys, imp,shlex, tempfile

class evaluate_javascriptCommand(manage_cliCommand):

  isNode = True
  alsoNonProject = True

  def prepare_command(self, **kwargs):

    is_line = kwargs.get("is_line") if "is_line" in kwargs else False

    view = self.window.active_view()
    sel = view.sel()[0]
    region_selected = None
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

    fp = tempfile.NamedTemporaryFile(delete=False)
    fp.write(str.encode("console.log('\\n'); console.time('Execution Time');\n"+str_selected+"\nconsole.log('\\n'); console.timeEnd('Execution Time');"))
    fp.close()

    if sublime.platform() == "windows":
      self.command = ["-p", "<", fp.name, "&", "del", "/f", "/q", fp.name]
    else :
      self.command = ["-p", "<", shlex.quote(fp.name), ";", "rm", "-rf", shlex.quote(fp.name)]

    self._run()
    
  def _run(self):
    super(evaluate_javascriptCommand, self)._run()

  def is_enabled(self, **args) :
    view = self.window.active_view()
    if not Util.selection_in_js_scope(view) :
      return False
    return True

  def is_visible(self, **args) :
    view = self.window.active_view()
    if not Util.selection_in_js_scope(view) :
      return False
    return True