import sublime, sublime_plugin
import os, sys, imp, platform, json, traceback, threading, urllib, shutil, re
from shutil import copyfile
from threading import Timer

PACKAGE_PATH = os.path.abspath(os.path.dirname(__file__))
PACKAGE_NAME = os.path.basename(PACKAGE_PATH)
SUBLIME_PACKAGES_PATH = os.path.dirname(PACKAGE_PATH)
 
sys.path += [PACKAGE_PATH] + [os.path.join(PACKAGE_PATH, f) for f in ['node', 'util']]

sublime_version = int(sublime.version())

if 'reloader' in sys.modules:
  imp.reload(sys.modules['reloader'])
import reloader

# platform
platform_switcher = {"osx": "OSX", "linux": "Linux", "windows": "Windows"}
PLATFORM = platform_switcher.get(sublime.platform())
PLATFORM_ARCHITECTURE = "64bit" if platform.architecture()[0] == "64bit" else "32bit" 

class handle_settingCommand(sublime_plugin.WindowCommand) :
  def run(self, folder_from_package, file_name, extension) :
    open_setting(folder_from_package, file_name, extension)

  def is_visible(self, folder_from_package, file_name, extension) :
    if file_name.find(" (") >= 0 and file_name.find(" ("+PLATFORM+")") >= 0 :
      return True
    elif file_name.find(" (") >= 0 and file_name.find(" ("+PLATFORM+")") < 0 :
      return False
    return True

def setTimeout(time, func):
  timer = Timer(time, func)
  timer.start()

def enable_setting(folder_from_package, file_name, extension) :
  path = os.path.join(PACKAGE_PATH, folder_from_package)
  file_name_enabled = file_name + "." + extension
  file_name_disabled = file_name + "_disabled" + "." + extension
  path_file_enabled = os.path.join(path, file_name_enabled)
  path_file_disabled = os.path.join(path, file_name_disabled)
  try :
    if os.path.isfile(path_file_disabled) :
      os.rename(path_file_disabled, path_file_enabled)
  except Exception as e :
    print("Error: "+traceback.format_exc())

def disable_setting(folder_from_package, file_name, extension) :
  path = os.path.join(PACKAGE_PATH, folder_from_package)
  file_name_enabled = file_name + "." + extension
  file_name_disabled = file_name + "_disabled" + "." + extension
  path_file_enabled = os.path.join(path, file_name_enabled)
  path_file_disabled = os.path.join(path, file_name_disabled)
  try :
    if os.path.isfile(path_file_enabled) :
      os.rename(path_file_enabled, path_file_disabled)
  except Exception as e :
    print("Error: "+traceback.format_exc())

def is_setting_enabled(folder_from_package, file_name, extension) :
  path = os.path.join(PACKAGE_PATH, folder_from_package)
  file_name_enabled = file_name + "." + extension
  path_file_enabled = os.path.join(path, file_name_enabled)
  return os.path.isfile(path_file_enabled)
      
def open_setting(folder_from_package, file_name, extension) :
  path = os.path.join(PACKAGE_PATH, folder_from_package)
  file_name_enabled = file_name + "." + extension
  file_name_disabled = file_name + "_disabled" + "." + extension
  path_file_enabled = os.path.join(path, file_name_enabled)
  path_file_disabled = os.path.join(path, file_name_disabled)

  if os.path.isfile(path_file_enabled) :
    sublime.active_window().open_file(path_file_enabled)
  elif os.path.isfile(path_file_disabled) :
    sublime.active_window().open_file(path_file_disabled)

class startPlugin():
  def init(self):
    import node.node_variables as node_variables
    import node.installer as installer

    if int(sublime.version()) >= 3000 :
      eval_js_json = None
      if os.path.isfile(os.path.join(PACKAGE_PATH, "evaluate_javascript", "Evaluate-JavaScript.sublime-settings")) :
        with open(os.path.join(PACKAGE_PATH, "evaluate_javascript", "Evaluate-JavaScript.sublime-settings")) as data_file:    
          eval_js_json = json.load(data_file)

      node_js_version = sublime.load_settings('Evaluate-JavaScript.sublime-settings').get("node_js_version") or eval_js_json.get("node_js_version") or node_variables.NODE_JS_VERSION
      
      installer.install(node_js_version)

mainPlugin = startPlugin()

JC_SETTINGS_FOLDER_NAME = "javascript_completions"
JC_SETTINGS_FOLDER = os.path.join(PACKAGE_PATH, JC_SETTINGS_FOLDER_NAME)

class JavaScriptCompletions():
  def init(self):
    self.api = {}
    self.settings = sublime.load_settings('JavaScript-Completions.sublime-settings')
    self.API_Setup = self.settings.get('completion_active_list')

    # Caching completions
    if self.API_Setup:
      for API_Keyword in self.API_Setup:
        self.api[API_Keyword] = sublime.load_settings( API_Keyword + '.sublime-settings')
      
    if self.settings.get("enable_key_map") :
      enable_setting(JC_SETTINGS_FOLDER, "Default ("+PLATFORM+")", "sublime-keymap")
    else :
      disable_setting(JC_SETTINGS_FOLDER, "Default ("+PLATFORM+")", "sublime-keymap")
javascriptCompletions = JavaScriptCompletions()

EJ_SETTINGS_FOLDER_NAME = "evaluate_javascript"
EJ_SETTINGS_FOLDER = os.path.join(PACKAGE_PATH, EJ_SETTINGS_FOLDER_NAME)

