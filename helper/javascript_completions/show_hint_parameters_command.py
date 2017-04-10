import sublime, sublime_plugin

class show_hint_parametersCommand(sublime_plugin.TextCommand):
  
  def run(self, edit, **args):
    view = self.view

    scope = view.scope_name(view.sel()[0].begin()).strip()

    meta_fun_call = "meta.function-call.method.js"
    result = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call+" meta.group.js")

    if not result :
      meta_fun_call = "meta.function-call.js"
      result = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call+" meta.group.js")

    if result :
      point = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call)["region"].begin()
      sublime.set_timeout_async(lambda: on_hover_description_async(view, point, sublime.HOVER_TEXT, view.sel()[0].begin()))

  def is_enabled(self) :
    view = self.view
    sel = view.sel()[0]
    if not view.match_selector(
        sel.begin(),
        'source.js - comment'
    ):
      return False

    scope = view.scope_name(view.sel()[0].begin()).strip()
    
    meta_fun_call = "meta.function-call.method.js"
    result = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call+" meta.group.js")

    if not result :
      meta_fun_call = "meta.function-call.js"
      result = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call+" meta.group.js")

    if result :
      point = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call)["region"].begin()
      scope_splitted = scope.split(" ")
      find_and_get_scope = Util.find_and_get_pre_string_and_matches(scope, meta_fun_call+" meta.group.js")
      find_and_get_scope_splitted = find_and_get_scope.split(" ")
      if (
          (
            len(scope_splitted) == len(find_and_get_scope_splitted) + 1 
            or scope == find_and_get_scope 
            or (
                len(scope_splitted) == len(find_and_get_scope_splitted) + 2 
                and ( Util.get_parent_region_scope(view, view.sel()[0])["scope"].split(" ")[-1] == "string.quoted.double.js"
                    or Util.get_parent_region_scope(view, view.sel()[0])["scope"].split(" ")[-1] == "string.quoted.single.js"
                    or Util.get_parent_region_scope(view, view.sel()[0])["scope"].split(" ")[-1] == "string.template.js"
                  ) 
              ) 
          ) 
          and not scope.endswith("meta.block.js") 
          and not scope.endswith("meta.object-literal.js")
        ) :
        return True
    return False

  def is_visible(self) :
    view = self.view
    sel = view.sel()[0]
    if not view.match_selector(
        sel.begin(),
        'source.js - comment'
    ):
      return False

    scope = view.scope_name(view.sel()[0].begin()).strip()
    
    meta_fun_call = "meta.function-call.method.js"
    result = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call+" meta.group.js")

    if not result :
      meta_fun_call = "meta.function-call.js"
      result = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call+" meta.group.js")

    if result :
      point = Util.get_region_scope_last_match(view, scope, view.sel()[0], meta_fun_call)["region"].begin()
      scope_splitted = scope.split(" ")
      find_and_get_scope = Util.find_and_get_pre_string_and_matches(scope, meta_fun_call+" meta.group.js")
      find_and_get_scope_splitted = find_and_get_scope.split(" ")
      if (
          (
            len(scope_splitted) == len(find_and_get_scope_splitted) + 1 
            or scope == find_and_get_scope 
            or (
                len(scope_splitted) == len(find_and_get_scope_splitted) + 2 
                and ( Util.get_parent_region_scope(view, view.sel()[0])["scope"].split(" ")[-1] == "string.quoted.double.js"
                    or Util.get_parent_region_scope(view, view.sel()[0])["scope"].split(" ")[-1] == "string.quoted.single.js"
                    or Util.get_parent_region_scope(view, view.sel()[0])["scope"].split(" ")[-1] == "string.template.js"
                  ) 
              ) 
          ) 
          and not scope.endswith("meta.block.js") 
          and not scope.endswith("meta.object-literal.js")
        ) :
        return True
    return False