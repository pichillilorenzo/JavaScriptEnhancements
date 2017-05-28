module.exports = {
  "title": "Ionic settings",
  "subtitle": "",
  "icon": "img/ionic-logo.png",
  "tile_bg_color": "bg-cyan",
  "tile_fg_color": "fg-white",
  "prepareClientJs": (variables) => {
    let app = variables.app
    let ipcMain = variables.ipcMain
    let util = variables.util
    let fs = variables.fs
    let data_project = variables.data_project
    let path = variables.path
    const npm = require('npm')

    ipcMain.on("form-ionic-settings",(event, ionic_settings) => {
      ionic_settings = util.mergeObjectsRecursive(data_project.settings.ionic_settings, ionic_settings, app)
      try{
        util.openWithSync((fd) => {
          fs.writeFileSync(fd, JSON.stringify(ionic_settings, null, 2))
        }, path.join(data_project.settings.settings_dir_name, "ionic_settings.json"), "w+")
      }
      catch(e){
        app.sendWeb("error", `Can't modify "${path.join(data_project.settings.settings_dir_name, "ionic_settings.json")}"\nError: ${e}.`)
        return
      }

      if (ionic_settings.package_json) {
        let package_json = JSON.parse(fs.readFileSync(path.join(data_project.settings.settings_dir_name, "package.json"), {encoding: 'utf8'}))
        package_json = util.mergeObjectsRecursive(package_json, data_project.settings.ionic_settings.package_json)
        util.openWithSync((fd) => {
          fs.writeFileSync(fd, JSON.stringify(package_json, null, 2))
        }, path.join(data_project.settings.settings_dir_name, "package.json"), "w+")
        process.chdir(path.join(data_project.settings.settings_dir_name));
        npm.load(function(err){
          npm.commands.install(function(err, data){
            if(err){
              app.sendWeb("error", JSON.stringify(err, null, 2))
              return
            }
            data_project.ionic_settings = ionic_settings
            app.sendWeb("success", "Successfully saved.")
            app.sendWeb("load_config", data_project)
          })

        })
      }
      else {
        data_project.ionic_settings = ionic_settings
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

    let list_config = ["platform", "build", "run", "resources", "state", "version"]
    let list_config_debug_release = ["emulate", "run", "build", "compile"]
    let input_text_command = ["address", "port", "livereload-port", "browser", "browseroption", "platform"]
    let load_input_text_command = ["emulate", "run", "serve"]

    for(let i = 0, length1 = data_project.ionic_settings.installed_platform.length; i < length1; i++){
      let platform = data_project.ionic_settings.installed_platform[i]
      $("#form-ionic-settings .platform_list").append('<option value="'+platform+'" '+( (i == 0) ? 'selected="selected"' : '' )+'>'+platform+'</option>')
      for(let j = 0, length2 = list_config.length; j < length2; j++){
        if (!$("#form-ionic-settings .container-input-platform-"+list_config[j])) {
          break
        }
        $("#form-ionic-settings .container-input-platform-"+list_config[j]).append('<div class="input-control text full-size " data-role="input"><input type="text" data-platform="'+platform+'" class="'+platform+'_'+list_config[j]+' form-control platform platform_'+list_config[j]+'_options '+( (i == 0) ? 'active' : '' )+'"><button class="button helper-button clear" type="button" tabindex="-1"><span class="mif-cross"></span></button><small>Platform specific options (--)</small></div>')
      }
      for(let j = 0, length2 = list_config_debug_release.length; j < length2; j++){
        if (!$("#form-ionic-settings .container-input-platform-"+list_config_debug_release[j])) {
          break
        }

        $("#form-ionic-settings .debug .container-input-platform-"+list_config_debug_release[j]).html('')
        $("#form-ionic-settings .release .container-input-platform-"+list_config_debug_release[j]).html('')

        $("#form-ionic-settings .debug .container-input-platform-"+list_config_debug_release[j]).append('<div class="input-control text full-size " data-role="input"><input type="text" data-mode="debug" data-platform="'+platform+'" class="'+platform+'_'+list_config_debug_release[j]+'_debug form-control platform platform_'+list_config_debug_release[j]+'_options '+( (i == 0) ? 'active' : '' )+'"><button class="button helper-button clear" type="button" tabindex="-1"><span class="mif-cross"></span></button><small>Platform specific options (--)</small></div>')
        $("#form-ionic-settings .release .container-input-platform-"+list_config_debug_release[j]).append('<div class="input-control text full-size " data-role="input"><input type="text" data-mode="release" data-platform="'+platform+'" class="'+platform+'_'+list_config_debug_release[j]+'_release form-control platform platform_'+list_config_debug_release[j]+'_options '+( (i == 0) ? 'active' : '' )+'"><button class="button helper-button clear" type="button" tabindex="-1"><span class="mif-cross"></span></button><small>Platform specific options (--)</small></div>')
      }
    }

    for(let i = 0, length1 = load_input_text_command.length; i < length1; i++){
      for(let j = 0, length2 = input_text_command.length; j < length2; j++){
        if ( $("#form-ionic-settings ."+input_text_command[j]+"_"+load_input_text_command[i]).length > 0 ) {
          let value = ""
          let index = data_project.ionic_settings["cli_"+load_input_text_command[i]+"_options"].indexOf("--"+input_text_command[j])
          if (index >= 0) {
            value = data_project.ionic_settings["cli_"+load_input_text_command[i]+"_options"][index+1]
          }
          $("#form-ionic-settings ."+input_text_command[j]+"_"+load_input_text_command[i]).val(value)
        }
      }
    }

    for(let j = 0, length2 = list_config.length; j < length2; j++){
      if ( $("#form-ionic-settings .cli_"+list_config[j]+"_options").length > 0 ) {
        $("#form-ionic-settings .cli_"+list_config[j]+"_options").val( data_project.ionic_settings["cli_"+list_config[j]+"_options"] )
      }

      $("#form-ionic-settings .platform_"+list_config[j]+"_options").each(function(index, item){
        $(this).val(data_project.ionic_settings["platform_"+list_config[j]+"_options"][$(this).attr("data-platform")])
      })
    }

    for(let j = 0, length2 = list_config_debug_release.length; j < length2; j++){
      if ( $("#form-ionic-settings .cli_"+list_config_debug_release[j]+"_options").length > 0 ) {
        $("#form-ionic-settings .cli_"+list_config_debug_release[j]+"_options").val( data_project.ionic_settings["cli_"+list_config_debug_release[j]+"_options"] )
      }

      $("#form-ionic-settings .platform_"+list_config_debug_release[j]+"_options").each(function(index, item){
        $(this).val(data_project.ionic_settings["platform_"+list_config_debug_release[j]+"_options"][$(this).attr("data-mode")][$(this).attr("data-platform")])
      })
    }

    $("#form-ionic-settings .platform_list").on("change", function(event) {
      let curr_platform = $(this).val()
      let mustActive = $(this).parent().find('.platform[data-platform="'+curr_platform+'"]')
      $(this).parent().find('.platform.active').toggleClass("active");
      $(mustActive).toggleClass("active");
    })

    $("#form-ionic-settings .mode_list").on("change", function(event) {
      let curr_mode = $(this).val()
      let mustActive = $(this).parent().find('.'+curr_mode+'.mode')
      $(this).parent().find('.mode.active').toggleClass("active");
      $(mustActive).toggleClass("active");
    })

    $("#global-ionic .use_local_cli").change(function(event){
      let id = $(this).attr("data-toggle-show")
      if($(this).prop("checked")){
        $("#"+id).removeClass("hidden")
        $("#"+id+" input.ionic-version").attr("data-validate-func", "required")
        $("#"+id+" input.ionic-version").attr("data-validate-hint", "This field can not be empty!")
        $("#"+id+" input.ionic-version").attr("data-validate-hint-position", "top")
        $('#global-ionic .cli_custom_path').removeAttr("data-validate-func")
        $('#global-ionic .cli_custom_path').removeAttr("data-validate-hint")
        $('#global-ionic .cli_custom_path').removeAttr("data-validate-hint-position")
        $('#global-ionic .cli_custom_path').removeClass("required")
      }
      else {
        $("#"+id).addClass("hidden")
        $("#"+id+" input.ionic-version").removeAttr("data-validate-func", "required")
        $("#"+id+" input.ionic-version").removeAttr("data-validate-hint", "This field can not be empty!")
        $("#"+id+" input.ionic-version").removeAttr("data-validate-hint-position", "top")
        $('#global-ionic .cli_custom_path').attr("data-validate-func")
        $('#global-ionic .cli_custom_path').attr("data-validate-hint")
        $('#global-ionic .cli_custom_path').attr("data-validate-hint-position")
        $('#global-ionic .cli_custom_path').addClass("required")
      }
    })

    $("#global-ionic .working_directory").val(data_project.ionic_settings.working_directory)

    $("#global-ionic .cli_custom_path").val(data_project.ionic_settings.cli_custom_path)

    $("#global-ionic .use_local_cli").prop('checked', data_project.ionic_settings.use_local_cli)
    $("#global-ionic .use_local_cli").change()

    if (data_project.ionic_settings.use_local_cli) {
      $("#custom-ionic-version input.ionic-version").val(data_project.ionic_settings.package_json.dependencies.ionic)
    }

    $("#form-ionic-settings").on("submit", function(event) {
      event.preventDefault()

      let cli_platform_options = $("#form-ionic-settings .cli_platform_options").val()
      let cli_compile_options = $("#form-ionic-settings .cli_compile_options").val()
      let cli_emulate_options = $("#form-ionic-settings .cli_emulate_options").val()
      let cli_build_options = $("#form-ionic-settings .cli_build_options").val()
      let cli_run_options = $("#form-ionic-settings .cli_run_options").val()
      let cli_serve_options = $("#form-ionic-settings .cli_serve_options").val()
      let cli_resources_options = $("#form-ionic-settings .cli_resources_options").val()
      let cli_state_options = $("#form-ionic-settings .cli_state_options").val()

      cli_platform_options = (cli_platform_options) ? cli_platform_options.filter(function(item){ return (item !== "") ? true : false }) : []
      cli_compile_options = (cli_compile_options) ? cli_compile_options.filter(function(item){ return (item !== "") ? true : false }) : []
      cli_emulate_options = (cli_emulate_options) ? cli_emulate_options.filter(function(item){ return (item !== "") ? true : false }) : []
      cli_build_options = (cli_build_options) ? cli_build_options.filter(function(item){ return (item !== "") ? true : false }) : []
      cli_run_options = (cli_run_options) ? cli_run_options.filter(function(item){ return (item !== "") ? true : false }) : []
      cli_serve_options = (cli_serve_options) ? cli_serve_options.filter(function(item){ return (item !== "") ? true : false }) : []
      cli_resources_options = (cli_resources_options) ? cli_resources_options.filter(function(item){ return (item !== "") ? true : false }) : []
      cli_state_options = (cli_state_options) ? cli_state_options.filter(function(item){ return (item !== "") ? true : false }) : []

      let ionic_settings = {
        "cli_platform_options": cli_platform_options,
        "cli_compile_options": cli_compile_options,
        "cli_build_options": cli_build_options,
        "cli_emulate_options": cli_emulate_options,
        "cli_run_options": cli_run_options,
        "cli_serve_options": cli_serve_options,   
        "cli_resources_options": cli_resources_options,
        "cli_state_options": cli_state_options,
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
        "platform_emulate_options": {
          "debug": {},
          "release": {}
        },
        "working_directory": $("#global-ionic .working_directory").val(),
        "cli_custom_path": $("#global-ionic .cli_custom_path").val(),
        "use_local_cli": ($("#global-ionic .use_local_cli").prop('checked')) ? true : false,
      }
      
      if (ionic_settings.use_local_cli) {
        ionic_settings.package_json = {
          "dependencies": {
            "ionic": $("#custom-ionic-version input.ionic-version").val()
          }
        }
      }
      else {
        ionic_settings.package_json = {}
      }

      for(let i = 0, length1 = load_input_text_command.length; i < length1; i++){
        for(let j = 0, length2 = input_text_command.length; j < length2; j++){
          if ($("#form-ionic-settings ."+input_text_command[j]+"_"+load_input_text_command[i]).length > 0 && $("#form-ionic-settings ."+input_text_command[j]+"_"+load_input_text_command[i]).val().trim()) {
            ionic_settings["cli_"+load_input_text_command[i]+"_options"] = ionic_settings["cli_"+load_input_text_command[i]+"_options"].concat(["--"+input_text_command[j], $("#form-ionic-settings ."+input_text_command[j]+"_"+load_input_text_command[i]).val().trim()])
          }
        }
      }

      for(let j = 0, length2 = list_config.length; j < length2; j++){
        for(let i = 0, length1 = data_project.ionic_settings.installed_platform.length; i < length1; i++){
          let platform = data_project.ionic_settings.installed_platform[i]
          if ($('#form-ionic-settings .'+platform+'_'+list_config[j]).length > 0) {
            ionic_settings["platform_"+list_config[j]+"_options"][platform] = $('#form-ionic-settings .'+platform+'_'+list_config[j]).val()
          }
        }
      }
      
      for(let j = 0, length2 = list_config_debug_release.length; j < length2; j++){
        for(let i = 0, length1 = data_project.ionic_settings.installed_platform.length; i < length1; i++){
          let platform = data_project.ionic_settings.installed_platform[i]
          if ($('#form-ionic-settings .'+platform+'_'+list_config_debug_release[j]+"_debug").length > 0) {
            ionic_settings["platform_"+list_config_debug_release[j]+"_options"].debug[platform] = $('#form-ionic-settings .'+platform+'_'+list_config_debug_release[j]+"_debug").val()
          }
          if ($('#form-ionic-settings .'+platform+'_'+list_config_debug_release[j]+"_release").length > 0) {
            ionic_settings["platform_"+list_config_debug_release[j]+"_options"].release[platform] = $('#form-ionic-settings .'+platform+'_'+list_config_debug_release[j]+"_release").val()
          }
        }
      }

      ipcRenderer.send("form-ionic-settings", ionic_settings)
    })

  }
}