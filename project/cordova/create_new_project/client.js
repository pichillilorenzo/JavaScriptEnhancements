module.exports = {
  "html_json": {
    "title": "Cordova",
    "subtitle": "",
    "fields": [
      {
        "tag": "input",
        "type": "value",
        "label": "App Name *",
        "attrs" : {
          "type": "text",
          "name": "name",
          "value": "HelloCordova",
          "data-validate-func": "required",
          "data-validate-hint": "This field can not be empty!",
          "data-validate-hint-position": "top"
        }
      },
      {
        "tag": "input",
        "type": "value",
        "label": "App ID",
        "attrs" : {
          "type": "text",
          "name": "id",
          "value": "io.cordova.hellocordova"
        }
      },
      {
        "tag": "input",
        "type": "value",
        "label": "Config file",
        "attrs" : {
          "type": "text",
          "name": "config",
          "value": ""
        }
      },
      {
        "tag": "input",
        "type": "option",
        "label": "--template",
        "attrs" : {
          "type": "text",
          "name": "template",
          "value": ""
        }
      },
      {
        "tag": "input",
        "type": "option",
        "label": "--copy-from",
        "attrs" : {
          "type": "text",
          "name": "copy-from",
          "value": ""
        }
      },
      {
        "tag": "input",
        "type": "option",
        "label": "--link-to",
        "attrs" : {
          "type": "text",
          "name": "link-to",
          "value": ""
        }
      }
    ]
  },
  "prepareClientHtml": (variables) => {
    let $ = variables.$
    let ipcRenderer = variables.ipcRenderer
    let utilWeb = variables.utilWeb
  },
  "setProject":  (variables) => {
    let project = variables.project
    let $ = variables.$
    let ipcRenderer = variables.ipcRenderer
    let utilWeb = variables.utilWeb

    let cli_create_cordova_options = []

    $("#cordova .cli_create_cordova_options").each(function(index, item){
      let field_type = $(item).attr("data-field-type") 
      let value = $(item).val().trim()
      if (field_type && value) {
        if (field_type == "option") {
          cli_create_cordova_options.push("--"+$(item).attr("name"))
          cli_create_cordova_options.push(value)
        }
        else {
          cli_create_cordova_options.push(value)
        }
      }
    })
    return cli_create_cordova_options
  },
}