class EvaluateJavascript():

  def init(self):
    self.api = {}
    self.settings = sublime.load_settings('Evaluate-JavaScript.sublime-settings')

    if self.settings.get("enable_context_menu_option") :
      enable_setting(EJ_SETTINGS_FOLDER, "Context", "sublime-menu")
    else :
      disable_setting(EJ_SETTINGS_FOLDER, "Context", "sublime-menu")

    if self.settings.get("enable_key_map") :
      enable_setting(EJ_SETTINGS_FOLDER, "Default ("+PLATFORM+")", "sublime-keymap")
    else :
      disable_setting(EJ_SETTINGS_FOLDER, "Default ("+PLATFORM+")", "sublime-keymap")
ej = EvaluateJavascript()

H_SETTINGS_FOLDER_NAME = "helper"
H_SETTINGS_FOLDER = os.path.join(PACKAGE_PATH, H_SETTINGS_FOLDER_NAME)

class JavaScriptCompletionsHelper():

  def init(self):
    self.api = {}
    self.settings = sublime.load_settings('helper.sublime-settings')
jc_helper = JavaScriptCompletionsHelper()

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

class JavaScriptCompletionsEventListener(sublime_plugin.EventListener):
  global javascriptCompletions

  def on_query_completions(self, view, prefix, locations):

    if not prefix.strip() :
      return []

    self.completions = []

    for API_Keyword in javascriptCompletions.api:
      # If completion active
      if(javascriptCompletions.API_Setup and javascriptCompletions.API_Setup.get(API_Keyword)):
        scope = javascriptCompletions.api[API_Keyword].get('scope')
        if scope and view.match_selector(locations[0], scope):
          self.completions += javascriptCompletions.api[API_Keyword].get('completions')

    if not self.completions:
      return []

    # extend word-completions to auto-completions
    compDefault = [view.extract_completions(prefix)]
    compDefault = [(item, item) for sublist in compDefault for item in sublist if len(item) > 3]
    compDefault = list(set(compDefault))
    #completions = list(self.completions)
    completions = list()
    for attr in self.completions :
      if not attr[0].startswith("description-") :
        completions.append(tuple(attr))
      else :
        attr[1] = attr[1].get("full_description")
        completions.append(tuple(attr))

    completions.extend(compDefault)
    return (completions)

js_css = ""
with open(os.path.join(JC_SETTINGS_FOLDER, "style.css")) as css_file:
  js_css = "<style>"+css_file.read()+"</style>"

