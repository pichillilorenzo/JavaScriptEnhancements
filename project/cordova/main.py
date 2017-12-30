import sublime, sublime_plugin
import os, webbrowser, shlex, json, collections

def cordova_ask_custom_path(project_path, type):
    sublime.active_window().show_input_panel("Cordova custom path", "cordova", lambda cordova_custom_path: cordova_prepare_project(project_path, shlex.quote(cordova_custom_path)) if type == "create_new_project" or type == "add_project_type" else add_cordova_settings(project_path, shlex.quote(cordova_custom_path)), None, None)

def add_cordova_settings(working_directory, cordova_custom_path):
  project_path = working_directory
  settings = get_project_settings()
  if settings :
    project_path = settings["project_dir_name"]

  flowconfig_file_path = os.path.join(project_path, ".flowconfig")
  with open(flowconfig_file_path, 'r+', encoding="utf-8") as file:
    content = file.read()
    content = content.replace("[ignore]", """[ignore]
<PROJECT_ROOT>/platforms/.*
<PROJECT_ROOT>/hooks/.*
<PROJECT_ROOT>/plugins/.*
<PROJECT_ROOT>/res/.*""")
    file.seek(0)
    file.truncate()
    file.write(content)

  PROJECT_SETTINGS_FOLDER_PATH = os.path.join(project_path, PROJECT_SETTINGS_FOLDER_NAME)

  default_config = json.loads(open(os.path.join(PROJECT_FOLDER, "cordova", "default_config.json")).read(), object_pairs_hook=collections.OrderedDict)
  default_config["working_directory"] = working_directory
  default_config["cli_custom_path"] = cordova_custom_path

  cordova_settings = os.path.join(PROJECT_SETTINGS_FOLDER_PATH, "cordova_settings.json")

  with open(cordova_settings, 'w+') as file:
    file.write(json.dumps(default_config, indent=2))

def cordova_prepare_project(project_path, cordova_custom_path):

  window = sublime.active_window()
  view = window.new_file() 

  if sublime.platform() in ("linux", "osx"): 
    open_project = (" && " + shlex.quote(sublime_executable_path()) + " " +shlex.quote(get_project_settings(project_path)["project_file_name"])) if not is_project_open(get_project_settings(project_path)["project_file_name"]) else ""
    args = {"cmd": "/bin/bash -l", "title": "Terminal", "cwd": project_path, "syntax": None, "keep_open": False} 
    view.run_command('terminal_view_activate', args=args)
    window.run_command("terminal_view_send_string", args={"string": cordova_custom_path+" create myApp com.example.hello HelloWorld && mv ./myApp/{.[!.],}* ./; rm -rf myApp" + open_project + "\n"})
  else:
    # windows
    pass

  add_cordova_settings(project_path, cordova_custom_path)

  #open_project_folder(get_project_settings(project_path)["project_file_name"])

Hook.add("cordova_after_create_new_project", cordova_ask_custom_path)
Hook.add("cordova_add_javascript_project_configuration", cordova_ask_custom_path)
Hook.add("cordova_add_javascript_project_type", cordova_ask_custom_path)

class enable_menu_cordovaEventListener(enable_menu_project_typeEventListener):
  project_type = "cordova"
  path = os.path.join(PROJECT_FOLDER, "cordova", "Main.sublime-menu")
  path_disabled = os.path.join(PROJECT_FOLDER, "cordova", "Main_disabled.sublime-menu")

class cordova_cliCommand(manage_cliCommand):

  cli = "cordova"
  custom_name = "cordova"
  settings_name = "cordova_settings"

  def prepare_command(self, **kwargs):

    if ":platform" in self.command:
      self.window.show_input_panel("Platform:", "", self.platform_on_done, None, None)
    else :
      self._run()

  def platform_on_done(self, platform):
    self.placeholders[":platform"] = shlex.quote(platform.strip())
    self.command = self.substitute_placeholders(self.command)
    self._run()

  def _run(self):
    try:
      self.command = {
        'run': lambda : self.command + self.settings["cordova_settings"]["platform_run_options"][self.command[2].replace('--', '')][self.command[1]],
        'compile': lambda : self.command + self.settings["cordova_settings"]["platform_compile_options"][self.command[2].replace('--', '')][self.command[1]],
        'build': lambda : self.command + self.settings["cordova_settings"]["platform_build_options"][self.command[2].replace('--', '')][self.command[1]],
        'serve': lambda : self.command + [self.settings["cordova_settings"]["serve_port"]]
      }[self.command[0]]()
    except KeyError as err:
      pass
    except Exception as err:
      print(traceback.format_exc())
      pass

    super(cordova_cliCommand, self)._run()

