module.exports = {
  "title": "Cordova settings",
  "subtitle": "",
  "icon": "img/cordova-logo.png",
  "tile_bg_color": "bg-black",
  "tile_fg_color": "fg-white",
  "prepareClientJs": (variables) => {
    let app = variables.app
    let ipcMain = variables.ipcMain
    let util = variables.util
    let fs = variables.fs
    let data_project = variables.data_project
    let path = variables.path
    const npm = require('npm')

    ipcMain.on("form-cordova-settings",(event, cordova_settings) => {
      cordova_settings = util.mergeObjectsRecursive(data_project.settings.cordova_settings, cordova_settings)
      try{
        util.openWithSync((fd) => {
          app.sendWeb("overlay-message", "Saving "+path.join(data_project.settings.settings_dir_name, "cordova_settings.json")+"...")
          fs.writeFileSync(fd, JSON.stringify(cordova_settings, null, 2))
        }, path.join(data_project.settings.settings_dir_name, "cordova_settings.json"), "w+")
      }
      catch(e){
        app.sendWeb("error", `Can't modify "${path.join(data_project.settings.settings_dir_name, "cordova_settings.json")}"\nError: ${e}.`)
        return
      }

      if (cordova_settings.package_json) {
        let package_json = JSON.parse(fs.readFileSync(path.join(data_project.settings.settings_dir_name, "package.json"), {encoding: 'utf8'}))
        package_json = util.mergeObjectsRecursive(package_json, data_project.settings.cordova_settings.package_json)
        util.openWithSync((fd) => {
          app.sendWeb("overlay-message", "Saving "+path.join(data_project.settings.settings_dir_name, "package.json")+"...")
          fs.writeFileSync(fd, JSON.stringify(package_json, null, 2))
        }, path.join(data_project.settings.settings_dir_name, "package.json"), "w+")
        process.chdir(path.join(data_project.settings.settings_dir_name));
        npm.load(function(err){
          app.sendWeb("overlay-message", "Running 'npm install' ...")
          npm.commands.install(function(err, data){
            if(err){
              app.sendWeb("error", JSON.stringify(err, null, 2))
              return
            }
            data_project.cordova_settings = cordova_settings
            app.sendWeb("success", "Successfully saved.")
            app.sendWeb("load_config", data_project)
          })

        })
      }
      else {
        data_project.cordova_settings = cordova_settings
        app.sendWeb("success", "Successfully saved.")
        app.sendWeb("load_config", data_project)
      }
    
    })
  },
  "prepareClientHtml": (variables) => {
    let $ = variables.$
    let ipcRenderer = variables.ipcRenderer
    let utilWeb = variables.utilWeb
    let data_project = variables.data_project.settings

    let list_config = ["version", "global"]
    let list_config_debug_release = ["run", "build", "compile"]

    $("#form-cordova-settings .serve_port").val( data_project.cordova_settings.serve_port)

    for(let i = 0, length1 = data_project.cordova_settings.installed_platform.length; i < length1; i++){
      let platform = data_project.cordova_settings.installed_platform[i]
      $("#form-cordova-settings .platform_list").append('<option value="'+platform+'" '+( (i == 0) ? 'selected="selected"' : '' )+'>'+platform+'</option>')
      for(let j = 0, length2 = list_config.length; j < length2; j++){
        if (!$("#form-cordova-settings .container-input-platform-"+list_config[j])) {
          break
        }
        $("#form-cordova-settings .container-input-platform-"+list_config[j]).append('<div class="input-control text full-size " data-role="input"><input type="text" data-platform="'+platform+'" class="'+platform+'_'+list_config[j]+' platform platform_'+list_config[j]+'_options '+( (i == 0) ? 'active' : '' )+'"><button class="button helper-button clear" type="button" tabindex="-1"><span class="mif-cross"></span></button>'+( (list_config[j] != "version") ? '<small>Platform specific options (--)</small>': '')+'</div>')
      }
      for(let j = 0, length2 = list_config_debug_release.length; j < length2; j++){
        if (!$("#form-cordova-settings .container-input-platform-"+list_config_debug_release[j])) {
          break
        }

        $("#form-cordova-settings .debug .container-input-platform-"+list_config_debug_release[j]).html('')
        $("#form-cordova-settings .release .container-input-platform-"+list_config_debug_release[j]).html('')
        
        $("#form-cordova-settings .debug .container-input-platform-"+list_config_debug_release[j]).append('<div class="input-control text full-size " data-role="input"><input type="text" data-mode="debug" data-platform="'+platform+'" class="'+platform+'_'+list_config_debug_release[j]+'_debug platform platform_'+list_config_debug_release[j]+'_options '+( (i == 0) ? 'active' : '' )+'"><button class="button helper-button clear" type="button" tabindex="-1"><span class="mif-cross"></span></button><small>Platform specific options (--)</small></div>')
        $("#form-cordova-settings .release .container-input-platform-"+list_config_debug_release[j]).append('<div class="input-control text full-size " data-role="input"><input type="text" data-mode="release" data-platform="'+platform+'" class="'+platform+'_'+list_config_debug_release[j]+'_release platform platform_'+list_config_debug_release[j]+'_options '+( (i == 0) ? 'active' : '' )+'"><button class="button helper-button clear" type="button" tabindex="-1"><span class="mif-cross"></span></button><small>Platform specific options (--)</small></div>')
      }
    }

    for(let j = 0, length2 = list_config.length; j < length2; j++){
      if ( $("#form-cordova-settings .cli_"+list_config[j]+"_options").length > 0 ) {
        $("#form-cordova-settings .cli_"+list_config[j]+"_options").val( data_project.cordova_settings["cli_"+list_config[j]+"_options"] )
      }

      $("#form-cordova-settings .platform_"+list_config[j]+"_options").each(function(index, item){
        $(this).val(data_project.cordova_settings["platform_"+list_config[j]+"_options"][$(this).attr("data-platform")])
      })
    }

    for(let j = 0, length2 = list_config_debug_release.length; j < length2; j++){
      if ( $("#form-cordova-settings .cli_"+list_config_debug_release[j]+"_options").length > 0 ) {
        $("#form-cordova-settings .cli_"+list_config_debug_release[j]+"_options").val( data_project.cordova_settings["cli_"+list_config_debug_release[j]+"_options"] )
      }

      $("#form-cordova-settings .platform_"+list_config_debug_release[j]+"_options").each(function(index, item){
        $(this).val(data_project.cordova_settings["platform_"+list_config_debug_release[j]+"_options"][$(this).attr("data-mode")][$(this).attr("data-platform")])
      })
    }

    $("#form-cordova-settings .platform_list").on("change", function(event) {
      let curr_platform = $(this).val()
      let mustActive = $(this).parent().find('.platform[data-platform="'+curr_platform+'"]')
      $(this).parent().find('.platform.active').toggleClass("active");
      $(mustActive).toggleClass("active");
    })

    $("#form-cordova-settings .mode_list").on("change", function(event) {
      let curr_mode = $(this).val()
      let mustActive = $(this).parent().find('.'+curr_mode+'.mode')
      $(this).parent().find('.mode.active').toggleClass("active");
      $(mustActive).toggleClass("active");
    })

    $("#global-cordova .use_local_cli").change(function(event){
      let id = $(this).attr("data-toggle-show")
      if($(this).prop("checked")){
        $("#"+id).removeClass("hidden")
        $("#"+id+" input.cordova-version").attr("data-validate-func", "required")
        $("#"+id+" input.cordova-version").attr("data-validate-hint", "This field can not be empty!")
        $("#"+id+" input.cordova-version").attr("data-validate-hint-position", "top")
        $('#global-cordova .cli_custom_path').removeAttr("data-validate-func")
        $('#global-cordova .cli_custom_path').removeAttr("data-validate-hint")
        $('#global-cordova .cli_custom_path').removeAttr("data-validate-hint-position")
        $('#global-cordova .cli_custom_path').removeClass("required")
      }
      else {
        $("#"+id).addClass("hidden")
        $("#"+id+" input.cordova-version").removeAttr("data-validate-func")
        $("#"+id+" input.cordova-version").removeAttr("data-validate-hint")
        $("#"+id+" input.cordova-version").removeAttr("data-validate-hint-position")
        $('#global-cordova .cli_custom_path').attr("data-validate-func")
        $('#global-cordova .cli_custom_path').attr("data-validate-hint")
        $('#global-cordova .cli_custom_path').attr("data-validate-hint-position")
        $('#global-cordova .cli_custom_path').addClass("required")
      }
    })

    $("#global-cordova .working_directory").val(data_project.cordova_settings.working_directory)

    $("#global-cordova .cli_custom_path").val(data_project.cordova_settings.cli_custom_path)

    $("#global-cordova .use_local_cli").prop('checked', data_project.cordova_settings.use_local_cli)
    $("#global-cordova .use_local_cli").change()

    if (data_project.cordova_settings.use_local_cli) {
      $("#custom-cordova-version input.cordova-version").val(data_project.cordova_settings.package_json.dependencies.cordova)
    }

    $("#form-cordova-settings").on("submit", function(event) {
      event.preventDefault()

      $('.overlay').show()
      
      let cli_global_options = $("#form-cordova-settings .cli_global_options").val()
      let cli_compile_options = $("#form-cordova-settings .cli_compile_options").val()
      let cli_build_options = $("#form-cordova-settings .cli_build_options").val()
      let cli_run_options = $("#form-cordova-settings .cli_run_options").val()

      cli_global_options = (cli_global_options) ? cli_global_options.filter(function(item){ return (item !== "") ? true : false }) : []
      cli_compile_options = (cli_compile_options) ? cli_compile_options.filter(function(item){ return (item !== "") ? true : false }) : []
      cli_build_options = (cli_build_options) ? cli_build_options.filter(function(item){ return (item !== "") ? true : false }) : []
      cli_run_options = (cli_run_options) ? cli_run_options.filter(function(item){ return (item !== "") ? true : false }) : []

      let cordova_settings = {
        "serve_port": $("#form-cordova-settings .serve_port").val().trim(),
        "cli_global_options": cli_global_options,
        "cli_compile_options": cli_compile_options,
        "cli_build_options": cli_build_options,
        "cli_run_options": cli_run_options,
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
        },
        "working_directory": $("#global-cordova .working_directory").val(),
        "cli_custom_path": $("#global-cordova .cli_custom_path").val(),
        "use_local_cli": ($("#global-cordova .use_local_cli").prop('checked')) ? true : false,
      }

      if (cordova_settings.use_local_cli) {
        cordova_settings.package_json = {
          "dependencies": {
            "cordova": $("#custom-cordova-version input.cordova-version").val()
          }
        }
      }
      else {
        cordova_settings.package_json = {}
      }

      for(let j = 0, length2 = list_config.length; j < length2; j++){
        for(let i = 0, length1 = data_project.cordova_settings.installed_platform.length; i < length1; i++){
          let platform = data_project.cordova_settings.installed_platform[i]
          if ($('#form-cordova-settings .'+platform+'_'+list_config[j]).length > 0) {
            cordova_settings["platform_"+list_config[j]+"_options"][platform] = $('#form-cordova-settings .'+platform+'_'+list_config[j]).val()
          }
        }
      }

      for(let j = 0, length2 = list_config_debug_release.length; j < length2; j++){
        for(let i = 0, length1 = data_project.cordova_settings.installed_platform.length; i < length1; i++){
          let platform = data_project.cordova_settings.installed_platform[i]
          if ($('#form-cordova-settings .'+platform+'_'+list_config_debug_release[j]+"_debug").length > 0) {
            cordova_settings["platform_"+list_config_debug_release[j]+"_options"].debug[platform] = $('#form-cordova-settings .'+platform+'_'+list_config_debug_release[j]+"_debug").val()
          }
          if ($('#form-cordova-settings .'+platform+'_'+list_config_debug_release[j]+"_release").length > 0) {
            cordova_settings["platform_"+list_config_debug_release[j]+"_options"].release[platform] = $('#form-cordova-settings .'+platform+'_'+list_config_debug_release[j]+"_release").val()
          }
        }
      }

      ipcRenderer.send("form-cordova-settings", cordova_settings)
    })
  }
}