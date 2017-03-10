from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import sys, threading, time, json, os, traceback, re

PACKAGE_PATH = os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
sys.path += [PACKAGE_PATH] + [os.path.join(PACKAGE_PATH, f) for f in ['node', 'util', 'my_socket', 'util_tkinter']]

host = sys.argv[1]
port = int(sys.argv[2])

import util_tkinter.main as UtilTkinter
from node.main import NodeJS
node = NodeJS()

from my_socket.main import mySocketClient

socket = mySocketClient("edit_javascript_project")

root = Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
settings = dict()
TITLE_FONT = ("Helvetica", 18, "bold")
WINDOW_WIDTH = 850
WINDOW_HEIGHT = 350
WINDOW_PADDING = 20

class ProjectDetails(ttk.Frame):
  def __init__(self, parent, controller, **options):
    super().__init__(parent, **options)
    self.controller = controller  
    self.children_frames = []
    self.display_name = "Project Details"
    self.json_name = "project_details"
    self.init_window()

  def init_window(self):

    self.project_name = StringVar()
    self.label_project_name = ttk.Label(self, text="Project Name")
    UtilTkinter.grid(self.label_project_name, row=0, column=0)
    self.entry_project_name = ttk.Entry(self, textvariable=self.project_name)
    UtilTkinter.grid(self.entry_project_name, row=0, column=1)

    self.author = StringVar()
    self.label_author = ttk.Label(self, text="Author")
    UtilTkinter.grid(self.label_author, row=1, column=0)
    self.entry_author = ttk.Entry(self, textvariable=self.author)
    UtilTkinter.grid(self.entry_author, row=1, column=1)

    self.author_uri = StringVar()
    self.label_author_uri = ttk.Label(self, text="Author URI")
    UtilTkinter.grid(self.label_author_uri, row=2, column=0)
    self.entry_author_uri = ttk.Entry(self, textvariable=self.author_uri)
    UtilTkinter.grid(self.entry_author_uri, row=2, column=1)

    self.description = StringVar()
    self.label_description = ttk.Label(self, text="Description")
    UtilTkinter.grid(self.label_description, row=3, column=0)
    self.entry_description = Text(self, width=25, height=2)
    UtilTkinter.grid(self.entry_description, row=3, column=1)

    self.version = StringVar()
    self.label_version = ttk.Label(self, text="Version")
    UtilTkinter.grid(self.label_version, row=4, column=0)
    self.entry_version = ttk.Entry(self, textvariable=self.version)
    UtilTkinter.grid(self.entry_version, row=4, column=1)

    self.license = StringVar()
    self.label_license = ttk.Label(self, text="License")
    UtilTkinter.grid(self.label_license, row=5, column=0)
    self.entry_license = ttk.Entry(self, textvariable=self.license)
    UtilTkinter.grid(self.entry_license, row=5, column=1)

    self.license_uri = StringVar()
    self.label_license_uri = ttk.Label(self, text="License URI")
    UtilTkinter.grid(self.label_license_uri, row=6, column=0)
    self.entry_license_uri = ttk.Entry(self, textvariable=self.license_uri)
    UtilTkinter.grid(self.entry_license_uri, row=6, column=1)

    self.tags = StringVar()
    self.label_tags = ttk.Label(self, text="Tags")
    UtilTkinter.grid(self.label_tags, row=7, column=0)
    self.entry_tags = ttk.Entry(self, textvariable=self.tags)
    UtilTkinter.grid(self.entry_tags, row=7, column=1)

    self.button_apply = ttk.Button(self, text="Apply", command=self.apply)
    UtilTkinter.grid(self.button_apply, row=8, column=1, sticky="SE", pady="20 0")

  def update_variables(self):
    global settings
    if not settings:
      return
    self.project_name.set(settings[self.json_name]["project_name"])
    self.author.set(settings[self.json_name]["author"])
    self.author_uri.set(settings[self.json_name]["author_uri"])
    self.description.set(settings[self.json_name]["description"])
    self.entry_description.delete('1.0', END)
    self.entry_description.insert(INSERT, settings[self.json_name]["description"])
    self.version.set(settings[self.json_name]["version"])
    self.license.set(settings[self.json_name]["license"])
    self.license_uri.set(settings[self.json_name]["license_uri"])
    self.tags.set(settings[self.json_name]["tags"])

  def apply(self):
    global settings
    if not settings:
      return
    settings[self.json_name]["project_name"] = self.project_name.get().strip()
    settings[self.json_name]["author"] = self.author.get().strip()
    settings[self.json_name]["author_uri"] = self.author_uri.get().strip()
    settings[self.json_name]["description"] = self.description.get().strip()
    settings[self.json_name]["description"] = self.entry_description.get("1.0",END).strip()
    settings[self.json_name]["version"] = self.version.get().strip()
    settings[self.json_name]["license"] = self.license.get().strip()
    settings[self.json_name]["license_uri"] = self.license_uri.get().strip()
    settings[self.json_name]["tags"] = self.tags.get().strip()

    json_file = os.path.join(settings["settings_dir_name"], self.json_name+".json")
    if os.path.isfile(json_file) :
      with open(json_file, "w") as file :
        data = json.dumps(settings[self.json_name])
        file.write(data)
        messagebox.showinfo(message="Done!")

