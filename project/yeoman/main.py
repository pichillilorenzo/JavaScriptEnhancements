import sublime, sublime_plugin
import os, webbrowser, shlex, json

def yeoman_ask_custom_path(project_path, type):
    sublime.active_window().show_input_panel("Yeoman CLI custom path", "yo", lambda yeoman_custom_path: yeoman_prepare_project(project_path, yeoman_custom_path), None, None)

def yeoman_prepare_project(project_path, yeoman_custom_path):

  terminal = Terminal(cwd=project_path)
  
  if sublime.platform() != "windows": 
    open_project = ["&&", shlex.quote(sublime_executable_path()), shlex.quote(get_project_settings(project_path)["project_file_name"])] if not is_project_open(get_project_settings(project_path)["project_file_name"]) else []
    terminal.run([shlex.quote(yeoman_custom_path)] + open_project)
  else:
    open_project = [sublime_executable_path(), get_project_settings(project_path)["project_file_name"], "&&", "exit"] if not is_project_open(get_project_settings(project_path)["project_file_name"]) else []
    terminal.run([yeoman_custom_path])
    if open_project:
      terminal.run(open_project)

Hook.add("yeoman_after_create_new_project", yeoman_ask_custom_path)
Hook.add("yeoman_add_javascript_project_type", yeoman_ask_custom_path)