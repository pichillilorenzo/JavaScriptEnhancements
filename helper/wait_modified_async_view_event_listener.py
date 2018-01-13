class wait_modified_asyncViewEventListener():
  last_change = time.time()
  waiting = False
  prefix_thread_name = ""
  wait_time = 1
  modified = False

  def on_modified_async(self, *args, **kwargs) :
    self.last_change = time.time()
    if not self.prefix_thread_name :
      raise Exception("No prefix_thread_name to wait_modified_asyncViewEventListener")
    Util.create_and_start_thread(self.on_modified_async_with_thread, self.prefix_thread_name+"_"+str(self.view.id()), args=args, kwargs=kwargs)

  def wait(self):
    if time.time() - self.last_change <= self.wait_time:
      if not self.waiting:
        self.waiting = True
      else :
        return
      self.last_change = time.time()
      while time.time() - self.last_change <= self.wait_time:
        time.sleep(.1)
      self.waiting = False

  def on_modified_async_with_thread(self, *args, **kwargs):
    return
