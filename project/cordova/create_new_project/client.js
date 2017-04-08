module.exports = {
  "prepareClientHtml": (variables) => {
    let $ = variables.$
    let ipcRenderer = variables.ipcRenderer
    let utilWeb = variables.utilWeb

    $(".use_local_cli").change(function(event){
      let id = $(this).attr("data-toggle-show")
      if($(this).prop("checked")){
        $("#"+id).removeClass("hidden")
        $("#"+id+" input.cordova-version").attr("data-validate-func", "required")
        $("#"+id+" input.cordova-version").attr("data-validate-hint", "This field can not be empty!")
        $("#"+id+" input.cordova-version").attr("data-validate-hint-position", "top")
      }
      else {
        $("#"+id).addClass("hidden")
        $("#"+id+" input.cordova-version").removeAttr("data-validate-func")
        $("#"+id+" input.cordova-version").removeAttr("data-validate-hint")
        $("#"+id+" input.cordova-version").removeAttr("data-validate-hint-position")
      }
    })
  },
  "setProject":  (variables) => {
    let utilWeb = variables.utilWeb
    let $ = variables.$
    let project = variables.project
    project.cordova_settings = {}
    if($(".use_local_cli").prop("checked")){
      project.cordova_settings.package_json = {
        "dependencies": {
          "cordova": $("#custom-cordova-version input.cordova-version").val()
        }
      }
      project.cordova_settings.use_local_cli = true
    }
    project.cordova_settings.cli_custom_path = ""
    if($("#custom-cordova-path input.cordova-path").val().trim()){
      project.cordova_settings.cli_custom_path = $("#custom-cordova-path input.cordova-path").val().trim()
    }
    return utilWeb.get_cli_create_options(variables, "cordova")
  }
}