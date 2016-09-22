import sublime, sublime_plugin
import json
import util.main as Util

class surround_withCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    selections = view.sel()
    region = None
    sub = None
    case = args.get("case")
    if case == "if_else_statement" :
      if len(selections) != 2 :
        return

      sel_1 = Util.trim_Region(view, selections[0])
      space_1 = Util.get_whitespace_from_line_begin(view, sel_1)
      new_text = Util.replace_with_tab(view, sel_1, space_1+"\n"+space_1+"if (bool) {\n"+space_1, "\n"+space_1+"} ")
      view.replace(edit, sel_1, new_text.strip())

      sel_2 = Util.trim_Region(view, selections[1])
      space_2 = Util.get_whitespace_from_line_begin(view, sel_2)
      new_text = Util.replace_with_tab(view, sel_2, " else {\n"+space_2, "\n"+space_2+"}\n"+space_2)
      view.replace(edit, sel_2, new_text.strip())
    else :
      for selection in selections :
        selection = Util.trim_Region(view, selection)
        if view.substr(selection).strip() == "" :
          continue
        space = Util.get_whitespace_from_line_begin(view, selection)

        if case == "multi_line_comment" :       
          new_text = Util.replace_without_tab(view, selection, space+"\n"+space+"/*\n"+space, "\n"+space+"*/\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "single_line_comment" :
          new_text = Util.replace_without_tab(view, selection, add_to_each_line_before="// ")
          view.replace(edit, selection, new_text)
        elif case == "if_statement" :

          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"if (bool) {\n"+space, "\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)
        elif case == "while_statement" :

          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"while (bool) {\n"+space, "\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)
        elif case == "do_while_statement" :

          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"do {\n"+space, "\n"+space+"} while (bool);\n"+space)
          view.replace(edit, selection, new_text)
        elif case == "for_statement" :

          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"for ( ; bool ; ) {\n"+space, "\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)
        elif case == "try_catch_statement" :

          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"try {\n"+space, "\n"+space+"} catch (e) {\n"+space+"\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)

        elif case == "try_catch_finally_statement" :
          new_text = Util.replace_with_tab(view, selection, space+"\n"+space+"try {\n"+space, "\n"+space+"} catch (e) {\n"+space+"\n"+space+"} finally {\n"+space+"\n"+space+"}\n"+space)
          view.replace(edit, selection, new_text)

  def is_visible(self, **args) :
    view = self.view
    if Util.split_string_and_find(view.scope_name(0), "source.js") < 0 :
      return False
    selections = view.sel()
    for selection in selections :
      if view.substr(selection).strip() != "" :
        return True
    return False

if int(sublime.version()) >= 3000 :

  class delete_surroundedCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
      view = self.view
      selections = view.sel()
      case = args.get("case")
      for selection in selections :
        scope = view.scope_name(selection.begin()).strip()
        scope_splitted = scope.split(" ")
        if case == "del_multi_line_comment" :
          item = Util.get_region_scope_first_match(view, scope, selection, "comment.block.js")
          if item :
            region_scope = item.get("region")
            new_str = item.get("region_string_stripped")
            new_str = new_str[2:-2].strip()
            view.replace(edit, region_scope, new_str)

        elif case == "del_single_line_comment" :
          item = Util.get_region_scope_first_match(view, scope, selection, "comment.line.double-slash.js")
          if item :
            region_scope = item.get("region")
            lines = item.get("region_string").split("\n")
            body = list()
            for line in lines:
              body.append(line.strip()[2:].lstrip())
            new_str = "\n".join(body)
            view.replace(edit, region_scope, new_str)

        elif case == "strip_quoted_string" :
          result = Util.firstIndexOfMultiple(scope_splitted, ("string.quoted.double.js", "string.quoted.single.js", "string.template.js"))
          selector = result.get("string")
          item = Util.get_region_scope_first_match(view, scope, selection, selector)
          if item :
            region_scope = item.get("region")
            new_str = item.get("region_string")
            new_str = new_str[1:-1]
            view.replace(edit, region_scope, new_str)

    def is_visible(self, **args) :
      view = self.view
      if Util.split_string_and_find(view.scope_name(0), "source.js") < 0 :
        return False
      return True


  class sort_arrayCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
      from node.main import NodeJS
      node = NodeJS()
      view = self.view
      selections = view.sel()
      for selection in selections :
        scope = view.scope_name(selection.begin()).strip()
        result = Util.get_region_scope_first_match(view, scope, selection, "meta.brackets.js")
        if result :
          region = result.get("region")
          array_string = result.get("region_string_stripped")
          from node.main import NodeJS
          node = NodeJS()
          case = args.get("case")
          sort_func = ""
          if case == "compare_func_desc" :
            sort_func = "function(x,y){return y-x;}"
          elif case == "compare_func_asc" :
            sort_func = "function(x,y){return x-y;}"
          elif case == "alpha_asc" :
            sort_func = ""
          elif case == "alpha_desc" :
            sort_func = ""
          sort_result = node.eval("var array = "+array_string+"; console.log(array.sort("+sort_func+")"+( ".reverse()" if case == "alpha_desc" else "" )+")").strip()
          view.replace(edit, region, sort_result)

    def is_visible(self, **args) :
      view = self.view
      if Util.split_string_and_find(view.scope_name(0), "source.js") < 0 :
        return False
      selections = view.sel()
      for selection in selections :
        scope = view.scope_name(selection.begin()).strip()
        index = Util.split_string_and_find(scope, "meta.brackets.js")
        if index < 0 :
          return False
      return True

        
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