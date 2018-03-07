import sublime, sublime_plugin

class PopupManager():

  popup_types = {}

  def get_visible(self):
    for k, v in self.popup_types.items():
      if v["visible"]:
        return k
        
  def set_visible(self, popup_type, visible):
    if popup_type in self.popup_types:
      self.popup_types[popup_type]["visible"] = visible

  def is_visible(self, popup_type):
    return (popup_type in self.popup_types and 
      self.popup_types[popup_type]["visible"] and 
      sublime.active_window().active_view().is_popup_visible())
    
  def register(self, popup_type):
    self.popup_types[popup_type] = {
      "visible": False
    }

  def unregister(self, popup_type):
    del self.popup_types[popup_type]

popup_manager = PopupManager()
popup_manager.register("javascript_enhancements_hint_parameters")
popup_manager.register("javascript_enhancements_flow_error")
popup_manager.register("javascript_enhancements_flow_warning")
popup_manager.register("javascript_enhancements_can_i_use")
popup_manager.register("javascript_enhancements_folder_explorer")
