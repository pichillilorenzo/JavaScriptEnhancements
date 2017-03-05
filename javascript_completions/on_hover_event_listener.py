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

    if not Util.selection_in_js_scope(view, point) or not javascriptCompletions.get("enable_on_hover_description") or hover_zone != sublime.HOVER_TEXT :
      return

    str_region = view.word(point)
    result = Util.get_current_region_scope(view, str_region)
    str_selected = result.get("region_string_stripped")
    completion_list = list()
    for API_Keyword in javascriptCompletions.api :
      if (javascriptCompletions.API_Setup and javascriptCompletions.API_Setup.get(API_Keyword)) :
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