"use strict";

const fs = require('fs-extra')
const path = require('path')
const util = require('../../../js/util.js')
const electron = require('electron')
const {ipcMain} = require('electron')
const SocketWindow = require('../../../js/SocketWindow.js')

const app = new SocketWindow('localhost', 11112, __dirname, 900, 700)

let project_dir_name = ""
let jc_project_settings_dir_name = ""
let settings_file = ""
let flow_settings = ""

app.listenSocketCommand('load_project_settings', (data) => {
  project_dir_name = data.settings.project_dir_name
  jc_project_settings_dir_name = data.settings.settings_dir_name
  settings_file = path.join(jc_project_settings_dir_name, "project_details.json")
  flow_settings = path.join(jc_project_settings_dir_name, "flow_settings.json")
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

ipcMain.on('form-flow-settings', (event, flow_form_settings) => {
  if (fs.existsSync(flow_settings)) {
    try{
      util.openWithSync((fd) => {
        fs.writeFileSync(fd, JSON.stringify(flow_form_settings, null, 2))
      }, flow_settings, "w+")
    }
    catch(e){
      app.sendWeb("error", `Can't modify "${flow_settings}"\nError: ${e}.`)
      return
    }
    try{
      util.openWithSync((fd) => {
        let include = flow_form_settings.include.join("\n")
        let ignore = flow_form_settings.ignore.join("\n")
        let libs = flow_form_settings.libs.join("\n")
        let options = flow_form_settings.options.map(function(item){
          return item[0].trim()+"="+item[1].trim()
        }).join("\n")

        let str = `[ignore]
${ignore}
[include]
${include}
[libs]
${libs}
[options]
${options}
`
        fs.writeFileSync(fd, str)
      }, path.join(project_dir_name, ".flowconfig"), "w+")
      app.sendWeb("success", "Successfully saved.")
    }
    catch(e){
      app.sendWeb("error", `Can't modify "${path.join(project_dir_name, ".flowconfig")}"\nError: ${e}.`)
      return
    }
  }
  else{
    app.sendWeb("error", `File "${flow_settings}" doesn't exists.`)
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
