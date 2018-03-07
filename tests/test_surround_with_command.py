import sublime
from unittest import TestCase

class TestSurroundWith(TestCase):

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

  def test_surround_with_case_if(self):
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

    self.view.run_command("javascript_enhancements_erase_text_view")

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


