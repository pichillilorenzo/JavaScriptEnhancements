# JavaScript Enhancements

**JavaScript Enhancements** is a plugin for **Sublime Text 3**.

This plugin uses **[Flow](https://github.com/facebook/flow)** (javascript static type checker from Facebook) under the hood.

This is in **BETA** version for **testing**. 

It offers better **javascript autocomplete** and also a lot of features about creating, developing and managing **javascript projects**, such as:

- Cordova projects (run cordova emulate, build, compile, serve, etc. directly from Sublime Text!)
- Ionic v1 and v2 projects (same as Cordova projects!)
- Angular v1 and v2 projects
- React projects
- Express projects
- Yeoman generators
- Local bookmarks project
- JavaScript real-time errors
- etc.

You could use it also in **existing projects** (see the [Wiki](https://github.com/pichillilorenzo/JavaScriptEnhancements/wiki/Using-it-with-an-existing-project))!

It turns Sublime Text into a **JavaScript IDE** like!

This project is based on my other Sublime Text plugin [JavaScript Completions](https://github.com/pichillilorenzo/JavaScript-Completions)

**Note**: 
If you want use this plugin, you may want **uninstall/disable** the **JavaScript Completions** plugin, if installed.

## OS supported now

- Linux (64-bit)
- Mac OS X 

## Dependencies

In order to work properly, this plugin has some dependencies:

- **Sublime Text 3** (build **3124** or newer)
- **Node.js** and **npm** ([nodejs.org](https://nodejs.org) or [nvm](https://github.com/creationix/nvm))
- **TerminalView** sublime text plugin ([TerminalView](https://github.com/Wramberg/TerminalView)) 

**Not required**, but **useful** for typescript files (Flow wont work on this type of files):

- **TypeScript** sublime text plugin ([TypeScript](https://github.com/Microsoft/TypeScript-Sublime-Plugin)) 

### Flow Requirements

It will use [Flow](https://github.com/facebook/flow) for type checking and auto-completions.

- Mac OS X
- Linux (64-bit)
- Windows (64-bit)

You can find more information about Flow on [flow.org](https://flow.org)

## Installation

With [Package Control](https://packagecontrol.io/) (**NOT PUBLISHED YET**):

- Run “Package Control: Install Package” command or click to the `Preferences > Package Control` menu item, find and install `JavaScript Enhancements` plugin.

Manually:

1. Download [latest release](https://github.com/pichillilorenzo/JavaScriptEnhancements/releases) and unzip it into your **Packages folder** (go to `Preferences > Browse Packages...` menu item to open this folder)
2. Rename the folder with `JavaScript Enhancements` name (**THIS STEP IS IMPORTANT**).

### Fixing node.js and npm custom path

If the plugin gives to you message errors like `Error during installation: "node.js" seems not installed on your system...` but instead you have installed node.js and npm (for example using [nvm](https://github.com/creationix/nvm)), then you could try to set your custom path in the [Global settings](https://github.com/pichillilorenzo/JavaScriptEnhancements/wiki/Global-settings) of the plugin and then restart Sublime Text.

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

**REMEMBER** to add `:` at the begin of the `PATH` value!! Like I already said, it uses the same syntax for the $PATH environment variable.

## Usage

[See the Wiki](https://github.com/pichillilorenzo/JavaScriptEnhancements/wiki).

## Quick Overview

### Auto-completions
![](https://drive.google.com/uc?authuser=0&id=1NZYWq4kOx9l93zxN7A9TEMUv0VcLfWrt&export=download)

### Errors
![](https://drive.google.com/uc?authuser=0&id=1r8IDItL03tPFwCCsTIdW54rRpascnHAF&export=download)

### Projects with terminal ([TerminalView](https://github.com/Wramberg/TerminalView)) 
![](https://drive.google.com/uc?authuser=0&id=1gmC6GROJXyhV8DZTHw8Zw_KGlB13g_bL&export=download)
![](https://drive.google.com/uc?authuser=0&id=1Y0NS1eb8aFoxhdn75JLoGgZMPPpqld3Z&export=download)
![](https://drive.google.com/uc?authuser=0&id=1lHXQGN3CoV5-IHAoesEmkiJBjnpU2Lxf&export=download)

See the [Wiki](https://github.com/pichillilorenzo/JavaScriptEnhancements/wiki) for complete examples and the other **features**.

## Support

Email me for any questions or doubts about this project on: [pichillilorenzo@gmail.com](mailto:pichillilorenzo@gmail.com)

### Issues

For any problems, open an issue with the Sublime Text console logs please!

### Feature request/enhancement

For feature requests or them enhancement, please open an issue with the corresponding label.

### Donation

If this project help you reduce time to develop and also you like it, please support it with a donation :smile::thumbsup:. Thanks!

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.me/LorenzoPichilli)
<a href="https://opencollective.com/javascriptenhancements/donate" target="_blank">
  <img alt="opencollective" src="https://opencollective.com/javascriptenhancements/donate/button@2x.png?color=blue" width=300 />
</a>

## License

_MIT License_