import sublime
import time, os, shutil
from collections import OrderedDict
from unittesting import DeferrableTestCase
JavaScriptEnhancements = __import__('JavaScript Enhancements')
util = JavaScriptEnhancements.src.libs.util
PACKAGE_PATH = JavaScriptEnhancements.src.libs.global_vars.PACKAGE_PATH

def plugin_ready():
  return os.path.exists(os.path.join(PACKAGE_PATH, "node_modules", ".bin"))

timeout = 30

project_path = os.path.join(PACKAGE_PATH, 'tests', 'test_project')
sublime_project_path = os.path.join(PACKAGE_PATH, 'tests', 'test_project', 'test_project.sublime-project')

error_regions = [
  sublime.Region(111, 112)
]

warning_regions = [
  sublime.Region(104, 105)
]

unused_regions = [
  sublime.Region(58, 73)
]

class TestRegions(DeferrableTestCase):

  def setUp(self):
    global sublime_project_path
    util.open_project_folder(sublime_project_path)

  def tearDown(self):
    self.window.run_command("close")
    self.window.run_command("close")

  def test_regions(self):
    global project_path

    start_time = time.time()

    while not plugin_ready():
      if time.time() - start_time <= timeout:
        yield 200
      else:
        raise TimeoutError("plugin is not ready in " + str(timeout) + " seconds")

    yield 1000
    self.window = sublime.active_window()

    view = self.window.open_file(os.path.join(project_path, 'index.js'))
    yield 10000
    self.assertListEqual(error_regions, view.get_regions('javascript_enhancements_flow_error'))
    self.assertListEqual(warning_regions, view.get_regions('javascript_enhancements_flow_warning'))
    self.assertListEqual(unused_regions, view.get_regions('javascript_enhancements_unused_variable'))
