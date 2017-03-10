"use strict";

const fs = require('fs-extra')
const path = require('path')
const util = require('../../js/util.js')
const electron = require('electron')
const {ipcMain} = require('electron')
const SocketWindow = require('../../js/SocketWindow.js')

const app = new SocketWindow('localhost', 11112, __dirname, 900, 700)

let jc_project_settings = ""
let settings_file = ""
let flow_settings = ""

app.listenSocketCommand('load_project_settings', (data) => {
  jc_project_settings = data.settings.settings_dir_name
  settings_file = path.join(jc_project_settings, "project_details.json")
  flow_settings = path.join(jc_project_settings, "flow_settings.json")
  app.sendWeb("load_config", data)
})

ipcMain.on('form-project-details', (event, project_details) => {
  if (fs.existsSync(settings_file)) {
    try{
      util.openWithSync((fd) => {
        fs.writeFileSync(fd, JSON.stringify(project_details, null, 2))
      }, settings_file, "w+")
      app.sendWeb("success", "Successfully saved.")
    }
    catch(e){
      app.sendWeb("error", `Can't modify "${settings_file}"\nError: ${e}.`)
    }
  }
  else{
    app.sendWeb("error", `File "${settings_file}" doesn't exists.`)
  }
})
// ipcMain.on('data', (event, project) => {
//   if (!fs.existsSync(project.path)){
//     fs.mkdirsSync(project.path)
//   }

//   let jc_project_settings = path.join(project.path, ".jc-project-settings")
//   let settings_file = path.join(jc_project_settings, "project_details.json")
//   let flow_settings = path.join(jc_project_settings, "flow_settings.json")

//   if (!fs.existsSync(jc_project_settings)) {
//     fs.mkdirSync(jc_project_settings)

//     util.openWithSync((fd) => {
//       default_config.project_details.project_name = project.name
//       fs.writeFileSync(fd, JSON.stringify(default_config.project_details, null, 2))
//     }, settings_file, "w+")

//     util.openWithSync((fd) => {
//       fs.writeFileSync(fd, JSON.stringify(default_config.flow_settings, null, 2))
//     }, flow_settings, "w+")

//     app.sendSocketJson({
//       "command": "try_flow_init",
//       "project": project
//     })

//   }
//   else{
//     app.sendWeb("error", "Can't create the project! A project already exists in that folder.")
//   }

// })

app.start(() => {
  app.window.setResizable(false)
})
