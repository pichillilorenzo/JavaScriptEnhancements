const jQuery = require('./vendor/jquery-1.12.2.min.js')
const $ = jQuery

exports.createPmdAlert = (type, text, fadeCreate = "fadeInDown", fadeRemove = "fadeInUp", wait = 2000) => {
  let alert = $(`<div class="pmd-alert ${fadeCreate} visible ${type}"></div`)
  $(alert).html(text)
  setTimeout(() => {
    $(alert).slideUp(() => {$(this).removeClass(`visible ${fadeInUp}`).remove();});
  }, wait)
  return alert
}
