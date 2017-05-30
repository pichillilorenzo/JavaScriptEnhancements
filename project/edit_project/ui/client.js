"use strict";

const npm = require('npm')
const fs = require('fs-extra')
const path = require('path')
const util = require('../../../js/util.js')
const electron = require('electron')
const {ipcMain} = require('electron')
const SocketWindow = require('../../../js/SocketWindow.js')
const PACKAGE_PATH = path.resolve(path.join(__dirname, "..", "..", ".."))
const app = new SocketWindow('localhost', 11112, __dirname, 960, 722)

let project_dir_name = ""
let jc_project_settings_dir_name = ""
let project_details_file = ""
let project_settings_file = ""
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
  project_details_file = path.join(jc_project_settings_dir_name, "project_details.json")
  project_settings_file = path.join(jc_project_settings_dir_name, "project_settings.json")
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
  if (fs.existsSync(project_details_file)) {
    
    data_project.settings.project_details = util.mergeObjectsRecursive( data_project.settings.project_details, project_details )
    try{
      util.openWithSync((fd) => {
        app.sendWeb("overlay-message", "Saving "+project_details_file+"...")
        fs.writeFileSync(fd, JSON.stringify(data_project.settings.project_details, null, 2))
      }, project_details_file, "w+")
    }
    catch(e){
      app.sendWeb("error", `Can't modify "${project_details_file}"\nError: ${e}.`)
      return
    }

    app.sendWeb("success", "Successfully saved.")
    app.sendWeb("load_config", data_project)
  }
  else{
    app.sendWeb("error", `File "${project_details_file}" doesn't exists.`)
  }
})

ipcMain.on('form-project-settings', (event, project_settings) => {
  if (fs.existsSync(project_settings_file)) {
    try{
      util.openWithSync((fd) => {
        app.sendWeb("overlay-message", "Saving "+project_settings_file+"...")
        fs.writeFileSync(fd, JSON.stringify(project_settings, null, 2))
      }, project_settings_file, "w+")
    }
    catch(e){
      app.sendWeb("error", `Can't modify "${project_settings_file}"\nError: ${e}.`)
      return
    }

    data_project.settings.project_settings = project_settings
    app.sendWeb("success", "Successfully saved.")
    app.sendWeb("load_config", data_project)
  }
  else{
    app.sendWeb("error", `File "${project_settings_file}" doesn't exists.`)
  }
})

