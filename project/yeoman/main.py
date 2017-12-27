import sublime, sublime_plugin
import os, webbrowser, shlex, json

def yeoman_prepare_project(project_path):
  open_project_folder(project_path)
  window = sublime.active_window()
  view = window.new_file() 

  if sublime.platform() in ("linux", "osx"): 
    args = {"cmd": "/bin/bash -l", "title": "Terminal", "cwd": project_path, "syntax": None, "keep_open": False} 
    view.run_command('terminal_view_activate', args=args)
    window.run_command("terminal_view_send_string", args={"string": "yo\n"})
  else:
    # windows
    pass

Hook.add("yeoman_after_create_new_project", yeoman_prepare_project)

