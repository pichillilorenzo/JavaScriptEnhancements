import sublime, sublime_plugin
import os
import xml.etree.ElementTree as ET
from .. import util
from .. import NodeJS
from ..global_vars import *

class CLIRequirements():
  filename = ""
  project_root = ""
  contents = ""
  cursor_pos = 0
  row = 0
  col = 0

  def __init__(self, filename, project_root, contents, cursor_pos, row, col):
    self.filename = filename
    self.project_root = project_root
    self.contents = contents
    self.cursor_pos = cursor_pos
    self.row = row
    self.col = col

class FlowCLI():

  def __init__(self, view):
    self.view = view

    self.flow_cli = "flow"
    self.is_from_bin = True
    self.chdir = ""
    self.use_node = True
    self.bin_path = ""

    settings = util.get_project_settings()
    if settings and settings["project_settings"]["flow_cli_custom_path"]:
      self.flow_cli = os.path.basename(settings["project_settings"]["flow_cli_custom_path"])
      self.bin_path = os.path.dirname(settings["project_settings"]["flow_cli_custom_path"])
      self.is_from_bin = False
      self.chdir = settings["project_dir_name"]
      self.use_node = False

  def ast(self, options=[], **kwargs):

    deps = self.parse_cli_dependencies(self.view, **kwargs)

    node = NodeJS(check_local=True)
    
    result = node.execute_check_output(
      self.flow_cli,
      [
        'ast',
        '--from', 'sublime_text'
      ] + options,
      is_from_bin=self.is_from_bin,
      use_fp_temp=True, 
      fp_temp_contents=deps.contents, 
      is_output_json=True,
      chdir=self.chdir,
      bin_path=self.bin_path,
      use_node=self.use_node,
      clean_output_flow=True
    )

    return result

  def autocomplete(self, options=[], **kwargs):

    deps = self.parse_cli_dependencies(self.view, **kwargs)

    node = NodeJS(check_local=True)
    
    result = node.execute_check_output(
      self.flow_cli,
      [
        'autocomplete',
        '--from', 'sublime_text',
        '--root', deps.project_root,
        '--json',
        deps.filename
      ] + options,
      is_from_bin=self.is_from_bin,
      use_fp_temp=True, 
      fp_temp_contents=deps.contents, 
      is_output_json=True,
      chdir=self.chdir,
      bin_path=self.bin_path,
      use_node=self.use_node,
      clean_output_flow=True
    )

    return result

  def type_at_pos(self, options=[], **kwargs):

    deps = self.parse_cli_dependencies(self.view, **kwargs)

    node = NodeJS(check_local=True)
    
    result = node.execute_check_output(
      self.flow_cli,
      [
        'type-at-pos',
        '--from', 'sublime_text',
        '--root', deps.project_root,
        '--path', deps.filename,
        '--json'
      ] + options,
      is_from_bin=self.is_from_bin,
      use_fp_temp=True, 
      fp_temp_contents=deps.contents, 
      is_output_json=True,
      chdir=self.chdir,
      bin_path=self.bin_path,
      use_node=self.use_node,
      clean_output_flow=True
    )

    return result

  def get_def(self, options=[], **kwargs):

    deps = self.parse_cli_dependencies(self.view, **kwargs)

    node = NodeJS(check_local=True)
    
    result = node.execute_check_output(
      self.flow_cli,
      [
        'get-def',
        '--from', 'sublime_text',
        '--root', deps.project_root,
        '--json',
        ':temp_file',
        str(deps.row + 1), str(deps.col + 1)
      ] + options,
      is_from_bin=self.is_from_bin,
      use_fp_temp=True, 
      fp_temp_contents=deps.contents, 
      is_output_json=True,
      use_only_filename_view_flow=True,
      chdir=self.chdir,
      bin_path=self.bin_path,
      use_node=self.use_node,
      clean_output_flow=True
    )

    return result

  def check_contents(self, options=[], **kwargs):

    deps = self.parse_cli_dependencies(self.view, **kwargs)

    node = NodeJS(check_local=True)
    
    result = node.execute_check_output(
      self.flow_cli,
      [
        'check-contents',
        '--from', 'sublime_text',
        '--root', deps.project_root,
        '--include-warnings',
        '--json',
        deps.filename
      ] + options,
      is_from_bin=self.is_from_bin,
      use_fp_temp=True, 
      fp_temp_contents=deps.contents, 
      is_output_json=True,
      chdir=self.chdir,
      bin_path=self.bin_path,
      use_node=self.use_node,
      clean_output_flow=True
    )

    return result

  def get_imports(self, files=[], options=[], **kwargs):

    deps = self.parse_cli_dependencies(self.view, **kwargs)

    node = NodeJS(check_local=True)

    result = [False, {}]
    
    if sublime.platform() == "windows":
      javascript_files_temp = ""
      index = 0
      for i in range(0, len(files)):

        # <= 7500 because Windows has a limited length for command arguments
        if len(javascript_files_temp + " " + json.dumps(files[i], ensure_ascii=False)) <= 7500 :

          if not javascript_files_temp:
            javascript_files_temp = json.dumps(files[i], ensure_ascii=False)
          else:
            javascript_files_temp += " " + json.dumps(files[i], ensure_ascii=False)
        
          if i < len(files) - 1:
            continue

        r = node.execute_check_output(
          self.flow_cli,
          [
            'get-imports',
            '--from', 'sublime_text',
            '--root', deps.project_root,
            '--json'
          ] + ( files[index:i] if i < len(files) - 1 else files[index:]),
          is_from_bin=self.is_from_bin,
          use_fp_temp=False, 
          is_output_json=True,
          chdir=self.chdir,
          bin_path=self.bin_path,
          use_node=self.use_node,
          command_arg_escape=False,
          clean_output_flow=True
        )

        if r[0]:
          result[0] = r[0]
          result[1].update(r[1])
        else:
          return r

        index = i
        javascript_files_temp = json.dumps(files[i], ensure_ascii=False)

    else:
      result = node.execute_check_output(
        self.flow_cli,
        [
          'get-imports',
          '--from', 'sublime_text',
          '--root', deps.project_root,
          '--json'
        ] + files,
        is_from_bin=self.is_from_bin,
        use_fp_temp=False, 
        is_output_json=True,
        chdir=self.chdir,
        bin_path=self.bin_path,
        use_node=self.use_node,
        clean_output_flow=True
      )

    return result

  @staticmethod
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
        project_root = FLOW_DEFAULT_CONFIG_PATH

    cursor_pos = 0
    if kwargs.get('cursor_pos') :
      cursor_pos = kwargs.get('cursor_pos')
    else :
      if len(view.sel()) > 0 :
        cursor_pos = view.sel()[0].begin()
      
    row, col = view.rowcol(cursor_pos)

    if kwargs.get('contents') :
      current_contents = kwargs.get('contents')
    else :
      if view.match_selector(
            cursor_pos,
            'source.js'
        ) and view.substr( sublime.Region(0, view.size()) ) == "" :
      
          current_contents = ""

      else :
        scope = view.scope_name(cursor_pos)
        embedded_regions = []

        if scope.startswith("source.js"):
          current_contents = view.substr(
            sublime.Region(0, view.size())
          )

        else:
          # add vue.js support
          if view.find_by_selector("text.html.vue source.js.embedded.html"):
            vue_regions = view.find_by_selector("text.html.vue source.js.embedded.html")
            for region in vue_regions:
              old_region = region
              new_region = util.trim_region(view, old_region)

              # vue.js regions contains <script> and </script> in their contents, so I need to remove it
              script_str = view.substr(new_region)
              root = ET.fromstring(script_str)
              content = root.text
              offset = script_str.split(content)
              new_region = sublime.Region(new_region.begin() + len(offset[0]), new_region.end() - len(offset[1]))

              embedded_regions.append(new_region)
          elif view.find_by_selector("source.js.embedded.html"):
            embedded_regions = view.find_by_selector("source.js.embedded.html")

          if not embedded_regions:
            return CLIRequirements(
                filename=None,
                project_root=None,
                contents="",
                cursor_pos=None,
                row=None, col=None
              )

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
