import sublime

class AnimationLoader():
  def __init__(self, animation, sec, str_before="", str_after=""):
    self.animation = animation
    self.sec = sec
    self.animation_length = len(animation)
    self.str_before = str_before
    self.str_after = str_after
    self.cur_anim = 0
  def animate(self):
    sublime.active_window().status_message(self.str_before+self.animation[self.cur_anim % self.animation_length]+self.str_after)
    self.cur_anim = self.cur_anim + 1
  def on_complete(self):
    sublime.active_window().status_message("")