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

    utilWeb.setMulitpleSelectValues("#cli_global_options", data_project.cordova_settings.cli_global_options)

    $("#form-cordova-settings").on("submit", (event) => {
      event.preventDefault()
      let cordova_settings = {
        "cli_global_options": utilWeb.getMulitpleSelectValues("#cli_global_options")
      }
      ipcRenderer.send("form-cordova-settings", cordova_settings)
    })
  }
}