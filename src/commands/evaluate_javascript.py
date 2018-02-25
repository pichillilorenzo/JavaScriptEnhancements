import sublime, sublime_plugin
import shlex, tempfile
from ..libs import util
from ..libs import JavascriptEnhancementsExecuteOnTerminalCommand

class JavascriptEnhancementsEvaluateJavascriptCommand(JavascriptEnhancementsExecuteOnTerminalCommand, sublime_plugin.WindowCommand):

  is_node = True
  also_non_project = True

  def prepare_command(self, **kwargs):

    is_line = kwargs.get("is_line") if "is_line" in kwargs else False

    view = self.window.active_view()
    sel = view.sel()[0]
    str_selected = view.substr(sel).strip()

    if is_line:
      lines = view.lines(sel)
      region_selected = lines[0]
      str_selected = view.substr(region_selected).strip()
    
    if not str_selected :
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
    super(JavascriptEnhancementsEvaluateJavascriptCommand, self)._run()

  def is_enabled(self, **args) :
    view = self.window.active_view()
    if not util.selection_in_js_scope(view) :
      return False
    return True

  def is_visible(self, **args) :
    view = self.window.active_view()
    if not util.selection_in_js_scope(view) :
      return False
    return True