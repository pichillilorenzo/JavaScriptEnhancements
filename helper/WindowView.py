import sublime, sublime_plugin

class WindowView():

  def __init__(self, title="WindowView", window=None, view=None):
    self.view = ( sublime.active_window().new_file() if not window else window.new_file() ) if not view else view
    self.view.set_name(title)
    self.view.set_read_only(True)
    self.view.set_scratch(True)
    self.view.settings().set("javascript_enhancements_window", True)
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
    self.view.settings().add_on_change('color_scheme', lambda: self.setColorScheme())
    self.events = dict()
    self.region_ids = []
    self.region_input_ids = []

    Hook.add("javascript_enhancements_window_close_"+str(self.view.id()), self.destroy)

  def __del__(self):
    Hook.removeAllHook("javascript_enhancements_window_close_"+str(self.view.id()))
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

  def addSubTitle(self, text, key="", scope="javascriptenhancements.subtitle", icon="", flags=sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE, region_id="", padding=1, display_block=True, insert_point=None, replace_points=[]):
    self.add(text, key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points)

  def addButton(self, text, scope, key="click", icon="", flags=sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE, region_id="", padding=1, display_block=False, insert_point=None, replace_points=[]):
    self.add(text, key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points)

  def addInput(self, value=" ", key="input", scope="javascriptenhancements.input", icon="", flags=sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE, region_id="", padding=1, display_block=False, insert_point=None, replace_points=[]):

    if not region_id:
      raise Exception("Error: ID isn't setted.")

    if region_id in self.region_input_ids:
      raise Exception("Error: ID "+region_id+" already used.")

    self.add(value, key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=replace_points)
    self.region_input_ids.append(region_id)

  def getInput(self, region_input_id):
    region = self.view.get_regions(region_input_id)
    if region:
      region = region[0]
      return self.view.substr(region)[1:-1]
    return None

  def getInputs(self):
    inputs = dict()
    for region_input_id in self.region_input_ids:
      inputs[region_id] = self.getInput(region_input_id)
    return inputs

  def replaceById(self, replace_region_id, text, key="", scope="", icon="", flags=sublime.HIDDEN, region_id="", padding=0, display_block=False, insert_point=None, replace_points=[]):

    print(self.view.get_regions("input.javascriptenhancements.input"))
    region = self.view.get_regions(replace_region_id)
    if region:
      region = region[0]
    else:
      return

    self.removeById(replace_region_id)

    self.add(text, key=key, scope=scope, icon=icon, flags=flags, region_id=region_id, padding=padding, display_block=display_block, insert_point=insert_point, replace_points=[region.begin(), region.end()])

    print(region)
    print(self.view.get_regions("input.javascriptenhancements.input"))

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

  def close(self):
    self.view.close()
    self.destroy()

  def destroy(self, *args, **kwargs):
    self.__del__()

class insertTextViewCommand(sublime_plugin.TextCommand):
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

class replaceRegionViewCommand(sublime_plugin.TextCommand):
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

class replaceTextViewCommand(sublime_plugin.TextCommand):
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

class appendTextViewCommand(sublime_plugin.TextCommand):
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

class windowKeypressCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    view = self.view

    if view.settings().get("javascript_enhancements_window"):
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

      if key == "ctrl+alt+a":
        input_regions = view.get_regions("input.javascriptenhancements.input")
        for region in input_regions:
          if region.contains(view.sel()[0]):   
            view.sel().clear()
            view.sel().add(sublime.Region(region.begin()+1, region.end()-1))

class windowEventListener(sublime_plugin.EventListener):

  def on_modified_async(self, view):
    if view.settings().get("javascript_enhancements_window"):

      for region in view.get_regions("input.javascriptenhancements.input"):

        # this order is important!
        
        if region.contains(view.sel()[0]) and view.substr(region)[0] != " ":
          view.set_read_only(False)
          char = view.substr(region)[0]
          view.run_command("insert_text_view", args={"text": " ", "point": region.begin()+1})
          view.run_command("replace_text_view", args={"text": " ", "start": region.begin(), "end": region.begin()+1})
          view.run_command("replace_text_view", args={"text": char, "start": region.begin()+1, "end": region.begin()+2})
          view.set_read_only(True)
          view.sel().clear()
          view.sel().add(region.begin()+1)

        elif region.contains(view.sel()[0]) and view.substr(region)[-1] != " ":
          view.set_read_only(False)
          char = view.substr(region)[-1]
          view.run_command("insert_text_view", args={"text": " ", "point": region.end()-1})
          view.run_command("replace_text_view", args={"text": " ", "start": region.end(), "end": region.end()+1})
          view.run_command("replace_text_view", args={"text": char, "start": region.end()-1, "end": region.end()})
          view.set_read_only(True)
          view.sel().clear()
          view.sel().add(region.end())

        elif region.contains(view.sel()[0]) and region.size() == 2:
          view.set_read_only(False)
          view.run_command("insert_text_view", args={"text": " ", "point": region.begin()+1})
          view.set_read_only(True)
          view.sel().clear()
          view.sel().add(region.begin()+1)
          break 

    return

  def on_selection_modified_async(self, view):
    if view.settings().get("javascript_enhancements_window"):

      for region in view.get_regions("input.javascriptenhancements.input"):
        if view.sel()[0].begin() >= region.begin() + 1 and view.sel()[0].end() <= region.end() - 1:
          view.set_read_only(False)
          return
        elif view.sel()[0].begin() == view.sel()[0].end():
          if view.sel()[0].begin() == region.begin():
            view.sel().clear()
            view.sel().add(region.begin()+1)
            return
          elif view.sel()[0].end() == region.end() :
            view.sel().clear()
            view.sel().add(region.end()-1)
            return

      view.set_read_only(True)

  def on_text_command(self, view, command_name, args):
    if view.settings().get("javascript_enhancements_window"):
      Hook.apply(command_name, view, args)

  def on_close(self, view):
    if view.settings().get("javascript_enhancements_window"):
      Hook.apply("javascript_enhancements_window_close_"+str(view.id()))
