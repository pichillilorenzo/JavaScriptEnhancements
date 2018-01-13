items_found_can_i_use = None
can_i_use_file = None
can_i_use_popup_is_showing = False
can_i_use_list_from_main_menu = False
path_to_can_i_use_data = os.path.join(HELPER_FOLDER, "can_i_use", "can_i_use_data.json")
path_to_test_can_i_use_data = os.path.join(HELPER_FOLDER, "can_i_use", "can_i_use_data2.json")
url_can_i_use_json_data = "https://raw.githubusercontent.com/Fyrd/caniuse/master/data.json"

can_i_use_css = ""
with open(os.path.join(HELPER_FOLDER, "can_i_use", "style.css")) as css_file:
  can_i_use_css = "<style>"+css_file.read()+"</style>"

def donwload_can_i_use_json_data() :
  global can_i_use_file

  if os.path.isfile(path_to_can_i_use_data) :
    with open(path_to_can_i_use_data) as json_file:    
      try :
        can_i_use_file = json.load(json_file)
      except Exception as e :
        print("Error: "+traceback.format_exc())
        sublime.active_window().status_message("Can't use \"Can I use\" json data from: https://raw.githubusercontent.com/Fyrd/caniuse/master/data.json")

  if Util.download_and_save(url_can_i_use_json_data, path_to_test_can_i_use_data) :
    if os.path.isfile(path_to_can_i_use_data) :
      if not Util.checksum_sha1_equalcompare(path_to_can_i_use_data, path_to_test_can_i_use_data) :
        json_file = open(path_to_test_can_i_use_data) 
        try :
          can_i_use_file = json.load(json_file)
          if os.path.isfile(path_to_can_i_use_data) :
            os.remove(path_to_can_i_use_data)
          json_file.close()
          os.rename(path_to_test_can_i_use_data, path_to_can_i_use_data)
        except Exception as e :
          print("Error: "+traceback.format_exc())
          sublime.active_window().status_message("Can't use new \"Can I use\" json data from: https://raw.githubusercontent.com/Fyrd/caniuse/master/data.json")
        if not json_file.closed:
          json_file.close()
      if os.path.isfile(path_to_test_can_i_use_data) :
        if not json_file.closed:
          json_file.close()
        try :
          os.remove(path_to_test_can_i_use_data)
        except Exception as e :
          pass
    else :
      os.rename(path_to_test_can_i_use_data, path_to_can_i_use_data)
      with open(path_to_can_i_use_data) as json_file :    
        try :
          can_i_use_file = json.load(json_file)
        except Exception as e :
          print("Error: "+traceback.format_exc())
          sublime.active_window().status_message("Can't use \"Can I use\" json data from: https://raw.githubusercontent.com/Fyrd/caniuse/master/data.json")

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

    if not can_i_use_file:
      sublime.active_window().status_message("\"Can I use\" feature is not ready.")
      return

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
    if args.get("from") == "main-menu" or javascriptCompletions.get("enable_can_i_use_menu_option") :
      return True 
    return False

  def is_visible(self, **args):
    view = self.view
    if args.get("from") == "main-menu" :
      return True
    if javascriptCompletions.get("enable_can_i_use_menu_option") :
      if Util.split_string_and_find_on_multiple(view.scope_name(0), ["source.js", "text.html.basic", "source.css"]) < 0 :
        return False
      return True
    return False
    
class can_i_use_hide_popupEventListener(sublime_plugin.EventListener):
  def on_selection_modified_async(self, view) :
    global can_i_use_popup_is_showing
    if can_i_use_popup_is_showing :
      view.hide_popup()
      can_i_use_popup_is_showing = False