import sys
import imp

reload_mods = []
for mod in sys.modules:
  if (mod.startswith('util') or
      mod.startswith('node')
    ) and sys.modules[mod] != None:
    reload_mods.append(mod)

mods_load_order = [
  'util.animation_loader',
  'util.repeated_timer',
  'util.main',
  'node.node_variables',
  'node.animation_loader',
  'node.repeated_timer',
  'node.main',
  'node.installer'
]

for mod in mods_load_order:
  if mod in reload_mods:
    m = sys.modules[mod]
    if 'on_module_reload' in m.__dict__:
      m.on_module_reload()
    imp.reload(sys.modules[mod])