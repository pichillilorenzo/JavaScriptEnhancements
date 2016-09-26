class JavaScriptCompletionsEventListener(sublime_plugin.EventListener):
  global javascriptCompletions

  def on_query_completions(self, view, prefix, locations):

    if not prefix.strip() :
      return []

    self.completions = []

    for API_Keyword in javascriptCompletions.api:
      # If completion active
      if(javascriptCompletions.API_Setup and javascriptCompletions.API_Setup.get(API_Keyword)):
        scope = javascriptCompletions.api[API_Keyword].get('scope')
        if scope and view.match_selector(locations[0], scope):
          self.completions += javascriptCompletions.api[API_Keyword].get('completions')

    if not self.completions:
      return []

    # extend word-completions to auto-completions
    compDefault = [view.extract_completions(prefix)]
    compDefault = [(item, item) for sublist in compDefault for item in sublist if len(item) > 3]
    compDefault = list(set(compDefault))
    #completions = list(self.completions)
    completions = list()
    for attr in self.completions :
      if not attr[0].startswith("description-") :
        completions.append(tuple(attr))
      else :
        attr[1] = attr[1].get("full_description")
        completions.append(tuple(attr))

    completions.extend(compDefault)
    return (completions)