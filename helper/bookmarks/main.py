import sublime, sublime_plugin
import json, time
import util.main as Util

bookmarks = []
latest_bookmarks_view = dict()

def set_bookmarks(is_project = False, set_dot = False):
  global bookmarks
  view = sublime.active_window().active_view()

  if is_project and ( not is_project_view(view) or not is_javascript_project() ) :
    sublime.error_message("Can't recognize JavaScript Project.")
    return
  elif is_project and is_project_view(view) and is_javascript_project() :
    project_settings = get_project_settings()
    bookmarks = Util.open_json(os.path.join(project_settings["settings_dir_name"], 'bookmarks.json')) or []
  else :
    bookmarks = Util.open_json(os.path.join(BOOKMARKS_FOLDER, 'bookmarks.json')) or []

  view.erase_regions("region-dot-bookmarks")
  if set_dot :
    lines = []
    lines = [view.line(view.text_point(bookmark["line"], 0)) for bookmark in search_bookmarks_by_view(view, is_project, is_from_set = True)]
    view.add_regions("region-dot-bookmarks", lines,  "code", "bookmark", sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE)

def update_bookmarks(is_project = False, set_dot = False):
  global bookmarks
  path = ""
  view = sublime.active_window().active_view()

  if is_project and ( not is_project_view(view) or not is_javascript_project() ) :
    sublime.error_message("Can't recognize JavaScript Project.")
    return
  elif is_project and is_project_view(view) and is_javascript_project() :
    project_settings = get_project_settings()
    path = os.path.join(project_settings["settings_dir_name"], 'bookmarks.json')
  else :
    path = os.path.join(BOOKMARKS_FOLDER, 'bookmarks.json')

  with open(path, 'w+') as bookmarks_json:
    bookmarks_json.write(json.dumps(bookmarks))

  view.erase_regions("region-dot-bookmarks")
  if set_dot :
    lines = []
    lines = [view.line(view.text_point(bookmark["line"], 0)) for bookmark in search_bookmarks_by_view(view, is_project)]

    view.add_regions("region-dot-bookmarks", lines,  "code", "bookmark", sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE)

def add_bookmark(view, line, name = "", is_project = False) :
  if not view.file_name() or line < 0:
    return False

  global bookmarks

  if is_project :
    set_bookmarks(True, True)
  else :
    set_bookmarks(False, True)

  bookmark = {
    "file_name": view.file_name(),
    "line": line,
    "name": name.strip()
  }

  if get_index_bookmark(bookmark) == -1:

    bookmarks.append(bookmark)
    update_bookmarks(is_project, True)

def remove_bookmark(bookmark, is_project = False) :

  if not bookmark["file_name"] or bookmark["line"] < 0:
    return False

  if is_project :
    set_bookmarks(True, True)
  else :
    set_bookmarks(False, True)

  global bookmarks

  if bookmark in bookmarks :
    bookmarks.remove(bookmark)
    update_bookmarks(is_project, True)

def search_bookmarks_by_view(view, is_project = False, is_from_set = False):
  if not view.file_name():
    return []

  global bookmarks

  if not is_from_set :
    if is_project :
      set_bookmarks(True, True)
    else :
      set_bookmarks(False, True)

  view_bookmarks = []

  for bookmark in bookmarks:
    if bookmark['file_name'] == view.file_name() :
      view_bookmarks.append(bookmark)

  return view_bookmarks

def delete_bookmarks_by_view(view, is_project = False):
  if not view.file_name():
    return False

  global bookmarks

  if is_project :
    set_bookmarks(True, True)
  else :
    set_bookmarks(False, True)

  new_bookmarks = []

  for bookmark in bookmarks:
    if bookmark['file_name'] != view.file_name() :
      new_bookmarks.append(bookmark)

  bookmarks = new_bookmarks
  update_bookmarks(is_project, True)

def get_index_bookmark(bookmark) :
  global bookmarks

  if bookmark in bookmarks :
    return bookmarks.index(bookmark)

  return -1

def open_bookmarks_and_show(index, bookmarks_view = []) :

  if index < 0 :
    return

  global bookmarks
  global latest_bookmarks_view

  if len(bookmarks_view) > 0 :
    bookmark = bookmarks_view[index]
  else :
    bookmark = bookmarks[index]

  latest_bookmarks_view = {"index": index, "bookmarks": bookmarks_view} if bookmarks_view else dict()

  view = sublime.active_window().open_file(bookmark["file_name"])

  sublime.set_timeout_async(lambda: Util.go_to_centered(view, bookmark["line"]-1, 0))

