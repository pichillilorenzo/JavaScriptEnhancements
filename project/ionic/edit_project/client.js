module.exports = {
  "title": "Ionic settings",
  "subtitle": "Ionic settings",
  "prepareClientJs": (variables) => {
    let app = variables.app
    let ipcMain = variables.ipcMain
    let util = variables.util
    let fs = variables.fs
    let data_project = variables.data_project
    let path = variables.path

    ipcMain.on("form-ionic-settings",(event, ionic_settings) => {
      try{
        util.openWithSync((fd) => {
          fs.writeFileSync(fd, JSON.stringify(ionic_settings, null, 2))
        }, path.join(data_project.settings.settings_dir_name, "ionic_settings.json"), "w+")
      }
      catch(e){
        app.sendWeb("error", `Can't modify "${path.join(data_project.settings.settings_dir_name, "ionic_settings.json")}"\nError: ${e}.`)
        return
      }
      data_project.ionic_settings = ionic_settings
      app.sendWeb("success", "Successfully saved.")
      app.sendWeb("load_config", data_project)
    })
  },
  "prepareClientHtml": (variables) => {
    let $ = variables.$
    let ipcRenderer = variables.ipcRenderer
    let utilWeb = variables.utilWeb
    let data_project = variables.data_project.settings

    let list_config = ["platform", "build", "run"]
    let list_config_debug_release = ["emulate"]
    let input_text_command = ["address", "port", "livereload-port", "browser", "browseroption", "platform"]
    let load_input_text_command = ["emulate", "run", "serve"]

    for(let i = 0, length1 = data_project.cordova_settings.installed_platform.length; i < length1; i++){
      let platform = data_project.cordova_settings.installed_platform[i]
      $("#ionic-settings .platform_list").append('<option value="'+platform+'" '+( (i == 0) ? 'selected="selected"' : '' )+'>'+platform+'</option>')
      for(let j = 0, length2 = list_config.length; j < length2; j++){
        if (!$("#ionic-settings .container-input-platform-"+list_config[j])) {
          break
        }
        $("#ionic-settings .container-input-platform-"+list_config[j]).append('<input type="text" data-platform="'+platform+'" class="'+platform+'_'+list_config[j]+' form-control platform platform_'+list_config[j]+'_options '+( (i == 0) ? 'active' : '' )+'">')
      }
      for(let j = 0, length2 = list_config_debug_release.length; j < length2; j++){
        if (!$("#ionic-settings .container-input-platform-"+list_config_debug_release[j])) {
          break
        }
        $("#ionic-settings .debug .container-input-platform-"+list_config_debug_release[j]).append('<input type="text" data-mode="debug" data-platform="'+platform+'" class="'+platform+'_'+list_config_debug_release[j]+'_debug form-control platform platform_'+list_config_debug_release[j]+'_options '+( (i == 0) ? 'active' : '' )+'">')
        $("#ionic-settings .release .container-input-platform-"+list_config_debug_release[j]).append('<input type="text" data-mode="release" data-platform="'+platform+'" class="'+platform+'_'+list_config_debug_release[j]+'_release form-control platform platform_'+list_config_debug_release[j]+'_options '+( (i == 0) ? 'active' : '' )+'">')
      }
    }

    for(let i = 0, length1 = load_input_text_command.length; i < length1; i++){
      for(let j = 0, length2 = input_text_command.length; j < length2; j++){
        if ( $("#ionic-settings ."+input_text_command[j]+"_"+load_input_text_command[i]).length > 0 ) {
          let value = ""
          let index = data_project.ionic_settings["cli_"+load_input_text_command[i]+"_options"].indexOf("--"+input_text_command[j])
          if (index >= 0) {
            value = data_project.ionic_settings["cli_"+load_input_text_command[i]+"_options"][index+1]
          }
          $("#ionic-settings ."+input_text_command[j]+"_"+load_input_text_command[i]).val(value)
        }
      }
    }

    for(let j = 0, length2 = list_config.length; j < length2; j++){
      if ( $("#ionic-settings .cli_"+list_config[j]+"_options").length > 0 ) {
        utilWeb.setMulitpleSelectValues("#ionic-settings .cli_"+list_config[j]+"_options", data_project.ionic_settings["cli_"+list_config[j]+"_options"])
      }

      $("#ionic-settings .platform_"+list_config[j]+"_options").each(function(index, item){
        $(this).val(data_project.ionic_settings["platform_"+list_config[j]+"_options"][$(this).attr("data-platform")])
      })
    }

    for(let j = 0, length2 = list_config_debug_release.length; j < length2; j++){
      if ( $("#ionic-settings .cli_"+list_config_debug_release[j]+"_options").length > 0 ) {
        utilWeb.setMulitpleSelectValues("#ionic-settings .cli_"+list_config_debug_release[j]+"_options", data_project.ionic_settings["cli_"+list_config_debug_release[j]+"_options"])
      }

      $("#ionic-settings .platform_"+list_config_debug_release[j]+"_options").each(function(index, item){
        $(this).val(data_project.ionic_settings["platform_"+list_config_debug_release[j]+"_options"][$(this).attr("data-mode")][$(this).attr("data-platform")])
      })
    }

    $("#ionic-settings .platform_list").on("change", function(event) {
      let curr_platform = $(this).val()
      let mustActive = $(this).parent().find('.platform[data-platform="'+curr_platform+'"]')
      $(this).parent().find('.platform.active').toggleClass("active");
      $(mustActive).toggleClass("active");
    })

    $("#ionic-settings .mode_list").on("change", function(event) {
      let curr_mode = $(this).val()
      let mustActive = $(this).parent().find('.'+curr_mode+'.mode')
      $(this).parent().find('.mode.active').toggleClass("active");
      $(mustActive).toggleClass("active");
    })

    $("#form-ionic-settings").on("submit", function(event) {
      event.preventDefault()

      let ionic_settings = {
        "cli_platform_options": utilWeb.getMulitpleSelectValues("#ionic-settings .cli_platform_options"),
        "cli_build_options": utilWeb.getMulitpleSelectValues("#ionic-settings .cli_build_options"),
        "cli_emulate_options": utilWeb.getMulitpleSelectValues("#ionic-settings .cli_emulate_options"),
        "cli_run_options": utilWeb.getMulitpleSelectValues("#ionic-settings .cli_run_options"),
        "cli_serve_options": utilWeb.getMulitpleSelectValues("#ionic-settings .cli_serve_options"),
        "platform_emulate_options": {
          "debug": {},
          "release": {}
        }
      }

      for(let i = 0, length1 = load_input_text_command.length; i < length1; i++){
        for(let j = 0, length2 = input_text_command.length; j < length2; j++){
          if ($("#ionic-settings ."+input_text_command[j]+"_"+load_input_text_command[i]).length > 0 && $("#ionic-settings ."+input_text_command[j]+"_"+load_input_text_command[i]).val().trim()) {
            ionic_settings["cli_"+load_input_text_command[i]+"_options"] = ionic_settings["cli_"+load_input_text_command[i]+"_options"].concat(["--"+input_text_command[j], $("#ionic-settings ."+input_text_command[j]+"_"+load_input_text_command[i]).val().trim()])
          }
        }
      }

      for(let j = 0, length2 = list_config.length; j < length2; j++){
        for(let i = 0, length1 = data_project.cordova_settings.installed_platform.length; i < length1; i++){
          let platform = data_project.cordova_settings.installed_platform[i]
          if ($('#ionic-settings .'+platform+'_'+list_config[j]).length > 0) {
            ionic_settings["platform_"+list_config[j]+"_options"][platform] = $('#ionic-settings .'+platform+'_'+list_config[j]).val()
          }
        }
      }
      
      for(let j = 0, length2 = list_config_debug_release.length; j < length2; j++){
        for(let i = 0, length1 = data_project.cordova_settings.installed_platform.length; i < length1; i++){
          let platform = data_project.cordova_settings.installed_platform[i]
          if ($('#ionic-settings .'+platform+'_'+list_config_debug_release[j]+"_debug").length > 0) {
            ionic_settings["platform_"+list_config_debug_release[j]+"_options"].debug[platform] = $('#ionic-settings .'+platform+'_'+list_config_debug_release[j]+"_debug").val()
          }
          if ($('#ionic-settings .'+platform+'_'+list_config_debug_release[j]+"_release").length > 0) {
            ionic_settings["platform_"+list_config_debug_release[j]+"_options"].release[platform] = $('#ionic-settings .'+platform+'_'+list_config_debug_release[j]+"_release").val()
          }
        }
      }

      ipcRenderer.send("form-ionic-settings", ionic_settings)
    })

  }
}