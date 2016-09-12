<h1>JavaScript Completions</h1>

[![Sublime Text](https://img.shields.io/badge/Sublime%20Text-2%20%2F%203-brightgreen.svg)](https://www.sublimetext.com/)
[![Package Control](https://img.shields.io/packagecontrol/dt/JavaScript%20Completions.svg?maxAge=2592000)](https://packagecontrol.io/packages/JavaScript%20Completions) 
[![Package Control](https://img.shields.io/packagecontrol/dd/JavaScript%20Completions.svg?maxAge=2592000)](https://packagecontrol.io/packages/JavaScript%20Completions)

JavaScript Completions for sublime text

It helps you to write your scripts more quickly with hints and completions.

In the next updates I will add the newest APIs of HTML5

<strong>jQuery</strong> and <strong>NativeScript</strong> completions added! They are disabled by default!
You can enable them on Preferences -> Package Settings -> JavaScript Completions and here you can set your settings.

<h2>Usage</h2>

To try it, just write.

Examples:

<img src="https://media.giphy.com/media/l0MYypWg9s9exQ0xi/giphy.gif" alt="example #1 of JavaScript Completions"/>

<img src="https://media.giphy.com/media/d31wQpJ2iCyGtS0M/giphy.gif" alt="example #2 of JavaScript Completions"/>

<code>description-Name_of_function/property/method</code> shows to you the explanation of the function/property/method and its syntax.

Information about the description of function/property/method has been taken on the site https://developer.mozilla.org
Information about the description of jQuery's function/property/method has been taken on the official site. 
Information about the description of NativeScript's function/property/method has been taken on the official site. 

<h3>"Show Description" Feature</h3>

Now you can check the description of function/property/method by selecting the word you want find and "right-click" of your mouse and click on "Find JavaScript Description" or, alternately, with "ctrl+super+c" from your keyboard!

It will show a popup with the list of possible descriptions or, in some case, the direct description. 

<img src="https://s22.postimg.io/xslsughdt/Schermata_2016_09_12_alle_02_53_20.png" alt="example #1 'Show Description' Feature"> 

<img src="https://s22.postimg.io/jaolmgq2p/Schermata_2016_09_12_alle_02_58_27.png" alt="example #2 'Show Description' Feature"> 

<h3>ENABLE or DISABLE completions</h3>

Now you can also ENABLE or DISABLE completions! Just go to Preferences -> Package Settings -> JavaScript Completions and set your settings!

Default settings are:

```json
{
    // --------------------
    // Setup
    // --------------------
    // `true` means enable it.
    // `false` means disable it.

    "completion_active_list": {

        "ajax": true,
        "description-ajax": true,

        "array-string-and-regexp": true,
        "description-array-string-and-regexp": true,

        "date": true,
        "description-date": true,

        "blob": true,
        "description-blob": true,

        "document": true,
        "description-document": true,

        "element": true,
        "description-element": true,

        "event": true,
        "description-event": true,

        "event-target": true,
        "description-event-target": true,

        "file": true,
        "description-file": true,

        "node": true,
        "description-node": true,

        "range": true,
        "description-range": true,

        "style-css": true,
        "description-style-css": true,

        "text": true,
        "description-text": true,

        "treewalker": true,
        "description-treewalker": true,

        "url": true,
        "description-url": true,

        "window": true,
        "description-window": true,

        "worker": true,
        "description-worker": true,

        "error": true,
        "description-error": true,

        "function": true,
        "description-function": true,

        "math": true,
        "description-math": true,

        "miscellaneous": true,
        "description-miscellaneous": true,

        "number": true,
        "description-number": true,

        "object": true,
        "description-object": true,

        "nativescript": false,
        "description-nativescript": false,

        "jquery": false,
        "description-jquery": false
    }
}
```

<i>MIT License</i>
