import re, webbrowser

def create_react_project_process(line, process, panel, project_data, sublime_project_file_name, open_project) :

  if line != None and panel:
    panel.run_command("print_panel_cli", {"line": line, "hide_panel_on_success": True})

  if line == "OUTPUT-SUCCESS":
    Util.move_content_to_parent_folder(os.path.join(project_data["react_settings"]["working_directory"], "temp"))
    
    if open_project :
      open_project_folder(sublime_project_file_name)

def create_react_project(json_data):
  project_data = json_data["project_data"]
  project_details = project_data["project_details"]
  project_folder = project_data["react_settings"]["working_directory"]
  create_options = []

  if "create_options" in project_data and project_data["create_options"]:
    create_options = project_data["create_options"]
    
  panel = Util.create_and_show_panel("react_panel_installer_project")

  node = NodeJS()

  Util.execute('git', ["clone", "--progress", "--depth=1", "https://github.com/react-boilerplate/react-boilerplate.git", "temp"], chdir=project_folder, wait_terminate=False, func_stdout=create_cordova_project_process, args_func_stdout=[panel, project_data, (project_data['project_file_name'] if "sublime_project_file_name" not in json_data else json_data["sublime_project_file_name"]), (False if "sublime_project_file_name" not in json_data else True) ])
  #node.execute('create-react-app', ["temp"] + create_options, is_from_bin=True, chdir=project_folder, wait_terminate=False, func_stdout=create_cordova_project_process, args_func_stdout=[panel, project_data, (project_data['project_file_name'] if "sublime_project_file_name" not in json_data else json_data["sublime_project_file_name"]), (False if "sublime_project_file_name" not in json_data else True) ])
    
  return json_data

Hook.add("react_create_new_project", create_react_project)

Hook.add("react_add_new_project_type", create_react_project)

class enable_menu_reactEventListener(enable_menu_project_typeEventListener):
  project_type = "react"
  path = os.path.join(PROJECT_FOLDER, "react", "Main.sublime-menu")
  path_disabled = os.path.join(PROJECT_FOLDER, "react", "Main_disabled.sublime-menu")

class manage_serve_reactCommand(manage_cliCommand):
  cli = "serve"
  name_cli = "Serve React"

  def process_communicate(self, line) :

    if line and "http://localhost" in line :
      pattern = re.compile("http\:\/\/localhost\:([0-9]+)")
      match = pattern.search(line)
      if match :
        port = match.group(1)
        url = "http://localhost:"+port
        webbrowser.open(url) 

  def is_enabled(self) :
    settings = get_project_settings()
    if os.path.isdir(os.path.join( settings["project_dir_name"], "build" )) :
      return True
    return False

  def is_visible(self) :
    settings = get_project_settings()
    if os.path.isdir(os.path.join( settings["project_dir_name"], "build" )) :
      return True
    return False
