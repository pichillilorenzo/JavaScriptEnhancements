module.exports = {
  "project_details": {
    "type": ["ionic"]
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
  "ionic_settings": {
    "working_directory": "",
    "cli_global_options": [],
    "cli_compile_options": [],
    "cli_platform_options": [],
    "cli_build_options": [],
    "cli_emulate_options": [],
    "cli_run_options": [],
    "cli_serve_options": [],
    "cli_resources_options": [],
    "cli_state_options": [],
    "installed_platform": [],
    "platform_version_options": {},
    "platform_emulate_options": {
      "debug": {},
      "release": {}
    },
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