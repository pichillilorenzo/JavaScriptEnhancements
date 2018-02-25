import sublime, sublime_plugin
from ..libs.popup_manager import popup_manager

class javascript_enhancements_can_i_use_hide_popupEventListener(sublime_plugin.EventListener):
  def on_selection_modified_async(self, view) :
    if popup_manager.is_visible("javascript_enhancements_can_i_use") :
      view.hide_popup()