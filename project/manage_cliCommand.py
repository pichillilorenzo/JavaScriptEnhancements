import sublime, sublime_plugin
import os

manage_cli_window_command_processes = {}

class send_input_to_cliCommand(sublime_plugin.TextCommand):
  last_output_panel_name = None
  window = None
  def run(self, edit, **args):
    self.window = self.view.window()
    self.last_output_panel_name = self.view.window().active_panel().replace("output.", "")
    sublime.set_timeout_async(lambda : self.window.show_input_panel("Input: ", "", self.send_input, None, None))

  def send_input(self, input) :
    global manage_cli_window_command_processes
    settings = get_project_settings()
    if self.window and self.last_output_panel_name and settings and settings["project_dir_name"]+"_"+self.last_output_panel_name in manage_cli_window_command_processes :
      process = manage_cli_window_command_processes[settings["project_dir_name"]+"_"+self.last_output_panel_name]["process"]
      process.stdin.write("{}\n".format(input).encode("utf-8"))
      process.stdin.flush()
      self.window.run_command("show_panel", {"panel": "output."+self.last_output_panel_name})

  def is_enabled(self):
    global manage_cli_window_command_processes
    self.window = self.view.window()
    self.last_output_panel_name = self.view.window().active_panel().replace("output.", "")
    settings = get_project_settings()
    return True if ( self.window and self.last_output_panel_name and settings and settings["project_dir_name"]+"_"+self.last_output_panel_name in manage_cli_window_command_processes ) else False
  
  def is_visible(self):
    global manage_cli_window_command_processes
    self.window = self.view.window()
    self.last_output_panel_name = self.view.window().active_panel().replace("output.", "")
    settings = get_project_settings()
    return True if ( self.window and self.last_output_panel_name and settings and settings["project_dir_name"]+"_"+self.last_output_panel_name in manage_cli_window_command_processes ) else False
  
class print_panel_cliCommand(sublime_plugin.TextCommand):
  def run(self, edit, **args):   
    line = args.get("line")
    if line.strip() :
      if line == "OUTPUT-SUCCESS":
        if self.view.window() and args.get("hide_panel_on_success") :
          sublime.set_timeout_async(self.hide_window_panel, args.get("wait_panel") if args.get("wait_panel") else 1000 )
        return
      elif line == "OUTPUT-ERROR" or line == "OUTPUT-DONE":
        return
      self.view.set_read_only(False)
      self.view.insert(edit, self.view.size(), line)
      self.view.show_at_center(self.view.size())
      self.view.set_read_only(True)

  def hide_window_panel(self):
    try :
      self.view.window().run_command("hide_panel")
    except AttributeError as e:
      pass

class enable_menu_cliViewEventListener(sublime_plugin.ViewEventListener):

  def on_activated_async(self, **kwargs):
    cli = kwargs.get("cli")
    path = kwargs.get("path")
    path_disabled = kwargs.get("path_disabled")
    if cli and path and path_disabled:
      if is_type_javascript_project(cli) :
        if os.path.isfile(path_disabled):
          os.rename(path_disabled, path)
      else :
        if os.path.isfile(path):
          os.rename(path, path_disabled)

