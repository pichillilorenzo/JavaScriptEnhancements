import sublime, sublime_plugin
import json, time

bookmarks = dict()

def set_bookmarks(set_dot = False, erase_regions = True):
  global bookmarks
  view = sublime.active_window().active_view()
  
  if is_project_view(view) and is_javascript_project() :
    project_settings = get_project_settings()
    bookmarks = Util.open_json(os.path.join(project_settings["settings_dir_name"], 'bookmarks.json')) or dict()
  else :
    sublime.error_message("Can't recognize JavaScript Project.")
    return

  if erase_regions:
    view.erase_regions("region-dot-bookmarks")
    if set_dot :
      lines = []
      lines = [view.line(view.text_point(bookmark_line, 0)) for bookmark_line in search_bookmarks_by_view(view, is_from_set = True)]
      view.add_regions("region-dot-bookmarks", lines,  "code", "bookmark", sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE)

def update_bookmarks(set_dot = False, erase_regions = True):
  global bookmarks
  path = ""
  view = sublime.active_window().active_view()

  if is_project_view(view) and is_javascript_project() :
    project_settings = get_project_settings()
    path = os.path.join(project_settings["settings_dir_name"], 'bookmarks.json')
  else :
    sublime.error_message("Can't recognize JavaScript Project.")
    return

  with open(path, 'w+') as bookmarks_json:
    bookmarks_json.write(json.dumps(bookmarks))

  if erase_regions:
    view.erase_regions("region-dot-bookmarks")
    if set_dot :
      lines = []
      lines = [view.line(view.text_point(bookmark_line, 0)) for bookmark_line in search_bookmarks_by_view(view)]
      view.add_regions("region-dot-bookmarks", lines,  "code", "bookmark", sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE)

def get_bookmark_by_line(view, line, is_project = False):
  if not view.file_name() or line < 0:
    return False

  global bookmarks

  if is_project :
    set_bookmarks(True, True, False)
  else :
    set_bookmarks(False, True, False)

  for bookmark in bookmarks:
    if bookmark['file_name'] == view.file_name() and bookmark["line"] == line :
      return bookmark

  return None

def add_bookmark(view, line) :
  if not view.file_name() or line < 0:
    return False

  global bookmarks

  set_bookmarks(True)

  if not view.file_name() in bookmarks:
    bookmarks[view.file_name()] = [line]
  elif not line in bookmarks[view.file_name()]:
    bookmarks[view.file_name()].append(line)
    
  update_bookmarks(True)

def overwrite_bookmarks(view, lines) :
  if not view.file_name():
    return False

  global bookmarks

  bookmarks[view.file_name()] = lines
  update_bookmarks(True)

def remove_bookmarks(view) :

  if not view.file_name():
    return False

  set_bookmarks(True)

  global bookmarks

  if view.file_name() in bookmarks :
    del bookmarks[view.file_name()]
    update_bookmarks(True)

def remove_bookmark_by_line(view, line) :

  if not view.file_name() or line < 0:
    return False

  set_bookmarks(True)

  global bookmarks

  if view.file_name() in bookmarks and line in bookmarks[view.file_name()] :
    bookmarks[view.file_name()].remove(line)
    update_bookmarks(True)

def search_bookmarks_by_view(view, is_from_set = False):
  if not view.file_name():
    return []

  global bookmarks

  if not is_from_set :
    set_bookmarks(True)

  return bookmarks[view.file_name()] if view.file_name() in bookmarks else []

def open_bookmarks_and_show(file_name, line) :

  view = sublime.active_window().open_file(file_name)

  sublime.set_timeout_async(lambda: Util.go_to_centered(view, line, 0))

class toggle_project_bookmarksCommand(sublime_plugin.TextCommand) :

  def run(self, edit):

    view = self.view

    if view.get_regions("region-dot-bookmarks"):
      view.erase_regions("region-dot-bookmarks")
    else:
      set_bookmarks(True)

  def is_enabled(self):
    return True if is_project_view(self.view) and is_javascript_project() else False

  def is_visible(self):
    return True if is_project_view(self.view) and is_javascript_project() else False    

class add_project_bookmark_hereCommand(sublime_plugin.TextCommand) :

  def run(self, edit):

    view = self.view

    for sel in view.sel():
      row, col = view.rowcol(sel.begin())
      add_bookmark(view, row)

  def is_enabled(self):
    return True if is_project_view(self.view) and is_javascript_project() else False

  def is_visible(self):
    return True if is_project_view(self.view) and is_javascript_project() else False

class show_project_bookmarksCommand(sublime_plugin.TextCommand):

  def run(self, edit, **args) :
    global bookmarks

    window = sublime.active_window()
    view = self.view

    show_type = args.get("type")

    set_bookmarks(True, True)

    if not bookmarks:
      return 

    items = []

    if show_type == "global_project" :

      for file_name in bookmarks.keys():
        for item in bookmarks[file_name]:
          items += [ ["line: " + str(item+1), file_name] ]

    elif show_type == "view_project" : 

      bookmarks_view = search_bookmarks_by_view(view)

      for item in bookmarks_view:
        items += [ ["line: " + str(item+1), view.file_name()] ]
    
    if items : 
      window.show_quick_panel(items, lambda index: open_bookmarks_and_show(items[index][1], int(items[index][0].replace("line: ", ""))-1 ) if index != -1 else None )

  def is_enabled(self):
    return is_javascript_project()

  def is_visible(self):
    return is_javascript_project()

class delete_project_bookmarksCommand(sublime_plugin.TextCommand):

  def run(self, edit, **args) :
    global bookmarks

    window = sublime.active_window()
    view = self.view

    show_type = args.get("type")

    if show_type == "global_project" :

      bookmarks = dict()
      update_bookmarks(True)

    elif show_type == "view" or show_type == "view_project" : 

      remove_bookmarks(view)

    elif show_type == "single_view_project" : 

      bookmarks_view = search_bookmarks_by_view(view)

      items = []

      for item in bookmarks_view:
        items += [ ["line: " + str(item+1), view.file_name()] ]

      window.show_quick_panel(items, lambda index: remove_bookmark_by_line( view, int(items[index][0].replace("line: ", ""))-1 ) if index != -1 else None )

  def is_enabled(self):
    return is_javascript_project()

  def is_visible(self):
    return is_javascript_project()

class navigate_project_bookmarksCommand(navigate_regionsCommand, sublime_plugin.TextCommand):

  region_key = "region-dot-bookmarks" 

class update_bookmarks_lineEventListener(sublime_plugin.EventListener):

  def on_post_save_async(self, view) :

    if is_project_view(view) and is_javascript_project(): 
      regions = view.get_regions("region-dot-bookmarks")

      lines = []
      for region in regions:
        row, col = view.rowcol(region.begin())
        lines += [row]

      if lines:
        overwrite_bookmarks( view, lines )
