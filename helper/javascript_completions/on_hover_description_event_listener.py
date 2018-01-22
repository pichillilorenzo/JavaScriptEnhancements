import sublime, sublime_plugin

def description_details_html(description):
  description_name = "<span class=\"name\">" + cgi.escape(description['name']) + "</span>"
  description_return_type = ""

  text_pre_params = ""

  parameters_html = ""
  if description['func_details'] :

    if not description['type'].startswith("(") :
      text_pre_params = description['type'][ : description['type'].rfind(" => ") if description['type'].rfind(" => ") >= 0 else None ]
      text_pre_params = "<span class=\"text-pre-params\">" + cgi.escape(text_pre_params[:text_pre_params.find("(")]) + "</span>"

    for param in description['func_details']["params"]:
      is_optional = True if param['name'].find("?") >= 0 else False
      param['name'] = cgi.escape(param['name'].replace("?", ""))
      param['type'] = cgi.escape(param['type']) if param.get('type') else None
      if not parameters_html:
        parameters_html += "<span class=\"parameter-name\">" + param['name'] + "</span>" + ( "<span class=\"parameter-is-optional\">?</span>" if is_optional else "" ) + ( ": <span class=\"parameter-type\">" + param['type'] + "</span>" if param['type'] else "" )
      else:
        parameters_html += ', ' + "<span class=\"parameter-name\">" + param['name'] + "</span>" + ( "<span class=\"parameter-is-optional\">?</span>" if is_optional else "" ) + ( ": <span class=\"parameter-type\">" + param['type'] + "</span>" if param['type'] else "" )
    parameters_html = "("+parameters_html+")"

    description_return_type = cgi.escape(description['func_details']["return_type"]) if description['func_details']["return_type"] else ""
  elif description['type'] :
    description_return_type = cgi.escape(description['type'])
  if description_return_type :
    description_return_type = " => <span class=\"return-type\">"+description_return_type+"</span>"

  html = """ 
  <div class=\"container-description\">
    <div>"""+description_name+text_pre_params+parameters_html+description_return_type+"""</div>
    <div class=\"container-go-to-def\"><a href="go_to_def" class="go-to-def">Go to definition</a></div>
  </div>
  """
  return html

class on_hover_descriptionEventListener(sublime_plugin.EventListener):

  def on_hover(self, view, point, hover_zone) :
    if not view.match_selector(
        point,
        'source.js - string - constant - comment'
    ):
      return

    if hover_zone != sublime.HOVER_TEXT :
      return

    for region in view.get_regions("flow_error"):
      if region.contains(point):
        return

    region = view.word(point)
    word = view.substr(region)
    if not word.strip() :
      return

    view.hide_popup()

    sublime.set_timeout_async(lambda: on_hover_description_async(view, point, hover_zone, point))

