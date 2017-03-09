const fs = require('fs')
const path = require('path')

exports.openWithSync = (fun, ...args) => {
  let fd = fs.openSync(...args)
  fun(fd)
  fs.closeSync(fd)
}

exports.clearString = (str) => {
  return str.toLowerCase().replace(/\s+/g, "-").replace(/[^\w\-]/g, "")
}