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

exports.mergeObjectsRecursive = (obj1, obj2) => {

  for (var p in obj2) {
    try {
      // Property in destination object set; update its value.
      if ( obj2[p].constructor==Object ) {
        obj1[p] = exports.mergeObjectsRecursive(obj1[p], obj2[p]);

      } else {
        obj1[p] = obj2[p];

      }

    } catch(e) {
      // Property in destination object not set; create it and set its value.
      obj1[p] = obj2[p];

    }
  }

  return obj1;
}