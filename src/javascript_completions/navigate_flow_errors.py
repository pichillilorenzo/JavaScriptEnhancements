import sublime, sublime_plugin

class navigate_flow_errorsCommand(navigate_regionsCommand, sublime_plugin.TextCommand):

  region_key = "flow_error"