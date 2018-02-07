import sublime, sublime_plugin
import os

class WindowViewManager():

  window_views = {}

  def add(self, view_id, window_view):
    if not view_id in self.window_views:
      self.window_views[view_id] = window_view

  def get(self, view_id):
    return self.window_views[view_id] if view_id in self.window_views else None

  def remove(self, view_id):
    if view_id in self.window_views:
      del self.window_views[view_id]

windowViewManager = WindowViewManager()

class WindowView():

  def __init__(self, title="WindowView", window=None, view=None, use_compare_layout=False):
    self.view_caller = sublime.active_window().active_view()
    self.view_id_caller = self.view_caller.id()
    self.window = sublime.active_window()

    self.use_compare_layout = use_compare_layout

    if self.use_compare_layout:
      self.layout_before = self.window.get_layout()
      self.window.set_layout({'rows': [0.0, 1.0], 'cells': [[0, 0, 1, 1], [1, 0, 2, 1]], 'cols': [0.0, 0.5, 1.0]})
      self.window.focus_group(1)
    else:
      self.layout_before = None

    self.view = ( self.window.new_file() if not window else window.new_file() ) if not view else view
    self.view.set_name(title)
    self.view.set_read_only(True)
    self.view.set_scratch(True)
    self.view.settings().set("javascript_enhancements_window_view", True)
    self.view.settings().set("gutter", False)
    self.view.settings().set("highlight_line", False)
    self.view.settings().set("auto_complete_commit_on_tab", False)
    self.view.settings().set("draw_centered", False)
    self.view.settings().set("word_wrap", False)
    self.view.settings().set("auto_complete", False)
    self.view.settings().set("draw_white_space", "none")
    self.view.settings().set("draw_indent_guides", False)
    self.view.settings().set("wide_caret", True)
    self.view.settings().set("rulers", "blink")
    self.view.settings().set("word_wrap", True)
    self.view.settings().add_on_change('color_scheme', lambda: self.setColorScheme())
    self.setColorScheme()
    self.events = dict()
    self.region_ids = []
    self.region_input_ids = []
    self.input_state = {}
    self.undo_state = False
    self.redo_state = False
    
    windowViewManager.add(self.view_id_caller, self)
    windowViewManager.add(self.view.id(), self)
    Hook.add("javascript_enhancements_window_view_close_"+str(self.view.id()), self.destroy)

  def __del__(self):
    if self.use_compare_layout and self.layout_before:
      self.window.set_layout(self.layout_before)
      self.window.focus_group(0)
    windowViewManager.remove(self.view_id_caller)
    windowViewManager.remove(self.view.id())
    Hook.removeAllHook("javascript_enhancements_window_view_close_"+str(self.view.id()))
    for event in self.events.keys():
      for eventRegionKey in self.events[event].keys():
        for callback in self.events[event][eventRegionKey].keys():
          self.removeEventListener(event, eventRegionKey, self.events[event][eventRegionKey][callback])

  def add(self, text, key="", scope="", icon="", flags=sublime.HIDDEN, region_id="", padding=0, display_block=False, insert_point=None, replace_points=[]):

    if region_id in self.region_ids:
      raise Exception("Error: ID "+region_id+" already used.")

    space = (" "*int(padding))
    text = space+text+space

    self.view.set_read_only(False)

    if insert_point:

      self.view.run_command("insert_text_view", args={"text": text, "key": key, "scope": scope, "icon": icon, "flags": flags, "region_id": region_id, "point": insert_point})
      if display_block:
        self.view.run_command("insert_text_view", args={"text": "\n", "key": "", "scope": "", "icon": "", "flags": sublime.HIDDEN, "point": insert_point+len(text)})

    elif replace_points:

      self.view.run_command("replace_region_view", args={"text": text, "key": key, "scope": scope, "icon": icon, "flags": flags, "region_id": region_id, "start": replace_points[0], "end": replace_points[1]})
    
    else:

      self.view.run_command("append_text_view", args={"text": text, "key": key, "scope": scope, "icon": icon, "flags": flags, "region_id": region_id})
      if display_block:
        self.view.run_command("append_text_view", args={"text": "\n", "key": "", "scope": "", "icon": "", "flags": sublime.HIDDEN})

    self.view.set_read_only(True)
    if region_id:
      self.region_ids.append(region_id)

  def addTitle(self, text, key="", scope="javascriptenhancements.title", icon="", flags=sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE, region_id="", padding=2, display_block=True, insert_point=None, replace_points=[]):
    space_padding = (" "*int(padding))
    space_row = (" "*len(text))+(" "*int(padding)*2)
    text = space_row+"\n"+space_padding+text+space_padding+"\n"+space_row+" "
    self.add(text, key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=0, display_block=display_block, insert_point=insert_point, replace_points=replace_points)

    self.add("\n\nNOTE: See the keymap ")
    self.addLink("here", "https://github.com/pichillilorenzo/JavaScriptEnhancements/wiki", "link")

  def addSubTitle(self, text, key="", scope="javascriptenhancements.subtitle", icon="", flags=sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE, region_id="", padding=1, display_block=True, insert_point=None, replace_points=[]):
    self.add(text, key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points)

  def addButton(self, text, scope, callback=None, key="click", icon="", flags=sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE, region_id="", padding=1, display_block=False, insert_point=None, replace_points=[]):
    self.add(text, key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points)

    if callback:
      self.addEventListener("drag_select", key+"."+scope, lambda view: callback(view))

  def addCloseButton(self, text, scope, callback=None, key="click", icon="", flags=sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE, region_id="", padding=1, display_block=False, insert_point=None, replace_points=[]):
    self.addButton(text, scope=scope, callback=lambda view: (callback(view) if callback else False) or self.close(), key=key, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points)

  def addInput(self, value=" ", label=None, key="input", scope="javascriptenhancements.input", icon="", flags=sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE, region_id="", padding=1, display_block=False, insert_point=None, replace_points=[]):

    if not region_id:
      raise Exception("Error: ID isn't setted.")

    if region_id in self.region_input_ids:
      raise Exception("Error: ID "+region_id+" already used.")

    if label:
      self.add(label)
    self.add(value, key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points)
    self.region_input_ids.append(region_id)

  def updateInput(self, value, key="input", scope="javascriptenhancements.input", icon="", flags=sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE, region_id="", padding=1, display_block=False, insert_point=None, replace_points=[]):

    self.replaceById(region_id, value, key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points)

    if not region_id:
      raise Exception("Error: ID isn't setted.")

    if region_id in self.region_input_ids:
      raise Exception("Error: ID "+region_id+" already used.")

    self.region_input_ids.append(region_id)

  def addSelect(self, default_option, options, label=None, key="select", scope="javascriptenhancements.input", icon="", flags=sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE, region_id="", padding=1, display_block=False, insert_point=None, replace_points=[]):

    if not region_id:
      raise Exception("Error: ID isn't setted.")

    if region_id in self.region_input_ids:
      raise Exception("Error: ID "+region_id+" already used.")

    if label:
      self.add(label)
    self.add(options[default_option] + " ▼", key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points)
    self.region_input_ids.append(region_id)

    self.addEventListener("drag_select", key+"."+scope, lambda view: sublime.set_timeout_async(lambda: self.view.window().show_quick_panel(options, lambda index: self.updateSelect(index, options, key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points))))

  def updateSelect(self, index, options, key="select", scope="javascriptenhancements.input", icon="", flags=sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE, region_id="", padding=1, display_block=False, insert_point=None, replace_points=[]):
    if index < 0:
      return

    self.replaceById(region_id, options[index] + " ▼", key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points)
    self.region_input_ids.append(region_id)

  def addLink(self, text, link, scope, key="click", icon="", flags=sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE | sublime.DRAW_SOLID_UNDERLINE, region_id="", padding=0, display_block=False, insert_point=None, replace_points=[]):
    self.add(text, key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points)

    self.addEventListener("drag_select", key+"."+scope, lambda view: sublime.active_window().run_command("open_url", args={"url": link}))

  def addExplorer(self, scope, key="click", icon="", flags=sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE, region_id="", padding=1, display_block=False, insert_point=None, replace_points=[]):
    self.addButton("...", callback=lambda view: self.openExplorer(), key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points)

  def openExplorer(self, path=""):

    path = path.strip()
    if path:
      pass
    elif self.view_caller and self.view_caller.file_name():
      path = self.view_caller.file_name()
    elif self.window.folders():
      path = self.window.folders()[0]
    else:
      sublime.error_message('JavaScript Enhancements: No place to open Explorer to')
      return False
    
    if not os.path.isdir(path):
      path = os.path.dirname(path)

    dirs = []
    files = []

    for item in os.listdir(path):
      abspath = os.path.join(path, item)
      is_dir = os.path.isdir(abspath)
      if is_dir:
        dirs.append(abspath)
      else:
        files.append(abspath)

    html = "<ul>"

    for d in dirs:
      html += "<li> DIR: <a>" + os.path.basename(d) + "</a></li>"

    for f in files:
      html += "<li> FILE: <a>" + os.path.basename(f) + "</a></li>"

    html += "</ul>"
    html += "<a>Choose</a>"
    sublime.set_timeout_async(lambda: self.view.show_popup(html, 0, 5, 500, 500), 50)

  def getInput(self, region_input_id):
    region = self.view.get_regions(region_input_id)
    if region:
      region = region[0]
      content = self.view.substr(region)[1:-1]
      if content.endswith(" ▼"):
        content = content[:-len(" ▼")]
      return content
    return None

  def getInputs(self):
    inputs = dict()
    for region_input_id in self.region_input_ids:
      inputs[region_input_id] = self.getInput(region_input_id)
    return inputs

  def replaceById(self, replace_region_id, text, key="", scope="", icon="", flags=sublime.HIDDEN, region_id="", padding=0, display_block=False, insert_point=None, replace_points=[]):

    region = self.view.get_regions(replace_region_id)
    if region:
      region = region[0]
    else:
      return

    self.removeById(replace_region_id)

    self.add(text, key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=[region.begin(), region.end()])

  def removeById(self, region_id):
    self.view.erase_regions(region_id)

    if region_id in self.region_ids:
      self.region_ids.remove(region_id)

    if region_id in self.region_input_ids:
      self.region_input_ids.remove(region_id)

  def addEventListener(self, event, region_key, callback):
    if not event in self.events:
      self.events[event] = dict()

    if not region_key in self.events[event]:
      self.events[event][region_key] = dict()

    eventCallback = lambda view, cmd_args: callback(self.view) if self.canCallback(view, cmd_args, region_key) else None
    self.events[event][region_key][callback] = eventCallback

    Hook.add(event, eventCallback)

  def removeEventListener(self, event, region_key, callback):

    if not event in self.events:
      return 

    if not region_key in self.events[event]:
      return 

    if not callback in self.events[event][region_key]:
      return 

    eventCallback = self.events[event][region_key][callback]

    Hook.removeHook(event, eventCallback)
    del self.events[event][region_key][callback]

  def canCallback(self, view, cmd_args, region_key):
    if not view:
      return False
    if view.id() != self.view.id():
      return False

    point = view.window_to_text((cmd_args.get("event").get("x"), cmd_args.get("event").get("y"))) if "event" in cmd_args and "x" in cmd_args.get("event") else self.view.sel()[0]

    for region in self.view.get_regions(region_key):
      if region.contains(point):
        return True

    return False

  def getView(self):
    return self.view

  def setColorScheme(self):
    color_scheme = "Packages/JavaScript Enhancements/JavaScript Enhancements.tmTheme"
    if self.view.settings().get('color_scheme') != color_scheme:
      self.view.settings().set('color_scheme', color_scheme)

  def setInputState(self, delta):
    self.undo_state = True
    self.redo_state = True

    for region_input_id in self.region_input_ids:
      region = self.view.get_regions(region_input_id)
      if region:
        region = region[0]
        if region.contains(self.view.sel()[0]) and region_input_id in self.input_state:
          if self.input_state[region_input_id]["index"] + delta >= 0 and self.input_state[region_input_id]["index"] + delta < len(self.input_state[region_input_id]["state"]):
            self.input_state[region_input_id]["index"] = self.input_state[region_input_id]["index"] + delta
            index = self.input_state[region_input_id]["index"]
            self.updateInput(self.input_state[region_input_id]["state"][ index ], region_id=region_input_id)
            if region.contains(self.input_state[region_input_id]["selections"][ index ][0]):
              self.view.sel().clear()
              self.view.sel().add_all(self.input_state[region_input_id]["selections"][ index ])
          break

    self.undo_state = False
    self.redo_state = False

  def updateInputState(self):
    if self.undo_state or self.redo_state:
      return
    
    inputs = self.getInputs()

    for k, v in inputs.items():

      if k in self.input_state:

        if self.input_state[k]["index"] != len(self.input_state[k]["state"]) - 1:
          self.input_state[k]["state"] = self.input_state[k]["state"][:self.input_state[k]["index"]+1]
          self.input_state[k]["selections"] = self.input_state[k]["selections"][:self.input_state[k]["index"]+1]

        if self.input_state[k]["state"][-1] != v:
          self.input_state[k]["state"].append(v) 
          selections = []
          for sel in self.view.sel():
            selections.append(sel)
          self.input_state[k]["selections"].append(selections) 
          self.input_state[k]["index"] = len(self.input_state[k]["state"]) - 1

      else:
        self.input_state[k] = {}
        self.input_state[k]["state"] = [v]
        selections = []
        for sel in self.view.sel():
          selections.append(sel)
        self.input_state[k]["selections"] = [selections]
        self.input_state[k]["index"] = len(self.input_state[k]["state"]) - 1

  def close(self):
    self.view.close()
    self.destroy()

  def destroy(self, *args, **kwargs):
    self.__del__()

class InsertTextViewCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    point = args.get("point")
    view.insert(edit, point, args.get("text"))
    region = sublime.Region(point, len(args.get("text")))
    if "key" in args:
      scope = args.get("scope") if "scope" in args else ""
      scope_dot = "." + scope if scope else ""
      icon = args.get("icon") if "icon" in args else ""
      flags = args.get("flags") if "flags" in args else sublime.HIDDEN
      key = args.get("key") + scope_dot
      regions = [region] + view.get_regions(args.get("key") + scope_dot)

      view.add_regions(key, regions, scope, icon, flags)

      if "region_id" in args and args.get("region_id"):
        view.add_regions(args.get("region_id"), [region], scope, icon, flags)

class ReplaceRegionViewCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    view.erase(edit, sublime.Region(args.get("start"), args.get("end")))
    view.insert(edit, args.get("start"), args.get("text"))
    region = sublime.Region(args.get("start"), args.get("start")+len(args.get("text")))
    if "key" in args:
      scope = args.get("scope") if "scope" in args else ""
      scope_dot = "." + scope if scope else ""
      icon = args.get("icon") if "icon" in args else ""
      flags = args.get("flags") if "flags" in args else sublime.HIDDEN
      key = args.get("key") + scope_dot
      regions = [region] + view.get_regions(args.get("key") + scope_dot)

      view.add_regions(key, regions, scope, icon, flags)

      if "region_id" in args and args.get("region_id"):
        view.add_regions(args.get("region_id"), [region], scope, icon, flags)

class ReplaceTextViewCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    region = sublime.Region(args.get("start"), args.get("end"))
    view.replace(edit, region, args.get("text"))
    if "key" in args:
      scope = args.get("scope") if "scope" in args else ""
      scope_dot = "." + scope if scope else ""
      icon = args.get("icon") if "icon" in args else ""
      flags = args.get("flags") if "flags" in args else sublime.HIDDEN
      key = args.get("key") + scope_dot
      regions = [region] + view.get_regions(args.get("key") + scope_dot)

      view.add_regions(key, regions, scope, icon, flags)

      if "region_id" in args and args.get("region_id"):
        view.add_regions(args.get("region_id"), [region], scope, icon, flags)

class AppendTextViewCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view
    point = view.size()
    view.insert(edit, point, args.get("text"))
    region = sublime.Region(point, view.size())
    if "key" in args:
      scope = args.get("scope") if "scope" in args else ""
      scope_dot = "." + scope if scope else ""
      icon = args.get("icon") if "icon" in args else ""
      flags = args.get("flags") if "flags" in args else sublime.HIDDEN
      key = args.get("key") + scope_dot
      regions = [region] + view.get_regions(args.get("key") + scope_dot)

      view.add_regions(key, regions, scope, icon, flags)

      if "region_id" in args and args.get("region_id"):
        view.add_regions(args.get("region_id"), [region], scope, icon, flags)

class WindowViewKeypressCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view

    if view.settings().get("javascript_enhancements_window_view"):
      key = args.get("key")

      if key == "tab" or key =="shift+tab":
        input_regions = view.get_regions("input.javascriptenhancements.input")
        for index in range(0, len(input_regions)):
          region = input_regions[index]
          if region.contains(view.sel()[0]):
            view.sel().clear()
            next_region = None
            if key == "tab":
              next_region = input_regions[index + 1] if index < len(input_regions) - 1 else input_regions[0]
            else:
              next_region = input_regions[index - 1] if index - 1 >= 0 else input_regions[-1]
            view.sel().add(next_region.begin()+1)
            return

        if len(input_regions) > 0:
          view.sel().clear()
          view.sel().add(input_regions[0].begin()+1)

      if key == "super+alt+a":
        input_regions = view.get_regions("input.javascriptenhancements.input")
        for region in input_regions:
          if region.contains(view.sel()[0]):   
            view.sel().clear()
            view.sel().add(sublime.Region(region.begin()+1, region.end()-1))

class WindowViewEventListener(sublime_plugin.EventListener):

  def on_activated_async(self, view):
    self.on_selection_modified(view)

  def on_modified(self, view):
    if view.settings().get("javascript_enhancements_window_view"):
      windowView = windowViewManager.get(view.id())
      if windowView:
        windowView.updateInputState()

  def on_selection_modified(self, view):
    if view.settings().get("javascript_enhancements_window_view"):

      for region in view.get_regions("input.javascriptenhancements.input"):

        if view.sel()[0].begin() >= region.begin() + 1 and view.sel()[0].end() <= region.end() - 1:
          view.set_read_only(False)
          return
        elif view.sel()[0].begin() == view.sel()[0].end():
          if view.sel()[0].begin() == region.begin():
            view.sel().clear()
            view.sel().add(region.begin()+1)
            return
          elif view.sel()[0].end() == region.end():
            view.sel().clear()
            view.sel().add(region.end()-1)
            return

      view.set_read_only(True)

  def on_text_command(self, view, command_name, args):
    if view.settings().get("javascript_enhancements_window_view"):
      Hook.apply(command_name, view, args)

      if command_name == "undo" or command_name == "redo_or_repeat" or command_name == "redo":
        windowView = windowViewManager.get(view.id())
        if windowView:
          windowView.setInputState( (-1 if command_name == "undo" else +1) )
          self.on_selection_modified(view)
        return ("noop", {})

      if command_name == "soft_undo" or command_name == "soft_redo":
        return ("noop", {})

      for region in view.get_regions("input.javascriptenhancements.input"):
        if view.sel()[0].begin() == view.sel()[0].end():
          if command_name == "left_delete" and view.sel()[0].begin() == region.begin() + 1:
            return ("noop", {})
          elif command_name == "right_delete" and view.sel()[0].end() == region.end() - 1:
            return ("noop", {})
        if command_name == "insert":
          return ("noop", {})

  def on_close(self, view):
    if view.settings().get("javascript_enhancements_window_view"):
      Hook.apply("javascript_enhancements_window_view_close_"+str(view.id()))
