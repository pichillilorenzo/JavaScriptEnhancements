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

    $("#form-ionic-settings").on("submit", function(event) {
      event.preventDefault()

      let ionic_settings = {}

      ipcRenderer.send("form-ionic-settings", ionic_settings)
    })
  }
}