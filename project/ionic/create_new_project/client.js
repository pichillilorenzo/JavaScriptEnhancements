module.exports = {
  "prepareClientHtml": (variables) => {
    let $ = variables.$
    let ipcRenderer = variables.ipcRenderer
    let utilWeb = variables.utilWeb

    $(".use_local_cli").change(function(event){
      let id = $(this).attr("data-toggle-show")
      if($(this).prop("checked")){
        $("#"+id).removeClass("hidden")
        $("#"+id+" input.ionic-version").attr("data-validate-func", "required")
        $("#"+id+" input.ionic-version").attr("data-validate-hint", "This field can not be empty!")
        $("#"+id+" input.ionic-version").attr("data-validate-hint-position", "top")
      }
      else {
        $("#"+id).addClass("hidden")
        $("#"+id+" input.ionic-version").removeAttr("data-validate-func")
        $("#"+id+" input.ionic-version").removeAttr("data-validate-hint")
        $("#"+id+" input.ionic-version").removeAttr("data-validate-hint-position")
      }
    })
  },
  "setProject":  (variables) => {
    let utilWeb = variables.utilWeb
    let $ = variables.$
    let project_data = variables.project_data
    project_data.ionic_settings = {}
    if($(".use_local_cli").prop("checked")){
      project_data.ionic_settings.package_json = {
        "dependencies": {
          "ionic": $("#custom-ionic-version input.ionic-version").val()
        }
      }
      project_data.ionic_settings.use_local_cli = true
    }
    project_data.ionic_settings.cli_custom_path = ""
    if($("#custom-ionic-path input.ionic-path").val().trim()){
      project_data.ionic_settings.cli_custom_path = $("#custom-ionic-path input.ionic-path").val().trim()
    }
    project_data.types_option = utilWeb.get_cli_create_options(variables, "ionic")
  }
}