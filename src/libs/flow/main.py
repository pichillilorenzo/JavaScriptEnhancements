import sublime, sublime_plugin
import os
from .. import util
from ..global_vars import *

def get_flow_path():
  
  flow_path = []
  flow_path = os.path.join(NODE_MODULES_BIN_PATH, "flow")
  is_from_bin = True

  settings = util.get_project_settings()
  if settings and settings["project_settings"]["flow_cli_custom_path"]:
    flow_path = settings["project_settings"]["flow_cli_custom_path"]
    is_from_bin = False

  if sublime.platform() == 'windows' and is_from_bin:
    flow_path = [flow_path+'.cmd']
  else :
    flow_path = [flow_path]

  return flow_path

def hide_errors(view, level="") :
  
  if level:
    view.erase_regions('javascript_enhancements_flow_' + level)
    view.erase_status('javascript_enhancements_flow_' + level)
    return

  view.erase_regions('javascript_enhancements_flow_error')
  view.erase_status('javascript_enhancements_flow_error')

  view.erase_regions('javascript_enhancements_flow_warning')
  view.erase_status('javascript_enhancements_flow_warning')

