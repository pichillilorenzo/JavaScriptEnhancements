import sublime, sublime_plugin

class PopupManager():

  popup_types = {}

  def getVisible(self):
    for k, v in self.popup_types.items():
      if v["visible"]:
        return k
        
  def setVisible(self, popup_type, visible):
    self.popup_types[popup_type]["visible"] = visible

  def isVisible(self, popup_type):
    return self.popup_types[popup_type]["visible"]

  def register(self, popup_type):
    self.popup_types[popup_type] = {
      "visible": False
    }

  def unregister(self, popup_type):
    del self.popup_types[popup_type]

popupManager = PopupManager()
popupManager.register("hint_parameters")
popupManager.register("flow_error")
popupManager.register("can_i_use")