class OptionsFlowSettings(ttk.Frame):
  def __init__(self, parent, controller, **options):
    super().__init__(parent, **options)
    self.controller = controller  
    self.children_frames = []
    self.display_name = "Options Flow Settings"
    self.json_name = "flow_settings"
    self.options_menu_list = (
      "log.file",
      "module.name_mapper",
      "module.name_mapper.extension",
      "module.system",
      "module.system.node.resolve_dirname",
      "module.ignore_non_literal_requires",
      "module.file_ext",
      "module.use_strict",
      "munge_underscores",
      "server.max_workers",
      "traces",
      "strip_root",
      "suppress_comment",
      "temp_dir",
      "esproposal.class_static_fields",
      "esproposal.class_instance_fields",
      "esproposal.decorators",
      "esproposal.export_star_as",
      "all"
    )
    self.options_item_list = dict()
    self.init_window()

  def init_window(self):

    self.option_menu = StringVar(self)
    self.option_menu.set(self.options_menu_list[0])
    self.add_option_menu = ttk.OptionMenu(self, self.option_menu, self.options_menu_list[0], *self.options_menu_list)
    UtilTkinter.grid(self.add_option_menu, row=0, column=0)
    self.add_option_menu.config(width=27)
    self.add_button = ttk.Button(self, text="+", command=self.add_option)
    UtilTkinter.grid(self.add_button, row=0, column=1)
    self.button_apply = ttk.Button(self, text="Apply", command=self.apply)
    UtilTkinter.grid(self.button_apply, row=0, column=2)

    self.update_variables()

  def add_option(self):
    i = len(self.options_item_list.items())+1
    item = dict()
    key = self.option_menu.get()
    item["key"] = key
    item["var"] = StringVar(self)
    label = ttk.Label(self, text=key)
    UtilTkinter.grid(label, row=i, column=0)
    entry = ttk.Entry(self, textvariable=item["var"])
    UtilTkinter.grid(entry, row=i, column=1)
    del_button = ttk.Button(self, text="X", command=lambda i=i: self.del_option(i))
    UtilTkinter.grid(del_button, row=i, column=2)
    self.options_item_list[i] = item
    self.controller.update_canvas_height(self, redraw=True)

  def del_option(self, row):
    for item in self.grid_slaves():
      if int(item.grid_info()["row"]) == row :
        item.grid_forget()
    del self.options_item_list[row]
    self.controller.update_canvas_height(self, redraw=True)

  def update_variables(self):
    global settings
    if not settings:
      return

    for widget in self.winfo_children():
      if widget != self.add_option_menu and widget != self.add_button and widget != self.button_apply :
        widget.destroy()


    self.options_item_list = dict()
    for i in range(len(settings[self.json_name]["options"])) :
      i = i + 1
      item = dict()
      option = settings[self.json_name]["options"][i-1]
      key = next(iter(option.keys()))
      value = option[key]
      item["key"] = key
      if type(value) is bool :
        if value :
          value = "true"
        else :
          value = "false"
      elif type(value) is str:
        value = json.dumps(value, ensure_ascii=False)[1:-1]
      else :
        value = json.dumps(value, ensure_ascii=False)
      item["var"] = StringVar(self, value=value)
      label = ttk.Label(self, text=key)
      UtilTkinter.grid(label, row=i, column=0)
      entry = ttk.Entry(self, textvariable=item["var"])
      UtilTkinter.grid(entry, row=i, column=1)
      del_button = ttk.Button(self, text="X", command=lambda i=i: self.del_option(i))
      UtilTkinter.grid(del_button, row=i, column=2)
      self.options_item_list[i] = item

    self.controller.update_canvas_height(self, redraw=True)

  def apply(self):
    settings[self.json_name]["options"] = list()
    for key, value in self.options_item_list.items():
      option = value
      settings[self.json_name]["options"].append({ option["key"]: option["var"].get() })
    FlowSettings.save_flow_settings(self)

