import sublime, sublime_plugin
import os, json
from ...libs import util
from ...libs import NodeJS

class JavascriptEnhancementsAddFlowDefinitionCommand(sublime_plugin.WindowCommand):

  flow_typed_searched_items = []

  def run(self, **kwargs):

    self.window.show_input_panel("Definition to search", "", lambda package_name: sublime.set_timeout_async(lambda: self.search(package_name)), None, None)

  def search(self, package_name):

    self.window.status_message("Searching for '" + package_name + "' definitions...")
    node = NodeJS(check_local=True)
    result = node.execute("flow-typed", command_args=["search", package_name], is_from_bin=True)

    if result[0]:
      lines = result[1].encode('ascii', errors='ignore').decode("utf-8").strip().split("\n")
      linesNotDecoded = result[1].strip().split("\n")
      found_definations_flag = False
      for i in range(0, len(lines)):
        line = lines[i].strip()
        lineNotDecoded = linesNotDecoded[i].strip()

        if found_definations_flag and line:
   
          item = lineNotDecoded.split(b'\xe2\x94\x82'.decode("utf-8"))
          for j in range(0, len(item)):
            item[j] = item[j].encode('ascii', errors='ignore').decode("utf-8").strip()

          self.flow_typed_searched_items += [[item[0] + " " + item[1], "Flow version supported: " + item[2]]]

        elif line.startswith("Name") and line.endswith("Flow Version"):
          found_definations_flag = True

      if len(self.flow_typed_searched_items) > 0:
        self.window.show_quick_panel(self.flow_typed_searched_items, lambda index: sublime.set_timeout_async(lambda: self.install_definition(index)), sublime.KEEP_OPEN_ON_FOCUS_LOST)
      else:
        self.window.status_message("No definitions found, sorry!")

  def install_definition(self, index):

    if index == -1:
      return
      
    settings = util.get_project_settings()
    if settings: 
      package = self.flow_typed_searched_items[index][0].rsplit(' ', 1)
      package_name = package[0].strip()
      version = package[1].strip()[1:]
      flow_bin_version = ""

      self.window.status_message("Installing definition '" + package_name + "@" + version + "'...")

      if settings["project_settings"]["flow_cli_custom_path"]:
        result = util.execute(settings["project_settings"]["flow_cli_custom_path"], command_args=["version", "--json"], chdir=settings["project_dir_name"])
        if result[0]:
          flow_bin_version = json.loads(result[1])["semver"]

      flow_cli = "flow"
      is_from_bin = True
      chdir = settings["project_dir_name"]
      use_node = True
      bin_path = ""

      if settings["project_settings"]["flow_cli_custom_path"]:
        flow_cli = os.path.basename(settings["project_settings"]["flow_cli_custom_path"])
        bin_path = os.path.dirname(settings["project_settings"]["flow_cli_custom_path"])
        is_from_bin = False
        use_node = False

      node = NodeJS(check_local=True)
      if not flow_bin_version:
        result = node.execute(flow_cli, command_args=["version", "--json"], is_from_bin=is_from_bin, chdir=chdir, bin_path=bin_path, use_node=use_node)
        if result[0]:
          flow_bin_version = json.loads(result[1])["semver"]

      if flow_bin_version:
        # example: flow-typed install -f 0.62.0 express@4.x.x
        result = node.execute("flow-typed", command_args=["install", "-f", flow_bin_version, package_name+"@"+version], is_from_bin=True, chdir=chdir)

        if result[0]:
          self.window.status_message("Defintion '" + package_name + "@" + version + "' installed successfully!")
        else:
          print(result)
          self.window.status_message("Can't install '" + package_name + "@" + version + "' definition! Something went wrong, sorry!")

      else:
        print(result)
        self.window.status_message("Can't install '" + package_name + "@" + version + "' definition! Something went wrong, sorry!")

    else:
      sublime.error_message("Error: can't get project settings")

  def is_enabled(self):
    return util.is_javascript_project()

  def is_visible(self):
    return util.is_javascript_project()
