import sublime, sublime_plugin
import json, time, os
from ..libs import util
from ..commands.bookmarks import overwrite_bookmarks

class JavascriptEnhancementsUpdateBookmarkLinesEventListener(sublime_plugin.EventListener):

  def on_post_save_async(self, view) :

    if util.is_project_view(view) and util.is_javascript_project(): 
      regions = view.get_regions("javascript_enhancements_region_bookmarks")

      lines = []
      for region in regions:
        row, col = view.rowcol(region.begin())
        lines += [row]

      if lines:
        overwrite_bookmarks( view, lines )
