import os, traceback

class FolderExplorer:

  view = None
  start_path = ""
  current_path = ""
  selected_dir = ""
  selected_file = ""
  callback_choose = None
  only_dir = False
  only_file = False
  closed = False
  point = 5

  def __init__(self, view, point=5, start_path="", callback_choose=None, only_dir=False, only_file=False):

    self.view = view
    self.start_path = start_path.strip()
    self.callback_choose = callback_choose
    self.only_dir = only_dir
    self.only_file = only_file
    self.point = point

    if self.start_path:
      pass
    elif self.view and self.view.file_name():
      self.start_path = self.view.file_name()
    elif self.view and self.view.window().folders():
      self.start_path = self.view.window().folders()[0]
    else:
      raise Exception('JavaScript Enhancements: No place to open Folder Explorer to.')

    if not os.path.isdir(self.start_path):
      self.start_path = os.path.dirname(self.start_path)

    self.current_path = self.start_path

    self.style_css = ""
    with open(os.path.join(SRC_FOLDER, "folder_explorer", "style.css")) as css_file:
      self.style_css = "<style>"+css_file.read()+"</style>"

  def open(self, path=""):

    dirs = []
    files = []

    self.current_path = path if path else self.current_path

    if not os.path.isdir(self.current_path):
      self.current_path = os.path.dirname(self.current_path)
      
    try:
      for item in os.listdir(self.current_path):
        abspath = os.path.join(self.current_path, item)
        is_dir = os.path.isdir(abspath)
        if is_dir:
          dirs.append(abspath)
        else:
          files.append(abspath)
    except PermissionError as e:
      sublime.error_message("Permission denied: " + self.current_path)
      if os.path.dirname(self.current_path) != self.current_path:
        try:
          os.listdir(os.path.dirname(self.current_path))
          self.open(os.path.dirname(self.current_path))
        except Exception as e2:
          if self.start_path != self.current_path:
            self.open(self.start_path)
      return

    dirs = sorted(dirs)
    files = sorted(files)

    html = """
    <html>
      <head></head>
      <body>""" + self.style_css + """
        <div class="content">
          <p>Folder Explorer """ + (" - Only Directories" if self.only_dir else (" - Only Files" if self.only_file else "")) + """</p>
          <p class="current-directory">""" + self.current_path + """</p>
    """

    html += """
          <div class="item-list">
    """

    img_directory_src = "file://" + IMG_FOLDER + "/folder.png"

    if self.current_path != os.path.dirname(self.current_path):
      action = "navigate_dir|" + os.path.dirname(self.current_path)
      html += "<div class=\"item directory\"><a href=\"" + action + "\"><img class=\"item-image directory-image\" src=\"" + img_directory_src + "\">..</a></div>"

    if not self.only_file:
      for d in dirs:

        action = "select_dir|" + d
        html += "<div class=\"item directory\"><a href=\"" + action + "\"><img class=\"item-image directory-image\" src=\"" + img_directory_src + "\">" + os.path.basename(d) + "</a></div>"

    if not self.only_dir:
      for f in files:

        action = "select_file|" + f
        html += "<div class=\"item file\"><a href=\"" + action + "\">" + os.path.basename(f) + "</a></div>"

    html += """
            </div>
            <a class="button reset-path-button" href=\"navigate_dir|""" + self.start_path + """\">reset path</a>
            <a class="button choose-button" href=\"choose\">choose</a>
            <a class="button close-button" href=\"close\">close</a>
          </div>
      </body>
    </html>
    """

    if not popupManager.isVisible("folder_explorer"):
      self.closed = False
      popupManager.setVisible("folder_explorer", True)
      sublime.set_timeout(lambda:
        self.view.show_popup(
          html, 
          sublime.COOPERATE_WITH_AUTO_COMPLETE, 
          self.point, 700, 500, 
          self.action, 
          lambda: popupManager.setVisible("folder_explorer", False) or ( self.open() if not self.closed else False ))
      , 50)
    else:
      self.view.update_popup(html)

  def action(self, action, parameters=[]):

    if not parameters:
      action = action.split("|")
      parameters = action[1:]
      action = action[0]

    if action == "select_dir":
      if self.selected_dir == parameters[0]:
        self.action("navigate_dir", parameters)
      else:
        self.selected_dir = parameters[0]
        self.selected_file = ""

    elif action == "select_file":
      if self.selected_file == parameters[0]:
        self.action("choose")
      else:
        self.selected_file = parameters[0]
        self.selected_dir = ""

    elif action == "navigate_dir":
      self.selected_dir = ""
      self.selected_file = ""
      self.open(parameters[0])

    elif action == "choose":
      if ( self.selected_dir or self.selected_file or self.current_path ) and self.callback_choose:
        self.callback_choose( self.selected_dir or self.selected_file or self.current_path )
        self.action("close")
        return

    elif action == "close":
      self.closed = True
      self.selected_dir = ""
      self.selected_file = ""
      self.view.hide_popup()

    if self.selected_dir or self.selected_file:
      panel = Util.create_and_show_panel("folder_explorer_selection", window=self.view.window(), return_if_exists=True, unlisted=True)
      panel.set_read_only(False)
      panel.run_command("erase_text_view")
      panel.run_command("insert_text_view", args={"text": "Selected: " + ( self.selected_dir or self.selected_file ), "point": 0 })
      panel.set_read_only(True)
    else:
      self.view.window().destroy_output_panel("folder_explorer_selection")
