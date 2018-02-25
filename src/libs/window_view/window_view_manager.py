class WindowViewManager():

  window_views = {}

  def add(self, view_id, window_view):
    if not view_id in self.window_views:
      self.window_views[view_id] = window_view

  def get(self, view_id):
    return self.window_views[view_id] if view_id in self.window_views else None

  def remove(self, view_id):
    if view_id in self.window_views:
      del self.window_views[view_id]

  def close(self, view_id):
    window_view = self.get(view_id)
    if window_view:
      window_view.close()
      self.remove(view_id)

window_view_manager = WindowViewManager()