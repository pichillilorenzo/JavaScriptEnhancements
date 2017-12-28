import sublime, sublime_plugin
import os, shlex, collections

PROJECT_SETTINGS_FOLDER_NAME = ".je-project-settings"

def open_project_folder(project):
  
  if not is_project_open(project) :
    subl(["--project", project])

def is_project_open(project): 

  project_folder_to_find = os.path.dirname(project)

  windows = sublime.windows()

  for window in windows :

    project_file_name = sublime.active_window().project_file_name()

    if project_file_name :
      project_folder = os.path.dirname(project_file_name)

      return True if project_folder == project_folder_to_find else False

    else :
      # try to look at window.folders()
      folders = window.folders()   
      if len(folders) > 0:

        project_folder = folders[0]

        return True if project_folder == project_folder_to_find else False

  return False
  
def is_javascript_project():
  project_file_name = sublime.active_window().project_file_name()
  project_dir_name = ""
  if project_file_name :
    project_dir_name = os.path.dirname(project_file_name)
    settings_dir_name = os.path.join(project_dir_name, PROJECT_SETTINGS_FOLDER_NAME)
    return os.path.isdir(settings_dir_name)
  else :
    # try to look at window.folders()
    folders = sublime.active_window().folders()   
    if len(folders) > 0:
      folders = folders[0]
      settings_dir_name = os.path.join(folders, PROJECT_SETTINGS_FOLDER_NAME)
      return os.path.isdir(settings_dir_name)
  return False

def is_type_javascript_project(type):
  settings = get_project_settings()
  return True if settings and os.path.exists(os.path.join(settings["settings_dir_name"], type+"_settings.json")) else False

def is_project_view(view) :
  settings = get_project_settings()
  if settings :
    return view.file_name() and view.file_name().startswith(settings["project_dir_name"])
  return False

def get_project_settings(project_dir_name = ""):

  project_settings = dict()

  project_file_name = sublime.active_window().project_file_name() if not project_dir_name else ""
  settings_dir_name = ""

  if not project_dir_name :

    if project_file_name :
      project_dir_name = os.path.dirname(project_file_name)
    else :
      # try to look at window.folders()
      folders = sublime.active_window().folders()
      if len(folders) > 0:
        project_dir_name = folders[0]

  if not project_dir_name :
    return dict()

  if project_file_name :
    settings_dir_name = os.path.join(project_dir_name, PROJECT_SETTINGS_FOLDER_NAME)
    if not os.path.isdir(settings_dir_name) :
      return dict()
  else :
    for file in os.listdir(project_dir_name) :
      if file.endswith(".sublime-project") :
        project_file_name = os.path.join(project_dir_name, file)
        break
    settings_dir_name = os.path.join(project_dir_name, PROJECT_SETTINGS_FOLDER_NAME)
    if not os.path.isdir(settings_dir_name) :
      return dict()
        
  project_settings["project_file_name"] = project_file_name
  project_settings["project_dir_name"] = project_dir_name
  project_settings["settings_dir_name"] = settings_dir_name
  settings_file = ["project_details.json", "project_settings.json"]
  for setting_file in os.listdir(project_settings["settings_dir_name"]) :
    with open(os.path.join(settings_dir_name, setting_file), encoding="utf-8") as file :
      key = os.path.splitext(setting_file)[0]
      project_settings[key] = json.loads(file.read(), encoding="utf-8", object_pairs_hook=collections.OrderedDict)
  
  return project_settings

def save_project_setting(setting_file, data):
  settings = get_project_settings()
  if settings :
    with open(os.path.join(settings["settings_dir_name"], setting_file), 'w+', encoding="utf-8") as file :
      file.write(json.dumps(data, indent=2))

${include manage_cli/main.py}

${include npm/main.py}

${include build_flow/main.py}

${include cordova/main.py}

${include ionicv1/main.py}

${include ionicv2/main.py}

${include angularv1/main.py}

${include angularv2/main.py}

${include react/main.py}

${include yeoman/main.py}

${include create_new_project/create_new_project.py}

${include close_flow_event_listener.py}
