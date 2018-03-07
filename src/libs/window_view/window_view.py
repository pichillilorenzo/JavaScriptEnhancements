import sublime, sublime_plugin
from ..hook import Hook
from .window_view_manager import window_view_manager
from ..folder_explorer import FolderExplorer

class WindowView():

  def __init__(self, title="WindowView", window=None, view=None, restore_layout=False):
    self.view_caller = sublime.active_window().active_view()
    self.view_id_caller = self.view_caller.id()
    self.window = sublime.active_window()

    self.restore_layout = restore_layout

    if self.restore_layout:
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
    self.view.settings().add_on_change('color_scheme', lambda: self.set_color_scheme())
    self.set_color_scheme()
    self.events = dict()
    self.region_ids = []
    self.region_input_ids = []
    self.input_state = {}
    self.undo_state = False
    self.redo_state = False
    
    window_view_manager.add(self.view_id_caller, self)
    window_view_manager.add(self.view.id(), self)
    Hook.add("javascript_enhancements_window_view_close_"+str(self.view.id()), self.destroy)

  def __del__(self):
    if self.restore_layout and self.layout_before:
      self.window.set_layout(self.layout_before)
      self.window.focus_group(0)
    window_view_manager.remove(self.view_id_caller)
    window_view_manager.remove(self.view.id())
    Hook.remove_all_hook("javascript_enhancements_window_view_close_"+str(self.view.id()))
    for event in self.events.keys():
      for eventRegionKey in self.events[event].keys():
        for callback in self.events[event][eventRegionKey].keys():
          self.remove_event_listener(event, eventRegionKey, self.events[event][eventRegionKey][callback])

  def add(self, text, key="", scope="", icon="", flags=sublime.HIDDEN, region_id="", padding=0, display_block=False, insert_point=None, replace_points=[]):

    if region_id in self.region_ids:
      raise Exception("Error: ID "+region_id+" already used.")

    if region_id:
      self.region_ids.append(region_id)

    space = (" "*int(padding))
    text = space+text+space

    self.view.set_read_only(False)

    if insert_point:

      self.view.run_command("javascript_enhancements_insert_text_view", args={"text": text, "key": key, "scope": scope, "icon": icon, "flags": flags, "region_id": region_id, "point": insert_point})
      if display_block:
        self.view.run_command("javascript_enhancements_insert_text_view", args={"text": "\n", "key": "", "scope": "", "icon": "", "flags": sublime.HIDDEN, "point": insert_point+len(text)})

    elif replace_points:

      self.view.run_command("javascript_enhancements_replace_region_view", args={"text": text, "key": key, "scope": scope, "icon": icon, "flags": flags, "region_id": region_id, "start": replace_points[0], "end": replace_points[1]})
    
    else:

      self.view.run_command("javascript_enhancements_append_text_view", args={"text": text, "key": key, "scope": scope, "icon": icon, "flags": flags, "region_id": region_id})
      if display_block:
        self.view.run_command("javascript_enhancements_append_text_view", args={"text": "\n", "key": "", "scope": "", "icon": "", "flags": sublime.HIDDEN})

    self.view.set_read_only(True)

  def add_title(self, text, key="", scope="javascriptenhancements.title", icon="", flags=sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE, region_id="", padding=2, display_block=True, insert_point=None, replace_points=[]):
    space_padding = (" "*int(padding))
    space_row = (" "*len(text))+(" "*int(padding)*2)
    text = space_row+"\n"+space_padding+text+space_padding+"\n"+space_row+" "
    self.add(text, key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=0, display_block=display_block, insert_point=insert_point, replace_points=replace_points)

    self.add("\n\nNOTE: See the keymap ")
    self.add_link(text="here", link="https://github.com/pichillilorenzo/JavaScriptEnhancements/wiki/WindowView", scope="link")
    self.add(". ")

  def add_sub_title(self, text, key="", scope="javascriptenhancements.subtitle", icon="", flags=sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE, region_id="", padding=1, display_block=True, insert_point=None, replace_points=[]):
    self.add(text, key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points)

  def add_button(self, text, scope, callback=None, key="click", icon="", flags=sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE, region_id="", padding=1, display_block=False, insert_point=None, replace_points=[]):
    self.add(text, key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points)

    if callback:
      self.add_event_listener("drag_select", key+"."+scope, lambda view: callback(view))

  def add_close_button(self, text, scope, callback=None, key="click", icon="", flags=sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE, region_id="", padding=1, display_block=False, insert_point=None, replace_points=[]):
    self.add_button(text, scope=scope, callback=lambda view: (callback(view) if callback else False) or self.close(), key=key, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points)

  def add_input(self, value=" ", label=None, key="input", scope="javascriptenhancements.input", icon="", flags=sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE, region_id="", padding=1, display_block=False, insert_point=None, replace_points=[]):

    if not region_id:
      raise Exception("Error: ID isn't setted.")

    if region_id in self.region_input_ids:
      raise Exception("Error: ID "+region_id+" already used.")

    if value == None:
      value = " "

    if label:
      self.add(label)

    self.region_input_ids.append(region_id)
    self.add(value, key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points)

  def update_input(self, value, key="input", scope="javascriptenhancements.input", icon="", flags=sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE, region_id="", padding=1, display_block=False, insert_point=None, replace_points=[]):

    self.replace_by_id(region_id, value, key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points)

    if not region_id:
      raise Exception("Error: ID isn't setted.")

    if region_id in self.region_input_ids:
      raise Exception("Error: ID "+region_id+" already used.")

    self.region_input_ids.append(region_id)
    self.update_input_state()

  def add_select(self, default_option, options, label=None, key="select", scope="javascriptenhancements.input", icon="", flags=sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE, region_id="", padding=1, display_block=False, insert_point=None, replace_points=[]):

    if not region_id:
      raise Exception("Error: ID isn't setted.")

    if region_id in self.region_input_ids:
      raise Exception("Error: ID "+region_id+" already used.")

    if label:
      self.add(label)
    self.region_input_ids.append(region_id)
    self.add(options[default_option] + " ▼", key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points)

    self.add_event_listener("drag_select", key+"."+scope, lambda view: sublime.set_timeout_async(lambda: self.view.window().show_quick_panel(options, lambda index: self.update_select(index, options, key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points))))

  def update_select(self, index, options, key="select", scope="javascriptenhancements.input", icon="", flags=sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE, region_id="", padding=1, display_block=False, insert_point=None, replace_points=[]):
    if index < 0:
      return

    self.replace_by_id(region_id, options[index] + " ▼", key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points)

    if not region_id:
      raise Exception("Error: ID isn't setted.")

    if region_id in self.region_input_ids:
      raise Exception("Error: ID "+region_id+" already used.")

    self.region_input_ids.append(region_id)
    self.update_input_state()

  def add_link(self, text, link, scope, key="click", icon="", flags=sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE | sublime.DRAW_SOLID_UNDERLINE, region_id="", padding=0, display_block=False, insert_point=None, replace_points=[]):
    self.add(text, key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points)

    self.add_event_listener("drag_select", key+"."+scope, lambda view: sublime.active_window().run_command("open_url", args={"url": link}))

  def add_folder_explorer(self, scope, region_input_id, start_path="", key="click", icon="", flags=sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE, region_id="", padding=1, display_block=False, insert_point=None, replace_points=[], only_dir=False, only_file=False):

    if start_path == None:
      start_path = ""
      
    folder_explorer = FolderExplorer(self.view, start_path=start_path, callback_choose=lambda path: self.update_input(path, region_id=region_input_id), only_dir=only_dir, only_file=only_file)

    self.add(text=" ")
    self.add_button("...", callback=lambda view: folder_explorer.open( self.get_input(region_input_id) ), key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points)

  def get_input(self, region_input_id):
    region = self.view.get_regions(region_input_id)
    if region:
      region = region[0]
      content = self.view.substr(region)[1:-1]
      if content.endswith(" ▼"):
        content = content[:-len(" ▼")]
      return content
    return None

  def get_inputs(self):
    inputs = dict()
    for region_input_id in self.region_input_ids:
      inputs[region_input_id] = self.get_input(region_input_id)
    return inputs

  def replace_by_id(self, replace_region_id, text, key="", scope="", icon="", flags=sublime.HIDDEN, region_id="", padding=0, display_block=False, insert_point=None, replace_points=[]):

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

  def add_event_listener(self, event, region_key, callback):
    if not event in self.events:
      self.events[event] = dict()

    if not region_key in self.events[event]:
      self.events[event][region_key] = dict()

    eventCallback = lambda view, cmd_args: callback(self.view) if self.can_callback(view, cmd_args, region_key) else None
    self.events[event][region_key][callback] = eventCallback

    Hook.add(event, eventCallback)

  def remove_event_listener(self, event, region_key, callback):

    if not event in self.events:
      return 

    if not region_key in self.events[event]:
      return 

    if not callback in self.events[event][region_key]:
      return 

    eventCallback = self.events[event][region_key][callback]

    Hook.remove_hook(event, eventCallback)
    del self.events[event][region_key][callback]

  def can_callback(self, view, cmd_args, region_key):
    if not view:
      return False
    if view.id() != self.view.id():
      return False

    point = view.window_to_text((cmd_args.get("event").get("x"), cmd_args.get("event").get("y"))) if "event" in cmd_args and "x" in cmd_args.get("event") else self.view.sel()[0]

    for region in self.view.get_regions(region_key):
      if region.contains(point):
        return True

    return False

  def get_view(self):
    return self.view

  def set_color_scheme(self):
    color_scheme = "Packages/JavaScript Enhancements/JavaScript Enhancements.tmTheme"
    if self.view.settings().get('color_scheme') != color_scheme:
      self.view.settings().set('color_scheme', color_scheme)

  def set_input_state(self, delta):
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
            self.update_input(self.input_state[region_input_id]["state"][ index ], region_id=region_input_id)
            if region.contains(self.input_state[region_input_id]["selections"][ index ][0]):
              self.view.sel().clear()
              self.view.sel().add_all(self.input_state[region_input_id]["selections"][ index ])
          break

    self.undo_state = False
    self.redo_state = False

  def update_input_state(self):
    if self.undo_state or self.redo_state:
      return
    
    inputs = self.get_inputs()

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

class JavascriptEnhancementsWindowViewKeypressCommand(sublime_plugin.TextCommand):
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

class JavascriptEnhancementsWindowViewEventListener(sublime_plugin.EventListener):

  def on_activated_async(self, view):
    self.on_selection_modified(view)

  def on_modified(self, view):
    if view.settings().get("javascript_enhancements_window_view"):
      windowView = window_view_manager.get(view.id())
      if windowView:
        windowView.update_input_state()

  def on_selection_modified(self, view):
    if view.settings().get("javascript_enhancements_window_view"):

      for region in view.get_regions("input.javascriptenhancements.input"):

        # Check if the user selection is in an input, 
        # then set_read_only to False in order to allow user to write text.
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
        windowView = window_view_manager.get(view.id())
        if windowView:
          windowView.set_input_state( (-1 if command_name == "undo" else +1) )
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
