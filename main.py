import sublime, sublime_plugin
import string


class JavaScriptCompletionsPackage():
  def init(self):
    self.api = {}
    self.settings = sublime.load_settings('JavaScript-Completions.sublime-settings')
    self.API_Setup = self.settings.get('completion_active_list')

    # Caching completions
    if self.API_Setup:
      for API_Keyword in self.API_Setup:
        self.api[API_Keyword] = sublime.load_settings( API_Keyword + '.sublime-settings')

# In Sublime Text 3 things are loaded async, using plugin_loaded() callback before try accessing.
javascriptCompletions = JavaScriptCompletionsPackage()

if int(sublime.version()) < 3000:
  javascriptCompletions.init()
else:
  def plugin_loaded():
    global javascriptCompletions
    javascriptCompletions.init()



class JavaScriptCompletionsPackageEventListener(sublime_plugin.EventListener):
  global javascriptCompletions

  def on_query_completions(self, view, prefix, locations):
    self.completions = []

    for API_Keyword in javascriptCompletions.api:
      # If completion active
      if (javascriptCompletions.API_Setup and javascriptCompletions.API_Setup.get(API_Keyword)):
        scope = javascriptCompletions.api[API_Keyword].get('scope')
        if scope and view.match_selector(locations[0], scope):
          self.completions += javascriptCompletions.api[API_Keyword].get('completions')

    if not self.completions:
      return []

    # extend word-completions to auto-completions
    compDefault = [view.extract_completions(prefix)]
    compDefault = [(item, item) for sublist in compDefault for item in sublist if len(item) > 3]
    compDefault = list(set(compDefault))
    completions = list(self.completions)
    completions = [tuple(attr) for attr in self.completions]
    completions.extend(compDefault)
    return (completions)


css = """
<style>
  body{
    padding: 10px;
    border-radius: 15px;
    color: #333;
  }
  .container-completion-link{
    margin: 5px 0;
    font-style: italic;
  }
  .completion-link{
    font-style: normal;
  }
  .highlighted{
    background-color: #333;
    color: #fff;
  }
</style>
"""

completions_link_html = ""
prev_selected = ""
maybe_is_one = 0
first_href = ""

def find_descriptionclick(href, *is_single):
  global javascriptCompletions
  href = href.split(",")
  completion_content = javascriptCompletions.api[href[0]].get('completions')[int(href[1])][1]
  sublime.active_window().active_view().hide_popup()
  sublime.active_window().active_view().show_popup("""
    <body>
    """+css+"""
    """ + ("<a href=\"back\">Back to the list</a>" if not is_single else "") + """
      <div>"""+completion_content[2:-2].replace("\n", "<br>")+"""</div>
    </body>""", sublime.COOPERATE_WITH_AUTO_COMPLETE, -1, 600, 500, back_to_list_find_description)

def back_to_list_find_description(action):
  sublime.active_window().active_view().run_command("find_description")

class find_descriptionCommand(sublime_plugin.TextCommand):
  global javascriptCompletions
  def run(self, edit):

    if int(sublime.version()) < 3000:
      sublime.message_dialog("This version of Sublime Text is not supported by this feature!\n\nMinimum System Requirements:\n - Sublime Text 3")

    global completions_link_html
    global prev_selected
    global maybe_is_one
    global first_href

    view = self.view
    view.hide_popup()
    sel = view.sel()[0]
    str_selected = view.substr(sel).strip()
    if not str_selected : return

    max_width = 800
    max_height = 200

    if prev_selected == str_selected :
      if maybe_is_one == 1 :
        find_descriptionclick(first_href, True)
      else :
        if completions_link_html :
          view.show_popup("<body>"+css+"<div>"+completions_link_html+"</div></body>", sublime.COOPERATE_WITH_AUTO_COMPLETE, -1, max_width, max_height, find_descriptionclick)
        else :
          view.show_popup("<body>No result found!</body>", sublime.COOPERATE_WITH_AUTO_COMPLETE)
      return 

    prev_selected = str_selected
    
    maybe_is_one = 0
    entered_loop = False
    first_href = ""
    completions_link_html = ""

    for API_Keyword in javascriptCompletions.api :
      if (javascriptCompletions.API_Setup and javascriptCompletions.API_Setup.get(API_Keyword)) :
        scope = javascriptCompletions.api[API_Keyword].get('scope')
        if scope and view.match_selector(0, scope):
          if not entered_loop :
            entered_loop = True
          if(API_Keyword.startswith("description-")):
            index_completion = 0
            completions = javascriptCompletions.api[API_Keyword].get('completions')
            for completion in completions:
              completion_name = completion[0][12:].split("\t")
              tab_name = ""
              tab_name_only = ""
              if len(completion_name) > 1:
                tab_name = " | "+(completion_name[1] if len(completion_name[1]) < 35 else completion_name[1][:35]+" ...")
              completion_name = completion_name[0].strip()
              if(completion_name.find(str_selected) >= 0):
                href = API_Keyword+","+str(index_completion)
                if len(completion_name.replace("()", "")) == len(str_selected) and maybe_is_one < 2 :
                  maybe_is_one = maybe_is_one + 1
                  first_href = href
                completion_name = completion_name.replace(str_selected, "<span class=\"highlighted\">"+str_selected+"</span>")
                completions_link_html += "<div class=\"container-completion-link\"><a class=\"completion-link\" href=\""+href+"\">"+completion_name+"</a>"+tab_name+"</div>"
              index_completion = index_completion + 1
            
    completions_link_html += ""

    if not entered_loop :
      return

    if maybe_is_one == 1 :
      find_descriptionclick(first_href, True)
    else :
      if completions_link_html :
        view.show_popup("<body>"+css+"<div>"+completions_link_html+"</div></body>", sublime.COOPERATE_WITH_AUTO_COMPLETE, -1, max_width, max_height, find_descriptionclick)
      else :
        view.show_popup("<body>No result found!</body>", sublime.COOPERATE_WITH_AUTO_COMPLETE)
