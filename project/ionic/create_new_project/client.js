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
        $('#custom-ionic-path').removeAttr("data-validate-func")
        $('#custom-ionic-path').removeAttr("data-validate-hint")
        $('#custom-ionic-path').removeAttr("data-validate-hint-position")
        $('#custom-ionic-path').removeClass("required")
      }
      else {
        $("#"+id).addClass("hidden")
        $("#"+id+" input.ionic-version").removeAttr("data-validate-func", "required")
        $("#"+id+" input.ionic-version").removeAttr("data-validate-hint", "This field can not be empty!")
        $("#"+id+" input.ionic-version").removeAttr("data-validate-hint-position", "top")
        $('#custom-ionic-path').attr("data-validate-func")
        $('#custom-ionic-path').attr("data-validate-hint")
        $('#custom-ionic-path').attr("data-validate-hint-position")
        $('#custom-ionic-path').addClass("required")
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
    project_data.create_options = utilWeb.get_cli_create_options(variables, "ionic")
  }
}