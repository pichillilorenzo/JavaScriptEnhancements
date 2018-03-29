import sublime, sublime_plugin
import os
from ..libs import NodeJS
from ..libs import javaScriptEnhancements
from ..libs import FlowCLI
from ..libs import util
from .wait_modified_async import JavascriptEnhancementsWaitModifiedAsyncViewEventListener

class JavascriptEnhancementsShowUnusedVariablesViewEventListener(JavascriptEnhancementsWaitModifiedAsyncViewEventListener, sublime_plugin.ViewEventListener):

  unused_variable_regions = []
  prefix_thread_name = "javascript_enhancements_unused_variable"
  wait_time = .15
  modified = False

  def on_load_async(self):
    self.on_modified_async()

  def on_activated_async(self):
    self.on_modified_async()

  def on_modified(self):
    self.modified = True

  def on_modified_async(self):
    super(JavascriptEnhancementsShowUnusedVariablesViewEventListener, self).on_modified_async()

  def on_selection_modified_async(self):

    view = self.view

    if not javaScriptEnhancements.get("enable_unused_variables_feature"):
      view.erase_status("javascript_enhancements_unused_variable")
      view.erase_regions("javascript_enhancements_unused_variable")
      return 
    elif view.find_by_selector('source.js.embedded.html'):
      pass
    elif not util.selection_in_js_scope(view) or not (self.unused_variable_regions or view.get_regions("javascript_enhancements_unused_variable")):
      view.erase_status("javascript_enhancements_unused_variable")
      view.erase_regions("javascript_enhancements_unused_variable")
      return

    view_status_curr_region = ""
    for region in self.unused_variable_regions:
      if region.contains(view.sel()[0]):
        view_status_curr_region = "'" + view.substr(region) + "'"

    if self.unused_variable_regions:
      if view_status_curr_region:
        view.set_status("javascript_enhancements_unused_variable", str(len(self.unused_variable_regions)) + " unused variables: " + view_status_curr_region )
      else:
        view.set_status("javascript_enhancements_unused_variable", str(len(self.unused_variable_regions)) + " unused variables" )

  def on_modified_async_with_thread(self, recheck=True):

    self.modified = False

    view = self.view

    if not javaScriptEnhancements.get("enable_unused_variables_feature"):
      view.erase_status("javascript_enhancements_unused_variable")
      view.erase_regions("javascript_enhancements_unused_variable")
      return 
    elif view.find_by_selector('source.js.embedded.html'):
      pass
    elif not util.selection_in_js_scope(view):
      view.erase_status("javascript_enhancements_unused_variable")
      view.erase_regions("javascript_enhancements_unused_variable")
      return

    self.wait()

    flow_cli = FlowCLI(view)
    result = flow_cli.ast()
    
    repetitions = dict()

    if result[0]:
      
      if "body" in result[1]:
        body = result[1]["body"]
        items = util.nested_lookup("type", ["VariableDeclarator", "FunctionDeclaration", "ClassDeclaration", "ImportDefaultSpecifier", "ImportNamespaceSpecifier", "ImportSpecifier", "ArrayPattern", "ObjectPattern"], body)
        for item in items:

          if "id" in item and isinstance(item["id"],dict) and "name" in item["id"] and item["id"]["type"] == "Identifier":
            item = item["id"]

          elif "local" in item and isinstance(item["local"],dict) and "name" in item["local"] and item["local"]["type"] == "Identifier":
            item = item["local"]

          elif "properties" in item:
            for prop in item["properties"]:
              if prop["type"] == "Property" and "value" in prop and isinstance(prop["value"],dict) and "name" in prop["value"] and prop["value"]["type"] == "Identifier":
                items += [prop["value"]]
            continue

          elif "elements" in item:
            for element in item["elements"]:
              if isinstance(element,dict) and "name" in element and element["type"] == "Identifier":
                items += [element]
            continue

          #else :
          #  item = util.nested_lookup("type", ["Identifier"], item)[0]

          variable_name = ""
          try:
            variable_name = item["name"]
          except (KeyError) as e:
            continue
            
          start_region = view.text_point(int(item["loc"]["start"]["line"]) - 1, int(item["loc"]["start"]["column"]))
          end_region = view.text_point(int(item["loc"]["end"]["line"]) - 1, int(item["loc"]["end"]["column"]))
          variable_region = sublime.Region(start_region, end_region) 

          scope = view.scope_name(variable_region.begin()-1).strip()
          scope_splitted = scope.split(" ")

          if scope.endswith(" punctuation.accessor.js") or scope.endswith(" keyword.operator.accessor.js"):
            continue

          if view.substr(view.line(variable_region)).strip().startswith("export") and not scope.startswith("source.js meta.export.js meta.block.js") and not scope.startswith("source.js meta.group.braces.curly.js") and len(scope_splitted) <= 4:
            continue  

          repetitions[variable_name] = [variable_region]

        items = util.nested_lookup("type", ["VariableDeclarator", "MemberExpression", "CallExpression", "BinaryExpression", "ExpressionStatement", "Property", "ArrayExpression", "ObjectPattern", "AssignmentExpression", "IfStatement", "ForStatement", "WhileStatement", "ForInStatement", "ForOfStatement", "LogicalExpression", "UpdateExpression", "ArrowFunctionExpression", "ConditionalExpression", "JSXIdentifier", "ExportDefaultDeclaration", "JSXExpressionContainer", "NewExpression", "ReturnStatement", "SpreadProperty", "TemplateLiteral", "ObjectPattern", "ObjectExpression", "TypeAnnotation", "ClassDeclaration"], body)
        for item in items:

          if item["type"] == "ClassDeclaration":
            if "superClass" in item and isinstance(item["superClass"],dict) and "name" in item["superClass"] and item["superClass"]["type"] == "Identifier":
              item = item["superClass"]
            elif "implements" in item and item["implements"]:
              for interface in item["implements"]:
                if "id" in interface and isinstance(interface["id"],dict) and "name" in interface["id"] and interface["id"]["type"] == "Identifier":
                  items += [interface["id"]]

          elif "exportKind" in item and "declaration" in item and isinstance(item["declaration"],dict) and "name" in item["declaration"] and item["declaration"]["type"] == "Identifier":
            item = item["declaration"]

          elif "object" in item :
            if "property" in item and isinstance(item["property"],dict) and "name" in item["property"] and item["property"]["type"] == "Identifier":
              items += [item["property"]]
            if "object" in item and isinstance(item["object"],dict) and "name" in item["object"] and item["object"]["type"] == "Identifier":
              item = item["object"]
            else:
              continue

          elif "properties" in item:
            for prop in item["properties"]:
              if prop["type"] == "Property" and "key" in prop and isinstance(prop["key"],dict) and "name" in prop["key"] and prop["key"]["type"] == "Identifier":
                items += [prop["key"]]
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

          elif "typeAnnotation" in item and isinstance(item["typeAnnotation"],dict) and "id" in item["typeAnnotation"] and "name" in item["typeAnnotation"]["id"] and item["typeAnnotation"]["id"]["type"] == "Identifier":
            item = item["typeAnnotation"]["id"]

          elif "expressions" in item and item["expressions"]:
            for expression in item["expressions"]:
              if isinstance(expression,dict) and "name" in expression and expression["type"] == "Identifier":
                items += [expression]
            continue

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
            if isinstance(item["test"],dict) and item["test"]["type"] == "UnaryExpression" and "argument" in item["test"] and "name" in item["test"]["argument"] and item["test"]["argument"]["type"] == "Identifier":
              item = item["test"]["argument"]
            else:
              continue

          elif "expression" in item and isinstance(item["expression"],dict) and "name" in item["expression"] and item["expression"]["type"] == "Identifier":
            item = item["expression"]

          elif "expression" in item and isinstance(item["expression"],dict) and item["expression"]["type"] == "TaggedTemplateExpression" and "tag" in item["expression"]:
            item = item["expression"]["tag"]

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

          variable_name = ""
          try:
            variable_name = item["name"]
          except (KeyError) as e:
            continue

          start_region = view.text_point(int(item["loc"]["start"]["line"]) - 1, int(item["loc"]["start"]["column"]))
          end_region = view.text_point(int(item["loc"]["end"]["line"]) - 1, int(item["loc"]["end"]["column"]))
          variable_region = sublime.Region(start_region, end_region) 

          scope = view.scope_name(variable_region.begin()-1).strip()

          if scope.endswith(" punctuation.accessor.js") or scope.endswith(" keyword.operator.accessor.js"):
            continue

          if variable_name in repetitions and not variable_region in repetitions[variable_name]:
            repetitions[variable_name] += [variable_region]

        self.unused_variable_regions = [] 
        error_regions = view.get_regions("javascript_enhancements_flow_error") + view.get_regions("javascript_enhancements_flow_warning")
        for variable_name in repetitions.keys():
          count = len(repetitions[variable_name])
          if count == 1:
            intersects = False
            for error_region in error_regions:
              if error_region.intersects(repetitions[variable_name][0]):
                intersects = True
                break
            if not intersects:
              self.unused_variable_regions += [repetitions[variable_name][0]]

    if not self.modified :
      view.erase_regions("javascript_enhancements_unused_variable")
      if self.unused_variable_regions:
        view.add_regions("javascript_enhancements_unused_variable", self.unused_variable_regions, "comment", "dot", sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE | sublime.DRAW_SQUIGGLY_UNDERLINE)
      else:
        view.erase_status("javascript_enhancements_unused_variable")
    elif (recheck) :
        sublime.set_timeout_async(lambda: self.on_modified_async_with_thread(recheck=False))
