import sublime, sublime_plugin
import os, shlex

def call_ui(client_file, host, port) :
  from node.main import NodeJS
  node = NodeJS()
  return Util.create_and_start_thread(node.execute, client_file, ("electron", [client_file], True))

def is_javascript_project():
  project_file_name = sublime.active_window().project_file_name()
  project_dir_name = ""
  if project_file_name :
    project_dir_name = os.path.dirname(project_file_name)
    settings_dir_name = os.path.join(project_dir_name, ".jc-project-settings")
    return os.path.isdir(settings_dir_name)
  else :
    # try to look at window.folders()
    folder = sublime.active_window().folders()   
    if len(folder) > 0:
      folder = folder[0]
      settings_dir_name = os.path.join(folder, ".jc-project-settings")
      return os.path.isdir(settings_dir_name)
  return False

def is_type_javascript_project(type):
  settings = get_project_settings()
  return True if settings and type in settings["project_details"]["type"] else False

def is_project_view(view) :
  settings = get_project_settings()
  if settings :
    return view.file_name() and view.file_name().startswith(settings["project_dir_name"])
  return False

def get_project_settings():

  project_settings = dict()

  project_file_name = sublime.active_window().project_file_name()
  project_dir_name = ""
  settings_dir_name = ""
  if project_file_name :
    project_dir_name = os.path.dirname(project_file_name)
    settings_dir_name = os.path.join(project_dir_name, ".jc-project-settings")
    if not os.path.isdir(settings_dir_name) :
      return dict()
  else :
    # try to look at window.folders()
    folder = sublime.active_window().folders()
    if len(folder) > 0:
      project_dir_name = folder[0]
      for file in os.listdir(project_dir_name) :
        if file.endswith(".sublime-project") :
          project_file_name = os.path.join(project_dir_name, file)
          break
      settings_dir_name = os.path.join(project_dir_name, ".jc-project-settings")
      if not os.path.isdir(settings_dir_name) :
        return dict()
    else :
      return dict()
        
  project_settings["project_file_name"] = project_file_name
  project_settings["project_dir_name"] = project_dir_name
  project_settings["settings_dir_name"] = settings_dir_name
  settings_file = ["project_details.json", "flow_settings.json"]
  for setting_file in settings_file :
    with open(os.path.join(settings_dir_name, setting_file), encoding="utf-8") as file :
      key = os.path.splitext(setting_file)[0]
      project_settings[key] = json.loads(file.read(), encoding="utf-8")
    if setting_file == "project_details.json" :
      for project_type in project_settings["project_details"]["type"]:
        with open(os.path.join(settings_dir_name, project_type+"_settings.json"), encoding="utf-8") as file :
          project_settings[project_type+"_settings"] = json.loads(file.read(), encoding="utf-8")

  return project_settings

def save_project_setting(setting_file, data):
  settings = get_project_settings()
  if settings :
    with open(os.path.join(settings["settings_dir_name"], setting_file), 'w+', encoding="utf-8") as file :
      file.write(json.dumps(data, indent=2))

def save_project_flowconfig(flow_settings):
  settings = get_project_settings()
  if settings :
    with open(os.path.join(settings["settings_dir_name"], "flow_settings.json"), 'w+', encoding="utf-8") as file :
      file.write(json.dumps(flow_settings, indent=2))
    with open(os.path.join(settings["project_dir_name"], ".flowconfig"), 'w+', encoding="utf-8") as file :
      include = "\n".join(flow_settings["include"])
      ignore = "\n".join(flow_settings["ignore"])
      libs = "\n".join(flow_settings["libs"])
      options = "\n".join(list(map(lambda item: item[0].strip()+"="+item[1].strip(), flow_settings["options"])))

      data = "[ignore]\n{ignore}\n[include]\n{include}\n[libs]\n{libs}\n[options]\n{options}".format(ignore=ignore, include=include, libs=libs, options=options)
      file.write(data.replace(':PACKAGE_PATH', PACKAGE_PATH))

${include create_new_project/create_new_project.py}

${include edit_project/edit_project.py}

${include close_all_servers_and_flow_event_listener.py}

${include manage_cliCommand.py}

## Cordova ##
${include cordova/main.py}