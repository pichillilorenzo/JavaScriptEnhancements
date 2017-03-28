module.exports = {
  "title": "Cordova settings",
  "subtitle": "Cordova settings",
  "prepareClientJs": (variables) => {
    let app = variables.app
    let ipcMain = variables.ipcMain
    let util = variables.util
    let fs = variables.fs
    let data_project = variables.data_project
    let path = variables.path

    ipcMain.on("form-cordova-settings",(event, cordova_settings) => {
      try{
        util.openWithSync((fd) => {
          fs.writeFileSync(fd, JSON.stringify(cordova_settings, null, 2))
        }, path.join(data_project.settings.settings_dir_name, "cordova_settings.json"), "w+")
      }
      catch(e){
        app.sendWeb("error", `Can't modify "${path.join(data_project.settings.settings_dir_name, "cordova_settings.json")}"\nError: ${e}.`)
        return
      }
      data_project.cordova_settings = cordova_settings
      app.sendWeb("success", "Successfully saved.")
      app.sendWeb("load_config", data_project)
    })
  },
  "prepareClientHtml": (variables) => {
    let $ = variables.$
    let ipcRenderer = variables.ipcRenderer
    let utilWeb = variables.utilWeb
    let data_project = variables.data_project.settings

    let list_config = ["version", "global"]
    let list_config_debug_release = ["run", "build", "compile"]

    $("#cordova-settings .serve_port").val( data_project.cordova_settings.serve_port)

    for(let i = 0, length1 = data_project.cordova_settings.installed_platform.length; i < length1; i++){
      let platform = data_project.cordova_settings.installed_platform[i]
      $("#cordova-settings .platform_list").append('<option value="'+platform+'" '+( (i == 0) ? 'selected="selected"' : '' )+'>'+platform+'</option>')
      for(let j = 0, length2 = list_config.length; j < length2; j++){
        if (!$("#cordova-settings .container-input-platform-"+list_config[j])) {
          break
        }
        $("#cordova-settings .container-input-platform-"+list_config[j]).append('<input type="text" data-platform="'+platform+'" class="'+platform+'_'+list_config[j]+' form-control platform platform_'+list_config[j]+'_options '+( (i == 0) ? 'active' : '' )+'">')
      }
      for(let j = 0, length2 = list_config_debug_release.length; j < length2; j++){
        if (!$("#cordova-settings .container-input-platform-"+list_config_debug_release[j])) {
          break
        }
        $("#cordova-settings .debug .container-input-platform-"+list_config_debug_release[j]).append('<input type="text" data-mode="debug" data-platform="'+platform+'" class="'+platform+'_'+list_config_debug_release[j]+'_debug form-control platform platform_'+list_config_debug_release[j]+'_options '+( (i == 0) ? 'active' : '' )+'">')
        $("#cordova-settings .release .container-input-platform-"+list_config_debug_release[j]).append('<input type="text" data-mode="release" data-platform="'+platform+'" class="'+platform+'_'+list_config_debug_release[j]+'_release form-control platform platform_'+list_config_debug_release[j]+'_options '+( (i == 0) ? 'active' : '' )+'">')
      }
    }

    for(let j = 0, length2 = list_config.length; j < length2; j++){
      if ( $("#cordova-settings .cli_"+list_config[j]+"_options").length > 0 ) {
        utilWeb.setMulitpleSelectValues("#cordova-settings .cli_"+list_config[j]+"_options", data_project.cordova_settings["cli_"+list_config[j]+"_options"])
      }

      $("#cordova-settings .platform_"+list_config[j]+"_options").each(function(index, item){
        $(this).val(data_project.cordova_settings["platform_"+list_config[j]+"_options"][$(this).attr("data-platform")])
      })
    }

    for(let j = 0, length2 = list_config_debug_release.length; j < length2; j++){
      if ( $("#cordova-settings .cli_"+list_config_debug_release[j]+"_options").length > 0 ) {
        utilWeb.setMulitpleSelectValues("#cordova-settings .cli_"+list_config_debug_release[j]+"_options", data_project.cordova_settings["cli_"+list_config_debug_release[j]+"_options"])
      }

      $("#cordova-settings .platform_"+list_config_debug_release[j]+"_options").each(function(index, item){
        $(this).val(data_project.cordova_settings["platform_"+list_config_debug_release[j]+"_options"][$(this).attr("data-mode")][$(this).attr("data-platform")])
      })
    }

    $("#cordova-settings .platform_list").on("change", function(event) {
      let curr_platform = $(this).val()
      let mustActive = $(this).parent().find('.platform[data-platform="'+curr_platform+'"]')
      $(this).parent().find('.platform.active').toggleClass("active");
      $(mustActive).toggleClass("active");
    })

    $("#cordova-settings .mode_list").on("change", function(event) {
      let curr_mode = $(this).val()
      let mustActive = $(this).parent().find('.'+curr_mode+'.mode')
      $(this).parent().find('.mode.active').toggleClass("active");
      $(mustActive).toggleClass("active");
    })

    $("#form-cordova-settings").on("submit", function(event) {
      event.preventDefault()

      let cordova_settings = {
        "serve_port": $("#cordova-settings .serve_port").val().trim(),
        "cli_global_options": utilWeb.getMulitpleSelectValues("#cordova-settings .cli_global_options"),
        "cli_compile_options": utilWeb.getMulitpleSelectValues("#cordova-settings .cli_compile_options"),
        "cli_build_options": utilWeb.getMulitpleSelectValues("#cordova-settings .cli_build_options"),
        "cli_run_options": utilWeb.getMulitpleSelectValues("#cordova-settings .cli_run_options"),
        "installed_platform": data_project.cordova_settings.installed_platform,
        "platform_version_options": {},
        "platform_compile_options": {
          "debug": {},
          "release": {}
        }, 
        "platform_build_options": {
          "debug": {},
          "release": {}
        }, 
        "platform_run_options": {
          "debug": {},
          "release": {}
        }
      }

      for(let j = 0, length2 = list_config.length; j < length2; j++){
        for(let i = 0, length1 = data_project.cordova_settings.installed_platform.length; i < length1; i++){
          let platform = data_project.cordova_settings.installed_platform[i]
          if ($('#cordova-settings .'+platform+'_'+list_config[j]).length > 0) {
            cordova_settings["platform_"+list_config[j]+"_options"][platform] = $('#cordova-settings .'+platform+'_'+list_config[j]).val()
          }
        }
      }

      for(let j = 0, length2 = list_config_debug_release.length; j < length2; j++){
        for(let i = 0, length1 = data_project.cordova_settings.installed_platform.length; i < length1; i++){
          let platform = data_project.cordova_settings.installed_platform[i]
          if ($('#cordova-settings .'+platform+'_'+list_config_debug_release[j]+"_debug").length > 0) {
            cordova_settings["platform_"+list_config_debug_release[j]+"_options"].debug[platform] = $('#cordova-settings .'+platform+'_'+list_config_debug_release[j]+"_debug").val()
          }
          if ($('#cordova-settings .'+platform+'_'+list_config_debug_release[j]+"_release").length > 0) {
            cordova_settings["platform_"+list_config_debug_release[j]+"_options"].release[platform] = $('#cordova-settings .'+platform+'_'+list_config_debug_release[j]+"_release").val()
          }
        }
      }

      ipcRenderer.send("form-cordova-settings", cordova_settings)
    })
  }
}