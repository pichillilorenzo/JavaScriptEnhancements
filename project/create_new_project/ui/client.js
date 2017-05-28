"use strict";

const npm = require('npm')
const fs = require('fs-extra')
const path = require('path')
let default_config = require('../default_config.js')
const util = require('../../../js/util.js')
const electron = require('electron')
const {ipcMain} = require('electron')
const SocketWindow = require('../../../js/SocketWindow.js')
const PACKAGE_PATH = path.resolve(path.join(__dirname, "..", "..", ".."))

const app = new SocketWindow('localhost', 11111, __dirname, 460, 640)

app.listenSocketCommand('close_window', (data) => {
  app.app.quit()
})

app.listenSocketCommand('result_flow_init', (data) => {

  if(!data.result[0]) {
    app.sendWeb("error", "Can't init Flow: "+data.result[1])
    return
  }

  let flowconfig = path.join(data.project_data.path, ".flowconfig")
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
    fs.writeFileSync(fd, str.replace(":PACKAGE_PATH", PACKAGE_PATH))
  }, flowconfig, "w+")

  let sublime_project_file_name = util.clearString(data.project_data.project_details.project_name)
  let data_to_send = {
    "project_data": data.project_data,
    "sublime_project_file_name": path.join(data.project_data.path, sublime_project_file_name+".sublime-project"),
    "command": "open_project"
  }
  util.openWithSync((fd) => {
    fs.writeFileSync(fd, JSON.stringify(default_config.sublime_project, null, 2))
  }, path.join(data.project_data.path, sublime_project_file_name+".sublime-project"), "w+")

  let package_json = {}
  for(let i = 0, length1 = data.project_data.project_details.type.length; i < length1; i++){
    if (data.project_data[data.project_data.project_details.type[i]+"_settings"] && data.project_data[data.project_data.project_details.type[i]+"_settings"].package_json) {
      package_json = util.mergeObjectsRecursive(package_json, data.project_data[data.project_data.project_details.type[i]+"_settings"].package_json)
    }
  }
  if (package_json) {
    util.openWithSync((fd) => {
      fs.writeFileSync(fd, JSON.stringify(package_json, null, 2))
    }, path.join(data.project_data.path, ".jc-project-settings", "package.json"), "w+")
    process.chdir(path.join(data.project_data.path, ".jc-project-settings"));
    npm.load(function(err){
      npm.commands.install(function(err, data){
        if(err){
          app.sendWeb("error", JSON.stringify(err, null, 2))
        }
        else {
          app.sendSocketJson(data_to_send)
        }
      })

    })
  }
  else {
    app.sendSocketJson(data_to_send)
  }
  
})

ipcMain.on('data', (event, project_data) => {
  
  if (!fs.existsSync(project_data.path)){
    fs.mkdirsSync(project_data.path)
  }

  let jc_project_settings = path.join(project_data.path, ".jc-project-settings")
  let bookmarks_path = path.join(jc_project_settings, "bookmarks.json")
  let project_details_file = path.join(jc_project_settings, "project_details.json")
  let project_settings = path.join(jc_project_settings, "project_settings.json")
  let flow_settings = path.join(jc_project_settings, "flow_settings.json")

  let project_type_default_settings = []
  /* project_data.project_details.type.length evaluate each time because of possible type dependecies */
  for(let i = 0; i < project_data.project_details.type.length; i++){
    let project_type_default_config = {}
    try {
      project_type_default_config = require('../../default_settings/'+project_data.project_details.type[i]+'/default_config.js')
      if (project_type_default_config.dependencies) {
        /* load dependencies */
        for(let j = 0, length2 = project_type_default_config.dependencies.length; j < length2; j++){
          let dipendency = project_type_default_config.dependencies[j]
          if (project_data.project_details.type.indexOf(dipendency) < 0) {
            project_data.project_details.type.push(dipendency)
          }
        }
      }
    } catch(e) {
      continue
    }
    if(project_type_default_config.project_details) {
      default_config.project_details.type = default_config.project_details.type.concat(project_type_default_config.project_details.type)
    }
    if(project_type_default_config.flow_settings) {
      for (let key in project_type_default_config.flow_settings) {
        if (Array.isArray(default_config.flow_settings[key])){
          default_config.flow_settings[key] = default_config.flow_settings[key].concat(project_type_default_config.flow_settings[key])
        }
      }
    }
    if(project_type_default_config[project_data.project_details.type[i]+"_settings"]){
      project_type_default_settings.push(
        [project_data.project_details.type[i], project_type_default_config[project_data.project_details.type[i]+"_settings"]]
      )
    }
  }

  if (!fs.existsSync(jc_project_settings)) {
    fs.mkdirSync(jc_project_settings)
    util.openWithSync((fd) => {
      default_config.project_details = JSON.parse(JSON.stringify(project_data.project_details)) // clone project object
      fs.writeFileSync(fd, JSON.stringify(default_config.project_details, null, 2))
    }, project_details_file, "w+")

    util.openWithSync((fd) => {
      default_config.project_settings = JSON.parse(JSON.stringify(project_data.project_settings))
      fs.writeFileSync(fd, JSON.stringify(default_config.project_settings, null, 2))
    }, project_settings, "w+")

    util.openWithSync((fd) => {
      fs.writeFileSync(fd, JSON.stringify(default_config.flow_settings, null, 2))
    }, flow_settings, "w+")

    util.openWithSync((fd) => {
      fs.writeFileSync(fd, JSON.stringify(default_config.bookmarks, null, 2))
    }, bookmarks_path, "w+")

    for(let i = 0, length1 = project_type_default_settings.length; i < length1; i++){

      if (!project_data[project_type_default_settings[i][0]+"_settings"]) {
        project_data[project_type_default_settings[i][0]+"_settings"] = {}
      }

      project_data[project_type_default_settings[i][0]+"_settings"].working_directory = project_data.path

      if (project_data[project_type_default_settings[i][0]+"_settings"]) {
        for (let key in project_data[project_type_default_settings[i][0]+"_settings"]) {
          project_type_default_settings[i][1][key] = project_data[project_type_default_settings[i][0]+"_settings"][key]
        }
      }
        
      util.openWithSync((fd) => {
        fs.writeFileSync(fd, JSON.stringify(project_type_default_settings[i][1], null, 2))
      }, path.join(jc_project_settings, project_type_default_settings[i][0]+"_settings.json"), "w+")
    }

    app.sendSocketJson({
      "command": "try_flow_init",
      "project_data": project_data
    })
  }
  else{
    app.sendWeb("error", "Can't create the project! A project already exists in that folder.")
  }

})

app.start(() => {
  app.window.setResizable(false)
})
