import sublime, sublime_plugin
import os, shlex

PROJECT_FOLDER_NAME = "project"
PROJECT_FOLDER = os.path.join(PACKAGE_PATH, PROJECT_FOLDER_NAME)
socket_server_list = dict()

def call_ui(client_file, host, port) :
  from node.main import NodeJS
  node = NodeJS()
  return Util.create_and_start_thread(node.execute, client_file, ("electron", [client_file], True))

def is_javascript_project():
  project_file_name = sublime.active_window().project_file_name()
  if project_file_name :
    project_folder = os.path.dirname(project_file_name)
    settings_dir_name = os.path.join(project_folder, ".jc-project-settings")
    return os.path.isdir(settings_dir_name)
  else :
    # try to look at window.folders()
    folder = sublime.active_window().folders()
    if len(folder) > 0:
      folder = folder[0]
      settings_dir_name = os.path.join(folder, ".jc-project-settings")
      return os.path.isdir(settings_dir_name)
  return False
  
def get_project_settings():

  project_settings = dict()

  project_file_name = sublime.active_window().project_file_name()
  project_folder = ""
  settings_dir_name = ""
  if project_file_name :
    project_folder = os.path.dirname(project_file_name)
    settings_dir_name = os.path.join(project_folder, ".jc-project-settings")
  else :
    # try to look at window.folders()
    folder = sublime.active_window().folders()
    if len(folder) > 0:
      project_folder = folder[0]
      project_file_name = os.path.basename(project_folder)
      settings_dir_name = os.path.join(project_folder, ".jc-project-settings")
      if not os.path.isdir(settings_dir_name) :
        return dict()
    else :
      return dict()
        
  project_settings["project_file_name"] = project_file_name
  project_settings["project_dir_name"] = os.path.dirname(project_file_name)
  project_settings["settings_dir_name"] = settings_dir_name
  settings_file = ["project_details.json", "flow_settings.json"]
  for setting_file in settings_file :
    with open(os.path.join(settings_dir_name, setting_file), encoding="utf-8") as file :
      key = os.path.splitext(setting_file)[0]
      project_settings[key] = json.loads(file.read(), encoding="utf-8")

  return project_settings

${include SocketCallUI.py}

${include structure_javascript/structure_javascript.py}

${include create_new_project/create_new_project.py}

${include edit_project/edit_project.py}

${include close_all_servers_and_flow_event_listener.py}
