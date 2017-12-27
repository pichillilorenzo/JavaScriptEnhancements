import sublime, sublime_plugin
import subprocess, shutil, traceback, os, json

class create_new_projectCommand(sublime_plugin.WindowCommand):
  project_type = None

  def run(self, *args):

    self.window.show_quick_panel(PROJECT_TYPE_SUPPORTED, self.project_type_selected)

  def project_type_selected(self, index):

    self.project_type = PROJECT_TYPE_SUPPORTED[index]
    self.window.show_input_panel("Project Path:", "", self.project_path_on_done, None, None)

  def project_path_on_done(self, path):

    path = path.strip()

    if not os.path.isdir(path):
      os.makedirs(path)

    Hook.apply(self.project_type+"_create_new_project", path)

    os.makedirs(os.path.join(path, PROJECT_SETTINGS_FOLDER_NAME))

    PROJECT_SETTINGS_FOLDER_PATH = os.path.join(path, PROJECT_SETTINGS_FOLDER_NAME)

    default_config = json.loads(open(os.path.join(PROJECT_FOLDER, "create_new_project", "default_config.json")).read())
    
    sublime_project_file_path = os.path.join(path, ".sublime-project")
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

    node = NodeJS()
    result = node.execute("flow", ["init"], is_from_bin=True, chdir=path)
    if not result[0]:
      sublime.error_message("Cannot init flow.")
    else:
      with open(flowconfig_file_path, 'r+', encoding="utf-8") as file:
        content = file.read()
        content = content.replace("[ignore]", """[ignore]
<PROJECT_ROOT>/node_modules/.*
<PROJECT_ROOT>/bower_components/.*""")
        file.seek(0)
        file.truncate()
        file.write(content)
      

    Hook.apply(self.project_type+"_after_create_new_project", path)
    Hook.apply("after_create_new_project", path)

