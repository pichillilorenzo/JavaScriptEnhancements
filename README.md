<h1>JavaScript Completions</h1>

[![Sublime Text](https://img.shields.io/badge/Sublime%20Text-2%20%2F%203-brightgreen.svg)](https://www.sublimetext.com/)
[![Package Control](https://img.shields.io/packagecontrol/dt/JavaScript%20Completions.svg)](https://packagecontrol.io/packages/JavaScript%20Completions) 
[![Package Control](https://img.shields.io/packagecontrol/dd/JavaScript%20Completions.svg)](https://packagecontrol.io/packages/JavaScript%20Completions)

JavaScript Completions for sublime text

It helps you to write your scripts more quickly with hints and completions.

<strong>jQuery</strong> and <strong>NativeScript</strong> completions disabled by default!
You can enable them on Preferences -> Package Settings -> JavaScript Completions.

<strong>Some features could use npm!</strong>

In Windows you must install it! Download it from [https://nodejs.org](https://nodejs.org).

To OSX and Linux, it will be downloaded automatically with nodejs.

Features list:
- <a href="#find-javascript-description">"Find JavaScript Description" Feature</a>
- <a href="#on-hover-description">"On Hover Description" Feature</a>
- <a href="#evaluate-javascript">"Evaluate JavaScript" Feature</a>
- <a href="#can-i-use">"Can I use?" Feature</a>
- <a href="#jsdoc">"JSDoc" Feature</a>
- <a href="#context-menu-options">Context menu options</a>

<h2>Usage</h2>

To try it, just write.

Examples:

<img src="https://media.giphy.com/media/l0MYypWg9s9exQ0xi/giphy.gif" alt="example #1 of JavaScript Completions"/>

<img src="https://media.giphy.com/media/d31wQpJ2iCyGtS0M/giphy.gif" alt="example #2 of JavaScript Completions"/>

<code>description-Name_of_function/property/method</code> shows to you the explanation of the function/property/method and its syntax.

Information about the description of function/property/method has been taken on this sites:

- [http://html5index.org/index.html](http://html5index.org/index.html)
- [https://html.spec.whatwg.org/](https://html.spec.whatwg.org/)
- [http://www.ecma-international.org/ecma-262/5.1/](http://www.ecma-international.org/ecma-262/5.1/)
- [https://www.w3.org](https://www.w3.org)
- [http://api.jquery.com/](http://api.jquery.com/)
- [https://docs.nativescript.org/api-reference/globals.html](https://docs.nativescript.org/api-reference/globals.html)

<h3>ENABLE or DISABLE completions</h3>

You can ENABLE or DISABLE completions! Just go to Preferences -> Package Settings -> JavaScript Completions


<h3 id="find-javascript-description">"Find JavaScript Description" Feature</h3>

<strong>Supported only by Sublime Text 3</strong>

You can check the description of function/property/method by selecting the word (or, in case, it will take the first word near the blinking cursor) you want find. "right-click" on your mouse and click on "Find JavaScript Description".

It will show a popup with the list of possible descriptions or, in some case, the direct description. 

Key-Map list: Preferences -> Package Settings ->  JavaScript Completions -> Key Bindings - Default.

<img src="https://s17.postimg.io/stsylwwn3/Schermata_2016_09_18_alle_17_41_17.png" alt="example #1 Find JavaScript Description Feature"> 

<img src="https://s17.postimg.io/pyfvf1sn3/Schermata_2016_09_18_alle_17_40_28.png" alt="example #2 Find JavaScript Description Feature"> 


<h3 id="on-hover-description">"On Hover Description" Feature</h3>

<strong>Supported only by Sublime Text 3, Build >= 3124</strong>

Just put the cursor over a name of a function, property or constructor and it will appear a little popup with all matching found from the <code>/sublime-completions</code> list enabled. 

- F = function
- P = property
- C = constructor

Example:

<img src="https://media.giphy.com/media/l2Sq7JFMFtMJY3Eo8/giphy.gif" alt="example #1 On Hover Description Feature"> 


<h3 id="evaluate-javascript">"Evaluate JavaScript" Feature</h3>

<strong>Supported only by Sublime Text 3</strong>

This feature uses node.js installed locally by this plugin.

You can change the path of "node.js" and "npm" on Preferences -> Package Settings ->  JavaScript Completions -> Settings - Default

You can evaluate the entire text selection or the current line! 
If you select a text region and evaluate it, in the gutter of the editor will appear 2 white dots.
The first white dot represents the start of the region and the second white dot represents the end of the region.
You can eventually modify the region and, without reselect the same region, you can evaluate it again! 
If you want hide this 2 dots, there is an entry on the context menu "Evaluate JavaScript".

When you evaluate code, this plugin will prepend <code>"use strict";</code> automaticaly!

There are two main mode to evaluate code:
- [eval](https://nodejs.org/dist/latest-v6.x/docs/api/cli.html#cli_e_eval_script)
- [print](https://nodejs.org/dist/latest-v6.x/docs/api/cli.html#cli_p_print_script)

Key-Map list: Preferences -> Package Settings ->  JavaScript Completions -> Key Bindings - Default.

<img src="https://s17.postimg.io/c7becu3pb/Schermata_2016_09_18_alle_18_07_00.png" alt="example #1 Evaluate JavaScript Feature"> 

<img src="https://s17.postimg.io/fs79w288v/Schermata_2016_09_18_alle_18_08_55.png" alt="example #2 Evaluate JavaScript Feature"> 


<h3 id="can-i-use">"Can I use?" Feature</h3>

<strong>Supported only by Sublime Text 3, Build >= 3124</strong>

This feature uses "can i use" json data from this [repository](https://github.com/Fyrd/caniuse), that contains raw data from the [http://caniuse.com](http://caniuse.com) support tables.

Thanks to @Fyrd.

You can use this feature in HTML, CSS and JavaScript context!

Just put the cursor on the word you want to check, "right-click" -> <code>"Can I use?"</code> and it will appear an input panel with all items that have a name matching with the word.

You can use key-map: <code>ctrl+alt+w</code>. Key-Map list: Preferences -> Package Settings ->  JavaScript Completions -> Key Bindings - Default.

After selecting an item from the list, it will appear a popup with all information from the [http://caniuse.com](http://caniuse.com) support tables.

You can find it under <code>"Tools"</code> menu -> <code>"JavaScript Completions"</code> -> <code>Search on "Can I use" list</code>.

Example :

<img src="https://media.giphy.com/media/26ufnXCKlXwFghwDS/giphy.gif" alt="example #1 Can I use? Feature"> 

<img src="http://s17.postimg.org/8hqxb0fvj/Schermata_2016_09_24_alle_21_07_44.png" alt="example #2 Can I use? Feature"> 

<img src="http://s17.postimg.org/wa4u0a7a7/Schermata_2016_09_24_alle_21_07_55.png" alt="example #3 Can I use? Feature"> 


<h3 id="jsdoc">"JSDoc" Feature</h3>

<strong>Supported only by Sublime Text 3</strong>

<strong>Requires npm</strong>

This feature uses [https://github.com/jsdoc3/jsdoc](https://github.com/jsdoc3/jsdoc) to generate API documentation.

You can find it under <code>"Tools"</code> menu -> <code>"JavaScript Completions"</code>.

There are 2 main menu items:
- Generate Documentation
- Add jsdoc configuration file to the current project folder

<strong>These items can be used only with a project folder opened.</strong>

<code>"Generate Documentation"</code> uses the jsdoc command line to generate documentation.

It uses the defaukt <code>conf.json</code> file for configuration.

The options (with default values) availables are:
```json
{
  "tags": {
    "allowUnknownTags": true,
    "dictionaries": ["jsdoc","closure"]
  },
  "source": {
    "include": [  ],
    "exclude": [  ],
    "includePattern": ".+\\.js(doc|x)?$",
    "excludePattern": "(^|\\/|\\\\)_"
  },
  "opts": {
    "template": "templates/default",
    "encoding": "utf8",
    "destination": "./out/",
    "recurse": true,
    "tutorials": ""
  },
  "plugins": [],
  "templates": {
    "cleverLinks": false,
    "monospaceLinks": false
  }
}
```

<code>"Add jsdoc configuration file to the current project folder"</code> will add a <code>conf.json</code> file with default values to the current project folder.

How to use JSDoc: [http://usejsdoc.org/](http://usejsdoc.org/)


<h3 id="context-menu-options">Context menu options</h3>

Context menu options:
- <a href="#surround-with">Surround With</a>
- <a href="#delete-surround">Delete Surrounded</a>
- <a href="#create-class-from-object-literal">Create Class from object literal</a>
- <a href="#sort-array">Sort array</a>
- <a href="#split-string-lines-to-variable">Split string lines to variable</a>

<h4 id="surround-with">Surround With</h4>

You MUST first select text to "enable" these options.

You can surround code with:
- if statement
- if else statement (this works only if you selected 2 regions, see <a href="#context-menu-option-example-2">example</a>)
- while statement
- do while statement
- for statement
- try catch statement
- try catch finally statement

This option works also on multiple selections at once.

<h4 id="delete-surround">Delete Surrounded</h4>

Options are:
- Strip quoted string

This option works also on multiple selections at once.

<h4 id="create-class-from-object-literal">Create Class from object literal</h4>

This option create a JavaScript Class from an object literal (Constructor with all setter and getter for each field).

You can set default values or use the string <code>"required"</code> to say that a field hasn't a default value.

To work properly, you MUST declare a variable and assign an object literal to it, like this example:

```javascript
var Person = {
  name: "required",
  surname: "required",
  email: "",
  age: 18
}
```

This option works also on multiple selections at once.

<h4 id="sort-array">Sort array</h4>

Just put the cursor between brackets and will appear a menu with these options:
- Sort array ASC ( compare function: <code>function(x,y){return x-y;}</code> )
- Sort array DESC ( compare function: <code>function(x,y){return y-x;}</code> )
- Sort array alphabetically ASC
- Sort array alphabetically DESC

This option works also on multiple selections at once.

Examples of usage:

<img src="https://media.giphy.com/media/3o7TKOwWEYUGPX4G6Q/giphy.gif" alt="example #1 Other Context menu option"> 

<img id="context-menu-option-example-2" src="https://media.giphy.com/media/l3vR1DjPDWRFfl3LG/giphy.gif" alt="example #2 Other Context menu option"> 

<h4 id="split-string-lines-to-variable">Split string lines to variable</h4>

Just put the cursor between a string with multiple lines and this option will appear in the context menu.

It will split the string and for each line will be concatenated to a variable named "str".

This option works also on multiple selections at once.

Example:

<img src="https://media.giphy.com/media/l2Sq0iS3ga6p9iXjq/giphy.gif" alt="example #1 Split string lines to variable"> 

<i>MIT License</i>
