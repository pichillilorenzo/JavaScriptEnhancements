const jQuery = require('../vendor/jquery/jquery-1.12.2.min.js')
const $ = jQuery

exports.get_options = (selector) => {
  let options = []

  $(selector).each(function(index, item){
    let field_type = $(item).attr("data-field-type") 
    let value = $(item).val()
    if (field_type && value) {
      if (field_type == "option") {
        options.push("--"+$(item).attr("name"))
        options.push(value.trim())
      }
      else if (field_type == "select") {
        if($(item).prop("multiple")) {
          options =  options.concat( value )
        }
        else {
          options.push(value)
        }
      }
      else {
        options.push(value.trim())
      }
    }
  })

  return options
}

exports.set_options = (selector, data) => {
  $(selector).each(function(index, item){
    let field_type = $(item).attr("data-field-type") 
    if (field_type) {
      if (field_type == "option") {
        let index_data = data.indexOf("--"+$(item).attr("name"))
        if (index_data >= 0) {
          $(item).val(data[index_data+1])
        }
      }
      else if (field_type == "select") {
        if($(item).prop("multiple")) {
          let values = []
          $(item).find("option").each(function(index, option){
            let index_data = data.indexOf($(option).attr("value"))
            if (index_data >= 0) {
              values.push(data[index_data])
            }
          })
          $(item).val(values)
        }
        else {
          let index_data = data.indexOf("--"+$(item).attr("name"))
          if (index_data >= 0) {
            $(item).val(data[index_data])
          }
        }
      }
    }
  })
}

exports.get_cli_create_options = (variables, project_type) => {
  let project = variables.project
  let $ = variables.$
  let ipcRenderer = variables.ipcRenderer
  let utilWeb = variables.utilWeb
  let cli_create_options = []

  $("#"+project_type+" .cli_create_"+project_type+"_options").each(function(index, item){
    let field_type = $(item).attr("data-field-type") 
    let value = $(item).val()
    if (field_type && value) {
      if (field_type == "option") {
        cli_create_options.push("--"+$(item).attr("name"))
        cli_create_options.push(value.trim())
      }
      else if (field_type == "select") {
        if($(item).prop("multiple")) {
          cli_create_options = cli_create_options.concat( value )
        }
        else {
          cli_create_options.push(value)
        }
      }
      else {
        cli_create_options.push(value.trim())
      }
    }
  })

  return cli_create_options
}