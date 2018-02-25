import sublime, sublime_plugin
import os, json, shlex, collections
from ...libs.global_vars import *
from ...libs import util
from ...libs import Hook
from ...libs import NodeJS

class JavascriptEnhancementsCreateNewProjectCommand(sublime_plugin.WindowCommand):
  project_type = None

  def run(self, **kwargs):

    self.window.show_quick_panel(PROJECT_TYPE_SUPPORTED, self.project_type_selected)

  def project_type_selected(self, index):

    if index == -1:
      return
      
    self.project_type = PROJECT_TYPE_SUPPORTED[index][1]

    self.window.show_input_panel("Project Path:", os.path.expanduser("~")+os.path.sep, self.project_path_on_done, None, None)

  def project_path_on_done(self, path):

    path = path.strip()

    if os.path.isdir(os.path.join(path, PROJECT_SETTINGS_FOLDER_NAME)):
      sublime.error_message("Can't create the project. There is already another project in "+path+".")
      return

    if not os.path.isdir(path):
      if sublime.ok_cancel_dialog("The path \""+path+"\" doesn't exists.\n\nDo you want create it?", "Yes"):
        os.makedirs(path)
      else:
        return

    Hook.apply("create_new_project", path)
    Hook.apply(self.project_type+"_create_new_project", path)

    os.makedirs(os.path.join(path, PROJECT_SETTINGS_FOLDER_NAME))

    PROJECT_SETTINGS_FOLDER_PATH = os.path.join(path, PROJECT_SETTINGS_FOLDER_NAME)

    default_config = json.loads(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "default_config.json")).read(), object_pairs_hook=collections.OrderedDict)
    
    sublime_project_file_path = os.path.join(path, os.path.basename(path)+".sublime-project")
    package_json_file_path = os.path.join(path, "package.json")
    flowconfig_file_path = os.path.join(path, ".flowconfig")
    bookmarks_path = os.path.join(PROJECT_SETTINGS_FOLDER_PATH, "bookmarks.json")
    project_details_file = os.path.join(PROJECT_SETTINGS_FOLDER_PATH, "project_details.json")
    project_settings = os.path.join(PROJECT_SETTINGS_FOLDER_PATH, "project_settings.json")

    if not os.path.exists(sublime_project_file_path) :
      with open(sublime_project_file_path, 'w+', encoding="utf-8") as file:
        file.write(json.dumps(default_config["sublime_project"], indent=2))

    if ( self.project_type == "empty" or self.project_type == "cordova" ) and not os.path.exists(package_json_file_path) :
      with open(package_json_file_path, 'w+', encoding="utf-8") as file:
        file.write(json.dumps(default_config["package_json"], indent=2))

    with open(bookmarks_path, 'w+', encoding="utf-8") as file:
      file.write(json.dumps(default_config["bookmarks"], indent=2))
    with open(project_details_file, 'w+', encoding="utf-8") as file:
      file.write(json.dumps(default_config["project_details"], indent=2))
    with open(project_settings, 'w+', encoding="utf-8") as file:
      file.write(json.dumps(default_config["project_settings"], indent=2))

    if not os.path.exists(flowconfig_file_path) :
      node = NodeJS(check_local=True)
      result = node.execute("flow", ["init"], is_from_bin=True, chdir=path)
      if not result[0]:
        sublime.error_message("Can't initialize flow. Error: " + result[1])
      else:
        with open(flowconfig_file_path, 'r+', encoding="utf-8") as file:
          content = file.read()
          content = content.replace("[ignore]", """[ignore]
<PROJECT_ROOT>/"""+PROJECT_SETTINGS_FOLDER_NAME+"""/.*""")
          file.seek(0)
          file.truncate()
          file.write(content)

    Hook.apply(self.project_type+"_after_create_new_project", path, "create_new_project")
    Hook.apply("after_create_new_project", path, "create_new_project")

    if self.project_type == "empty":
      util.open_project_folder(util.get_project_settings(path)["project_file_name"])
