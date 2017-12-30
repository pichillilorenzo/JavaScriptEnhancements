import sublime, sublime_plugin
import os, webbrowser, shlex, json

def yeoman_prepare_project(project_path, type):

  window = sublime.active_window()
  view = window.new_file() 

  if sublime.platform() in ("linux", "osx"): 
    open_project = (" && " + shlex.quote(sublime_executable_path()) + " " +shlex.quote(get_project_settings(project_path)["project_file_name"])) if not is_project_open(get_project_settings(project_path)["project_file_name"]) else ""
    args = {"cmd": "/bin/bash -l", "title": "Terminal", "cwd": project_path, "syntax": None, "keep_open": False} 
    view.run_command('terminal_view_activate', args=args)
    window.run_command("terminal_view_send_string", args={"string": "yo" + open_project + "\n"})
  else:
    # windows
    pass

Hook.add("yeoman_after_create_new_project", yeoman_prepare_project)