class manage_cliCommand(sublime_plugin.WindowCommand):
  cli = ""
  name_cli = ""
  panel = None
  output_panel_name = "output_panel_cli"
  panel_command = "print_panel_cli"
  status_message_before = ""
  status_message_after_on_success = ""
  status_message_after_on_error = ""
  settings = {}
  command_with_options = []
  show_panel = True
  placeholders = {}
  hide_panel_on_success = True
  process = None
  is_stoppable = False
  stop_now = None
  command_stopped_text = "\n\nCommand Stopped\n\n"
  can_send_input = False

  def run(self, **kwargs):
    self.is_stoppable = kwargs.get("is_stoppable") if "is_stoppable" in kwargs else self.is_stoppable
    if self.is_stoppable and self.stop_process():
      return
    self.settings = get_project_settings()
    if self.settings:
      self.callback_after_get_settings(**kwargs)
      self.cli = kwargs.get("cli") if "cli" in kwargs else self.cli
      if not self.cli:
        raise Exception("'cli' field of the manage_cliCommand not defined.")

      self.command_with_options = self.substitute_placeholders(kwargs.get("command_with_options"))
      if not self.command_with_options or len(self.command_with_options) <= 0:
        raise Exception("'command_with_options' field of the manage_cliCommand not defined.")

      self.show_panel = kwargs.get("show_panel") if "show_panel" in kwargs != None else self.show_panel
      self.output_panel_name = self.substitute_placeholders( str(kwargs.get("output_panel_name") if "output_panel_name" in kwargs else self.output_panel_name) )
      self.status_message_before = self.substitute_placeholders( str(kwargs.get("status_message_before")) if "status_message_before" in kwargs else self.status_message_before )
      self.status_message_after_on_success = self.substitute_placeholders( str(kwargs.get("status_message_after_on_success")) if "status_message_after_on_success" in kwargs else self.status_message_after_on_success )
      self.status_message_after_on_error = self.substitute_placeholders( str(kwargs.get("status_message_after_on_error")) if "status_message_after_on_error" in kwargs else self.status_message_after_on_error )
      self.hide_panel_on_success = kwargs.get("hide_panel_on_success") if "hide_panel_on_success" in kwargs else self.hide_panel_on_success
      self.can_send_input = kwargs.get("can_send_input") if "can_send_input" in kwargs else self.can_send_input
      
      sublime.set_timeout_async(lambda: self.manage())
    else :
      sublime.error_message("Error: can't get project settings")

  def manage(self) :
    global manage_cli_window_command_processes

    if self.status_message_before :
      self.window.status_message(self.name_cli+": "+self.status_message_before)
    if self.show_panel :
      self.panel = self.window.create_output_panel(self.output_panel_name, False)
      self.panel.set_read_only(True)
      self.panel.set_syntax_file(os.path.join("Packages", "JavaScript Completions", "javascript_completions.sublime-syntax"))
      self.window.run_command("show_panel", {"panel": "output."+self.output_panel_name})
    self.command_with_options = self.command_with_options + self.append_args_execute()
    
    if self.is_stoppable and self.settings["project_dir_name"]+"_"+self.output_panel_name in manage_cli_window_command_processes:
      if (manage_cli_window_command_processes[self.settings["project_dir_name"]+"_"+self.output_panel_name]["process"].poll() == None) :
        self.stop_now = True
        self.process = manage_cli_window_command_processes[self.settings["project_dir_name"]+"_"+self.output_panel_name]["process"]
        del manage_cli_window_command_processes[self.settings["project_dir_name"]+"_"+self.output_panel_name]
        self.stop_process()
      else :
        del manage_cli_window_command_processes[self.settings["project_dir_name"]+"_"+self.output_panel_name]
      return

    self.before_execute()

    if ( self.can_execute() ) :
      node = NodeJS()
      node.execute(self.cli, self.command_with_options, is_from_bin=True, chdir=self.settings["project_dir_name"], wait_terminate=False, func_stdout=self.print_panel)
    
  def print_panel(self, line, process):
    global manage_cli_window_command_processes

    if not self.process :
      self.process = process

    self.process_communicate(line)

    if self.can_send_input :
      if not self.settings["project_dir_name"]+"_"+self.output_panel_name in manage_cli_window_command_processes :
        manage_cli_window_command_processes[self.settings["project_dir_name"]+"_"+self.output_panel_name] = {
          "process": self.process
        }

    if line != None and self.show_panel:
      self.panel.run_command(self.panel_command, {"line": line, "hide_panel_on_success": self.hide_panel_on_success})
  
    if line == "OUTPUT-SUCCESS" and self.status_message_after_on_success :
      self.window.status_message(self.name_cli+": "+self.status_message_after_on_success)

    if line == "OUTPUT-ERROR" and self.status_message_after_on_error :
      self.window.status_message(self.name_cli+": "+self.status_message_after_on_error)

    if line == "OUTPUT-SUCCESS" :
      self.on_success()

    if line == "OUTPUT-ERROR" :
      self.on_error()

    if line == "OUTPUT-DONE":
      self.process = None

      if self.can_send_input :
        if self.settings["project_dir_name"]+"_"+self.output_panel_name in manage_cli_window_command_processes :
          del manage_cli_window_command_processes[self.settings["project_dir_name"]+"_"+self.output_panel_name]

      self.on_done()

  def stop_process(self):
    if self.stop_now == None:
      self.stop_now = False
    elif self.stop_now == False and self.process != None:
      self.stop_now = True

    if self.stop_now:
      self.before_kill_process()
      self.process.terminate()
      self.process = None
      self.stop_now = None
      self.panel.run_command(self.panel_command, {"line": self.command_stopped_text})
      self.panel.run_command(self.panel_command, {"line": "OUTPUT-SUCCESS", "hide_panel_on_success": True, "wait_panel": 3000})
      self.after_killed_process()
      return True

    return False

  def substitute_placeholders(self, variable):
    if isinstance(variable, list) :
      for index in range(len(variable)):
        for key, placeholder in self.placeholders.items():
          variable[index] = variable[index].replace(key, placeholder)
      return variable
    elif isinstance(variable, str) :
      for key, placeholder in self.placeholders.items():
        variable = variable.replace(key, placeholder)
      return variable

  def before_kill_process(self):
    return
  
  def after_killed_process(self):
    return

  def can_execute(self) :
    return True

  def before_execute(self) :
    return 

  def append_args_execute(self):
    return []

  def process_communicate(self, line):
    return
    
  def callback_after_get_settings(self, **kwargs):
    return

  def on_success(self):
    return

  def on_error(self):
    return

  def on_done(self):
    return