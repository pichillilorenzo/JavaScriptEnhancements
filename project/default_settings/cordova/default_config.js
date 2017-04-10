module.exports = {
  "project_details": {
    "type": ["cordova"]
  },
  "flow_settings": {
    "ignore": [
      "<PROJECT_ROOT>/platforms/.*",
      "<PROJECT_ROOT>/hooks/.*",
      "<PROJECT_ROOT>/plugins/.*",
      "<PROJECT_ROOT>/node_modules/.*"
    ],
    "include": [
    
    ],
    "libs":[
      ":PACKAGE_PATH/flow/libs/cordova/cordova.js"
    ]
  },
  "cordova_settings": {
    "serve_port": "",
    "cli_global_options": [],
    "cli_compile_options": [],
    "cli_build_options": [],
    "cli_run_options": [],
    "installed_platform": [],
    "platform_version_options": {},
    "platform_compile_options": {
      "debug": {},
      "release": {}
    },
    "platform_build_options": {
      "debug": {},
      "release": {}
    },
    "platform_run_options": {
      "debug": {},
      "release": {}
    },
    "use_local_cli": false,
    "package_json": {},
    "cli_custom_path": ""
  }
}