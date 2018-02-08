class enable_menu_npmEventListener(enable_menu_project_typeEventListener):
  path = os.path.join(PROJECT_FOLDER, "npm", "Main.sublime-menu")
  path_disabled = os.path.join(PROJECT_FOLDER, "npm", "Main_disabled.sublime-menu")

  def on_activated(self, view):
    super(enable_menu_npmEventListener, self).on_activated(view)

    default_value = [
      {
        "caption": "Tools",
        "id": "tools",
        "children": [
          {
            "caption": "Npm/Yarn Scripts",
            "id": "npm_scripts",
            "children":[]
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
              if item2["id"] == "npm_scripts" :
                item2["children"] = []
                npm_scripts = item2["children"]
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
                  "command": ["run", script]
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

  isNpm = True

  def prepare_command(self, **kwargs):

    self._run()

  def is_enabled(self):
    settings = get_project_settings()
    return True if settings and os.path.isfile( os.path.join(settings["project_dir_name"], "package.json") ) else False

  def is_visible(self):
    settings = get_project_settings()
    return True if settings and os.path.isfile( os.path.join(settings["project_dir_name"], "package.json") ) else False
