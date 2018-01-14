import sublime, sublime_plugin

class sort_javascript_importsCommand(sublime_plugin.TextCommand):

  def run(self, edit, **args):
    view = self.view

    if "imports" in args and "regionPoints" in args:
      imports = args.get('imports')
      regionPoints = args.get('regionPoints')
      first_line = view.substr(view.full_line(0)).strip()
      first_line_empty = True if not first_line or not first_line.startswith("import") else False
      if regionPoints:
        for i in range(1, len(regionPoints)+1):
          regionPoint = regionPoints[-i]
          region = sublime.Region(regionPoint[0], regionPoint[1])
          full_line = view.substr(view.full_line(region)).replace(view.substr(region), '').strip()
          if not full_line:
            region = sublime.Region(regionPoint[0]-1, regionPoint[1])
          view.erase(edit, region)

        if view.match_selector(0, 'comment'):
          comment = view.extract_scope(0)
          view.replace(edit, sublime.Region(comment.end(), comment.end()), "\n" + "\n".join(sorted(imports)))
        elif first_line_empty:
          view.replace(edit, sublime.Region(0,0), "\n".join(sorted(imports)) + "\n\n")
        else:
          view.replace(edit, sublime.Region(0,0), "\n".join(sorted(imports)))

    else:
      sublime.set_timeout_async(self.get_imports)

  def get_imports(self):

    view = self.view

    deps = flow_parse_cli_dependencies(view)

    flow_cli = "flow"
    is_from_bin = True
    chdir = ""
    use_node = True
    bin_path = ""

    settings = get_project_settings()
    if settings and settings["project_settings"]["flow_cli_custom_path"]:
      flow_cli = os.path.basename(settings["project_settings"]["flow_cli_custom_path"])
      bin_path = os.path.dirname(settings["project_settings"]["flow_cli_custom_path"])
      is_from_bin = False
      chdir = settings["project_dir_name"]
      use_node = False

    node = NodeJS(check_local=True)
    
    result = node.execute_check_output(
      flow_cli,
      [
        'ast',
        '--from', 'sublime_text'
      ],
      is_from_bin=is_from_bin,
      use_fp_temp=True, 
      fp_temp_contents=deps.contents, 
      is_output_json=True,
      chdir=chdir,
      bin_path=bin_path,
      use_node=use_node
    )

    if result[0]:
      if "body" in result[1]:
        body = result[1]["body"]
        items = Util.nested_lookup("type", ["ImportDeclaration"], body)
        imports = []
        regionPoints = []
        for item in items:
          row = int(item['loc']['start']['line']) - 1
          endrow = int(item['loc']['end']['line']) - 1
          col = int(item['loc']['start']['column']) - 1
          endcol = int(item['loc']['end']['column'])

          startRegion = view.text_point(row, col)
          endRegion = view.text_point(endrow, endcol)
          regionPoints += [[startRegion, endRegion]]

          importRegion = sublime.Region(startRegion, endRegion) 

          imports += [view.substr(importRegion)]

        view.run_command('sort_javascript_imports', args={"imports": imports, "regionPoints": regionPoints})
  
  def is_enabled(self):
    view = self.view
    if not Util.selection_in_js_scope(view) and view.find_by_selector('source.js.embedded.html'):
      return False

    if view.find_by_selector('meta.import.js'):
      return True

    # try JavaScript (Babel) syntax
    import_regions = view.find_by_selector('keyword.operator.module.js')
    for import_region in import_regions:
      if (view.substr(import_region).startswith("import")) :
        return True

    return False

  def is_visible(self):
    view = self.view
    if not Util.selection_in_js_scope(view) and view.find_by_selector('source.js.embedded.html'):
      return False

    if view.find_by_selector('meta.import.js'):
      return True

    # try JavaScript (Babel) syntax
    import_regions = view.find_by_selector('keyword.operator.module.js')
    for import_region in import_regions:
      if (view.substr(import_region).startswith("import")) :
        return True

    return False
