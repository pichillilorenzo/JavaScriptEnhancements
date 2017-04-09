import sublime, sublime_plugin
import os
from collections import namedtuple

flowCLIRequirements = namedtuple('flowCLIRequirements', [
    'filename', 'project_root', 'contents', 'cursor_pos', 'row', 'col', 'row_offset'
])

FLOW_DEFAULT_CONFIG_PATH = os.path.join(PACKAGE_PATH, "flow", ".flowconfig")

def find_flow_config(filename):
  if not filename or filename is '/':
    return FLOW_DEFAULT_CONFIG_PATH

  potential_root = os.path.dirname(filename)
  if os.path.isfile(os.path.join(potential_root, '.flowconfig')):
    return potential_root

  return find_flow_config(potential_root)

def flow_parse_cli_dependencies(view, **kwargs):
  filename = view.file_name()
  contextual_keys = sublime.active_window().extract_variables()
  folder_path = contextual_keys.get("folder")
  if folder_path and os.path.isdir(folder_path) and os.path.isfile(os.path.join(folder_path, '.flowconfig')) :    
    project_root = folder_path
  else :
    project_root = find_flow_config(filename)

  cursor_pos = 0
  if kwargs.get('cursor_pos') :
    cursor_pos = kwargs.get('cursor_pos')
  else :
    if len(view.sel()) > 0 :
      cursor_pos = view.sel()[0].begin()
    
  row, col = view.rowcol(cursor_pos)

  if kwargs.get('check_all_source_js_embedded'):
    embedded_regions = view.find_by_selector("source.js.embedded.html")
    if not embedded_regions :
      return flowCLIRequirements(
        filename=None,
        project_root=None,
        contents="",
        cursor_pos=None,
        row=None, col=None,
        row_offset=0
      )
    flowCLIRequirements_list = list()
    for region in embedded_regions:
      current_contents = view.substr(region)
      row_scope, col_scope = view.rowcol(region.begin())
      row_offset = row_scope
      row_scope = row - row_scope

      flowCLIRequirements_list.append(flowCLIRequirements(
        filename=filename,
        project_root=project_root,
        contents=current_contents,
        cursor_pos=cursor_pos,
        row=row, col=col,
        row_offset=row_offset
      ))
    return flowCLIRequirements_list
  else :
    scope_region = None
    if view.match_selector(
        cursor_pos,
        'source.js'
    ) and view.substr(sublime.Region(0, view.size()) ) == "" :
      scope_region = sublime.Region(0, 0)
    else :
      scope = view.scope_name(cursor_pos)
      result = Util.get_region_scope_first_match(view, scope, sublime.Region(cursor_pos, cursor_pos), "source.js")
      if not result:
        result = Util.get_region_scope_first_match(view, scope, sublime.Region(cursor_pos, cursor_pos), "source.js.embedded.html")
        if not result:
          return flowCLIRequirements(
            filename=None,
            project_root=None,
            contents="",
            cursor_pos=None,
            row=None, col=None,
            row_offset=0
          )
      scope_region = result["region"]
    current_contents = view.substr(scope_region)
    row_scope, col_scope = view.rowcol(scope_region.begin())
    row_offset = row_scope
    row_scope = row - row_scope
    """
    current_contents = view.substr(
      sublime.Region(0, view.size())
    )
    """
    
    if kwargs.get('add_magic_token'):
      current_lines = current_contents.splitlines()
      try :
        current_line = current_lines[row_scope]
      except IndexError as e:
        return flowCLIRequirements(
            filename=None,
            project_root=None,
            contents="",
            cursor_pos=None,
            row=None, col=None,
            row_offset=0
          )
      tokenized_line = ""
      if not kwargs.get('not_add_last_part_tokenized_line') :
        tokenized_line = current_line[0:col] + 'AUTO332' + current_line[col:-1]
      else :
        tokenized_line = current_line[0:col] + 'AUTO332'
      current_lines[row_scope] = tokenized_line
      current_contents = '\n'.join(current_lines)

    return flowCLIRequirements(
      filename=filename,
      project_root=project_root,
      contents=current_contents,
      cursor_pos=cursor_pos,
      row=row, col=col,
      row_offset=row_offset
    )
