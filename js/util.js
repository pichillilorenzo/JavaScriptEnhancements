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

exports.mergeObjectsRecursive = (obj1, obj2, checkSubObjToDelete = false) => {

  if (checkSubObjToDelete && Object.keys(obj2).length == 0) {
    return obj2;
  }

  for (let p in obj2) {
    try {
      // Property in destination object set; update its value.
      if ( obj2[p].constructor==Object ) {
        obj1[p] = exports.mergeObjectsRecursive(obj1[p], obj2[p], true);

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

exports.concatUnique = (arr1, arr2) => {
  return arr1.concat(arr2.filter(function (item) {
    return arr1.indexOf(item) < 0
  }))
}