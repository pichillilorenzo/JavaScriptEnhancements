import sublime, sublime_plugin
import os

class RefactorExportFunctionCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    selection = view.sel()[0]
    window = view.window()
    file_name = view.file_name()
    inputs = args.get("inputs")
    tp = args.get("type")
    new_path = os.path.normpath(inputs["new_path"].strip())
    settings = get_project_settings()
    preview_view = None

    if not file_name:
      sublime.error_message("Cannot export " + tp + ". File name is empty.")
      return 

    if not new_path or new_path.endswith(os.path.sep) or os.path.isdir(new_path):
      sublime.error_message("The File path is empty or incorrect.")
      return 

    if new_path == file_name:
      sublime.message_dialog("The file path is the same as before.")
      return

    file_already_exists = os.path.isfile(new_path)

    if settings:

      if not args.get("preview"):

        if file_already_exists:
          if not sublime.ok_cancel_dialog(new_path + " already exists.", "Append export anyway"):
            return

        if not os.path.isdir(os.path.dirname(new_path)):
          try:
            os.makedirs(os.path.dirname(new_path))
          except FileNotFoundError as e:
            print(traceback.format_exc())
            sublime.error_message("Cannot create the path. On Windows could be caused by the '[WinError 206] The filename or extension is too long' error.")
            return
          except Exception as e:
            print(traceback.format_exc())
            sublime.error_message("Cannot create the path. The filename, directory name, or volume label syntax could be incorrect.")
            return

      else:
        preview_view = RefactorPreview("Refactor - Export " + tp.title() + " Preview")
        preview_view.append_text("Refactor - Export " + tp.title() + " Preview\n\n")

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
        fp_temp_contents=view.substr(sublime.Region(0, view.size())), 
        is_output_json=True,
        chdir=chdir,
        bin_path=bin_path,
        use_node=use_node
      )

      if result[0]:

        export_to_search = "FunctionDeclaration" if tp == "function" else ( "ClassDeclaration" if tp == "class" else "VariableDeclaration" )

        body = result[1]["body"]
        items = Util.nested_lookup("type", [export_to_search], body)
        export_name = ""
        kind = ""
        variable_declaration_region = None
        variable_declarations = []
        variable_declaration_index = -1

        for item in items:
          region = sublime.Region(int(item["range"][0]), int(item["range"][1]))
          if region.contains(selection):
            if export_to_search == "VariableDeclaration":
              variable_declaration_region = region
              variable_declarations = item["declarations"]
              for i in range(0, len(item["declarations"])):
                dec = item["declarations"][i]
                region = sublime.Region(int(dec["range"][0]), int(dec["range"][1]))
                if region.contains(selection) and dec["id"]:
                  variable_declaration_index = i
                  kind = item["kind"] + " "
                  item = dec
                  break
              if variable_declaration_index == -1:
                sublime.error_message("No " + tp + " to export. Select a " + tp + ".")
                return
            elif not item["id"]:
              return

            content = kind + view.substr(region)
            export_name = item["id"]["name"]

            if file_already_exists:
              with open(new_path, "r+") as file:
                result_exists = node.execute_check_output(
                  flow_cli,
                  [
                    'ast',
                    '--from', 'sublime_text'
                  ],
                  is_from_bin=is_from_bin,
                  use_fp_temp=True, 
                  fp_temp_contents=file.read(), 
                  is_output_json=True,
                  chdir=chdir,
                  bin_path=bin_path,
                  use_node=use_node
                )
              if result_exists[0]:
                body2 = result_exists[1]["body"]
                items2 = Util.nested_lookup("type", ["ExportDefaultDeclaration"], body2)
                items2 = items2 + Util.nested_lookup("type", ["ExportNamedDeclaration"], body2)
                for item2 in items2:
                  item2 = item2["declaration"]
                  if item2["type"] == "VariableDeclaration": 
                    if export_to_search == "VariableDeclaration":
                      for dec in item2["declarations"]:
                        if dec["id"] and export_name == dec["id"]["name"]:
                          sublime.error_message("Cannot export " + tp + ". A " + tp + " with the same name already exists.")
                          return
                  else:
                    if item2["id"] and export_name == item2["id"]["name"]:
                      sublime.error_message("Cannot export " + tp + ". A " + tp + " with the same name already exists.")
                      return

            if not args.get("preview"):
              if export_to_search == "FunctionDeclaration":
                params = "(" + ", ".join([ param["name"] for param in item["params"] ]) + ")"
                view.replace(edit, region, export_name + params)
              elif export_to_search == "ClassDeclaration":
                view.replace(edit, region, "let new_instance = new " + export_name + "()")
                view.sel().clear()
                view.sel().add(sublime.Region(region.begin() + len("let "), region.begin() + len("let new_instance")))
              else:
                if len(variable_declarations) == 1:
                  view.erase(edit, variable_declaration_region)
                elif variable_declaration_index == len(variable_declarations) - 1:
                  dec = variable_declarations[variable_declaration_index - 1]
                  second_last_variable_declaration_region = sublime.Region(int(dec["range"][0]), int(dec["range"][1]))
                  view.erase( edit, sublime.Region(second_last_variable_declaration_region.end(), region.end()) ) 
                else:
                  dec = variable_declarations[variable_declaration_index + 1]
                  next_variable_declaration_region = sublime.Region(int(dec["range"][0]), int(dec["range"][1]))
                  view.erase( edit, sublime.Region(region.begin(), next_variable_declaration_region.begin()) ) 

              if file_already_exists:
                with open(new_path, "r+") as file:
                  file_content = file.read().rstrip()
                  file.seek(0)
                  file.write( file_content + "\n\nexport " + content)
                  file.truncate()

              else:
                with open(new_path, "w+") as file:
                  file.seek(0)
                  file.write("// @flow \n\nexport" + (" default" if export_to_search != "VariableDeclaration" else "") + " " + content)
                  file.truncate()

            else:
              preview_content = "- Export to\n" + new_path + ":\n\n"
              if file_already_exists:
                with open(new_path, "r+") as file:
                  file_content = file.read().rstrip()
                  line = len(file_content.splitlines()) - 1
                  splitted_content = ( file_content + "\n\nexport " + content ).splitlines()
                  range_start = max(0, line)
                  range_end = min(line + 4, len(splitted_content) - 1)
                  while range_start <= range_end:
                    line_number = str(range_start + 1)
                    space_before_line_number = " " * ( 5 - len(line_number) )
                    preview_content += space_before_line_number + line_number + (": " if line + 2 == range_start else "  ") + splitted_content[range_start] + "\n"
                    range_start += 1
                  preview_content += "\n"
              else:
                splitted_content = ( "// @flow \n\nexport" + (" default" if export_to_search != "VariableDeclaration" else "") + " " + content ).splitlines()
                range_start = 0
                range_end = min(5, len(splitted_content) - 1)
                while range_start <= range_end:
                  line_number = str(range_start + 1)
                  space_before_line_number = " " * ( 5 - len(line_number) )
                  preview_content += space_before_line_number + line_number + "  " + splitted_content[range_start] + "\n"
                  range_start += 1
                preview_content += "\n"

              preview_view.append_text(preview_content)

            break

        if not export_name:
          sublime.error_message("No " + tp + " to export. Select a " + tp + ".")
          return

        rel_new_path = ""
        if os.path.dirname(new_path) == os.path.dirname(file_name):
          rel_new_path = "./" + os.path.basename(new_path)
        else:
          rel_new_path = os.path.relpath(new_path, start=os.path.dirname(file_name))

          if sublime.platform() == "windows":
            rel_new_path = Util.convert_path_to_unix(rel_new_path)

          if not rel_new_path.startswith(".."):
            rel_new_path = "./" + rel_new_path

        items = Util.nested_lookup("type", ["ImportDeclaration"], body)
        import_regions = []
        need_to_import = True

        for item in items:
          row = int(item['loc']['start']['line']) - 1
          endrow = int(item['loc']['end']['line']) - 1
          col = int(item['loc']['start']['column']) - 1
          endcol = int(item['loc']['end']['column'])

          if (item["source"]["value"] == rel_new_path if item["source"]["value"].endswith(".js") else item["source"]["value"] == rel_new_path[:-3]) and "specifiers" in item and item["specifiers"]:
            last_specifier = item["specifiers"][-1]
            if last_specifier["type"] != "ImportDefaultSpecifier":
              if not args.get("preview"):
                view.insert(edit, int(last_specifier["range"][1]), ", " + export_name)
              else:
                splitted_content = view.substr(sublime.Region(0, view.size())).splitlines()
                line = int(last_specifier['loc']['end']['line']) - 1
                line_col_offset = int(last_specifier['loc']['end']['column'])
                splitted_content[line] = splitted_content[line][:line_col_offset] + ", " + export_name + splitted_content[line][line_col_offset:]
                range_start = max(0, line - 2)
                range_end = min(line + 2, len(splitted_content) - 1)
                preview_content = "- Import to\n" + file_name + ":\n\n"
                while range_start <= range_end:
                  line_number = str(range_start + 1)
                  space_before_line_number = " " * ( 5 - len(line_number) )
                  preview_content += space_before_line_number + line_number + (": " if line == range_start else "  ") + splitted_content[range_start] + "\n"
                  range_start += 1
                preview_content += "\n"
                preview_view.append_text(preview_content)

              need_to_import = False
              break

          start_region = view.text_point(row, col)
          end_region = view.text_point(endrow, endcol)

          import_regions.append(sublime.Region(start_region, end_region))

        if need_to_import:
          last_import_region = ( import_regions[-1] if import_regions else (sublime.Region(0, 0) if not view.match_selector(0, 'comment') else view.extract_scope(0)) )

          text = "\nimport " + ( "{ " + export_name + " }" if file_already_exists or export_to_search == "VariableDeclaration" else export_name ) + " from '" + rel_new_path + "'\n"

          if not args.get("preview"):
            view.insert(edit, last_import_region.end(), text)
          else:
            splitted_content = view.substr(sublime.Region(0, view.size())).splitlines()
            line = view.rowcol(last_import_region.end())[0]
            splitted_content = splitted_content[:line] + text.splitlines() + ["\n"] + splitted_content[line + 1:]
            range_start = max(0, line - 2)
            range_end = min(line + 2, len(splitted_content) - 1)
            preview_content = "- Import to\n" + file_name + ":\n\n"
            while range_start <= range_end:
              line_number = str(range_start + 1)
              space_before_line_number = " " * ( 5 - len(line_number) )
              preview_content += space_before_line_number + line_number + (": " if line == range_start - 1 else "  ") + splitted_content[range_start] + "\n"
              range_start += 1
            preview_content += "\n"
            preview_view.append_text(preview_content)

      if not args.get("preview"):
        RefactorPreview.close("Refactor - Export " + tp.title() + " Preview")
        windowViewManager.close(view.id())

    else:
      sublime.error_message("Error: can't get project settings")
      
  def is_enabled(self, **args) :
    view = self.view
    if not view.file_name():
      return False
    settings = get_project_settings()
    if not settings or not Util.selection_in_js_scope(view):
      return False
    return True

  def is_visible(self, **args) :
    view = self.view
    if not view.file_name():
      return False
    settings = get_project_settings()
    if not settings or not Util.selection_in_js_scope(view):
      return False
    return True
      