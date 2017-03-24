const jQuery = require('./vendor/jquery-1.12.2.min.js')
const $ = jQuery

exports.createPmdAlert = (type, text, fadeCreate = "fadeInDown", fadeRemove = "fadeInUp", wait = 2000) => {
  let alert = $(`<div class="pmd-alert ${fadeCreate} visible ${type}"></div`)
  $(alert).html(text)
  setTimeout(() => {
    $(alert).slideUp(() => {$(this).removeClass(`visible ${fadeRemove}`).remove();});
  }, wait)
  return alert
}

exports.getMulitpleSelectValues = (select) => {
  var selectedValues = [];    
  $(select).find("option:selected").each(function(){
    if ($(this).val()) 
      selectedValues.push($(this).val()); 
  });
  return selectedValues
}

exports.setMulitpleSelectValues = (select, types) => {
  for(let i = 0, length1 = types.length; i < length1; i++){
    if( $(select).find("option[value=\""+types[i]+"\"]") ){
      $(select).find("option[value=\""+types[i]+"\"]").attr("selected","selected")
    }
  } 
}