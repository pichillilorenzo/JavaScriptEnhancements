# import sublime, sublime_plugin
# import re


#   { "caption": "-" },
#   {
#     "caption": "Refactor (Working on it ...)",
#     "id": "refactor",
#     "children": [
#       {
#         "caption": "Extract",
#         "children": [
#           {
#             "caption": "Method",
#             "command": "refactor",
#             "args": {"case": "extract_method"}
#           }
#         ]
#       }
#     ]
#   }

# class refactorCommand(sublime_plugin.TextCommand):
#   def run(self, edit, **args):
#     view = self.view
#     case = args.get("case")
#     if not "answer" in args :
#       caption = ""
#       initial_text = ""

#       if case == "extract_method" :
#         caption = "Method:"
#         initial_text = "func ()"

#       view.window().show_input_panel(caption, initial_text, lambda answer: view.run_command('refactor', args={"case": case, "answer": answer}), None, None)
#     else :
#       answer = args.get("answer").strip()
#       scope = view.scope_name(view.sel()[0].begin())
#       space = Util.get_whitespace_from_line_begin(view, view.sel()[0])
#       if case == "extract_method" :
#         new_text = Util.replace_with_tab(view, view.sel()[0], "\t\n\t"+answer+" {\n\t", "\n\t}\n")
#         view.replace(edit, view.sel()[0], "this."+(re.sub('\s+\(', '(', answer)) )
#         region_class = Util.get_region_scope_first_match(view, scope, view.sel()[0], 'meta.class.js')["region"]
#         view.insert(edit, region_class.end()-1, new_text)

#   def is_enabled(self, **args) :
#     view = self.view
#     if not Util.selection_in_js_scope(view) :
#       return False
#     selections = view.sel()
#     for selection in selections :
#       if view.substr(selection).strip() != "" :
#         return True
#     return False

#   def is_visible(self, **args) :
#     view = self.view
#     if not Util.selection_in_js_scope(view) :
#       return False
#     selections = view.sel()
#     for selection in selections :
#       if view.substr(selection).strip() != "" :
#         return True
#     return False