ipcMain.on('form-flow-settings', (event, flow_form_settings) => {
  if (fs.existsSync(flow_settings)) {
    try{
      util.openWithSync((fd) => {
        app.sendWeb("overlay-message", "Saving "+flow_form_settings+"...")
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
        app.sendWeb("overlay-message", "Saving "+path.join(project_dir_name, ".flowconfig")+"...")
        fs.writeFileSync(fd, str.replace(":PACKAGE_PATH", PACKAGE_PATH))
      }, path.join(project_dir_name, ".flowconfig"), "w+")

      app.sendWeb("success", "Successfully saved.")
      app.sendWeb("load_config", data_project)
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

ipcMain.on('add_project_type', (event, project_data) => {
  
  if (!fs.existsSync(project_data.project_dir_name)){
    fs.mkdirsSync(project_data.project_dir_name)
  }

  if ( !project_data.type_added || project_data.project_details.type.indexOf(project_data.type_added) >= 0 ) {
    app.sendWeb("error", "Can't add project type. This type already exists")
    return
  }

  if ( !project_data.working_directory ) {
    app.sendWeb("error", "Can't add project type. Working Directory field is empty.")
    return
  }

  let jc_project_settings = path.join(project_data.project_dir_name, ".jc-project-settings")
  let project_details_file = path.join(jc_project_settings, "project_details.json")
  let project_settings = path.join(jc_project_settings, "project_settings.json")
  let flow_settings = path.join(jc_project_settings, "flow_settings.json")

  let project_type_default_settings = []
  /* project_data.project_details.type.length evaluate each time because of possible type dependecies */
  let project_type_default_config = {}
  try {
    project_type_default_config = require('../../default_settings/'+project_data.type_added+'/default_config.js')
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
    
  }

  if (project_type_default_config) {
    if(project_type_default_config.project_details) {
      project_data.project_details.type = project_data.project_details.type.concat(project_type_default_config.project_details.type)
    }
    if(project_type_default_config.flow_settings) {
      for (let key in project_type_default_config.flow_settings) {
        if ( Array.isArray(project_data.flow_settings[key]) && project_data.flow_settings[key].indexOf() < 0 ){
          project_data.flow_settings[key] = util.concatUnique( project_data.flow_settings[key], project_type_default_config.flow_settings[key])
        }
      }
    }
    if(project_type_default_config[project_data.type_added+"_settings"]){
      project_type_default_settings.push(
        [project_data.type_added, project_type_default_config[project_data.type_added+"_settings"]]
      )
    }
  }

  if (fs.existsSync(jc_project_settings)) {

    util.openWithSync((fd) => {
      app.sendWeb("overlay-message", "Saving "+project_details_file+"...")
      //project_data.project_details = JSON.parse(JSON.stringify(project_data.project_details)) // clone project object
      fs.writeFileSync(fd, JSON.stringify(project_data.project_details, null, 2))
    }, project_details_file, "w+")

    util.openWithSync((fd) => {
      app.sendWeb("overlay-message", "Saving "+project_settings+"...")
      //project_data.project_settings = JSON.parse(JSON.stringify(project_data.project_settings))
      fs.writeFileSync(fd, JSON.stringify(project_data.project_settings, null, 2))
    }, project_settings, "w+")

    util.openWithSync((fd) => {
      app.sendWeb("overlay-message", "Saving "+flow_settings+"...")
      fs.writeFileSync(fd, JSON.stringify(project_data.flow_settings, null, 2))
    }, flow_settings, "w+")

    for(let i = 0, length1 = project_type_default_settings.length; i < length1; i++){

      if (!project_data[project_type_default_settings[i][0]+"_settings"]) {
        project_data[project_type_default_settings[i][0]+"_settings"] = {}
      }

      project_data[project_type_default_settings[i][0]+"_settings"] = util.mergeObjectsRecursive( project_type_default_settings[i][1], project_data[project_type_default_settings[i][0]+"_settings"] )

      project_data[project_type_default_settings[i][0]+"_settings"].working_directory = path.join(project_data.project_dir_name, project_data.working_directory)
      
      if (!fs.existsSync(project_data[project_type_default_settings[i][0]+"_settings"].working_directory)) {
        fs.mkdirsSync(project_data[project_type_default_settings[i][0]+"_settings"].working_directory)
      }

      util.openWithSync((fd) => {
        app.sendWeb("overlay-message", "Saving "+path.join(jc_project_settings, project_type_default_settings[i][0]+"_settings.json")+"...")
        fs.writeFileSync(fd, JSON.stringify(project_data[project_type_default_settings[i][0]+"_settings"], null, 2))
      }, path.join(jc_project_settings, project_type_default_settings[i][0]+"_settings.json"), "w+")
    }

    util.openWithSync((fd) => {
      let include = project_data.flow_settings.include.join("\n")
      let ignore = project_data.flow_settings.ignore.join("\n")
      let libs = project_data.flow_settings.libs.join("\n")
      let options = project_data.flow_settings.options.map(function(item){
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
      app.sendWeb("overlay-message", "Saving "+path.join(project_dir_name, ".flowconfig")+"...")
      fs.writeFileSync(fd, str.replace(":PACKAGE_PATH", PACKAGE_PATH))
    }, path.join(project_dir_name, ".flowconfig"), "w+")

    let sublime_project_file_name = util.clearString(project_data.project_details.project_name)

    let package_json = {}
    for(let i = 0, length1 = project_data.project_details.type.length; i < length1; i++){
      if (project_data[project_data.project_details.type[i]+"_settings"] && project_data[project_data.project_details.type[i]+"_settings"].package_json) {
        package_json = util.mergeObjectsRecursive(package_json, project_data[project_data.project_details.type[i]+"_settings"].package_json)
      }
    }
    if (package_json) {
      util.openWithSync((fd) => {
        app.sendWeb("overlay-message", "Saving "+path.join(project_data.project_dir_name, ".jc-project-settings", "package.json")+"...")
        fs.writeFileSync(fd, JSON.stringify(package_json, null, 2))
      }, path.join(project_data.project_dir_name, ".jc-project-settings", "package.json"), "w+")
      process.chdir(path.join(project_data.project_dir_name, ".jc-project-settings"));
      npm.load(function(err){
        app.sendWeb("overlay-message", "Running 'npm install'...")
        npm.commands.install(function(err, data){
          if(err){
            app.sendWeb("error", JSON.stringify(err, null, 2))
          }
          else {
            app.sendSocketJson({
              "command": "add_project_type",
              "project_data": project_data
            })
            app.sendWeb("success", "Successfully added.")
            app.app.quit()
          }
        })

      })
    }
    else {
      app.sendSocketJson({
        "command": "add_project_type",
        "project_data": project_data
      })
      app.sendWeb("success", "Successfully added.")
      app.app.quit()
    }
  }
  else{
    app.sendWeb("error", "Can't find the project!")
  }

})

ipcMain.on('remove_project_type', (event, data) => {
  let index_type = data.project_data.project_details.type.indexOf(data.type)
  // index_type > 0 because user can't delete the first type of the project
  if ( data.type && index_type > 0 ) {

    let jc_project_settings = path.join(data.project_data.project_dir_name, ".jc-project-settings")
    let project_details_file = path.join(jc_project_settings, "project_details.json")
    data.project_data.project_details.type.splice(index_type, 1)
    try{
      util.openWithSync((fd) => {
        app.sendWeb("overlay-message", "Saving "+project_details_file+"...")
        fs.writeFileSync(fd, JSON.stringify(data.project_data.project_details, null, 2))
      }, project_details_file, "w+")
    }
    catch(e){
      app.sendWeb("error", `Can't modify "${project_details_file}"\nError: ${e}.`)
      return
    }

    try{
      app.sendWeb("overlay-message", "Removing "+path.join(jc_project_settings, data.type+"_settings.json")+"...")
      fs.removeSync(path.join(jc_project_settings, data.type+"_settings.json"))
    }
    catch(e){
      app.sendWeb("error", `Can't delete "${path.join(jc_project_settings, data.type+"_settings.json")}"\nError: ${e}.`)
      return
    }

    try{
      app.sendWeb("overlay-message", "Removing "+data.project_data[data.type+"_settings"].working_directory+"...")
      fs.removeSync(data.project_data[data.type+"_settings"].working_directory)
    }
    catch(e){
      app.sendWeb("error", `Can't delete "${data.project_data[data.type+"_settings"].working_directory}"\nError: ${e}.`)
      return
    }

    app.sendWeb("success", "Successfully added.")
    data_project.settings.project_details = data.project_data.project_details
    app.sendWeb("load_config", data_project)
  }
  else{
    app.sendWeb("error", "Can't find the project type.")
  }
})

app.start(() => {
  app.window.setResizable(false)
})
