import sublime, sublime_plugin
from ..libs.global_vars import *
from ..libs import javaScriptEnhancements

class JavascriptEnhancementsEnableKeymapEventListener(sublime_plugin.EventListener):

  def on_text_command(self, view, command_name, args):

    if command_name in KEYMAP_COMMANDS and not javaScriptEnhancements.get("enable_keymap"):
      return ("noop", {})