if int(sublime.version()) >= 3124 :
  
  def open_browser(action):
    if action.startswith("http") :
      webbrowser.open(action)
    else :
      parts = action.split(",")
      location = int(parts[2])
      action = parts[0] + "," + parts[1]
      find_descriptionclick(action, location=location, is_single=True)
  
  class JavaScriptCompletionsHoverEventListener(sublime_plugin.EventListener):
    global javascriptCompletions
  
    def on_hover(self, view, point, hover_zone) :
  
      if not javascriptCompletions.settings.get("enable_on_hover_description") or hover_zone != sublime.HOVER_TEXT :
        return
  
      scope = view.scope_name(point).strip()
      
      scope_splitted = scope.split(" ")
      last_scope = scope_splitted[-1]
      second_last = scope_splitted[-1] if len(scope_splitted) > 1 else None
      if scope_splitted[0] != "source.js" or ( last_scope != "variable.function.js" and last_scope != "meta.property.object.js" and not last_scope.startswith("support.function.") and not last_scope.startswith("support.class.") and not last_scope.startswith("support.type.") ) :
        if second_last and second_last != "meta.function-call.constructor.js" : 
          return
        elif not second_last :
          return
  
      str_region = view.word(point)
      result = Util.get_current_region_scope(view, str_region)
      str_selected = result.get("region_string_stripped")
      completion_list = list()
      for API_Keyword in javascriptCompletions.api :
        if (javascriptCompletions.API_Setup and javascriptCompletions.API_Setup.get(API_Keyword)) :
          scope = javascriptCompletions.api[API_Keyword].get('scope')
          if scope and view.match_selector(0, scope):
            if(API_Keyword.startswith("description-")):
              index_completion = 0
              completions = javascriptCompletions.api[API_Keyword].get('completions')
              for completion in completions:
                completion_name = completion[0][12:].split("\t")
                completion_name = strip_tags(completion_name[0].strip())
                index_parenthesis = completion_name.find("(")
                completion_name_to_compare = ""
                if index_parenthesis >= 0 :
                  completion_name_to_compare = completion_name[0: index_parenthesis]
                else :
                  completion_name_to_compare = completion_name
                if(completion_name_to_compare == str_selected):
                  href = API_Keyword+","+str(index_completion)+","+str(point)
                  completion.insert(2, href)
                  completion_list.append(completion)
                index_completion = index_completion + 1
  
      if len(completion_list) == 0:
        return 
  
      i = 0
      completion_list_to_show = list()
      while i < len(completion_list) :
  
        if len(completion_list_to_show) >= 1 :
          j = 0
          completion_already_exists = False
          while j < len(completion_list_to_show) :
            if completion_list_to_show[j][1].get("type") == completion_list[i][1].get("type") and completion_list_to_show[j][1].get("description") == completion_list[i][1].get("description") and completion_list_to_show[j][1].get("return_type") == completion_list[i][1].get("return_type") :
              if (completion_list_to_show[j][1].get("type") == "operation" or completion_list_to_show[j][1].get("type") == "constructor") :
                if completion_list_to_show[j][1].get("parameters") == completion_list[i][1].get("parameters") :
                  completion_already_exists = True
                  break
            j = j + 1
  
          if not completion_already_exists :
            completion_list_to_show.append(completion_list[i])
  
        else :
          completion_list_to_show.append(completion_list[i])
  
        i = i + 1
  
      self.hint_popup(point, completion_list_to_show)
  
    def hint_popup(self, location, completions):
      html = ""
      for completion in completions :
        parameters_html = "()"
        completion_class_name = completion[0].split("\t")[1].strip()
        if len(completion_class_name) > 15 :
          completion_class_name = completion_class_name[0:15] + ".."
        completion_description = completion[1]
        if completion_description.get("type") == "operation" :
          parameters = []
          for parameter in completion_description.get("parameters") :
            parameters.append( "<span class=\"parameter-name\">" + parameter.get("name") + "</span>" + ( "<span class=\"parameter-is-optional\">?</span>" if parameter.get("is_optional") else "" ) + "<span class=\"parameter-symbol\">:</span> " + "<span class=\"parameter-type\">" + parameter.get("type") + "</span>" )
          if len(parameters) > 0 :
            parameters_html = "( " + ", ".join(parameters) + " )"
          html += """ 
          <div class=\"container-description\">
            <div><span class=\"operation-class-name\">"""+completion_class_name+""" <span class=\"circle\">F</span></span><div class=\"container-info\"><span class=\"operation-name\">"""+completion_description.get("name")+"</span>"+parameters_html+""" : <span class=\"operation-return-type\">"""+completion_description.get("return_type")+"""</span></div></div>
            <div class=\"container-url-doc\"><a href=\""""+completion[2]+"""\">View complete doc</a> <span class=\"label\">URL doc: </span><a class=\"operation-url-doc-link\" href=\""""+completion_description.get("url_doc")+"""\">"""+completion_description.get("url_doc")+"""</a></div>
          </div>
          """
        elif completion_description.get("type") == "property" :
          html += """ 
          <div class=\"container-description\">
            <div><span class=\"property-class-name\">"""+completion_class_name+""" <span class=\"circle\">P</span></span><div class=\"container-info\"><span class=\"property-name\">"""+completion_description.get("name")+"</span>"+" : <span class=\"property-return-type\">"""+completion_description.get("return_type")+"""</span></div></div>
            <div class=\"container-url-doc\"><a href=\""""+completion[2]+"""\">View complete doc</a> <span class=\"label\">URL doc: </span><a class=\"property-url-doc-link\" href=\""""+completion_description.get("url_doc")+"""\">"""+completion_description.get("url_doc")+"""</a></div>
          </div>
          """
        elif completion_description.get("type") == "constructor" :
          parameters = []
          for parameter in completion_description.get("parameters") :
            parameters.append( "<span class=\"parameter-name\">" + parameter.get("name") + "</span>" + ( "<span class=\"parameter-is-optional\">?</span>" if parameter.get("is_optional") else "" ) + "<span class=\"parameter-symbol\">:</span> " + "<span class=\"parameter-type\">" + parameter.get("type") + "</span>" )
          if len(parameters) > 0 :
            parameters_html = "( " + ", ".join(parameters) + " )"
          html += """ 
          <div class=\"container-description\">
            <div><span class=\"constructor-class-name\">"""+completion_class_name+""" <span class=\"circle\">C</span></span><div class=\"container-info\"><span class=\"constructor-name\">"""+completion_description.get("name")+"</span>"+parameters_html+""" : <span class=\"constructor-return-type\">"""+completion_description.get("return_type")+"""</span></div></div>
            <div class=\"container-url-doc\"><a href=\""""+completion[2]+"""\">View complete doc</a> <span class=\"label\">URL doc: </span><a class=\"constructor-url-doc-link\" href=\""""+completion_description.get("url_doc")+"""\">"""+completion_description.get("url_doc")+"""</a></div>
          </div>
          """
  
      sublime.active_window().active_view().show_popup("""
      <html><head></head><body>
      """+js_css+"""
        <div class=\"container-hint-popup\">
          """ + html + """    
        </div>
      </body></html>""", sublime.COOPERATE_WITH_AUTO_COMPLETE | sublime.HIDE_ON_MOUSE_MOVE_AWAY, location, 1150, 60, open_browser)

