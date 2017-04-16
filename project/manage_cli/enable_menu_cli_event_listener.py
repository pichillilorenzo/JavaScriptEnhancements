class enable_menu_cliEventListener(sublime_plugin.EventListener):
  cli = ""
  path = ""
  path_disabled = ""

  def on_activated_async(self, view):
    if self.cli and self.path and self.path_disabled:
      if is_type_javascript_project(self.cli) :
        if os.path.isfile(self.path_disabled):
          os.rename(self.path_disabled, self.path)
      else :
        if os.path.isfile(self.path):
          os.rename(self.path, self.path_disabled)
    elif self.path and self.path_disabled:
      if is_javascript_project() :
        if os.path.isfile(self.path_disabled):
          os.rename(self.path_disabled, self.path)
      else :
        if os.path.isfile(self.path):
          os.rename(self.path, self.path_disabled)

  def on_new_async(self, view):
    self.on_activated_async(view)

  def on_load_async(self, view):
    self.on_activated_async(view)