class ManageFolderFlowSettings(ttk.Frame):
  def __init__(self, parent, controller, **options):
    super().__init__(parent, **options)
    self.controller = controller  
    self.children_frames = []
    self.json_name = "flow_settings"
    self.item_list = dict()
    self.init_window()

  def init_window(self):

    self.add_button = ttk.Button(self, text="+", command=self.add_option)
    UtilTkinter.grid(self.add_button, row=0, column=1)
    self.button_apply = ttk.Button(self, text="Apply", command=self.apply)
    UtilTkinter.grid(self.button_apply, row=0, column=2)

    self.update_variables()

  def add_option(self):
    i = len(self.item_list.items())+1
    item = dict()
    item["var"] = StringVar(self)
    entry = ttk.Entry(self, textvariable=item["var"])
    UtilTkinter.grid(entry, row=i, column=0)
    button_askopenfilename = ttk.Button(self, text="...", command=lambda item=item: self.askopenfilename(item["var"]), width=1)
    UtilTkinter.grid(button_askopenfilename, row=i, column=1)
    del_button = ttk.Button(self, text="X", command=lambda i=i: self.del_option(i))
    UtilTkinter.grid(del_button, row=i, column=2)
    self.item_list[i] = item
    self.controller.update_canvas_height(self, redraw=True)

  def del_option(self, row):
    for item in self.grid_slaves():
      if int(item.grid_info()["row"]) == row :
        item.grid_forget()
    del self.item_list[row]
    self.controller.update_canvas_height(self, redraw=True)

  def askopenfilename(self, var):
    path = filedialog.askopenfilename()
    if path :
      var.set(path)

  def update_variables(self):
    global settings
    if not settings:
      return

    for widget in self.winfo_children():
      if widget != self.add_button and widget != self.button_apply :
        widget.destroy()


    self.item_list = dict()
    for i in range(len(settings[self.json_name][self.json_key])) :
      i = i + 1
      item = dict()
      value = settings[self.json_name][self.json_key][i-1]
      item["var"] = StringVar(self, value=value)
      entry = ttk.Entry(self, textvariable=item["var"])
      UtilTkinter.grid(entry, row=i, column=0)
      button_askopenfilename = ttk.Button(self, text="...", command=lambda item=item: self.askopenfilename(item["var"]), width=1)
      UtilTkinter.grid(button_askopenfilename, row=i, column=1)
      del_button = ttk.Button(self, text="X", command=lambda i=i: self.del_option(i))
      UtilTkinter.grid(del_button, row=i, column=2)
      self.item_list[i] = item

    self.controller.update_canvas_height(self, redraw=True)

  def apply(self):
    settings[self.json_name][self.json_key] = list()
    for key, value in self.item_list.items():
      item = value
      settings[self.json_name][self.json_key].append(item["var"].get())
    FlowSettings.save_flow_settings(self)

class IgnoreFolderFlowSettings(ManageFolderFlowSettings):
  def __init__(self, parent, controller, **options):
    super().__init__(parent, controller, **options)
    self.display_name = "Ignore Flow Settings"
    self.json_key = "ignore"

