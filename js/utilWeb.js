const jQuery = require('../vendor/jquery/jquery-1.12.2.min.js')
const $ = jQuery

exports.get_cli_create_options = (variables, project_type) => {
  let project = variables.project
  let $ = variables.$
  let ipcRenderer = variables.ipcRenderer
  let utilWeb = variables.utilWeb
  let clie_create_options = []

  $("#"+project_type+" .cli_create_"+project_type+"_options").each(function(index, item){
    let field_type = $(item).attr("data-field-type") 
    let value = $(item).val()
    if (field_type && value) {
      if (field_type == "option") {
        clie_create_options.push("--"+$(item).attr("name"))
        clie_create_options.push(value.trim())
      }
      else if (field_type == "select") {
        if($(item).prop("multiple")) {
          clie_create_options =  clie_create_options.concat( value )
        }
        else {
          clie_create_options.push(value)
        }
      }
      else {
        clie_create_options.push(value.trim())
      }
    }
  })

  return clie_create_options
}