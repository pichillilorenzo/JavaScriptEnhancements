import sublime, sublime_plugin
import sys, imp, os, webbrowser
import util.main as Util

import _init

SETTINGS_FOLDER_NAME = "javascript_completions"
SETTINGS_FOLDER = os.path.join(_init.PACKAGE_PATH, SETTINGS_FOLDER_NAME)

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

class JavaScriptCompletionsPackage():
  def init(self):
    self.api = {}
    self.settings = sublime.load_settings('JavaScript-Completions.sublime-settings')
    self.API_Setup = self.settings.get('completion_active_list')

    # Caching completions
    if self.API_Setup:
      for API_Keyword in self.API_Setup:
        self.api[API_Keyword] = sublime.load_settings( API_Keyword + '.sublime-settings')
      
    if self.settings.get("enable_key_map") :
      _init.enable_setting(SETTINGS_FOLDER, "Default ("+_init.PLATFORM+")", "sublime-keymap")
    else :
      _init.disable_setting(SETTINGS_FOLDER, "Default ("+_init.PLATFORM+")", "sublime-keymap")

javascriptCompletions = JavaScriptCompletionsPackage()

if int(sublime.version()) < 3000 :
  javascriptCompletions.init()
else :
  def plugin_loaded():
    global javascriptCompletions
    javascriptCompletions.init()

class JavaScriptCompletionsPackageEventListener(sublime_plugin.EventListener):
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

css = """
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
    .container-hint-popup{
      background-color: #202A31;
      padding: 10px 20px 10px 10px;
    }
    .container-completion-link{
      margin: 5px 0;
      font-style: italic;
    }
    .completion-link{
      font-style: normal;
      color: #fff;
    }
    .highlighted, .back-button, .operation-name, .property-name, .constructor-name{
      color: #69BDBF;
    }
    .label{
      margin-bottom: 10px;
      font-weight: bold;
    }
    .parameter-type, .operation-return-type, .property-return-type, .constructor-return-type{
      color: #66BB6A;
    }
    .parameter-name{
      color: #FFA726;
    }
    .parameter-symbol, .class-name{
      color: #EF5350;
    }
    .operation-url-doc-link, .property-url-doc-link, .constructor-url-doc-link{
      font-style: normal;
      color: #fff;
    }
    .container-hint-popup .container-description{
      margin-bottom: 5px;
    }
    .container-hint-popup .container-info{
      display: inline;
      position: relative;
      left: 10px;
    }
    .container-hint-popup .container-url-doc{
      margin-top: 5px;
      font-size: 10px;
    }
    .container-hint-popup .constructor-class-name, .container-hint-popup .operation-class-name, .container-hint-popup .property-class-name{
      padding: 2.5px 12px;
      border-radius: 10px;
      color: #fff;
      background-color: #EF5350;
    }
    .container-hint-popup .constructor-class-name .circle, .container-hint-popup .operation-class-name .circle, .container-hint-popup .property-class-name .circle{
      padding: 2px 6px;
      font-weight: bold;
      background-color: #333;
      color: #fff;
      border-radius: 10px;
      font-size: 10px;
      position: relative;
      top: -1px;
    }
  </style>
"""
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
      """+css+"""
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
      """+css+"""
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
            view.show_popup("<html><head></head><body>"+css+"<div class=\"container\">"+completions_link_html+"</div></body></html>", sublime.COOPERATE_WITH_AUTO_COMPLETE, -1, max_width, max_height, find_descriptionclick)
          else :
            view.show_popup("<html><head></head><body>"+css+"<div class=\"container\"><p>No results found!</p></div></body></html>", sublime.COOPERATE_WITH_AUTO_COMPLETE, max_width, max_height)
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
          view.show_popup("<html><head></head><body>"+css+"<div class=\"container\">"+completions_link_html+"</div></body></html>", sublime.COOPERATE_WITH_AUTO_COMPLETE, -1, max_width, max_height, find_descriptionclick)
        else :
          view.show_popup("<html><head></head><body>"+css+"<div class=\"container\"><p>No results found!</p></div></body></html>", sublime.COOPERATE_WITH_AUTO_COMPLETE, max_width, max_height)
 