import sublime, sublime_plugin
import os, json, traceback
from ....libs import NPM
from ... import JavascriptEnhancementsEnableProjectTypeMenuEventListener

class JavascriptEnhancementsEnableNpmMenuEventListener(JavascriptEnhancementsEnableProjectTypeMenuEventListener, sublime_plugin.EventListener):
  path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Main.sublime-menu")
  path_disabled = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Main_disabled.sublime-menu")

  def on_activated(self, view):
    super(JavascriptEnhancementsEnableNpmMenuEventListener, self).on_activated(view)

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
      with open(self.path, 'r+', encoding="utf-8") as menu:
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
                "command": "javascript_enhancements_npm_cli",
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
      with open(self.path_disabled, 'w+', encoding="utf-8") as menu:
        menu.write(json.dumps(default_value))
