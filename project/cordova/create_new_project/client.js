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
        $('#custom-cordova-path').removeAttr("data-validate-func")
        $('#custom-cordova-path').removeAttr("data-validate-hint")
        $('#custom-cordova-path').removeAttr("data-validate-hint-position")
        $('#custom-cordova-path').removeClass("required")
      }
      else {
        $("#"+id).addClass("hidden")
        $("#"+id+" input.cordova-version").removeAttr("data-validate-func")
        $("#"+id+" input.cordova-version").removeAttr("data-validate-hint")
        $("#"+id+" input.cordova-version").removeAttr("data-validate-hint-position")
        $('#custom-cordova-path').attr("data-validate-func")
        $('#custom-cordova-path').attr("data-validate-hint")
        $('#custom-cordova-path').attr("data-validate-hint-position")
        $('#custom-cordova-path').addClass("required")
      }
    })
  },
  "setProject":  (variables) => {
    let utilWeb = variables.utilWeb
    let $ = variables.$
    let project_data = variables.project_data
    project_data.cordova_settings = {}
    if($(".use_local_cli").prop("checked")){
      project_data.cordova_settings.package_json = {
        "dependencies": {
          "cordova": $("#custom-cordova-version input.cordova-version").val()
        }
      }
      project_data.cordova_settings.use_local_cli = true
    }
    project_data.cordova_settings.cli_custom_path = ""
    if($("#custom-cordova-path input.cordova-path").val().trim()){
      project_data.cordova_settings.cli_custom_path = $("#custom-cordova-path input.cordova-path").val().trim()
    }
    project_data.create_options = utilWeb.get_cli_create_options(variables, "cordova")
  }
}