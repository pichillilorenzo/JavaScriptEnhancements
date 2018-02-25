import sublime, sublime_plugin
from ...libs import util

class JavascriptEnhancementsBuildFlowOnSaveEventListener(sublime_plugin.EventListener):

  def on_post_save_async(self, view):
    settings = util.get_project_settings()
    if util.selection_in_js_scope(view) and settings and settings["project_settings"]["build_flow"]["on_save"] and len(settings["project_settings"]["build_flow"]["source_folders"]) > 0 and settings["project_settings"]["build_flow"]["destination_folder"] :
      view.window().run_command("javascript_enhancements_build_flow", args={"command": ["flow-remove-types", ":source_folders", "--out-dir", ":destination_folder"]})
