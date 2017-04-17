class enable_menu_project_typeEventListener(sublime_plugin.EventListener):
  project_type = ""
  path = ""
  path_disabled = ""

  def on_activated_async(self, view):
    if self.project_type and self.path and self.path_disabled:
      if is_type_javascript_project(self.project_type) :
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