class IncludeFolderFlowSettings(ManageFolderFlowSettings):
  def __init__(self, parent, controller, **options):
    super().__init__(parent, controller, **options)
    self.display_name = "Include Flow Settings"
    self.json_key = "include"

class LibsFolderFlowSettings(ManageFolderFlowSettings):
  def __init__(self, parent, controller, **options):
    super().__init__(parent, controller, **options)
    self.display_name = "Libs Flow Settings"
    self.json_key = "libs"

class FlowSettings(ttk.Frame):
  def __init__(self, parent, controller, **options):
    super().__init__(parent, **options)
    self.controller = controller  
    self.children_frames = [IgnoreFolderFlowSettings, IncludeFolderFlowSettings, LibsFolderFlowSettings, OptionsFlowSettings]
    self.display_name = "Flow Settings"
    self.json_name = "flow_settings"
    self.init_window()

  def init_window(self):

    self.use_flow_checker = IntVar(self, value=0)
    self.label_use_flow_checker = ttk.Label(self, text="Use Flow checker")
    UtilTkinter.grid(self.label_use_flow_checker, row=0, column=0)
    self.checkbutton_use_flow_checker = ttk.Checkbutton(self, variable=self.use_flow_checker)
    UtilTkinter.grid(self.checkbutton_use_flow_checker, row=0, column=1)

    self.button_apply = ttk.Button(self, text="Apply", command=self.apply)
    UtilTkinter.grid(self.button_apply, row=1, column=1, sticky="SE", pady="20 0")

  def update_variables(self):
    global settings
    if not settings:
      return

    self.use_flow_checker.set(settings[self.json_name]["use_flow_checker"])

  def apply(self):
    global settings
    if not settings:
      return
    settings[self.json_name]["use_flow_checker"] = True if self.use_flow_checker.get() else False
    self.save_flow_settings(self)

  @classmethod
  def save_flow_settings(self, cls):
    global settings
    if not settings:
      return

    json_file = os.path.join(settings["settings_dir_name"], cls.json_name+".json")
    flowconfig_file = os.path.join(settings["project_dir_name"], ".flowconfig")
    if os.path.isfile(json_file) and os.path.isfile(flowconfig_file) :
      with open(json_file, "w", encoding="utf-8") as file :
        data = json.dumps(settings[cls.json_name], ensure_ascii=False)
        file.write(data)
        with open(flowconfig_file, "w", encoding="utf-8") as flow_file:
          ignore_txt = "[ignore]\n"
          include_txt = "[include]\n"
          libs_txt = "[libs]\n"
          options_txt = "[options]\n"

          for item in settings[cls.json_name]["ignore"] :
            ignore_txt += item + "\n"

          for item in settings[cls.json_name]["include"] :
            include_txt += item + "\n" 

          for item in settings[cls.json_name]["libs"] :
            libs_txt += item + "\n"

          for item in settings[cls.json_name]["options"] :
            key = next(iter(item.keys()))
            value = item[key]
            if type(value) is bool :
              if value :
                value = "true"
              else :
                value = "false"
            elif type(value) is str:
              value = json.dumps(value, ensure_ascii=False)[1:-1]
            else :
              value = json.dumps(value, ensure_ascii=False)

            options_txt += key + "=" + value + "\n"

          flow_file.write(ignore_txt+"\n"+include_txt+"\n"+libs_txt+"\n"+options_txt)
          messagebox.showinfo(message="Done!")
    else :
      messagebox.showerror(title="Error", message="Can't find " + json_file + " and " + flowconfig_file + " files!")

