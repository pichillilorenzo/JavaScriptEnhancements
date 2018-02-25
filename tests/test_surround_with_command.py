import sublime
import sys
from unittest import TestCase

class TestSurroundWith(TestCase):

  def setUp(self):
    self.view = sublime.active_window().new_file()
    # make sure we have a window to work with
    self.view.settings().set("syntax", "Packages/JavaScript/JavaScript.sublime-syntax")

  def tearDown(self):
    if self.view:
      self.view.set_scratch(True)
      self.view.window().focus_view(self.view)
      self.view.window().run_command("close_file")

  def test_surround_with_case_if_1(self):
    self.view.run_command("insert", {"characters": "let a = 3;"})
    self.view.sel().clear()
    self.view.sel().add(sublime.Region(0, self.view.size()))
    self.view.run_command("javascript_enhancements_surround_with", {"case": "if_statement"})
    need_to_be_equal = """
if (bool) {
  let a = 3;
}
""" 
    self.assertEqual(self.view.substr(sublime.Region(0, self.view.size())), need_to_be_equal)

  def test_surround_with_case_if_2(self):
    self.view.run_command("insert", {"characters": "\tlet a = 3;"})
    self.view.sel().clear()
    self.view.sel().add(sublime.Region(0, self.view.size()))
    self.view.run_command("javascript_enhancements_surround_with", {"case": "if_statement"})
    need_to_be_equal = """    
  if (bool) {
    let a = 3;
  }
  """ 
    self.assertEqual(self.view.substr(sublime.Region(0, self.view.size())), need_to_be_equal)


