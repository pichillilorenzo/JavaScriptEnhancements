# JavaScript Enhancements

[![Minimum Sublime Build Version](https://img.shields.io/badge/sublime%20build-%3E%3D%203124-brightgreen.svg?style=flat)](https://sublimetext.com)
[![GitHub stars](https://img.shields.io/github/stars/pichillilorenzo/JavaScriptEnhancements.svg?style=flat)](https://github.com/pichillilorenzo/JavaScriptEnhancements/stargazers)
[![Gitter](https://img.shields.io/gitter/room/nwjs/nw.js.svg)](https://gitter.im/JavaScriptEnhancements/Lobby)
[![Build Status](https://travis-ci.org/pichillilorenzo/JavaScriptEnhancements.svg?branch=master)](https://travis-ci.org/pichillilorenzo/JavaScriptEnhancements)
[![codecov](https://codecov.io/gh/pichillilorenzo/JavaScriptEnhancements/branch/master/graph/badge.svg)](https://codecov.io/gh/pichillilorenzo/JavaScriptEnhancements)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg)](/LICENSE.txt)

[![Donate to this project using Paypal](https://img.shields.io/badge/paypal-donate-yellow.svg)](https://www.paypal.me/LorenzoPichilli)
[![Donate to this project using Patreon](https://img.shields.io/badge/patreon-donate-yellow.svg)](https://www.patreon.com/bePatron?u=9269604)
[![Donate to this project using Open Collective](https://img.shields.io/badge/open%20collective-donate-yellow.svg)](https://opencollective.com/javascriptenhancements/donate) [![Backers on Open Collective](https://opencollective.com/javascriptenhancements/backers/badge.svg)](#backers) [![Sponsors on Open Collective](https://opencollective.com/javascriptenhancements/sponsors/badge.svg)](#sponsors)

**JavaScript Enhancements** is a plugin for **Sublime Text 3**.

This plugin uses **[Flow](https://github.com/facebook/flow)** (javascript static type checker from Facebook) under the hood.

This is in **BETA** version for **testing**. 

It offers better **JavaScript autocomplete** and also a lot of features about creating, developing and managing [**JavaScript projects**](https://github.com/pichillilorenzo/JavaScriptEnhancements/wiki/Creating-a-JavaScript-Project), such as:

- Cordova projects (run cordova emulate, build, compile, serve, etc. directly from Sublime Text!)
- Ionic v1 and v2 (it includes also v3) projects (same as Cordova projects!)
- Angular v1 and v2 (it includes also v4 and v5) projects
- Vue projects (only about the creation at this moment, see the [wiki](https://github.com/pichillilorenzo/JavaScriptEnhancements/wiki/Example-Vue.js-project))
- React projects (only about the creation at this moment)
- React Native projects (only about the creation at this moment. I will add also **NativeScript** support)
- Express projects (only about the creation at this moment)
- Yeoman generators
- [Local bookmarks project](https://github.com/pichillilorenzo/JavaScriptEnhancements/wiki/Features#bookmarks-project)
- [JavaScript real-time errors](https://github.com/pichillilorenzo/JavaScriptEnhancements/wiki/Errors-and-linting)
- [Code Refactoring](https://github.com/pichillilorenzo/JavaScriptEnhancements/wiki/Code-Refactoring)
- etc.

You could use it also in **existing projects** (see the [Wiki](https://github.com/pichillilorenzo/JavaScriptEnhancements/wiki/Using-it-with-an-existing-project))!

It turns Sublime Text into a **JavaScript IDE** like!

This project is based on my other Sublime Text plugin [JavaScript Completions](https://github.com/pichillilorenzo/JavaScript-Completions)

**Note**: 
If you want use this plugin, you may want **uninstall/disable** the **JavaScript Completions** plugin, if installed.

## OS SUPPORTED

- Linux (64-bit)
- Mac OS X
- Windows (64-bit): released without the use of [TerminalView](https://github.com/Wramberg/TerminalView) plugin. For each feature (like also creating a project) will be used the `cmd.exe` shell (so during the creation of a project **don't close it** until it finishes!). Unfortunately the TerminalView plugin supports only **Linux-based OS** 😞 . Has someone any advice or idea about that? Is there something similar to the TerminalView plugin for Windows?? Thanks!

## Dependencies

In order to work properly, this plugin has some dependencies:

- **Sublime Text 3** (build **3124** or newer)
- **Node.js** (6 or newer) and **npm** ([nodejs.org](https://nodejs.org) or [nvm](https://github.com/creationix/nvm))
- **TerminalView** (only for _Linux_ and _Mac OS X_) sublime text plugin ([TerminalView](https://github.com/Wramberg/TerminalView)) 

**Not required**, but **useful** for typescript files (Flow wont work on this type of files):

- **TypeScript** sublime text plugin ([TypeScript](https://github.com/Microsoft/TypeScript-Sublime-Plugin)) 

### Flow Requirements

It will use [Flow](https://github.com/facebook/flow) for type checking and auto-completions.

- Mac OS X
- Linux (64-bit)
- Windows (64-bit)

You can find more information about Flow on [flow.org](https://flow.org)

## Installation

With [Package Control](https://packagecontrol.io/):

- Run “Package Control: Install Package” command or click to the `Preferences > Package Control` menu item, find and install `JavaScript Enhancements` plugin.

Manually:

1. Download [latest release](https://github.com/pichillilorenzo/JavaScriptEnhancements/releases) (**DON'T CLONE THE REPOSITORY!**) and unzip it into your **Packages folder** (go to `Preferences > Browse Packages...` menu item to open this folder)
2. Rename the folder with `JavaScript Enhancements` name (**THIS STEP IS IMPORTANT**).

If all is going in the right way, you will see `JavaScript Enhancements - installing npm dependencies...` and, after a while, `JavaScript Enhancements - npm dependencies installed correctly.` messages in the status bar of Sublime Text 3. Now the plugin is ready!

### Fixing node.js and npm custom path

If the plugin gives to you message errors like `Error during installation: "node.js" seems not installed on your system...` but instead you have installed node.js and npm (for example using [nvm](https://github.com/creationix/nvm)), then you could try to set your custom path in the [Global settings](https://github.com/pichillilorenzo/JavaScriptEnhancements/wiki/Global-settings) of the plugin and then restart Sublime Text. 

If you don't know the path of them, use `which node`/`which npm` (for Linux-based OS) or `where node.exe`/`where npm` (for Windows OS) to get it.

If this doesn't work too, then you could try to add the custom path that contains binaries of node.js and npm in the **`PATH`** key-value on the same JavaScript Enhancements settings file. This variable will be **appended** to the **$PATH** environment variable, so you could use the same syntax in it. After this you need to restart Sublime Text. Example of a global setting for `Linux` that uses `nvm`:

```
{
  // ...

  "PATH": ":/home/lorenzo/.nvm/versions/node/v9.2.0/bin",
  "node_js_custom_path": "node",
  "npm_custom_path": "npm",

  // ...
}
```

For _Linux-based OS_ **REMEMBER** to add `:` (for _Windows OS_ **REMEMBER** to add `;`) at the begin of the `PATH` value!! Like I already said, it uses the same syntax for the $PATH environment variable.

## Usage

[See the Wiki](https://github.com/pichillilorenzo/JavaScriptEnhancements/wiki).

## Quick Overview

### Auto-completions
![](https://drive.google.com/uc?authuser=0&id=1NZYWq4kOx9l93zxN7A9TEMUv0VcLfWrt&export=download)

### Errors
![](https://drive.google.com/uc?authuser=0&id=1r8IDItL03tPFwCCsTIdW54rRpascnHAF&export=download)
![](https://drive.google.com/uc?authuser=0&id=1hjtcvuMNZe7NP3_nE10X_6qEEbLvl-AA&export=download)

### Projects with terminal ([TerminalView](https://github.com/Wramberg/TerminalView)) 
![](https://drive.google.com/uc?authuser=0&id=1gmC6GROJXyhV8DZTHw8Zw_KGlB13g_bL&export=download)
![](https://drive.google.com/uc?authuser=0&id=1Y0NS1eb8aFoxhdn75JLoGgZMPPpqld3Z&export=download)
![](https://drive.google.com/uc?authuser=0&id=1lHXQGN3CoV5-IHAoesEmkiJBjnpU2Lxf&export=download)

See the [Wiki](https://github.com/pichillilorenzo/JavaScriptEnhancements/wiki) for complete examples and the other **features**.

## Support

### Issues/Questions

If you have any problems, create an [issue](https://github.com/pichillilorenzo/JavaScriptEnhancements/issues) (protip: do a quick search first to see if someone else didn't ask the same question before!). For small questions, you can use [![Gitter](https://img.shields.io/gitter/room/nwjs/nw.js.svg)](https://gitter.im/JavaScriptEnhancements/Lobby).

Email me for any questions or doubts about this project on: [pichillilorenzo@gmail.com](mailto:pichillilorenzo@gmail.com)

### Feature request/enhancement

For feature requests/enhancement, create an issue or use [![Gitter](https://img.shields.io/gitter/room/nwjs/nw.js.svg)](https://gitter.im/JavaScriptEnhancements/Features).

### Financial contributions

If this project helps you reduce time to develop and also you like it, please support it with a donation on [Patreon](https://www.patreon.com/bePatron?u=9269604), [Open Collective](https://opencollective.com/javascriptenhancements/donate) or using [PayPal](https://www.paypal.me/LorenzoPichilli) 😄👍. Thanks!

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.me/LorenzoPichilli)
[![Become a Patron](https://img.shields.io/badge/-Become%20a%20Patron!-red.svg?style=for-the-badge)](https://www.patreon.com/bePatron?u=9269604)
<a href="https://opencollective.com/javascriptenhancements/donate" target="_blank">
  <img alt="opencollective" src="https://opencollective.com/javascriptenhancements/donate/button@2x.png?color=blue" width=300 />
</a>

## Credits

### Sponsors

Support this project by becoming a sponsor. Your logo will show up here with a link to your website. [[Become a sponsor](https://opencollective.com/javascriptenhancements#sponsor)]

<!-- 
<a href="https://opencollective.com/javascriptenhancements/sponsor/0/website" target="_blank"><img src="https://opencollective.com/javascriptenhancements/sponsor/0/avatar.svg"></a>
-->
<a href="https://opencollective.com/javascriptenhancements#sponsors" target="_blank"><img src="https://opencollective.com/javascriptenhancements/sponsors.svg?width=890"></a>

### Backers

Thank you to all our backers! 🙏 [[Become a backer](https://opencollective.com/javascriptenhancements#backer)]

<a href="https://opencollective.com/javascriptenhancements#backers" target="_blank"><img src="https://opencollective.com/javascriptenhancements/backers.svg?width=890"></a>

### Contributors

This project exists thanks to all the people who contribute. [[Contribute](CONTRIBUTING.md)].
<a href="/../../graphs/contributors"><img src="https://opencollective.com/javascriptenhancements/contributors.svg?width=890" /></a>


## License

_MIT License_
