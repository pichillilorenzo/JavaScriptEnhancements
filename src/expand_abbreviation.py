import sublime, sublime_plugin
import re

class expand_abbreviationCommand(sublime_plugin.TextCommand):

  def run(self, edit, *args) :

    view = self.view

    for sel in view.sel():

      row, col = view.rowcol(sel.begin())

      string = view.substr(sel).strip()

      index = string.rfind("*")

      n_times = int(string[index+1:])

      string = string[:index]

      final_string =  ""
      string_pieces = re.split(r"\$+", string)
      delimeters = re.findall(r"(\$+)", string)

      for x in range(1, n_times+1):
        for y in range(len(string_pieces)):
          if y < len(string_pieces) - 1:
            final_string += string_pieces[y] + str(x).zfill(len(delimeters[y]))
          else :
            final_string += string_pieces[y] + "\n" + ( " " * col)

      view.replace(edit, sel, final_string)

  def is_enabled(self) :

    view = self.view

    sel = view.sel()[0]
    string = view.substr(sel).strip()
    index = string.rfind("*")
    if index >= 0 :
      try :
        int(string[index+1:])
        return True
      except ValueError as e:
        pass

    return False

  def is_visible(self) :

    view = self.view

    sel = view.sel()[0]
    string = view.substr(sel).strip()
    index = string.rfind("*")
    if index >= 0 :
      try :
        int(string[index+1:])
        return True
      except ValueError as e:
        pass

    return False