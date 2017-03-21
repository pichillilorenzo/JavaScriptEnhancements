def show_flow_errors(view) :

  view_settings = view.settings()
  sel = view.sel()[0]
  if not view.match_selector(
      sel.begin(),
      'source.js'
  ) and not view.find_by_selector("source.js.embedded.html") :
    return None

  deps_list = list()
  if view.find_by_selector("source.js.embedded.html") :
    deps_list = flow_parse_cli_dependencies(view, check_all_source_js_embedded=True)
  else :
    deps_list = [flow_parse_cli_dependencies(view)]

  errors = []
  description_by_row = {}
  regions = []
  for deps in deps_list:
    if deps.project_root is '/':
      return None

    """
    if (
      '// @flow' not in deps.contents and
      '/* @flow */' not in deps.contents
    ):
      return view.erase_regions('flow_error')
    """

    if view_settings.get("flow_weak_mode") :
      deps = deps._replace(contents = "/* @flow weak */" + deps.contents)

    result = node.execute_check_output(
      "flow",
      [
        'check-contents',
        '--from', 'sublime_text',
        '--root', deps.project_root,
        '--json',
        deps.filename
      ],
      is_from_bin=True,
      use_fp_temp=True, 
      fp_temp_contents=deps.contents, 
      is_output_json=True,
      clean_output_flow=True
    )

    if result[0]:

      if result[1]['passed']:
        continue

      for error in result[1]['errors']:
        description = ''
        operation = error.get('operation')
        row = -1
        for i in range(len(error['message'])):
          message = error['message'][i]
          if i == 0 :
            row = int(message['line']) + deps.row_offset - 1
            col = int(message['start']) - 1
            endcol = int(message['end'])

            if row == 0 and view_settings.get("flow_weak_mode") : #fix when error start at the first line with @flow weak mode
              col = col - len("/* @flow weak */")
              endcol = endcol - len("/* @flow weak */")

            regions.append(Util.rowcol_to_region(view, row, col, endcol))

            if operation:
              description += operation["descr"]

          if not description :
            description += message['descr']
          else :
            description += ". " + message['descr']

        if row >= 0 :
          row_description = description_by_row.get(row)
          if not row_description:
            description_by_row[row] = description
          if row_description and description not in row_description:
            description_by_row[row] += '; ' + description
            
      errors = result[1]['errors']

  if errors :
    view.add_regions(
      'flow_error', regions, 'scope.js', 'dot',
      sublime.DRAW_SQUIGGLY_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
    )
    return {"errors": errors, "description_by_row": description_by_row}
  
  view.erase_regions('flow_error')
  view.set_status('flow_error', 'Flow: no errors')
  return None

def hide_flow_errors(view) :
  view.erase_regions('flow_error')
  view.erase_status('flow_error')

class handle_flow_errorsCommand(sublime_plugin.TextCommand):

  def run(self, edit, **args):
    if args :
      if args["type"] == "show" :
        show_flow_errors(self.view)
      elif args["type"] == "hide" :
        hide_flow_errors(self.view)
