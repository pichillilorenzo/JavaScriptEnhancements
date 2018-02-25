import sublime, sublime_plugin
import os
from .. import JavascriptEnhancementsEnableProjectTypeMenuEventListener

class JavascriptEnhancementsEnableFlowMenuEventListener(JavascriptEnhancementsEnableProjectTypeMenuEventListener, sublime_plugin.EventListener):
  path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Main.sublime-menu")
  path_disabled = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Main_disabled.sublime-menu")
