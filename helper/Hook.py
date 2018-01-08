class Hook(object):
  hook_list = {}

  @staticmethod
  def add (hook_name, hook_func, priority = 10) :
    if not hook_name in Hook.hook_list :
      Hook.hook_list[hook_name] = []

    Hook.hook_list[hook_name].append({
      "hook_func": hook_func,
      "priority": priority if priority >= 0 else 0
    })

    Hook.hook_list[hook_name] = sorted(Hook.hook_list[hook_name], key=lambda hook: hook["priority"])

  @staticmethod
  def apply(hook_name, value='', *args, **kwargs) :

    args = (value,) + args

    if hook_name in Hook.hook_list :
      for hook in Hook.hook_list[hook_name] :
        hook["hook_func"](*args, **kwargs)
        #value = hook["hook_func"](*args, **kwargs)
        #args = (value,) + args[1:]

    return value

  @staticmethod
  def count(hook_name) :

    if hook_name in Hook.hook_list :
      return len(Hook.hook_list[hook_name])
    return 0

  @staticmethod
  def removeHook(hook_name, hook_func, priority = -1) :

    if hook_name in Hook.hook_list :
      if priority >= 0 :
        hook = { 
          "hook_func": hook_func, 
          "priority": priority 
        }
        while hook in Hook.hook_list[hook_name] : 
          Hook.hook_list[hook_name].remove(hook)
      else :
         for hook in Hook.hook_list[hook_name] :
          if hook["hook_func"] == hook_func :
            Hook.hook_list[hook_name].remove(hook)

  @staticmethod
  def removeAllHook(hook_name) :

    if hook_name in Hook.hook_list :
      Hook.hook_list[hook_name] = []
      