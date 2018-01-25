import sublime, sublime_plugin

class enableKeymap(sublime_plugin.EventListener):

  def on_text_command(self, view, command_name, args):

    if command_name in KEYMAP_COMMANDS and not javascriptCompletions.get("enable_keymap"):
      return ("noop", {})