# used also by show_hint_parametersCommand
def on_hover_description_async(view, point, hover_zone, popup_position, show_hint=False) :
  if not view.match_selector(
      point,
      'source.js - comment'
  ):
    return

  if hover_zone != sublime.HOVER_TEXT :
    return

  if not show_hint:
    for region in view.get_regions("flow_error"):
      if region.contains(point):
        return

  region = view.word(point)
  word = view.substr(region)
  if not word.strip() :
    return

  cursor_pos = region.end()

  deps = flow_parse_cli_dependencies(view, cursor_pos=cursor_pos, add_magic_token=True, not_add_last_part_tokenized_line=True)

  flow_cli = "flow"
  is_from_bin = True
  chdir = ""
  use_node = True
  bin_path = ""

  settings = get_project_settings()
  if settings and settings["project_settings"]["flow_cli_custom_path"]:
    flow_cli = os.path.basename(settings["project_settings"]["flow_cli_custom_path"])
    bin_path = os.path.dirname(settings["project_settings"]["flow_cli_custom_path"])
    is_from_bin = False
    chdir = settings["project_dir_name"]
    use_node = False

  node = NodeJS(check_local=True)

  result = node.execute_check_output(
    flow_cli,
    [
      'autocomplete',
      '--from', 'sublime_text',
      '--root', deps.project_root,
      '--json',
      deps.filename
    ],
    is_from_bin=is_from_bin,
    use_fp_temp=True, 
    fp_temp_contents=deps.contents, 
    is_output_json=True,
    chdir=chdir,
    bin_path=bin_path,
    use_node=use_node
  )

  html = ""
  results_found = 0

  if result[0]:
    descriptions = result[1]["result"] + load_default_autocomplete(view, result[1]["result"], word, region.begin(), True)

    for description in descriptions :
      if description['name'] == word :

        if description['type'].startswith("((") or description['type'].find("&") >= 0 :
          sub_completions = description['type'].split("&")
          for sub_comp in sub_completions :

            results_found += 1

            sub_comp = sub_comp.strip()
            sub_type = sub_comp[1:-1] if description['type'].startswith("((") else sub_comp
                       
            text_params = sub_type[ : sub_type.rfind(" => ") if sub_type.rfind(" => ") >= 0 else None ]
            text_params = text_params.strip()
            description["func_details"] = dict()
            description["func_details"]["params"] = list()
            description["func_details"]["return_type"] = ""
            if sub_type.rfind(" => ") >= 0 :
              description["func_details"]["return_type"] = sub_type[sub_type.rfind(" => ")+4:].strip()
            start = 1 if sub_type.find("(") == 0 else sub_type.find("(")+1
            end = text_params.rfind(")")
            params = text_params[start:end].split(",")
            for param in params :
              param_dict = dict()
              param_info = param.split(":")
              param_dict["name"] = param_info[0].strip()
              if len(param_info) > 1 :
                param_dict["type"] = param_info[1].strip()
              description['func_details']["params"].append(param_dict)

            html += description_details_html(description)
        else :

          html += description_details_html(description)

  if not html :
    deps = flow_parse_cli_dependencies(view)

    row, col = view.rowcol(point)

    flow_cli = "flow"
    is_from_bin = True
    chdir = ""
    use_node = True
    bin_path = ""

    settings = get_project_settings()
    if settings and settings["project_settings"]["flow_cli_custom_path"]:
      flow_cli = os.path.basename(settings["project_settings"]["flow_cli_custom_path"])
      bin_path = os.path.dirname(settings["project_settings"]["flow_cli_custom_path"])
      is_from_bin = False
      chdir = settings["project_dir_name"]
      use_node = False
      
    node = NodeJS(check_local=True)
    result = node.execute_check_output(
      flow_cli,
      [
        'type-at-pos',
        '--from', 'sublime_text',
        '--root', deps.project_root,
        '--path', deps.filename,
        '--json',
        str(row - deps.row_offset + 1), str(col + 1)
      ],
      is_from_bin=is_from_bin,
      use_fp_temp=True, 
      fp_temp_contents=deps.contents, 
      is_output_json=True,
      chdir=chdir,
      bin_path=bin_path,
      use_node=use_node
    )

    if result[0] and result[1].get("type") and result[1]["type"] != "(unknown)":

      print(result[1])
      results_found = 1

      description = dict()
      description["name"] = ""
      description['func_details'] = dict()
      description['func_details']["params"] = list()
      description['func_details']["return_type"] = ""
      is_function = False
      matches = re.match("^([a-zA-Z_]\w+)", result[1]["type"])
      if matches :
        description["name"] = matches.group()
      if result[1]["type"].find(" => ") >= 0 :
        description['func_details']["return_type"] = cgi.escape(result[1]["type"][result[1]["type"].find(" => ")+4:])
      else :
        description['func_details']["return_type"] = cgi.escape(result[1]["type"])
      if result[1]["type"].find("(") == 0:
        is_function = True
        start = 1
        end = result[1]["type"].find(")")
        params = result[1]["type"][start:end].split(",")
        description['func_details']["params"] = list()
        for param in params :
          param_dict = dict()
          param_info = param.split(":")
          param_dict["name"] = cgi.escape(param_info[0].strip())
          if len(param_info) == 2 :
            param_dict["type"] = cgi.escape(param_info[1].strip())
          else :
            param_dict["type"] = None
          description['func_details']["params"].append(param_dict)

      description_name = "<span class=\"name\">" + cgi.escape(description['name']) + "</span>"
      description_return_type = ""

      parameters_html = ""
      if description['func_details'] :

        for param in description['func_details']["params"]:
          is_optional = True if param['name'].find("?") >= 0 else False
          param['name'] = param['name'].replace("?", "")
          if not parameters_html:
            parameters_html += "<span class=\"parameter-name\">" + param['name'] + "</span>" + ( "<span class=\"parameter-is-optional\">?</span>" if is_optional else "" ) + ( ": <span class=\"parameter-type\">" + param['type'] + "</span>" if param['type'] else "" )
          else:
            parameters_html += ', ' + "<span class=\"parameter-name\">" + param['name'] + "</span>" + ( "<span class=\"parameter-is-optional\">?</span>" if is_optional else "" ) + ( ": <span class=\"parameter-type\">" + param['type'] + "</span>" if param['type'] else "" )
        parameters_html = "("+parameters_html+")" if is_function else ""

        description_return_type = description['func_details']["return_type"]
      elif description['type'] :
        description_return_type = description['type']
      if description_return_type :
        description_return_type = (" => " if description['name'] or is_function else "") + "<span class=\"return-type\">"+description_return_type+"</span>"

      html += """ 
      <div class=\"container-description\">
        <div>"""+description_name+parameters_html+description_return_type+"""</div>
        <div class=\"container-go-to-def\"><a href="go_to_def" class="go-to-def">Go to definition</a></div>
      </div>
      """

  func_action = lambda x: view.run_command("go_to_def", args={"point": point}) if x == "go_to_def" else ""

  if html:
      view.show_popup("""
      <html><head></head><body class=\""""+("single-result-found" if results_found == 1 else "more-results-found")+"""\">
      """+js_css+"""
        <div class=\"container-hint-popup\">
          """ + html + """    
        </div>
      </body></html>""", sublime.COOPERATE_WITH_AUTO_COMPLETE | sublime.HIDE_ON_MOUSE_MOVE_AWAY, popup_position, 1150, 80 if results_found == 1 else 160, func_action )
  