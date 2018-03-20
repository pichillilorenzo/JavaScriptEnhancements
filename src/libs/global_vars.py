import os

PLUGIN_VERSION = "0.16.11"
DEVELOPER_MODE = False

PACKAGE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PACKAGE_NAME = os.path.basename(PACKAGE_PATH)
SUBLIME_PACKAGES_PATH = os.path.dirname(PACKAGE_PATH)

socket_server_list = dict()

SRC_FOLDER_NAME = "src"
SRC_FOLDER_PATH = os.path.join(PACKAGE_PATH, SRC_FOLDER_NAME)

WINDOWS_BATCH_FOLDER_PATH = os.path.join(PACKAGE_PATH, 'windows_batch')

IMG_FOLDER_NAME = "img"
IMG_FOLDER_PATH = os.path.join(PACKAGE_PATH, IMG_FOLDER_NAME)

PROJECT_TYPE_SUPPORTED = [
  ['Empty', 'empty'], 
  ['Angular v1', 'angularv1'], 
  ['Angular v2, v4, v5', 'angularv2'], 
  ['Cordova', 'cordova'], 
  ['Express', 'express'],
  ['Ionic v1', 'ionicv1'],
  ['Ionic v2, v3', 'ionicv2'],
  ['React', 'react'],
  ['React Native', 'react_native'],
  ['Yeoman', 'yeoman'],
  ['Vue', 'vue']
]

KEYMAP_COMMANDS = []

NODE_JS_EXEC = "node"
NPM_EXEC = "npm"
YARN_EXEC = "yarn"

NODE_MODULES_FOLDER_NAME = "node_modules"
NODE_MODULES_PATH = os.path.join(PACKAGE_PATH, NODE_MODULES_FOLDER_NAME)
NODE_MODULES_BIN_PATH = os.path.join(NODE_MODULES_PATH, ".bin")

PROJECT_SETTINGS_FOLDER_NAME = ".je-project-settings"

FLOW_DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flow")