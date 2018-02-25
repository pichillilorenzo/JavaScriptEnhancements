import sublime, sublime_plugin
import os
from ...libs import util
from ...libs import NodeJS

class JavascriptEnhancementsRefactorExtractFieldCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    selection = view.sel()[0]
    inputs = args.get("inputs")
    content = view.substr(selection).strip()
    content = content[:-1] if content[-1] == ";" else content
    field_name = inputs["field_name"].strip()

    flow_cli = "flow"
    is_from_bin = True
    chdir = ""
    use_node = True
    bin_path = ""

    settings = util.get_project_settings()
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
      fp_temp_contents=content, 
      is_output_json=True,
      chdir=chdir,
      bin_path=bin_path,
      use_node=use_node
    )

    if result[0] and not result[1]["errors"] and result[1]["body"] and "type" in result[1]["body"][0] and result[1]["body"][0]["type"] == "ExpressionStatement":

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
        if "body" in result[1]:
          body = result[1]["body"]
          classes = util.nested_lookup("type", ["ClassDeclaration"], body)
          _class = None
          class_region = None

          for c in classes:
            r = sublime.Region(int(c["range"][0]), int(c["range"][1]))
            if r.contains(selection):
              _class = c
              class_region = r
              break

          if class_region: 

            items = util.nested_lookup("type", ["BlockStatement"], _class)
            last_block_statement = None
            last_item = None
            region = None
            constructor_region = None
            constructor_method = None

            method_definitions = util.nested_lookup("type", ["MethodDefinition"], _class)

            for method in method_definitions:
              if method["kind"] == "constructor":
                constructor_method = method
                constructor_region = sublime.Region(int(method["value"]["body"]["range"][0]), int(method["value"]["body"]["range"][1]))
                break

            for item in items:
              r = sublime.Region(int(item["range"][0]), int(item["range"][1]))
              if r.contains(selection):
                last_block_statement = r
                last_item = item

            if last_block_statement:
              for item in last_item["body"]:
                r = sublime.Region(int(item["range"][0]), int(item["range"][1]))
                if r.contains(selection):
                  region = r
                  break

            if region: 

              class_properties = util.nested_lookup("type", ["ClassProperty"], _class)
              last_class_property = None
              region_last_class_property = None
              if len(class_properties) > 0:
                last_class_property = class_properties[-1]
                region_last_class_property = sublime.Region(int(last_class_property["range"][0]), int(last_class_property["range"][1]))

              if not constructor_region and inputs["scope"] == "Class constructor":
                if region_last_class_property:
                  view.insert(edit, region_last_class_property.end(), "\n\n\tconstructor () {\n\t}")
                else:
                  view.insert(edit, int(_class["body"]["range"][0]) + 1, "\n\n\tconstructor () {\n\t}")

                # create the constructor method and then execute this command again
                view.run_command("refactor_extract_field", args={"inputs": inputs})
                return

              prev_line_is_empty = util.prev_line_is_empty(view, region)
              
              space = ""
              if inputs["scope"] == "Current method" or inputs["scope"] == "Class constructor":
                space = util.get_whitespace_from_line_begin(
                  view, 
                  ( 
                    region 
                    if inputs["scope"] == "Current method" 
                    else sublime.Region(int(constructor_method["range"][0]), int(constructor_method["range"][1])) 
                  )
                )
                if inputs["scope"] == "Class constructor":
                  space += util.convert_tabs_using_tab_size(view, "\t")

              str_assignement = "this." + (field_name + " = " + content if inputs["scope"] == "Current method" or inputs["scope"] == "Class constructor" else field_name)

              is_line_empty = view.substr(view.line(selection)).strip().replace(view.substr(selection), "") == ""

              view.erase(edit, selection)

              if not is_line_empty:
                view.insert(edit, selection.begin(), "this." + field_name)
                if inputs["scope"] == "Current method":
                  str_assignement = ("\n" + space if not prev_line_is_empty else "") + "this." + field_name + " = " + content + "\n" + space
                  view.insert(edit, region.begin(), str_assignement)
                else:
                  str_assignement = ""
              else:
                if inputs["scope"] == "Class constructor":
                  view.insert(edit, selection.begin(), "this." + field_name)
                else:
                  view.insert(edit, selection.begin(), str_assignement)

              if inputs["scope"] == "Class constructor":
                str_assignement = "\n" + space + "this." + field_name + " = " + content + ("\n" + space if view.substr(constructor_region).splitlines()[0].strip().replace("{", "") != "" else "")
                view.insert(edit, constructor_region.begin() + 1, str_assignement)

              str_class_property = ""
              if region_last_class_property:
                str_class_property = "\n\t" + (field_name if inputs["scope"] == "Current method" or inputs["scope"] == "Class constructor" else field_name + " = " + content) + ";"
                view.insert(edit, region_last_class_property.end(), str_class_property)
              else:
                str_class_property = "\n\n\t" + (field_name if inputs["scope"] == "Current method" or inputs["scope"] == "Class constructor" else field_name + " = " + content) + ";"
                view.insert(edit, int(_class["body"]["range"][0])+1, str_class_property)

              str_class_property = util.convert_tabs_using_tab_size(view, str_class_property)

              view.sel().clear()

              if not is_line_empty:

                view.sel().add(
                  sublime.Region(
                    selection.begin()+len("this.")+len(str_assignement)+len(str_class_property), 
                    selection.begin()+len("this.")+len(str_assignement)+len(field_name)+len(str_class_property)
                  )
                )

                if inputs["scope"] == "Current method" or inputs["scope"] == "Class constructor":

                  view.sel().add(
                    sublime.Region(
                      (
                        region.begin() 
                        if inputs["scope"] == "Current method" 
                        else constructor_region.begin() + 1
                      ) + 
                      len(("\n" + space if not prev_line_is_empty else "") + "this.") + 
                      len(str_class_property)

                      , 

                      (
                        region.begin() 
                        if inputs["scope"] == "Current method" 
                        else constructor_region.begin() + 1
                      ) + 
                      len(("\n" + space if not prev_line_is_empty else "") + "this.") + 
                      len(field_name) + 
                      len(str_class_property)
                    )
                  )

              else:  
                view.sel().add(
                  sublime.Region(
                    selection.begin() +
                    len("this.") +
                    len(str_class_property) +
                    (len(str_assignement) if inputs["scope"] == "Class constructor" else 0)

                    , 

                    selection.begin() +
                    len("this.") +
                    len(field_name) +
                    len(str_class_property) +
                    (len(str_assignement) if inputs["scope"] == "Class constructor" else 0)
                  )
                )

                if inputs["scope"] == "Class constructor":
                  view.sel().add(
                    sublime.Region(
                      constructor_region.begin() + 1 + 
                      len(("\n" + space if not prev_line_is_empty else "") + "this.") + 
                      len(str_class_property)

                      , 

                      constructor_region.begin() + 1 + 
                      len(("\n" + space if not prev_line_is_empty else "") + "this.") + 
                      len(field_name) + 
                      len(str_class_property)
                    )
                  )

              tab_to_string =  util.convert_tabs_using_tab_size(view, "\t")

              if region_last_class_property:
                view.sel().add(
                  sublime.Region(
                    region_last_class_property.end()+len("\n" + tab_to_string), 
                    region_last_class_property.end()+len("\n" + tab_to_string)+len(field_name)
                  )
                )
              else:
                view.sel().add(
                  sublime.Region(
                    int(_class["body"]["range"][0])+1+len("\n\n" + tab_to_string), 
                    int(_class["body"]["range"][0])+1+len("\n\n" + tab_to_string)+len(field_name)
                  )
                )

      else:
        sublime.error_message("Cannot introduce property. Some problems occured.")

    else:
      sublime.error_message("Cannot introduce property. Selection does not form an ExpressionStatement.")

  def is_enabled(self, **args) :
    view = self.view
    if not util.selection_in_js_scope(view) :
      return False
    selection = view.sel()[0]
    return selection.begin() != selection.end()

  def is_visible(self, **args) :
    view = self.view
    if not util.selection_in_js_scope(view) :
      return False
    selection = view.sel()[0]
    return selection.begin() != selection.end()
