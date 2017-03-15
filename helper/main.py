import sublime, sublime_plugin
import json, os, re, webbrowser, cgi, threading, shutil
import util.main as Util
from util.animation_loader import AnimationLoader
from util.repeated_timer import RepeatedTimer
from distutils.version import LooseVersion

HELPER_FOLDER_NAME = "helper"
HELPER_FOLDER = os.path.join(PACKAGE_PATH, HELPER_FOLDER_NAME)

${include SocketCallUI.py}

${include surround_with_command.py}

${include delete_surrounded_command.py}

${include sort_array_command.py}

${include create_class_from_object_literal_command.py}
      
${include split_string_lines_to_variable_command.py}

${include add_type_any_paramater_command.py}

${include javascript_completions/main.py}

${include evaluate_javascript/main.py}

${include structure_javascript/structure_javascript.py}

${include bookmarks/main.py}

if int(sublime.version()) >= 3124 :

  ${include can_i_use/can_i_use_command.py}

