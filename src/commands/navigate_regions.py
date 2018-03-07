from ..libs import util

class JavascriptEnhancementsNavigateRegionsCommand():

  region_keys = []

  def run(self, edit, **args) :
    
    view = self.view
    regions = []

    for region_key in self.region_keys:
      regions += view.get_regions(region_key)

    regions = sorted(regions, key=lambda region: region.begin())
    
    if not regions:
      return
      
    move_type = args.get("type")

    if move_type == "next" :

      r_next = self.find_next(regions)
      if r_next != None :
        row, col = view.rowcol(r_next.begin())

        util.go_to_centered(view, row, col)

    elif move_type == "previous" :

      r_prev = self.find_prev(regions)
      if r_prev != None :
        row, col = view.rowcol(r_prev.begin())

        util.go_to_centered(view, row, col)

  def find_next(self, regions):
    view = self.view

    sel = view.sel()[0]

    for region in regions :
      if region.begin() > sel.begin() :
        return region

    if(len(regions) > 0) :
      return regions[0]

    return None

  def find_prev(self, regions):
    view = self.view

    sel = view.sel()[0]

    previous_regions = []
    for region in regions :
      if region.begin() < sel.begin() :
        previous_regions.append(region)

    if not previous_regions and len(regions) > 0:
      previous_regions.append(regions[len(regions)-1])

    return previous_regions[len(previous_regions)-1] if len(previous_regions) > 0 else None