def set_multiple_bookmarks_names(view, index, selections, is_project = False):

  if len(selections) <= 0:
    return

  row = selections[0].begin()

  new_selections = []

  for index, sel in enumerate(selections):
    if index == 0:
      continue
    new_selections.append(sel)

  sublime.active_window().show_input_panel("Bookmark Name "+str(index+1)+": ", "",
    lambda name: add_bookmark(view, view.rowcol(row)[0], name, is_project) or set_multiple_bookmarks_names(view, index+1, new_selections),
    None,
    None
  )

class add_global_bookmark_hereCommand(sublime_plugin.TextCommand) :

  def run(self, edit):

    view = self.view

    selections = view.sel()

    set_multiple_bookmarks_names(view, 0, selections, False)
      
class add_project_bookmark_hereCommand(sublime_plugin.TextCommand) :

  def run(self, edit):

    if not is_javascript_project() :
      sublime.error_message("Can't recognize JavaScript Project.")
      return 

    view = self.view

    selections = view.sel()

    set_multiple_bookmarks_names(view, 0, selections, True)


class show_bookmarksCommand(sublime_plugin.TextCommand):

  def run(self, edit, **args) :
    global bookmarks
    global latest_bookmarks_view

    window = sublime.active_window()
    view = self.view

    show_type = args.get("type")

    if show_type == "global" or show_type == "view" :
      set_bookmarks(False, True)
    else :
      set_bookmarks(True, True)

    if len(bookmarks) <= 0:
      return 

    if show_type == "global" or show_type == "global_project" :

      items = [ ( bookmark['name'] + ", line: " + str(bookmark["line"]) ) if bookmark['name'] else ( bookmark['file_name'] + ", line: " + str(bookmark["line"]) ) for bookmark in bookmarks]

      window.show_quick_panel(items, lambda index: open_bookmarks_and_show(index))

    elif show_type == "view" or show_type == "view_project" : 

      bookmarks_view = search_bookmarks_by_view(view, False if show_type == "view" else True)

      latest_bookmarks_view = {"index": 0, "bookmarks": bookmarks_view} if bookmarks_view else dict()

      items = [ ( bookmark['name'] + ", line: " + str(bookmark["line"]) ) if bookmark['name'] else ( "line: " + str(bookmark["line"]) ) for bookmark in bookmarks_view]
      
      window.show_quick_panel(items, lambda index: open_bookmarks_and_show(index, bookmarks_view))

class delete_bookmarksCommand(sublime_plugin.TextCommand):

  def run(self, edit, **args) :
    global bookmarks

    window = sublime.active_window()
    view = self.view

    show_type = args.get("type")

    if show_type == "global" or show_type == "global_project" :

      bookmarks = []
      update_bookmarks(False if show_type == "global" else True, True)

    elif show_type == "view" or show_type == "view_project" : 

      delete_bookmarks_by_view(view, False if show_type == "view" else True)

    elif show_type == "single_global" or show_type == "single_global_project" : 

      items = [ ( bookmark['name'] + ", line: " + str(bookmark["line"]) ) if bookmark['name'] else ( bookmark['file_name'] + ", line: " + str(bookmark["line"]) ) for bookmark in bookmarks]

      window.show_quick_panel(items, lambda index: remove_bookmark(bookmarks[index], False if show_type == "single_global" else True))

class navigate_bookmarksCommand(sublime_plugin.TextCommand):

  def run(self, edit, **args) :

    window = sublime.active_window()
    view = self.view

    move_type = args.get("type")

    regions = view.get_regions("region-dot-bookmarks")

    if move_type == "next" :

      r_next = self.find_next(regions)
      if r_next :
        row, col = view.rowcol(r_next.begin())

        Util.go_to_centered(view, row, col)

    elif move_type == "previous" :

      r_prev = self.find_prev(regions)
      if r_prev :
        row, col = view.rowcol(r_prev.begin())

        Util.go_to_centered(view, row, col)

  def find_next(self, regions):
    view = self.view

    sel = view.sel()[0]

    for region in regions :
      if region.begin() > sel.begin() :
        return region

    if(len(regions) > 0) :
      return regions[0]

    return None

  def find_prev(self, regions):
    view = self.view

    sel = view.sel()[0]

    previous_regions = []
    for region in regions :
      if region.begin() < sel.begin() :
        previous_regions.append(region)

    if not previous_regions and len(regions) > 0:
      previous_regions.append(regions[len(regions)-1])

    return previous_regions[len(previous_regions)-1] if len(previous_regions) > 0 else None
      
class load_bookmarks_viewViewEventListener(sublime_plugin.ViewEventListener):

  def on_load_async(self) :

    view = self.view

    view.erase_regions("region-dot-bookmarks")
    lines = []
    lines = [view.line(view.text_point(bookmark["line"], 0)) for bookmark in search_bookmarks_by_view(view, ( True if is_project_view(view) and is_javascript_project() else False ))]
    view.add_regions("region-dot-bookmarks", lines,  "code", "bookmark", sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE)