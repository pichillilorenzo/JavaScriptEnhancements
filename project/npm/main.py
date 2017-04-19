class enable_menu_npmEventListener(enable_menu_project_typeEventListener):
  path = os.path.join(PROJECT_FOLDER, "npm", "Main.sublime-menu")
  path_disabled = os.path.join(PROJECT_FOLDER, "npm", "Main_disabled.sublime-menu")

  def on_activated_async(self, view):
    super(enable_menu_npmEventListener, self).on_activated_async(view)

    default_value = [
      {
        "caption": "Tools",
        "id": "tools",
        "children": [
          {
            "caption": "Npm/Yarn",
            "id": "npm",
            "children":[
              {
                "caption": "Scripts",
                "id": "npm_scripts",
                "children": []
              },
              {
                "caption": "Install All",
                "command": "manage_npm_package",
                "args": {
                  "command_with_options": ["install", ":save-mode"],
                  "output_panel_name": "panel_install_all_npm_script",
                  "hide_panel_on_success": True
                }
              },
              {
                "caption": "Update All",
                "command": "manage_npm_package",
                "args": {
                  "command_with_options": ["update", ":save-mode"],
                  "output_panel_name": "panel_update_all_npm_script",
                  "hide_panel_on_success": True
                }
              },
              {
                "caption": "Install Package",
                "command": "manage_npm_package",
                "args": {
                  "command_with_options": ["install", ":save-mode", ":package"],
                  "status_message_before": "installing :package...",
                  "output_panel_name": "panel_install_package_npm_script",
                  "hide_panel_on_success": True
                }
              },
              {
                "caption": "Uninstall Package",
                "command": "manage_npm_package",
                "args": {
                  "command_with_options": ["uninstall", ":save-mode", ":package"],
                  "status_message_before": "uninstalling :package...",
                  "output_panel_name": "panel_uninstall_package_npm_script",
                  "hide_panel_on_success": True
                }
              },
              {
                "caption": "Update Package",
                "command": "manage_npm_package",
                "args": {
                  "command_with_options": ["update", ":save-mode", ":package"],
                  "status_message_before": "updating :package...",
                  "output_panel_name": "panel_update_package_npm_script",
                  "hide_panel_on_success": True
                }
              }
            ]
          }
        ]
      }
    ]

    if os.path.isfile(self.path) :
      with open(self.path, 'r+') as menu:
        content = menu.read()
        menu.seek(0)
        menu.write(json.dumps(default_value))
        menu.truncate()
        json_data = json.loads(content)
        npm_scripts = None
        for item in json_data :
          if item["id"] == "tools" :
            for item2 in item["children"] :
              if item2["id"] == "npm" :
                for item3 in item2["children"] :
                  if "id" in item3 and item3["id"] == "npm_scripts" :
                    item3["children"] = []
                    npm_scripts = item3["children"]
                break
            break
        if npm_scripts == None :
          return 
        try:
          npm = NPM(check_local=True)
          package_json = npm.getPackageJson()
          if package_json and "scripts" in package_json and len(package_json["scripts"].keys()) > 0 :
            for script in package_json["scripts"].keys():
              npm_scripts.append({
                "caption": script,
                "command": "manage_npm",
                "args": {
                  "command_with_options": ["run", script],
                  "output_panel_name": "panel_"+script+"_npm_script",
                  "hide_panel_on_success": True,
                  "ask_custom_options": True
                }
              })
            menu.seek(0)
            menu.write(json.dumps(json_data))
            menu.truncate()
        except Exception as e:
          print(traceback.format_exc())
          menu.seek(0)
          menu.write(json.dumps(default_value))
          menu.truncate()

    if os.path.isfile(self.path_disabled) :
      with open(self.path_disabled, 'w+') as menu:
        menu.write(json.dumps(default_value))

class manage_npmCommand(manage_cliCommand):
  is_node = False
  is_npm = True

  def is_enabled(self):
    settings = get_project_settings()
    return True if settings and os.path.isfile( os.path.join(settings["project_dir_name"], "package.json") ) else False

  def is_visible(self):
    settings = get_project_settings()
    return True if settings and os.path.isfile( os.path.join(settings["project_dir_name"], "package.json") ) else False

class manage_npm_packageCommand(manage_npmCommand):

  def run(self, **kwargs):
    if ":save-mode" in kwargs["command_with_options"]:
      self.window.show_input_panel("Save mode: ", "--save", lambda save_mode="": self.set_save_mode(save_mode.strip(), **kwargs), None, None)
    else :
      self.set_save_mode('', **kwargs)

  def set_save_mode(self, save_mode, **kwargs) :
    self.placeholders[":save-mode"] = save_mode
    if kwargs.get("command_with_options") :
      if ":package" in kwargs["command_with_options"]:
        self.window.show_input_panel("Package name: ", "", lambda package_name="": self.set_package_name(package_name.strip(), **kwargs), None, None)
        return
    super(manage_npm_packageCommand, self).run(**kwargs)

  def set_package_name(self, package_name, **kwargs):
    self.placeholders[":package"] = package_name
    super(manage_npm_packageCommand, self).run(**kwargs)