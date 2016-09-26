import sublime, sublime_plugin
import sys, imp, os, webbrowser
import util.main as Util

if int(sublime.version()) < 3000:
  from HTMLParser import HTMLParser
else:
  from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

${include on_query_completions_event_listener.py}

js_css = ""
with open(os.path.join(JC_SETTINGS_FOLDER, "style.css")) as css_file:
  js_css = "<style>"+css_file.read()+"</style>"

if int(sublime.version()) >= 3124 :
  
  ${include on_hover_event_listener.py}

if int(sublime.version()) >= 3000 :

  ${include find_description_command.py}
