"use strict";

const electron = require('electron')
const {ipcMain} = require('electron')
const SocketWindow = require('../../../js/SocketWindow.js')

const app = new SocketWindow('localhost', 11113, __dirname, 600, 600)

app.listenSocketCommand('show_structure_javascript', (data) => {
  app.sendWeb('data', data)
})

ipcMain.on('data', (event, line) => {
  let data = {
    "command": "set_dot_line",
    "line": line
  }
  app.sendSocketJson(data)
})

app.start()
