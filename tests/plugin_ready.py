import time
from ..src.libs import Hook

plugin_ready = False
timeout = 30

def wait_plugin_ready():
  global plugin_ready

  if plugin_ready:
    return

  Hook.add('plugin_ready', set_plugin_ready)

  start_time = time.time()

  # wait until the plugin has installed all the npm dependecies
  # wait at maximum "timeout" seconds
  while not plugin_ready:
    if time.time() - start_time <= timeout:
      yield False
    else:
      raise TimeoutError("plugin is not ready in " + str(timeout) + " seconds")

  return True

def set_plugin_ready(*args):
  global plugin_ready
  plugin_ready = True
