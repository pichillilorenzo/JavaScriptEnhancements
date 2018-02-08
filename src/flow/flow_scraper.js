var elements = []
var lines = $0.textContent.split("\n")

for ( var i = 0; i < lines.length; i++) {
  if(lines[i].substring(0, "declare class ".length) == "declare class "){
    var matches = lines[i].match(/declare class ([a-zA-Z]+)(\<.+\>)?/)

    elements.push([
      matches[1]+"\t"+"[class: "+ ( (matches.length > 2) ? matches[1]+matches[2] : matches[1] )+"]",
      matches[1],
      {
        "name": matches[1],
        "type": "[class: "+ ( (matches.length > 2) ? matches[1]+matches[2] : matches[1] )+"]",
        "func_details": null
      }
    ])
  }
  else if(lines[i].substring(0, "declare var ".length) == "declare var "){
    var matches = lines[i].match(/declare var ([a-zA-Z]+)\: (.+)\;/)
    elements.push([
      matches[1]+"\t"+matches[2],
      matches[1]
    ])
  }
  else if(lines[i].substring(0, "declare function ".length) == "declare function "){
    if (lines[i].charAt(lines[i].length-1) != ";"){
      var j = 1
      while (lines[i].charAt(lines[i].length-1) != ";"){
        lines[i] += " " + lines[i+j]
        j++
      }
    }
    var matches = lines[i].trim().match(/declare function ([a-zA-Z]+)\((.+)?\)\: (.+)\;/)
    var name = matches[1].trim()
    var params = ( (matches[2]) ? matches[2].trim() : "" )
    var params_arr = []
    if(params){
      var regex = /([a-zA-Z]+\??)\: (\(.+\)|\[.+\]|[a-zA-Z]+)( => ([a-zA-Z]+))?/g;
      var match = []
      while (match = regex.exec(params))
      {
        console.log(match)
        params_arr.push({
          "name": match[1].trim(), "type": match[2].trim()
        })
      }

    }
    var return_type = ( (matches[3]) ? matches[3].trim() : matches[2].trim() )
    elements.push([
      name.trim()+"\t("+params.trim()+") => "+return_type.trim() ,
      name.trim(),
      {
        "name": name.trim(),
        "type": "("+params.trim()+")",
        "func_details": {
          "params": params_arr,
          "return_type": return_type.trim()
        }
      }
    ])
  }
}

JSON.stringify(elements, null, 2)

