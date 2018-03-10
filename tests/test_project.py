import sublime
import time, os, shutil
from collections import OrderedDict
from unittesting import DeferrableTestCase
JavaScriptEnhancements = __import__('JavaScript Enhancements')
util = JavaScriptEnhancements.src.libs.util

project_path = os.path.join(os.path.expanduser("~"), "javascript_enhancements_project_test")
project_settings = {
  'project_file_name': os.path.join(project_path, 'javascript_enhancements_project_test.sublime-project'), 
  'settings_dir_name': os.path.join(project_path, '.je-project-settings'), 
  'project_settings': OrderedDict([('node_js_custom_path', ''), ('npm_custom_path', ''), ('yarn_custom_path', ''), ('use_yarn', False), ('build_flow', OrderedDict([('source_folders', []), ('destination_folder', ''), ('options', []), ('on_save', True)])), ('flow_checker_enabled', True), ('flow_cli_custom_path', ''), ('flow_remove_types_custom_path', ''), ('jsdoc', OrderedDict([('conf_file', '')]))]), 
  'project_dir_name': project_path, 
  'project_details': OrderedDict([('project_name', ''), ('author', ''), ('author_uri', ''), ('description', ''), ('version', ''), ('license', ''), ('license_uri', ''), ('tags', '')]), 
  'bookmarks': []
}

class TestProject(DeferrableTestCase):

  def setUp(self):
    self.window = sublime.active_window()
    if os.path.isdir(project_path):
      shutil.rmtree(project_path)

  def tearDown(self):
    global project_path
    sublime.active_window().run_command("close")
    if os.path.isdir(project_path):
      shutil.rmtree(project_path)

  def test_project(self):
    self.window.run_command("javascript_enhancements_create_new_project")
    self.window.run_command("insert", {"characters": "empty"})
    yield 500
    self.window.run_command("keypress", {"key": "enter"})
    yield 500
    self.window.run_command("insert", {"characters": "javascript_enhancements_project_test"})
    yield 500
    self.window.run_command("keypress", {"key": "enter"})
    yield 500
    self.window.run_command("keypress", {"key": "enter"})
    yield 500
    self.assertDictEqual(project_settings, util.get_project_settings())

