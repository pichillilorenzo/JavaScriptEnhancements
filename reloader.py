import sys
import imp

reload_mods = []
for mod in sys.modules:
  if (mod.startswith('util') or
      mod.startswith('helper') or
      mod.startswith('node') or
      mod.startswith('evaluate_javascript') or
      mod.startswith('javascript_completions') 
    ) and sys.modules[mod] != None:
    reload_mods.append(mod)

mods_load_order = [
  'util.main',
  'node.node_variables',
  'node.animation_loader',
  'node.repeated_timer',
  'node.main',
  'node.installer',
  'helper.main',
  'javascript_completions.main',
  'evaluate_javascript.main'
]

for mod in mods_load_order:
  if mod in reload_mods:
    m = sys.modules[mod]
    if 'on_module_reload' in m.__dict__:
      m.on_module_reload()
    imp.reload(sys.modules[mod])