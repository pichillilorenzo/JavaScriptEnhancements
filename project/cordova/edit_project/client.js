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

    let i = 0
    for (let platform in data_project.cordova_settings.platform_versions) {
      $("#platform_versions").append('<option value="'+platform+'" '+( (i == 0) ? 'selected="selected"' : '' )+'>'+platform+'</option>')
      $(".container-input-platform-version").append('<input type="text" id="'+platform+'_version" data-platform="'+platform+'" class="form-control platform_version '+( (i == 0) ? 'active' : '' )+'">')
      i++
    }

    $("#platform_versions")

    utilWeb.setMulitpleSelectValues("#cli_global_options", data_project.cordova_settings.cli_global_options)

    $(".platform_version").each(function(index, item){
      $(this).val(data_project.cordova_settings.platform_versions[$(this).attr("data-platform")])
    })

    $("#platform_versions").on("change", function(event) {
      let curr_platform = $(this).val()
      $(this).parent().find('.platform_version.active').toggleClass("active");
      $("#"+curr_platform+"_version").toggleClass("active");
    })

    $("#form-cordova-settings").on("submit", function(event) {
      event.preventDefault()

      let cordova_settings = {
        "cli_global_options": utilWeb.getMulitpleSelectValues("#cli_global_options"),
        "platform_versions": {}
      }
      for (let platform in data_project.cordova_settings.platform_versions) {
        cordova_settings.platform_versions[platform] = ($('#'+platform+'_version')) ? $('#'+platform+'_version').val() : ""
      }

      ipcRenderer.send("form-cordova-settings", cordova_settings)
    })
  }
}