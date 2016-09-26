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