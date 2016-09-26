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
