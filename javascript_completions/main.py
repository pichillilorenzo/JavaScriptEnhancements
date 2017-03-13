import sublime, sublime_plugin
import sys, imp, os, webbrowser, re, cgi
import util.main as Util

JC_SETTINGS_FOLDER_NAME = "javascript_completions"
JC_SETTINGS_FOLDER = os.path.join(PACKAGE_PATH, JC_SETTINGS_FOLDER_NAME)

class JavaScriptCompletions():

  def get(self, key):
    return sublime.load_settings('JavaScript-Completions.sublime-settings').get(key)

javascriptCompletions = JavaScriptCompletions()

${include on_query_completions_event_listener.py}

${include go_to_def_command.py}

js_css = ""
with open(os.path.join(JC_SETTINGS_FOLDER, "style.css")) as css_file:
  js_css = "<style>"+css_file.read()+"</style>"

if int(sublime.version()) >= 3124 :

  default_completions = Util.open_json(os.path.join(PACKAGE_PATH, 'default_autocomplete.json')).get('completions')

  def load_default_autocomplete(view, comps_to_campare, prefix, isHover = False):

    scope = view.scope_name(view.sel()[0].begin()-(len(prefix)+1)).strip()
    if scope.endswith(" punctuation.accessor.js") :
      return []

    prefix = prefix.lower()
    completions = default_completions
    completions_to_add = []
    for completion in completions: 
      c = completion[0].lower()
      if not isHover:
        if c.startswith(prefix):
          completions_to_add.append((completion[0], completion[1]))
      else :
        if len(completion) == 3 and c.startswith(prefix) :
          completions_to_add.append(completion[2])
    final_completions = []
    for completion in completions_to_add:
      flag = False
      for c_to_campare in comps_to_campare:
        if not isHover and completion[0].split("\t")[0] == c_to_campare[0].split("\t")[0] :
          flag = True
          break
        elif isHover and completion["name"] == c_to_campare["name"] :
          flag = True
          break
      if not flag :
        final_completions.append(completion)

    return final_completions

  ${include on_hover_description_event_listener.py}

  ${include show_hint_parameters_command.py}

  ${include handle_flow_errors_command.py}

  ${include show_flow_errors_view_event_listener.py}