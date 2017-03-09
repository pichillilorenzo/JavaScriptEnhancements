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

  ${include on_hover_description_event_listener.py}

  ${include show_hint_parameters_command.py}

  ${include handle_flow_errors_command.py}

  ${include show_flow_errors_view_event_listener.py}