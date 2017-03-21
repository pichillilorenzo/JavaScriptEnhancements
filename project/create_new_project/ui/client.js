"use strict";

const fs = require('fs-extra')
const path = require('path')
let default_config = require('../default_config.js')
const util = require('../../../js/util.js')
const electron = require('electron')
const {ipcMain} = require('electron')
const SocketWindow = require('../../../js/SocketWindow.js')
let project_type = ""

const app = new SocketWindow('localhost', 11111, __dirname, 460, 840)

app.listenSocketCommand('close_window', (data) => {
  app.app.quit()
})

app.listenSocketCommand('result_flow_init', (data) => {

  if(!data.result[0]) {
    app.sendWeb("error", "Can't init Flow: "+data.result[1])
    return
  }

  let flowconfig = path.join(data.project.path, ".flowconfig")
  util.openWithSync((fd) => {
    let include = default_config.flow_settings.include.join("\n")
    let ignore = default_config.flow_settings.ignore.join("\n")
    let libs = default_config.flow_settings.libs.join("\n")
    let options = default_config.flow_settings.options.map(function(item){
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
  }, flowconfig, "w+")

  let sublime_project_file_name = util.clearString(data.project.project_name)
  let data_to_send = {
    "type": project_type,
    "project": path.join(data.project.path, sublime_project_file_name+".sublime-project"),
    "command": "open_project"
  }
  util.openWithSync((fd) => {
    fs.writeFileSync(fd, JSON.stringify(default_config.sublime_project, null, 2))
  }, path.join(data.project.path, sublime_project_file_name+".sublime-project"), "w+")

  app.sendSocketJson(data_to_send)

})

ipcMain.on('data', (event, project) => {

  if (!fs.existsSync(project.path)){
    fs.mkdirsSync(project.path)
  }

  let jc_project_settings = path.join(project.path, ".jc-project-settings")
  let bookmarks_path = path.join(jc_project_settings, "bookmarks.json")
  let settings_file = path.join(jc_project_settings, "project_details.json")
  let flow_settings = path.join(jc_project_settings, "flow_settings.json")
  project_type = project.type
  if( project_type ){
    default_config = require('../'+project_type+'/default_config.js')
  }

  if (!fs.existsSync(jc_project_settings)) {
    fs.mkdirSync(jc_project_settings)
    util.openWithSync((fd) => {
      default_config.project_details = JSON.parse(JSON.stringify(project))
      delete default_config.project_details.path
      fs.writeFileSync(fd, JSON.stringify(default_config.project_details, null, 2))
    }, settings_file, "w+")

    util.openWithSync((fd) => {
      fs.writeFileSync(fd, JSON.stringify(default_config.flow_settings, null, 2))
    }, flow_settings, "w+")

    util.openWithSync((fd) => {
      fs.writeFileSync(fd, JSON.stringify(default_config.bookmarks, null, 2))
    }, bookmarks_path, "w+")

    app.sendSocketJson({
      "command": "try_flow_init",
      "project": project
    })
  }
  else{
    app.sendWeb("error", "Can't create the project! A project already exists in that folder.")
  }

})

app.start(() => {
  app.window.setResizable(false)
})
