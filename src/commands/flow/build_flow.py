import sublime, sublime_plugin
import os, shlex, json, shutil
from ...libs import util
from ...libs import JavascriptEnhancementsExecuteOnTerminalCommand

class JavascriptEnhancementsBuildFlowCommand(JavascriptEnhancementsExecuteOnTerminalCommand, sublime_plugin.WindowCommand):

  is_node = True
  is_bin_path = True

  def prepare_command(self, **kwargs):

    # dest_folder = self.settings["project_settings"]["build_flow"]["destination_folder"]

    # if os.path.isabs(dest_folder):
    #   shutil.rmtree(dest_folder)
    # elif os.path.exists(os.path.join(self.settings["project_dir_name"], dest_folder)):
    #   shutil.rmtree(os.path.join(self.settings["project_dir_name"], dest_folder))

    self.placeholders[":source_folders"] = " ".join(self.settings["project_settings"]["build_flow"]["source_folders"])
    self.placeholders[":destination_folder"] = self.settings["project_settings"]["build_flow"]["destination_folder"]
    self.command += self.settings["project_settings"]["build_flow"]["options"]
    self.command = self.substitute_placeholders(self.command)

    if self.settings["project_settings"]["flow_remove_types_custom_path"]:
      self.is_bin_path = False
      self.command[0] = shlex.quote(self.settings["project_settings"]["flow_remove_types_custom_path"]) if sublime.platform() != "windows" else self.settings["project_settings"]["flow_remove_types_custom_path"]

    self._run()

  def _run(self):
    super(JavascriptEnhancementsBuildFlowCommand, self)._run()

  def is_enabled(self) :
    settings = util.get_project_settings()
    if settings and len(settings["project_settings"]["build_flow"]["source_folders"]) > 0 and settings["project_settings"]["build_flow"]["destination_folder"] :
      return True
    return False