if int(sublime.version()) >= 3000 :

  completions_link_html = ""
  prev_selected = ""
  maybe_is_one = 0
  first_href = ""
  popup_is_showing = False
  
  def find_descriptionclick(href, location=-1, is_single=False):
    global javascriptCompletions
    global popup_is_showing
    href = href.split(",")
    completion_description = javascriptCompletions.api[href[0]].get('completions')[int(href[1])][1]
    class_name = javascriptCompletions.api[href[0]].get('completions')[int(href[1])][0].split("\t")[1]
    sublime.active_window().active_view().hide_popup()
    html = ""
    parameters_html = "()"
    if completion_description.get("type") == "operation" :
      parameters = []
      for parameter in completion_description.get("parameters") :
        parameters.append( "<span class=\"parameter-name\">" + parameter.get("name") + "</span>" + ( "<span class=\"parameter-is-optional\">?</span>" if parameter.get("is_optional") else "" ) + "<span class=\"parameter-symbol\">:</span> " + "<span class=\"parameter-type\">" + parameter.get("type") + "</span>" )
      if len(parameters) > 0 :
        parameters_html = "( " + ", ".join(parameters) + " )"
      html = """ 
      <div class=\"container-description\">
        <p><div class=\"label\">Syntax:</div><span class=\"operation-name\">"""+completion_description.get("name")+"</span>"+parameters_html+(" : <span class=\"operation-is-static\">static</span>" if completion_description.get("is_static") else "")+"""</p>
        <p><div class=\"label\">Return Type:</div><span class=\"operation-return-type\">"""+completion_description.get("return_type")+"""</span></p>
        <p><div class=\"label\">Description:</div><span class=\"operation-description\">"""+completion_description.get("description")+"""</span></p>
        <p><div class=\"label\">URL doc:</div><a class=\"operation-url-doc-link\" href=\""""+completion_description.get("url_doc")+"""\">"""+completion_description.get("url_doc")+"""</a></p>
      </div>
      """
    elif completion_description.get("type") == "property" :
      html = """ 
      <div class=\"container-description\">
        <p><div class=\"label\">Syntax:</div><span class=\"property-name\">"""+completion_description.get("name")+"""</span>"""+(" : <span class=\"property-is-static\">static</span>" if completion_description.get("is_static") else "")+"""</p>
        <p><div class=\"label\">Return Type:</div><span class=\"property-return-type\">"""+completion_description.get("return_type")+"""</span></p>
        <p><div class=\"label\">Description:</div><span class=\"property-description\">"""+completion_description.get("description")+"""</span></p>
        <p><div class=\"label\">URL doc:</div><a class=\"property-url-doc-link\" href=\""""+completion_description.get("url_doc")+"""\">"""+completion_description.get("url_doc")+"""</a></p>
      </div>
      """
    elif completion_description.get("type") == "constructor" :
      parameters = []
      for parameter in completion_description.get("parameters") :
        parameters.append( "<span class=\"parameter-name\">" + parameter.get("name") + "</span>" + ( "<span class=\"parameter-is-optional\">?</span>" if parameter.get("is_optional") else "" ) + "<span class=\"parameter-symbol\">:</span> " + "<span class=\"parameter-type\">" + parameter.get("type") + "</span>" )
      if len(parameters) > 0 :
        parameters_html = "( " + ", ".join(parameters) + " )"
      html = """ 
      <div class=\"container-description\">
        <p><div class=\"label\">Syntax:</div><span class=\"constructor-name\">"""+completion_description.get("name")+"</span>"+parameters_html+"""</p>
        <p><div class=\"label\">Return Type:</div><span class=\"constructor-return-type\">"""+completion_description.get("return_type")+"""</span></p>
        <p><div class=\"label\">Description:</div><span class=\"constructor-description\">"""+completion_description.get("description")+"""</span></p>
        <p><div class=\"label\">URL doc:</div><a class=\"constructor-url-doc-link\" href=\""""+completion_description.get("url_doc")+"""\">"""+completion_description.get("url_doc")+"""</a></p>
      </div>
      """
  
    popup_is_showing = True
    sublime.active_window().active_view().show_popup("""
      <html><head></head><body>
      """+js_css+"""
        <div class=\"container\">
          """ + ("<a class=\"back-button\" href=\"back\">Back to the list</a>" if not is_single else "") + """
          <h3 class=\"class-name\">"""+class_name+"""</h3>
          """ + html + """    
        </div>
      </body></html>""", sublime.COOPERATE_WITH_AUTO_COMPLETE, location, 1000, 500, back_to_list_find_description)
  
  def back_to_list_find_description(action):
    if action == "back" :
      sublime.active_window().active_view().run_command("find_description")
    else :
      webbrowser.open(action)
  
  class jc_hide_popupEventListener(sublime_plugin.EventListener):
    def on_modified_async(self, view) :
      global popup_is_showing
      if popup_is_showing :
        view.hide_popup()
        popup_is_showing = False
  
  class find_descriptionCommand(sublime_plugin.TextCommand):
    global javascriptCompletions
    def run(self, edit):
  
      global completions_link_html
      global prev_selected
      global maybe_is_one
      global first_href
      global popup_is_showing
  
      view = self.view
      popup_is_showing = False
      view.hide_popup()
      sel = view.sel()[0]
      str_selected = view.substr(sel).strip()
      if not str_selected :
        str_selected = view.substr(view.word(sel)).strip()
        if not str_selected :
          return
            
      max_width = 800
      max_height = 200
  
      if prev_selected == str_selected :
        if maybe_is_one == 1 :
          find_descriptionclick(first_href, is_single=True)
        else :
          if completions_link_html :
            popup_is_showing = True
            view.show_popup("<html><head></head><body>"+js_css+"<div class=\"container\">"+completions_link_html+"</div></body></html>", sublime.COOPERATE_WITH_AUTO_COMPLETE, -1, max_width, max_height, find_descriptionclick)
          else :
            view.show_popup("<html><head></head><body>"+js_css+"<div class=\"container\"><p>No results found!</p></div></body></html>", sublime.COOPERATE_WITH_AUTO_COMPLETE, max_width, max_height)
        return 
  
      prev_selected = str_selected
      
      maybe_is_one = 0
      entered_loop = False
      first_href = ""
      completions_link_html = ""
  
      for API_Keyword in javascriptCompletions.api :
        if (javascriptCompletions.API_Setup and javascriptCompletions.API_Setup.get(API_Keyword)) :
          #scope = javascriptCompletions.api[API_Keyword].get('scope')
          #if scope and view.match_selector(0, scope):
            if not entered_loop :
              entered_loop = True
            if(API_Keyword.startswith("description-")):
              index_completion = 0
              completions = javascriptCompletions.api[API_Keyword].get('completions')
              for completion in completions:
                completion_name = completion[0][12:].split("\t")
                tab_name = ""
                if len(completion_name) > 1:
                  tab_name = " | "+(strip_tags(completion_name[1]) if len(completion_name[1]) < 50 else strip_tags(completion_name[1][:50])+" ...")
                completion_name = strip_tags(completion_name[0].strip())
                index_parenthesis = completion_name.find("(")
                completion_name_to_compare = ""
                if index_parenthesis >= 0 :
                  completion_name_to_compare = completion_name[0: index_parenthesis]
                else :
                  completion_name_to_compare = completion_name
                if completion_name_to_compare.find(str_selected) >= 0 :
                  href = API_Keyword+","+str(index_completion)
                  if len(completion_name_to_compare) == len(str_selected) and maybe_is_one < 2 :
                    maybe_is_one = maybe_is_one + 1
                    first_href = href
                  completion_name = completion_name.replace(str_selected, "<span class=\"highlighted\">"+str_selected+"</span>")
                  completions_link_html += "<div class=\"container-completion-link\"><a class=\"completion-link\" href=\""+href+"\">"+completion_name+"</a>"+tab_name+"</div>"
                index_completion = index_completion + 1
  
      if maybe_is_one == 1 and entered_loop :
        popup_is_showing = True
        find_descriptionclick(first_href, is_single=True)
      else :
        if completions_link_html and entered_loop :
          popup_is_showing = True
          view.show_popup("<html><head></head><body>"+js_css+"<div class=\"container\">"+completions_link_html+"</div></body></html>", sublime.COOPERATE_WITH_AUTO_COMPLETE, -1, max_width, max_height, find_descriptionclick)
        else :
          view.show_popup("<html><head></head><body>"+js_css+"<div class=\"container\"><p>No results found!</p></div></body></html>", sublime.COOPERATE_WITH_AUTO_COMPLETE, max_width, max_height)
  


