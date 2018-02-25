import sublime, sublime_plugin
import os
from ..libs import util
from ..libs import NodeJS
from ..libs import javaScriptEnhancements
from ..libs.global_vars import *

class JavascriptEnhancementsGetAstCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args): 
    view = self.view
    flow_cli = "flow"
    is_from_bin = True
    chdir = ""
    use_node = True
    bin_path = ""

    node = NodeJS(check_local=True)
    
    result = node.execute_check_output(
      flow_cli,
      [
        'ast',
        '--from', 'sublime_text',
        '--pretty'
      ],
      is_from_bin=is_from_bin,
      use_fp_temp=True, 
      fp_temp_contents=view.substr(sublime.Region(0, view.size())), 
      is_output_json=False,
      chdir=chdir,
      bin_path=bin_path,
      use_node=use_node
    )

    print(result[1])

  def is_enabled(self, **args) :
    view = self.view
    if not util.selection_in_js_scope(view) or not DEVELOPER_MODE :
      return False
    return True

  def is_visible(self, **args) :
    view = self.view
    if not util.selection_in_js_scope(view) or not DEVELOPER_MODE :
      return False
    return True