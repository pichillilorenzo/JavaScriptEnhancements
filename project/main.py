import sublime, sublime_plugin
import os, shlex

PROJECT_FOLDER_NAME = "project"
PROJECT_FOLDER = os.path.join(PACKAGE_PATH, PROJECT_FOLDER_NAME)
socket_server_list = dict()

def call_ui(client_file, host, port) :
  # PYTHON_PATH = main_settings_json["python_path"]
  # if platform.system() == 'Windows' :
  #   args = [PYTHON_PATH, client_file, host, str(port)]
  # else :
  #   args = shlex.quote(PYTHON_PATH)+" "+shlex.quote(client_file)+" "+shlex.quote(host)+" "+shlex.quote(str(port))

  # return subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  from node.main import NodeJS
  node = NodeJS()
  return Util.create_and_start_thread(node.execute, client_file, ("electron", [client_file], True))

def test_python():
  PYTHON_PATH = main_settings_json["python_path"]
  if platform.system() == 'Windows' :
    args = [PYTHON_PATH, "--version"]
  else :
    args = shlex.quote(PYTHON_PATH)+" --version"

  try :
    output = subprocess.check_output(args, shell=True, stderr=subprocess.STDOUT).decode("utf-8", "ignore").strip()
    if output.startswith("Python 3") :
      return True
  except :
    pass
  return False

def is_javascript_project():
  project_file_name = sublime.active_window().project_file_name()
  if project_file_name :
    project_folder = os.path.dirname(project_file_name)
    settings_dir_name = os.path.join(project_folder, ".jc-project-settings")
    return os.path.isdir(settings_dir_name)
  return False
  
def get_project_settings():

  project_settings = dict()

  project_file_name = sublime.active_window().project_file_name()
  if project_file_name :
    project_folder = os.path.dirname(project_file_name)
    settings_dir_name = os.path.join(project_folder, ".jc-project-settings")
    if os.path.isdir(settings_dir_name) :
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
