import sublime, sublime_plugin
import os
from ... import JavascriptEnhancementsEnableProjectTypeMenuEventListener

class JavascriptEnhancementsEnableIonicv1MenuEventListener(JavascriptEnhancementsEnableProjectTypeMenuEventListener, sublime_plugin.EventListener):
  project_type = "ionicv1"
  path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Main.sublime-menu")
  path_disabled = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Main_disabled.sublime-menu")