import sublime, sublime_plugin
import traceback, os, json, io, sys, imp
import util.main as Util

if int(sublime.version()) >= 3000 :
  result_js = ""
  region_selected = None
  popup_is_showing = False
  ej_css = """
  <style>
  html{
    margin: 0;
    padding: 0;
  }
  body{
    color: #fff;
    margin: 0;
    padding: 0;
  }
  .container{
    background-color: #202A31;
    padding: 10px;
  }
  a{
    color: #fff;
    display: block;
    margin: 10px 0;
  }
  </style>
  """
  
  def action_result(action):
    global result_js
    global region_selected
  
    view = sublime.active_window().active_view()
    sel = region_selected
    str_selected = view.substr(sel).strip()
  
    if action == "copy_to_clipboard" :
      sublime.set_clipboard(result_js)
  
    elif action == "replace_text" :
      view.run_command("replace_text")
  
    elif action == "view_result_with_allspaces":
      view.run_command("view_result_with_allspaces")
  
    view.hide_popup()
    result_js = ""
  
  class view_result_with_allspacesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
      global result_js
      global region_selected
  
      sublime.active_window().show_input_panel("Result", result_js, back_to_popup, back_to_popup, back_to_popup)
  
  class replace_textCommand(sublime_plugin.TextCommand):
  
    def run(self, edit):
      global result_js
      global region_selected
  
      view = self.view
      sel = Util.trim_Region(view, region_selected)
      view.replace(edit, sel, result_js)
      if region_selected.a < region_selected.b :
        region_selected.b = region_selected.a+len(result_js)
      else :
        region_selected.a = region_selected.b+len(result_js)
  
  class ej_hide_popupEventListener(sublime_plugin.EventListener):
    def on_modified_async(self, view) :
      global popup_is_showing
      if popup_is_showing :
        view.hide_popup()
        popup_is_showing = False
  
  class evaluate_javascriptCommand(sublime_plugin.TextCommand):
  
    def run(self, edit, is_line=False, eval_type="eval"):
      global result_js
      global region_selected
      global popup_is_showing
  
      view = self.view
      sel = view.sel()[0]
      popup_is_showing = False
      str_selected = view.substr(sel).strip()
  
      if is_line:
        lines = view.lines(sel)
        region_selected = lines[0]
        str_selected = view.substr(region_selected)
      else: 
        if not str_selected and region_selected : 
          region = get_start_end_code_highlights_eval()
          region_selected = sublime.Region(region[0], region[1])
          lines = view.lines(region_selected)
          str_selected = ""
          for line in lines:
            str_selected += view.substr(view.full_line(line))
        elif str_selected:
          lines = view.lines(sel)
          region_selected = sublime.Region if not region_selected else region_selected
          region_selected = sublime.Region(lines[0].begin(), lines[-1:][0].end())
        elif not str_selected :
          return
      
      if not region_selected :
        return
  
      view.run_command("show_start_end_dot_eval")
  
      try:
        from node.main import NodeJS
        node = NodeJS()
        result_js = node.eval(str_selected, eval_type, True)
        popup_is_showing = True
        view.show_popup("<html><head></head><body>"+ej_css+"""<div class=\"container\">
          <p class="result">Result: """+result_js+"""</p>
          <div><a href="view_result_with_allspaces">View result with all spaces(\\t,\\n,...)</a></div>
          <div><a href="copy_to_clipboard">Copy result to clipboard</a></div>
          <div><a href="replace_text">Replace text with result</a></div>
          </div>
        </body></html>""", sublime.COOPERATE_WITH_AUTO_COMPLETE, -1, 400, 400, action_result)
      except Exception as e:
        #sublime.error_message("Error: "+traceback.format_exc())
        sublime.active_window().show_input_panel("Result", "Error: "+traceback.format_exc(), lambda x: "" , lambda x: "", lambda : "")
  
  class show_start_end_dot_evalCommand(sublime_plugin.TextCommand) :
    def run(self, edit) :
      global region_selected
      view = self.view
      lines = view.lines(region_selected)
      view.add_regions("region-dot", [lines[0], lines[-1:][0]],  "code", "dot", sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE)
      #view.add_regions("region-body", [region_selected],  "code", "", sublime.DRAW_NO_FILL)
  
  class hide_start_end_dot_evalCommand(sublime_plugin.TextCommand) :
    def run(self, edit) :
      view = self.view
      view.erase_regions("region-dot")
      #view.erase_regions("region-body")
  
  def get_start_end_code_highlights_eval() :
    view = sublime.active_window().active_view()
    return [view.line(view.get_regions("region-dot")[0]).begin(), view.line(view.get_regions("region-dot")[1]).end()]
  
  def back_to_popup(*str_arg):
    view = sublime.active_window().active_view()
    view.run_command("evaluate_javascript")
    return
  


