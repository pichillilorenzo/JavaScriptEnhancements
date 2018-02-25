import sublime, sublime_plugin
import os
from ... import JavascriptEnhancementsEnableProjectTypeMenuEventListener

class JavascriptEnhancementsEnableAngularv1MenuEventListener(JavascriptEnhancementsEnableProjectTypeMenuEventListener, sublime_plugin.EventListener):
  project_type = "angularv1"
  path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Main.sublime-menu")
  path_disabled = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Main_disabled.sublime-menu")