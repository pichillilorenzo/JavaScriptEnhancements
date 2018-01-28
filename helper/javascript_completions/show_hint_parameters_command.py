import sublime, sublime_plugin

class show_hint_parametersCommand(sublime_plugin.TextCommand):
  
  # flow doesn't work with meta.function-call.constructor.js
  meta_fun_calls = [
    "meta.function-call.method.js", 
    "meta.function-call.js",
    # JavaScript (Babel) Syntax support
    "meta.function-call.with-arguments.js",
    "meta.function-call.static.with-arguments.js",
    "meta.function-call.method.with-arguments.js",
    "meta.function-call.without-arguments.js",
    "meta.function-call.static.without-arguments.js",
    "meta.function-call.method.without-arguments.js",
    "meta.function-call.tagged-template.js",
    "source.js"
  ]

  meta_groups = [
    "meta.group.js",
    # JavaScript (Babel) Syntax support, this order is important!
    "meta.group.braces.round.function.arguments.js",
    "meta.group.braces.round.js"
  ]

  def run(self, edit, **args):
    view = self.view

    point = view.sel()[0].begin()
    
    meta_group = 0
    mate_group_scope = ""

    for mt in self.meta_groups:
      meta_group = view.scope_name(point).strip().split(" ").count(mt)
      if meta_group > 0:
        mate_group_scope = mt
        break

    if meta_group == 0:
      return

    while point >= 0:
      scope = view.scope_name(point).strip()
      scope_splitted = scope.split(" ")
      if len(scope_splitted) < 2:
        return 

      if scope_splitted[-2] in self.meta_fun_calls and scope_splitted.count(mate_group_scope) == meta_group - 1:
        sublime.set_timeout_async(lambda: on_hover_description_async(view, point, sublime.HOVER_TEXT, point if 'popup_position_on_point' in args and args.get('popup_position_on_point') else view.sel()[0].begin(), show_hint=True))
        return

      point = view.word(point).begin() - 1 if view.substr(point) != "(" else point - 1

  def is_enabled(self) :
    view = self.view
    sel = view.sel()[0]
    if not view.match_selector(
        sel.begin(),
        'source.js - comment'
    ):
      return False

    point = view.sel()[0].begin()
    
    meta_group = 0
    mate_group_scope = ""

    for mt in self.meta_groups:
      meta_group = view.scope_name(point).strip().split(" ").count(mt)
      if meta_group > 0:
        mate_group_scope = mt
        break

    if meta_group == 0:
      return False

    while point >= 0:
      scope = view.scope_name(point).strip()
      scope_splitted = scope.split(" ")
      if len(scope_splitted) < 2:
        return False

      if scope_splitted[-2] in self.meta_fun_calls and scope_splitted.count(mate_group_scope) == meta_group - 1:
        #print(view.substr(view.word(point)))
        return True

      point = view.word(point).begin() - 1 if view.substr(point) != "(" else point - 1

    return False

  def is_visible(self) :
    view = self.view
    sel = view.sel()[0]
    if not view.match_selector(
        sel.begin(),
        'source.js - comment'
    ):
      return False
    
    point = view.sel()[0].begin()
    
    meta_group = 0
    mate_group_scope = ""

    for mt in self.meta_groups:
      meta_group = view.scope_name(point).strip().split(" ").count(mt)
      if meta_group > 0:
        mate_group_scope = mt
        break

    if meta_group == 0:
      return False

    while point >= 0:
      scope = view.scope_name(point).strip()
      scope_splitted = scope.split(" ")
      if len(scope_splitted) < 2:
        return False

      if scope_splitted[-2] in self.meta_fun_calls and scope_splitted.count(mate_group_scope) == meta_group - 1:
        return True

      point = view.word(point).begin() - 1 if view.substr(point) != "(" else point - 1

    return False
    