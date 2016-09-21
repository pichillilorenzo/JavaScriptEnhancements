import sublime
import platform
import os

PACKAGE_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

PLATFORM_ARCHITECTURE = "64bit" if platform.architecture()[0] == "64bit" else "32bit"

NODE_JS_VERSION = "v6.6.0" # Default value
NODE_JS_BINARIES_FOLDER_NAME = "node_binaries"
NODE_JS_VERSION_URL_LIST_ONLINE = "https://nodejs.org/dist/index.json"
NODE_JS_BINARIES_FOLDER = os.path.join(PACKAGE_PATH, NODE_JS_BINARIES_FOLDER_NAME)
NODE_JS_BINARIES_FOLDER_PLATFORM = os.path.join(NODE_JS_BINARIES_FOLDER, sublime.platform() + "-" + PLATFORM_ARCHITECTURE)
os_switcher = {"osx": "darwin", "linux": "linux", "windows": "win"}
NODE_JS_OS = os_switcher.get(sublime.platform())
NODE_JS_ARCHITECTURE = "x64" if PLATFORM_ARCHITECTURE == "64bit" else "x86"
NODE_JS_BINARY_NAME = "node" if NODE_JS_OS != 'win' else "node.exe"
NODE_JS_PATH_EXECUTABLE = os.path.join(NODE_JS_BINARIES_FOLDER_PLATFORM, NODE_JS_BINARY_NAME)
