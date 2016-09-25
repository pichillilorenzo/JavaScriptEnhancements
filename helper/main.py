import sublime, sublime_plugin
import json, os, _init, re, webbrowser, cgi, threading
import util.main as Util
from distutils.version import LooseVersion

SETTINGS_FOLDER_NAME = "helper"
SETTINGS_FOLDER = os.path.join(_init.PACKAGE_PATH, SETTINGS_FOLDER_NAME)

class JavaScriptCompletionsHelper():

  def init(self):
    self.api = {}
    self.settings = sublime.load_settings('helper.sublime-settings')

jc_helper = JavaScriptCompletionsHelper()

if int(sublime.version()) < 3000 :
  jc_helper.init()
else :
  def plugin_loaded():
    global jc_helper
    jc_helper.init()
     
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
  path_to_can_i_use_data = os.path.join(_init.PACKAGE_PATH, "helper", "can_i_use_data.json")
  url_can_i_use_json_data = "https://raw.githubusercontent.com/Fyrd/caniuse/master/data.json"

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

  if not Util.check_thread_is_alive("DownloadCanIuseJsonData") :
    thread = threading.Thread(target=donwload_can_i_use_json_data, name="DownloadCanIuseJsonData")
    thread.setDaemon(True)
    thread.start()

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

    css = """
    <style>
      html, body{
        margin: 0;
        padding: 0;
      }
      body{
        background-color: #202A31;
      }
      .content{
        padding: 0 40px 20px 40px;
      }
      .view-on-site{
        font-size: 1rem;
        text-decoration: none;
        color: #fff;
        padding: 10px;
        border-radius: 10px;
        background-color: #DB5600;
      }
      .container-browser-list{
        font-family: Courier;
      }
      .version-stat-item{
        margin: 25px 0;
      }
      .browser-name{
        font-size: 1.15rem;
        font-weight: bold;
      }
      .version-stat{
        margin: 5px 10px;
        font-weight: bold;
        font-size: 1.2rem;
      }
      .y, .p, .a, .n, .u{
        padding: 10px 15px;
      } 
      .y{
        background-color: #39b54a;
      }
      .p, .a{
        background-color: #A8BD04;
      }
      .n{
        background-color: #c44230;
      }
      .u{
        background-color: #838383;
      }
      .annotation-number{
        padding: 3px;
        background-color: #fff;
        color: #333;
        font-size: 10px;
        position: relative;
        top: -10px;
        left: -12px;
      }
      .legend .container-legend-items{
        margin: 10px 0;
      }
      .legend-item{
        padding: 3.25px 12.5px;
      }
      .container-back-button{
        padding: 20px 0 0 15px;
      }
      .back-button{
        padding: 10px;
        background-color: #fff;
        text-decoration: none;
        border-radius: 10px;
        color: #333;
        font-weight: bold;
      }
      .requires-prefix{
        background-color: #FFFF5F;
        position: relative;
        top: -14px;
        right: -13px;
        padding: 7px;
        font-size: 1px;
      }
      .can-be-enabled{
        background-color: #78CC76;
        position: relative;
        top: -14px;
        right: -11px;
        font-size: 1px;
        padding: 7px;
      }
      .legend .requires-prefix, .legend .can-be-enabled{
        top: -4px;
        right: 0;
      }
      .status{
        font-weight: bold;
        font-size: 14px;
        text-decoration: none;
        position: relative;
        top: -4px;
      }
      .status.rec, .status.ietf, .status.ls{
        color: #007700;
      }
      .status.pr{
        color: #387700;
      }
      .status.wd{
        color: #770000;
      }
      .status.cr{
        color: #777700;
      }
      .status.unoff{
        color: #777777;
      }
      .support{
        padding: 5px 15px;
        background-color: #f2e8d5;
        border-radius: 10px;
        color: #333;
        font-weight: bold;
      }
      .support-y{
        color: #009114;
      }
      .support-a{
        color: #7e7e00;
      }
      .category{
        padding: 5px 15px;
        border-radius: 10px;
        background-color: #f2e8d5;
        color: #333;
      }
    </style>
    """
    
    can_i_use_popup_is_showing = True
    view.show_popup("""
      <html>
        <head></head>
        <body>
        """+css+"""
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