import sublime, sublime_plugin
import os, tempfile, queue
from collections import namedtuple
from .. import util
from .. import global_vars

CLIRequirements = namedtuple('CLIRequirements', [
    'filename', 'project_root', 'contents', 'cursor_pos', 'row', 'col'
])

def parse_cli_dependencies(view, **kwargs):
  filename = view.file_name()
  
  project_settings = util.get_project_settings()
  if project_settings:
    project_root = project_settings["project_dir_name"]
  else:
    contextual_keys = sublime.active_window().extract_variables()
    folder_path = contextual_keys.get("folder")
    if folder_path and os.path.isdir(folder_path) and os.path.isfile(os.path.join(folder_path, '.flowconfig')) :  
      project_root = folder_path
    else :
      project_root = global_vars.FLOW_DEFAULT_CONFIG_PATH

  cursor_pos = 0
  if kwargs.get('cursor_pos') :
    cursor_pos = kwargs.get('cursor_pos')
  else :
    if len(view.sel()) > 0 :
      cursor_pos = view.sel()[0].begin()
    
  row, col = view.rowcol(cursor_pos)

  if view.match_selector(
        cursor_pos,
        'source.js'
    ) and view.substr( sublime.Region(0, view.size()) ) == "" :
  
      current_contents = ""

  else :
    scope = view.scope_name(cursor_pos)

    if scope.startswith("source.js"):
      current_contents = view.substr(
        sublime.Region(0, view.size())
      )

    elif view.find_by_selector("source.js.embedded.html"):
      embedded_regions = view.find_by_selector("source.js.embedded.html")
      current_contents = ""
      prev_row_offset_end = 0
      prev_col_scope_end = 0
      for region in embedded_regions:
        row_scope, col_scope = view.rowcol(region.begin())
        row_offset = row_scope
        row_offset_end, col_scope_end = view.rowcol(region.end())
        row_scope = row - row_scope
        
        current_contents += (" " * (col_scope - prev_col_scope_end)) + ("\n" * (row_offset - prev_row_offset_end))
        prev_row_offset_end = row_offset_end
        prev_col_scope_end = col_scope_end
        current_contents += view.substr(region)

    else:
      return CLIRequirements(
          filename=None,
          project_root=None,
          contents="",
          cursor_pos=None,
          row=None, col=None
        )
  
  if kwargs.get('add_magic_token'):
    current_lines = current_contents.splitlines()

    try :
      current_line = current_lines[row]
    except IndexError as e:
      return CLIRequirements(
          filename=None,
          project_root=None,
          contents="",
          cursor_pos=None,
          row=None, col=None
        )

    tokenized_line = ""
    if not kwargs.get('not_add_last_part_tokenized_line') :
      tokenized_line = current_line[0:col] + 'AUTO332' + current_line[col:-1]
    else :
      tokenized_line = current_line[0:col] + 'AUTO332'
    current_lines[row] = tokenized_line
    current_contents = '\n'.join(current_lines)

  return CLIRequirements(
    filename=filename,
    project_root=project_root,
    contents=current_contents,
    cursor_pos=cursor_pos,
    row=row, col=col
  )

def hide_errors(view) :
  view.erase_regions('flow_error')
  view.erase_status('flow_error')