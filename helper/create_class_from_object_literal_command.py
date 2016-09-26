class create_class_from_object_literalCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    selections = view.sel()
    for selection in selections :
      scope = view.scope_name(selection.begin()).strip()
      depth_level = Util.split_string_and_find(scope, "meta.object-literal.js")
      item_object_literal = Util.get_region_scope_first_match(view, scope, selection, "meta.object-literal.js")

      if item_object_literal :

        scope = item_object_literal.get("scope")
        object_literal_region = item_object_literal.get("region")
        selection = item_object_literal.get("selection")
        object_literal = item_object_literal.get("region_string_stripped")
        from node.main import NodeJS
        node = NodeJS()
        object_literal = json.loads(node.eval("JSON.stringify("+object_literal+")", "print"))
        object_literal = [(key, json.dumps(value)) for key, value in object_literal.items()]

        list_ordered = ("keyword.operator.assignment.js", "variable.other.readwrite.js", "storage.type.js")
        items = Util.find_regions_on_same_depth_level(view, scope, selection, list_ordered, depth_level, False)
        if items :
          last_selection = items[-1:][0].get("selection")
          class_name = items[1].get("region_string_stripped")
          regions = [(item.get("region")) for item in items]
          regions.append(object_literal_region)
          regions = Util.cover_regions(regions)
          parameters = list()
          constructor_body = list()
          get_set = list()
          for parameter in object_literal: 
            parameters.append( parameter[0] + ( "="+parameter[1] if json.loads(parameter[1]) != "required" else "") )
            constructor_body.append( "\t\tthis."+parameter[0]+" = "+parameter[0]+";" )
            get_set.append("\tget "+parameter[0]+"() {\n\t\treturn this."+parameter[0]+";\n\t}")
            get_set.append("\tset "+parameter[0]+"("+parameter[0]+") {\n\t\tthis."+parameter[0]+" = "+parameter[0]+";\n\t}")
          parameters = ", ".join(parameters)
          constructor_body = '\n'.join(constructor_body)
          get_set = '\n\n'.join(get_set)
          js_syntax  = "class "+class_name+" {\n"
          js_syntax += "\n\tconstructor ("+parameters+") {\n"
          js_syntax += constructor_body
          js_syntax += "\n\t}\n\n"
          js_syntax += get_set
          js_syntax += "\n}"
          js_syntax = Util.add_whitespace_indentation(view, regions, js_syntax)
          view.replace(edit, regions, js_syntax)

  def is_visible(self, **args) :
    view = self.view
    if Util.split_string_and_find(view.scope_name(0), "source.js") < 0 :
      return False
    selection = view.sel()[0]
    scope = view.scope_name(selection.begin()).strip()
    index = Util.split_string_and_find(scope, "meta.object-literal.js")
    if index < 0 :
      return False
    return True