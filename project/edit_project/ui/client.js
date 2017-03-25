"use strict";

const fs = require('fs-extra')
const path = require('path')
const util = require('../../../js/util.js')
const electron = require('electron')
const {ipcMain} = require('electron')
const SocketWindow = require('../../../js/SocketWindow.js')
const PACKAGE_PATH = path.resolve(path.join(__dirname, "..", "..", ".."))
const app = new SocketWindow('localhost', 11112, __dirname, 900, 700)

let project_dir_name = ""
let jc_project_settings_dir_name = ""
let settings_file = ""
let flow_settings = ""
let data_project = {}

function difference(a, b) {
    return a.filter(function(i) {return b.indexOf(i) < 0;});
};

function get_update_type(_old, _new){
  return {
    "must_delete": difference(_old, _new),
    "must_add": difference(_new, _old)
  }
}
app.listenSocketCommand('load_project_settings', (data) => {
  project_dir_name = data.settings.project_dir_name
  jc_project_settings_dir_name = data.settings.settings_dir_name
  settings_file = path.join(jc_project_settings_dir_name, "project_details.json")
  flow_settings = path.join(jc_project_settings_dir_name, "flow_settings.json")
  data_project = data
  for(let i = 0, length1 = data.settings.project_details.type.length; i < length1; i++){
    let type = data.settings.project_details.type[i]
    if (fs.existsSync(__dirname+"/../../"+type+"/edit_project/client.js") ){
      let client_js = require(__dirname+"/../../"+type+"/edit_project/client.js")
      client_js.prepareClientJs({
        "app": app,
        "util": util,
        "data_project": data,
        "ipcMain": ipcMain,
        "electron": electron,
        "path": path,
        "fs": fs
      })
    }
  }
  app.sendWeb("load_config", data)
})

ipcMain.on('form-project-details', (event, project_details) => {
  if (fs.existsSync(settings_file)) {
  
    let types = get_update_type(data_project.settings.project_details.type, project_details.type)

    if(types.must_delete){
      for(let i = 0, length1 = types.must_delete.length; i < length1; i++){
        let project_type_default_config =  {}
        try {
          project_type_default_config = require('../../default_settings/'+types.must_delete[i]+'/default_config.js')
        } catch(e) {
          continue
        }
        if(project_type_default_config.flow_settings) {
          for (let key in project_type_default_config.flow_settings) {
            if (Array.isArray(data_project.settings.flow_settings[key])){
              data_project.settings.flow_settings[key] = difference(data_project.settings.flow_settings[key], project_type_default_config.flow_settings[key])
            }
          }
        }
        if(project_type_default_config[types.must_delete[i]+"_settings"]){
          fs.unlinkSync(path.join(jc_project_settings_dir_name, types.must_delete[i]+"_settings.json"))
          app.sendWeb("delete-item-menu", types.must_delete[i])
        }
      }
    }
    if(types.must_add){
      for(let i = 0, length1 = types.must_add.length; i < length1; i++){
        let project_type_default_config =  {}
        try {
          project_type_default_config = require('../../default_settings/'+types.must_add[i]+'/default_config.js')
        } catch(e) {
          continue
        }
        if(project_type_default_config.flow_settings) {
          for (let key in project_type_default_config.flow_settings) {
            if (Array.isArray(data_project.settings.flow_settings[key])){
              data_project.settings.flow_settings[key] = data_project.settings.flow_settings[key].concat(project_type_default_config.flow_settings[key])
            }
          }
        }
        if(project_type_default_config[types.must_add[i]+"_settings"]){
          util.openWithSync((fd) => {
            fs.writeFileSync(fd, JSON.stringify(project_type_default_config[types.must_add[i]+"_settings"], null, 2))
          }, path.join(jc_project_settings_dir_name, types.must_add[i]+"_settings.json"), "w+")
        }
      }
    }

    try{
      util.openWithSync((fd) => {
        fs.writeFileSync(fd, JSON.stringify(project_details, null, 2))
      }, settings_file, "w+")
    }
    catch(e){
      app.sendWeb("error", `Can't modify "${settings_file}"\nError: ${e}.`)
      return
    }
    try{
      util.openWithSync((fd) => {
        fs.writeFileSync(fd, JSON.stringify(data_project.settings.flow_settings, null, 2))
      }, flow_settings, "w+")
    }
    catch(e){
      app.sendWeb("error", `Can't modify "${flow_settings}"\nError: ${e}.`)
      return
    }
    try{
      util.openWithSync((fd) => {
        let include = data_project.settings.flow_settings.include.join("\n")
        let ignore = data_project.settings.flow_settings.ignore.join("\n")
        let libs = data_project.settings.flow_settings.libs.join("\n")
        let options = data_project.settings.flow_settings.options.map(function(item){
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
      }, path.join(project_dir_name, ".flowconfig"), "w+")
    }
    catch(e){
      app.sendWeb("error", `Can't modify "${path.join(project_dir_name, ".flowconfig")}"\nError: ${e}.`)
      return
    }
    data_project.settings.project_details = project_details
    app.sendWeb("success", "Successfully saved.")
    app.sendWeb("load_config", data_project)
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
    data_project.settings.flow_settings = flow_form_settings
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
        fs.writeFileSync(fd, str.replace(":PACKAGE_PATH", PACKAGE_PATH))
      }, path.join(project_dir_name, ".flowconfig"), "w+")

      app.sendWeb("load_config", data_project)
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

app.start(() => {
  app.window.setResizable(false)
})
