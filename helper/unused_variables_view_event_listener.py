import sublime, sublime_plugin

class unused_variablesViewEventListener(wait_modified_asyncViewEventListener, sublime_plugin.ViewEventListener):

  unusedVariableRegions = []
  prefix_thread_name = "unused_variables"
  wait_time = .15
  modified = False

  def on_activated_async(self):
    self.on_modified_async()

  def on_modified(self):
    self.modified = True

  def on_modified_async(self):
    super(unused_variablesViewEventListener, self).on_modified_async()

  def on_selection_modified_async(self):

    view = self.view

    if not javascriptCompletions.get("enable_unused_variables_feature"):
      view.erase_status("unused_variables")
      view.erase_regions("unused_variables")
      return 
    elif view.find_by_selector('source.js.embedded.html'):
      pass
    elif not Util.selection_in_js_scope(view):
      view.erase_status("unused_variables")
      view.erase_regions("unused_variables")
      return

    statusInRegion = ""
    for region in self.unusedVariableRegions:
      if region.contains(view.sel()[0]):
        statusInRegion = "'" + view.substr(region) + "'"

    if self.unusedVariableRegions:
      if statusInRegion:
        view.set_status("unused_variables", str(len(self.unusedVariableRegions)) + " unused variables: " + statusInRegion )
      else:
        view.set_status("unused_variables", str(len(self.unusedVariableRegions)) + " unused variables" )

  def on_modified_async_with_thread(self, recheck=True):

    self.modified = False

    view = self.view

    if not javascriptCompletions.get("enable_unused_variables_feature"):
      view.erase_status("unused_variables")
      view.erase_regions("unused_variables")
      return 
    elif view.find_by_selector('source.js.embedded.html'):
      pass
    elif not Util.selection_in_js_scope(view):
      view.erase_status("unused_variables")
      view.erase_regions("unused_variables")
      return

    self.wait()

    deps_list = list()
    if view.find_by_selector("source.js.embedded.html") :
      deps_list = flow_parse_cli_dependencies(view, check_all_source_js_embedded=True)
    else :
      deps_list = [flow_parse_cli_dependencies(view)]

    flag = False

    for deps in deps_list:
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

      repetitions = dict()

      if result[0]:
        
        if "body" in result[1]:
          body = result[1]["body"]
          items = Util.nested_lookup("type", ["VariableDeclarator", "FunctionDeclaration", "ClassDeclaration", "ImportDefaultSpecifier", "ImportNamespaceSpecifier", "ImportSpecifier", "ArrayPattern", "ObjectPattern"], body)
          for item in items:

            if "id" in item and isinstance(item["id"],dict) and "name" in item["id"] and item["id"]["type"] == "Identifier":
              item = item["id"]

            elif "local" in item and isinstance(item["local"],dict) and "name" in item["local"] and item["local"]["type"] == "Identifier":
              item = item["local"]

            elif "properties" in item:
              for prop in item["properties"]:
                if prop["type"] == "Property" and "key" in prop and isinstance(prop["key"],dict) and "name" in prop["key"] and prop["key"]["type"] == "Identifier":
                  items += [prop["key"]]
              continue

            elif "elements" in item:
              for element in item["elements"]:
                if isinstance(element,dict) and "name" in element and element["type"] == "Identifier":
                  items += [element]
              continue

            #else :
            #  item = Util.nested_lookup("type", ["Identifier"], item)[0]

            variableName = ""
            try:
              variableName = item["name"]
            except (KeyError) as e:
              continue
            startRegion = view.text_point(int(item["loc"]["start"]["line"]) + deps.row_offset - 1, int(item["loc"]["start"]["column"]))
            endRegion = view.text_point(int(item["loc"]["end"]["line"]) + deps.row_offset - 1, int(item["loc"]["end"]["column"]))
            variableRegion = sublime.Region(startRegion, endRegion) 

            scope = view.scope_name(variableRegion.begin()-1).strip()
            scope_splitted = scope.split(" ")

            if scope.endswith(" punctuation.accessor.js") or scope.endswith(" keyword.operator.accessor.js"):
              continue

            if view.substr(view.line(variableRegion)).strip().startswith("export") and not scope.startswith("source.js meta.export.js meta.block.js") and not scope.startswith("source.js meta.group.braces.curly.js") and len(scope_splitted) <= 4:
              continue  

            repetitions[variableName] = [variableRegion]

          items = Util.nested_lookup("type", ["VariableDeclarator", "MemberExpression", "CallExpression", "BinaryExpression", "ExpressionStatement", "Property", "ArrayExpression", "ObjectPattern", "AssignmentExpression", "IfStatement", "ForStatement", "WhileStatement", "ForInStatement", "ForOfStatement", "LogicalExpression", "UpdateExpression", "ArrowFunctionExpression", "ConditionalExpression", "JSXIdentifier", "ExportDefaultDeclaration", "JSXExpressionContainer", "NewExpression", "ReturnStatement"], body)
          for item in items:

            if "exportKind" in item and "declaration" in item and isinstance(item["declaration"],dict) and "name" in item["declaration"] and item["declaration"]["type"] == "Identifier":
              item = item["declaration"]

            elif "object" in item :
              if "property" in item and isinstance(item["property"],dict) and "name" in item["property"] and item["property"]["type"] == "Identifier":
                items += [item["property"]]
              if "object" in item and isinstance(item["object"],dict) and "name" in item["object"] and item["object"]["type"] == "Identifier":
                item = item["object"]
              else:
                continue

            elif "callee" in item :    
              if "arguments" in item:
                for argument in item["arguments"]:
                  if isinstance(argument,dict) and "name" in argument and argument["type"] == "Identifier":
                    items += [argument]
                  elif "expressions" in argument and argument["expressions"]:
                    for expression in argument["expressions"]:
                      if isinstance(expression,dict) and "name" in expression and expression["type"] == "Identifier":
                        items += [expression]

              item = item["callee"]

            elif "left" in item or "right" in item:

              if "left" in item and isinstance(item["left"],dict) and "name" in item["left"] and item["left"]["type"] == "Identifier":
                items += [item["left"]]
              if "right" in item and isinstance(item["right"],dict) and "name" in item["right"] and item["right"]["type"] == "Identifier":
                items += [item["right"]]

            elif "test" in item:
              if "consequent" in item and isinstance(item["consequent"],dict) and "name" in item["consequent"] and item["consequent"]["type"] == "Identifier":
                items += [item["consequent"]]
              if "alternate" in item and isinstance(item["alternate"],dict) and "name" in item["alternate"] and item["alternate"]["type"] == "Identifier":
                items += [item["alternate"]]
              if isinstance(item["test"],dict) and "name" in item["test"] and item["test"]["type"] == "Identifier":
                item = item["test"]
              else:
                continue

            elif "expression" in item and isinstance(item["expression"],dict) and "name" in item["expression"] and item["expression"]["type"] == "Identifier":
              item = item["expression"]

            elif "argument" in item and isinstance(item["argument"],dict) and "name" in item["argument"] and item["argument"]["type"] == "Identifier":
              item = item["argument"]

            elif "elements" in item :
              for element in item["elements"]:
                if isinstance(element,dict) and "name" in element and element["type"] == "Identifier":
                  items += [element]
              continue

            elif "value" in item and isinstance(item["value"],dict) and "name" in item["value"] and item["value"]["type"] == "Identifier":
              item = item["value"]

            elif "init" in item and isinstance(item["init"],dict) and "name" in item["init"] and item["init"]["type"] == "Identifier":
              item = item["init"]

            elif "body" in item and isinstance(item["body"],dict) and "name" in item["body"] and item["body"]["type"] == "Identifier":
              item = item["body"]

            variableName = ""
            try:
              variableName = item["name"]
            except (KeyError) as e:
              continue

            startRegion = view.text_point(int(item["loc"]["start"]["line"]) + deps.row_offset - 1, int(item["loc"]["start"]["column"]))
            endRegion = view.text_point(int(item["loc"]["end"]["line"]) + deps.row_offset - 1, int(item["loc"]["end"]["column"]))
            variableRegion = sublime.Region(startRegion, endRegion) 

            scope = view.scope_name(variableRegion.begin()-1).strip()

            if scope.endswith(" punctuation.accessor.js") or scope.endswith(" keyword.operator.accessor.js"):
              continue

            if variableName in repetitions and not variableRegion in repetitions[variableName]:
              repetitions[variableName] += [variableRegion]

          if not flag:
            self.unusedVariableRegions = [] 
            flag = True
          
          errorRegions = view.get_regions("flow_error")
          for variableName in repetitions.keys():
            count = len(repetitions[variableName])
            if count == 1:
              intersects = False
              for errorRegion in errorRegions:
                if errorRegion.intersects(repetitions[variableName][0]):
                  intersects = True
                  break
              if not intersects:
                self.unusedVariableRegions += [repetitions[variableName][0]]

    if not self.modified :
      view.erase_regions("unused_variables")
      if self.unusedVariableRegions:
        view.add_regions("unused_variables", self.unusedVariableRegions, "string", "dot", sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE | sublime.DRAW_SQUIGGLY_UNDERLINE)
      else:
        view.erase_status("unused_variables")
    elif (recheck) :
        sublime.set_timeout_async(lambda: self.on_modified_async_with_thread(recheck=False))

class navigate_unused_variablesCommand(navigate_regionsCommand, sublime_plugin.TextCommand):

  region_key = "unused_variables"