import sublime, sublime_plugin
import json, os, re, webbrowser, cgi, threading, shutil
import util.main as Util
from util.animation_loader import AnimationLoader
from util.repeated_timer import RepeatedTimer
from distutils.version import LooseVersion

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

# Only for Sublime Text Build >= 3124
if int(sublime.version()) >= 3124 :

  items_found_can_i_use = None
  can_i_use_file = None
  can_i_use_popup_is_showing = False
  can_i_use_list_from_main_menu = False
  path_to_can_i_use_data = os.path.join(H_SETTINGS_FOLDER, "can_i_use", "can_i_use_data.json")
  url_can_i_use_json_data = "https://raw.githubusercontent.com/Fyrd/caniuse/master/data.json"
  
  can_i_use_css = ""
  with open(os.path.join(H_SETTINGS_FOLDER, "can_i_use", "style.css")) as css_file:
    can_i_use_css = "<style>"+css_file.read()+"</style>"
  
  def donwload_can_i_use_json_data() :
    global can_i_use_file
    if os.path.isfile(path_to_can_i_use_data) :
      with open(path_to_can_i_use_data) as json_file:    
        json_file = json.load(json_file)
        can_i_use_file = json_file
    if Util.download_and_save(url_can_i_use_json_data, path_to_can_i_use_data) :
      with open(path_to_can_i_use_data) as json_file:    
        json_file = json.load(json_file)
        can_i_use_file = json_file
        return
    if not os.path.isfile(path_to_can_i_use_data) : 
      sublime.active_window().status_message("Can't download \"Can I use\" json data from: https://raw.githubusercontent.com/Fyrd/caniuse/master/data.json")
  
  Util.create_and_start_thread(donwload_can_i_use_json_data, "DownloadCanIuseJsonData")
  
  def find_in_can_i_use(word) :
    global can_i_use_file
    can_i_use_data = can_i_use_file.get("data")
    word = word.lower()
    return [value for key, value in can_i_use_data.items() if value["title"].lower().find(word) >= 0]
  
  def back_to_can_i_use_list(action):
    global can_i_use_popup_is_showing
    if action.find("http") >= 0:
      webbrowser.open(action)
      return
    view = sublime.active_window().active_view()
    can_i_use_popup_is_showing = False
    view.hide_popup()
    if len(action.split(",")) > 1 and action.split(",")[1] == "main-menu" :
      view.run_command("can_i_use", args={"from": "main-menu"})
    else :  
      view.run_command("can_i_use")
  
  def show_pop_can_i_use(index):
    global can_i_use_file
    global items_found_can_i_use
    global can_i_use_popup_is_showing
    if index < 0:
      return
    item = items_found_can_i_use[index]
  
    browser_accepted = ["ie", "edge", "firefox", "chrome", "safari", "opera", "ios_saf", "op_mini", "android", "and_chr"]
    browser_name = [
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IE",
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;EDGE",
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Firefox", 
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Chrome", 
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Safari", 
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Opera", 
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;iOS Safari", 
      "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Opera Mini", 
      "&nbsp;&nbsp;&nbsp;Android Browser", 
      "Chrome for Android"
    ]
  
    html_browser = ""
  
    html_browser += "<div>"
    html_browser += "<h1 class=\"title\">"+cgi.escape(item["title"])+" <a href=\""+item["spec"].replace(" ", "%20")+"\"><span class=\"status "+item["status"]+"\"> - "+item["status"].upper()+"</span></a></h1>"
    html_browser += "<p class=\"description\">"+cgi.escape(item["description"])+"</p>"
    html_browser += "<p class=\"\"><span class=\"support\">Global Support: <span class=\"support-y\">"+str(item["usage_perc_y"])+"%</span>"+( " + <span class=\"support-a\">"+str(item["usage_perc_a"])+"%</span> = " if float(item["usage_perc_a"]) > 0 else "" )+( "<span class=\"support-total\">"+str( "{:10.2f}".format(float(item["usage_perc_y"]) + float(item["usage_perc_a"])) )+"%</span>" if float(item["usage_perc_a"]) > 0 else "" )+"</span> "+( " ".join(["<span class=\"category\">"+category+"</span>" for category in item["categories"]]) )+"</p>"
    html_browser += "</div>"
  
    html_browser += "<div class=\"container-browser-list\">"
    i = 0
    for browser in browser_accepted :
  
      browser_versions = can_i_use_file["agents"]
      stat = item["stats"].get(browser)
      stat_items_ordered = list()
      for k in stat.keys() :
        if k != "TP" : 
          stat_items_ordered.append(k)
  
      if len(stat_items_ordered) >= 1 and stat_items_ordered[0] != "all" :
        stat_items_ordered.sort(key=LooseVersion)
        stat_items_ordered = stat_items_ordered[::-1]
  
      html_p = "<p class=\"version-stat-item\"><span class=\"browser-name\">"+browser_name[i]+"</span> : "
      j = 0
      while j < len(stat_items_ordered) :
        if j == 7:
          break
        class_name = stat.get(stat_items_ordered[j])
        html_annotation_numbers = ""
        requires_prefix = ""
        can_be_enabled = ""
  
        if re.search(r"\bx\b", class_name) :
          requires_prefix = "x"
        if re.search(r"\bd\b", class_name) :
          can_be_enabled = "d"
  
        if class_name.find("#") >= 0 :
          numbers = class_name[class_name.find("#"):].strip().split(" ")
          for number in numbers :
            number = int(number.replace("#", ""))
            html_annotation_numbers += "<span class=\"annotation-number\">"+str(number)+"</span>"
  
        html_p += "<span class=\"version-stat "+stat.get(stat_items_ordered[j])+" \">"+( html_annotation_numbers if html_annotation_numbers else "" )+stat_items_ordered[j]+( "<span class=\"can-be-enabled\">&nbsp;</span>" if can_be_enabled else "" )+( "<span class=\"requires-prefix\">&nbsp;</span>" if requires_prefix else "" )+"</span> "
  
        j = j + 1
  
      html_p += "</p>"
      html_browser += html_p
      i = i + 1
  
    html_browser += "</div>"
  
    if item["notes_by_num"] :
      html_browser += "<div>"
      html_browser += "<h3>Notes</h3>"
      notes_by_num = item["notes_by_num"]
  
      notes_by_num_ordered = list()
      for k in notes_by_num.keys() :
        notes_by_num_ordered.append(k)
      notes_by_num_ordered.sort()
  
      i = 0
      while i < len(notes_by_num_ordered) :
        note = notes_by_num.get(notes_by_num_ordered[i])
        html_p = "<p class=\"note\"><span class=\"annotation-number\">"+str(notes_by_num_ordered[i])+"</span>"+cgi.escape(note)+"</p>"
        html_browser += html_p
        i = i + 1
      html_browser += "</div>"
  
    if item["links"] :
      html_browser += "<div>"
      html_browser += "<h3>Links</h3>"
      links = item["links"]
  
      for link in links :
        html_p = "<p class=\"link\"><a href=\""+link.get("url")+"\">"+cgi.escape(link.get("title"))+"</a></p>"
        html_browser += html_p
      html_browser += "</div>"
  
    view = sublime.active_window().active_view()
    
    can_i_use_popup_is_showing = True
    view.show_popup("""
      <html>
        <head></head>
        <body>
        """+can_i_use_css+"""
        <div class=\"container-back-button\">
          <a class=\"back-button\" href=\"back"""+( ",main-menu" if can_i_use_list_from_main_menu else "")+"""\">&lt; Back</a>
          <a class=\"view-on-site\" href=\"http://caniuse.com/#search="""+item["title"].replace(" ", "%20")+"""\"># View on \"Can I use\" site #</a>
        </div>
        <div class=\"content\">
          """+html_browser+"""
          <div class=\"legend\">
            <h3>Legend</h3>
            <div class=\"container-legend-items\">
              <span class=\"legend-item y\">&nbsp;</span> = Supported 
              <span class=\"legend-item n\">&nbsp;</span> = Not Supported 
              <span class=\"legend-item p a\">&nbsp;</span> = Partial support 
              <span class=\"legend-item u\">&nbsp;</span> = Support unknown 
              <span class=\"legend-item requires-prefix\">&nbsp;</span> = Requires Prefix 
              <span class=\"legend-item can-be-enabled\">&nbsp;</span> = Can Be Enabled 
            </div>
          </div>
        </div>
        </body>
      </html>""", sublime.COOPERATE_WITH_AUTO_COMPLETE, -1, 1250, 650, back_to_can_i_use_list)
  
  class can_i_useCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
  
      global items_found_can_i_use
      global can_i_use_file
      global can_i_use_list_from_main_menu
      can_i_use_data = can_i_use_file.get("data")
      if not can_i_use_data :
        return
  
      view = self.view
      selection = view.sel()[0]
      if args.get("from") != "main-menu" :
        can_i_use_list_from_main_menu = False
        word = view.substr(view.word(selection)).strip()
        items_found_can_i_use = find_in_can_i_use(word)
        sublime.active_window().show_quick_panel([item["title"] for item in items_found_can_i_use], show_pop_can_i_use)
      else :
        can_i_use_list_from_main_menu = True
        items_found_can_i_use = find_in_can_i_use("")
        sublime.active_window().show_quick_panel([item["title"] for item in items_found_can_i_use], show_pop_can_i_use)
  
    def is_enabled(self, **args):
      view = self.view
      if args.get("from") == "main-menu" or jc_helper.settings.get("enable_can_i_use_menu_option") :
        return True 
      return False
  
    def is_visible(self, **args):
      view = self.view
      if args.get("from") == "main-menu" :
        return True
      if jc_helper.settings.get("enable_can_i_use_menu_option") :
        if Util.split_string_and_find_on_multiple(view.scope_name(0), ["source.js", "text.html.basic", "source.css"]) < 0 :
          return False
        return True
      return False
  
  class can_i_use_hide_popupEventListener(sublime_plugin.EventListener):
    def on_modified_async(self, view) :
      global can_i_use_popup_is_showing
      if can_i_use_popup_is_showing :
        view.hide_popup()
        can_i_use_popup_is_showing = False