class Application(ttk.Frame):
  def __init__(self, master=None):
    super().__init__(master, padding=str(WINDOW_PADDING)+" "+str(WINDOW_PADDING))  
    self.vscrollbar = Scrollbar(self)
    self.canvas = Canvas(self, yscrollcommand=self.vscrollbar.set, height=0, borderwidth=-3)
    self.current_frame = None
    self.id_frame_canvas = 0
    self.treeview = ttk.Treeview(self)
    self.list_frame = dict()
    self.frames = {} 

    def ric(tree_id, list_frame):
      for F in list_frame:
        page_name = F.__name__
        frame = F(parent=self.canvas, controller=self)
        self.frames[page_name] = frame
        curr_id = self.treeview.insert(tree_id, 'end', text=frame.display_name)
        self.list_frame[curr_id] = page_name
        if (frame.children_frames) :
          ric(curr_id, frame.children_frames)

    ric('', [ProjectDetails,FlowSettings])

    self.treeview.bind('<<TreeviewSelect>>', self.change_frame)
    self.init_window()

  def init_window(self):
    self.title_frame = StringVar()
    self.title_frame_label = ttk.Label(self, textvariable=self.title_frame, font=TITLE_FONT, padding="0 0 0 10")
    UtilTkinter.grid(self.title_frame_label, row=0, columnspan=2, sticky=(N))

    UtilTkinter.grid(self.treeview, row=1, column=0, sticky=(N, W))

    UtilTkinter.grid(self.vscrollbar, row=1, column=2, sticky=(N, S))
    self.vscrollbar.config(command=self.canvas.yview)
    self.canvas.grid(row=1, column=1, sticky=(N, E, W))
    self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    UtilTkinter.grid(self, row=0, column=0, sticky=(N, S, E, W))
    self.grid_rowconfigure(0, weight=0)
    self.grid_columnconfigure(1, weight=100)

    self.show_frame("ProjectDetails")

  def _bound_to_mousewheel(self):
    self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)   

  def _unbound_to_mousewheel(self):
    self.canvas.unbind_all("<MouseWheel>")

  def _on_mousewheel(self, event):
    self.canvas.yview_scroll(-1*event.delta, "units")

  def show_frame(self, page_name):
    if self.id_frame_canvas > 0 :
      self.canvas.delete(self.id_frame_canvas)
    frame = self.frames[page_name]
    self.title_frame.set(frame.display_name)   

    self.id_frame_canvas = self.canvas.create_window((2,4), anchor=NW, window=frame, width=WINDOW_WIDTH - WINDOW_PADDING - self.treeview.winfo_reqwidth())
    frame.update_variables()
    self.update_canvas_height(frame)
    self.current_frame = frame

  def update_canvas_height(self, frame, redraw=False) :
    if redraw :
      self.canvas.delete(self.id_frame_canvas)
      self.id_frame_canvas = self.canvas.create_window((2,4), anchor=NW, window=frame, width=WINDOW_WIDTH - WINDOW_PADDING - self.treeview.winfo_reqwidth())
    frame.update_idletasks()
    if frame.winfo_reqheight() > WINDOW_HEIGHT - WINDOW_PADDING*2 - self.title_frame_label.winfo_reqheight() :
      self._bound_to_mousewheel()
    else :
      self.canvas.itemconfig(self.id_frame_canvas, height=WINDOW_HEIGHT - WINDOW_PADDING*2 - self.title_frame_label.winfo_reqheight())
      self._unbound_to_mousewheel()
    self.canvas["height"] = WINDOW_HEIGHT - WINDOW_PADDING*2 - self.title_frame_label.winfo_reqheight()
    self.canvas.config(scrollregion=self.canvas.bbox("all"))

  def change_frame(self, event):
    page_name = self.list_frame[self.treeview.focus()]
    self.show_frame(page_name)

  def on_closing(self) :
    global socket
    socket.close()
    root.destroy()

app = Application(master=root)

def recv_from_server(server_data):
  global settings
  if server_data:

    json_data = json.loads(server_data, encoding="utf-8")
    
    if json_data["command"] == "server_closing" :

      app.on_closing()

    if json_data["command"] == "load_project_settings":

      settings = json_data["settings"]
      if app.current_frame:
        app.current_frame.update_variables()

socket.handle_recv(recv_from_server)
socket.connect(host, port)

# hack to spawn window centered
root.withdraw()
root.update_idletasks()
x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
y = (root.winfo_screenheight() - root.winfo_reqheight()) / 3.5
root.geometry("%dx%d+%d+%d" % (WINDOW_WIDTH, WINDOW_HEIGHT, x, y))
root.deiconify()

root.wm_attributes("-topmost", "true")
root.after(1000, lambda: root.wm_attributes("-topmost", "false"))
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.resizable(width=False, height=False)
app.master.title("Edit Project")
app.mainloop()