import sublime
import time, os
from unittesting import DeferrableTestCase
JavaScriptEnhancements = __import__('JavaScript Enhancements')
flow_ide_clients = JavaScriptEnhancements.src.libs.flow_ide_clients
JavascriptEnhancementsStartFlowIDEServerEventListener = JavaScriptEnhancements.src.libs.JavascriptEnhancementsStartFlowIDEServerEventListener
PACKAGE_PATH = JavaScriptEnhancements.src.libs.global_vars.PACKAGE_PATH

def plugin_ready():
  return os.path.exists(os.path.join(PACKAGE_PATH, "node_modules", ".bin"))

timeout = 30

class TestCompletions(DeferrableTestCase):

  def setUp(self):
    self.view = sublime.active_window().new_file()
    self.view.settings().set("tab_size", 2)
    self.view.settings().set("translate_tabs_to_spaces", True)
    self.view.settings().set("syntax", "Packages/JavaScript/JavaScript.sublime-syntax")

  def tearDown(self):
    if self.view:
      self.view.set_scratch(True)
      self.view.window().focus_view(self.view)
      self.view.window().run_command("close_file")

  def test_completions(self):
    
    start_time = time.time()

    while not plugin_ready():
      if time.time() - start_time <= timeout:
        yield 200
      else:
        raise TimeoutError("plugin is not ready in " + str(timeout) + " seconds")

    self.view.run_command("insert", {"characters": "document.querySelector('嗨');\ndocument."})

    JavascriptEnhancementsStartFlowIDEServerEventListener().start_server(self.view)
    self.view.run_command("auto_complete")

    start_time = time.time()

    while not self.view.is_auto_complete_visible():

      if time.time() - start_time <= timeout:
        self.view.run_command("auto_complete")
        if not flow_ide_clients:
          JavascriptEnhancementsStartFlowIDEServerEventListener().start_server(self.view)

        yield 500

      else:
        raise TimeoutError("auto_complete popup doesn't show up in " + str(timeout) + " seconds")

    self.view.run_command("commit_completion")
    
    content = self.view.substr(sublime.Region(0, self.view.size()))

    self.assertEqual(content, "document.querySelector('嗨');\ndocument.URL")