# Only for Sublime Text Build >= 3000
if int(sublime.version()) >= 3000 :

  class add_jsdoc_settings_to_curr_project_folder(sublime_plugin.WindowCommand) :
    def run(self, **args):
      window = self.window
      contextual_keys = window.extract_variables()
      folder_path = contextual_keys.get("folder")
      if folder_path and os.path.isdir(folder_path) :
        shutil.copyfile(os.path.join(H_SETTINGS_FOLDER, "jsdoc", "jsdoc-settings-default.json"), os.path.join(folder_path, "jsdoc-settings.json"))
        
    def is_enabled(self):
      window = self.window
      contextual_keys = window.extract_variables()
      folder_path = contextual_keys.get("folder")
      return True if folder_path and os.path.isdir(folder_path) else False
  
  class generate_jsdocCommand(sublime_plugin.WindowCommand):
    def run(self, **args):
      window = self.window
      contextual_keys = window.extract_variables()
      folder_path = contextual_keys.get("folder")
      if folder_path and os.path.isdir(folder_path) :
        jsdoc_json = os.path.join(folder_path, "jsdoc-settings.json")
        jsdoc_settings = dict()
        node_command_args = list()
  
        if os.path.isfile(jsdoc_json) :
           with open(jsdoc_json) as json_file: 
            try :
              jsdoc_settings = json.load(json_file)
            except Exception as e:
              sublime.error_message("ERROR: Can't load "+jsdoc_json+" file!")
              return           
  
        jsdoc_conf_path_file = os.path.join(folder_path, jsdoc_settings.get("jsdoc_conf_file")) if jsdoc_settings.get("jsdoc_conf_file") else os.path.join(folder_path, "conf.json")
        if os.path.isfile(jsdoc_conf_path_file) :
          node_command_args.append("-c")
          node_command_args.append(jsdoc_conf_path_file)
        else :
          sublime.error_message("ERROR: Can't load "+jsdoc_conf_path_file+" file!\nConfiguration file REQUIRED!")
          return  
  
        display_symbols_access_property = jsdoc_settings.get("display_symbols_access_property") if jsdoc_settings.get("display_symbols_access_property") in ["private", "protected", "public", "undefined", "all"] else "all"
        node_command_args.append("-a")
        node_command_args.append(display_symbols_access_property)
  
        destination_folder = os.path.join(folder_path, jsdoc_settings.get("destination_folder")) if jsdoc_settings.get("destination_folder") else os.path.join(folder_path, "out")
        node_command_args.append("-d")
        node_command_args.append(destination_folder)
  
        if jsdoc_settings.get("include_symbols_marked_with_the_private_tag") :
          node_command_args.append("-p")
  
        if jsdoc_settings.get("pedantic_mode") :
          node_command_args.append("--pedantic")
  
        query_string_to_parse_and_store_in_global_variable = jsdoc_settings.get("query_string_to_parse_and_store_in_global_variable")
        if query_string_to_parse_and_store_in_global_variable :
          node_command_args.append("-q")
          node_command_args.append(query_string_to_parse_and_store_in_global_variable)
  
        tutorials_path = os.path.join(folder_path, jsdoc_settings.get("tutorials_path")) if jsdoc_settings.get("tutorials_path") else ""
        if tutorials_path :
          node_command_args.append("-u")
          node_command_args.append(tutorials_path)
  
        encoding_when_reading_all_source_files = jsdoc_settings.get("encoding_when_reading_all_source_files") or "utf-8";
        node_command_args.append("-e")
        node_command_args.append(encoding_when_reading_all_source_files)
  
        template_path = os.path.join(folder_path, jsdoc_settings.get("template_path")) if jsdoc_settings.get("template_path") else "templates/default";
        node_command_args.append("-t")
        node_command_args.append(template_path)
  
        if jsdoc_settings.get("search_within_subdirectories") :
          node_command_args.append("-r")
  
        thread = Util.create_and_start_thread(self.exec_node, "JSDocGenerating", [folder_path, node_command_args])
  
    def exec_node(self, folder_path, node_command_args) :
      os.chdir(folder_path)
      from node.main import NodeJS
      node = NodeJS()
      animation_loader = AnimationLoader(["[=     ]", "[ =    ]", "[   =  ]", "[    = ]", "[     =]", "[    = ]", "[   =  ]", "[ =    ]"], 0.067, "Generating docs ")
      interval_animation = RepeatedTimer(animation_loader.sec, animation_loader.animate)
      result = node.execute("jsdoc", node_command_args, True)
      if not result[0] :
        sublime.error_message(result[1])
      animation_loader.on_complete()
      interval_animation.stop()
  
    def is_enabled(self):
      window = self.window
      contextual_keys = window.extract_variables()
      folder_path = contextual_keys.get("folder")
      return True if folder_path and os.path.isdir(folder_path) else False

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
        
  class split_string_lines_to_variableCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
      view = self.view
      selections = view.sel()
      for selection in selections :
        scope = view.scope_name(selection.begin()).strip()
        scope_splitted = scope.split(" ")
        case = args.get("case")
        if case == "split" :
          result = Util.firstIndexOfMultiple(scope_splitted, ("string.quoted.double.js", "string.quoted.single.js", "string.template.js"))
          scope_string = scope_splitted[result.get("index")]
          selector = result.get("string")
          item = Util.get_region_scope_first_match(view, scope, selection, selector)
          if item :
            lines = item.get("region_string_stripped")[1:-1].split("\n")
            str_splitted = list()
            str_splitted.append("var str = \"\"")
            for line in lines :
              line = line if scope_string == "string.template.js" else line.strip()[0:-1]
              line = line.strip()
              if line :
                str_splitted.append( "str += "+"%r"%line )
            str_splitted = "\n".join(str_splitted)
            str_splitted = Util.add_whitespace_indentation(view, selection, str_splitted, "\n")
            view.replace(edit, item.get("region"), str_splitted)
            
    def is_visible(self, **args) :
      view = self.view
      if Util.split_string_and_find(view.scope_name(0), "source.js") < 0 :
        return False
      selection = view.sel()[0]
      scope = view.scope_name(selection.begin()).strip()
      scope_splitted = scope.split(" ")
      result = Util.firstIndexOfMultiple(scope_splitted, ("string.quoted.double.js", "string.quoted.single.js", "string.template.js"))
      if result.get("index") < 0 :
        return False
      return True
  

if int(sublime.version()) < 3000 :
  mainPlugin.init()
  javascriptCompletions.init()
  ej.init()
  jc_helper.init()
else :
  def plugin_loaded():
    global mainPlugin
    mainPlugin.init()
    global javascriptCompletions
    javascriptCompletions.init()
    global ej
    ej.init()
    global jc_helper
    jc_helper.init()

