"use strict";

const electron = require('electron')
const {ipcMain} = require('electron')
const net = require('net')
const struct = require('python-struct')
const path = require('path')
const url = require('url')

module.exports = class SocketWindow {

  constructor(host, port, dirname, width, height){
    this.host = host
    this.port = port
    this.dirname = dirname
    this.width = width
    this.height = height
    this.app = electron.app
    this.window = null
    this.client = new net.Socket()
    this.socketCommands = {}
    this.currData = null
    this.dataSize = 0
  }

  init(){
    this.app.on('window-all-closed', () => {
      this.app.quit()
    })
  }

  createWindow(){
    this.window = new electron.BrowserWindow({width: this.width, height: this.height})
    this.window.loadURL(url.format({
      pathname: path.join(this.dirname, 'index.html'),
      protocol: 'file:',
      slashes: true
    }))
    //this.window.webContents.openDevTools()
    this.window.on('closed', () => {
      this.window = null
    })
  }

  connect(){
    this.client.connect(this.port, this.host, () => {
      let data = {
        "command": "ready"
      }
      this.sendSocketJson(data)
    })
  }

  listenSocket(){
    this.client.on('data', (data) => {
      if(!this.currData){
        this.sizeData = struct.unpack("i", data)
        this.currData = data.slice(struct.sizeOf("i")).toString('utf8').substring(0, this.sizeData)
      }
      else{
        this.currData += data.toString('utf8')
        this.currData = this.currData.substring(0, this.sizeData)
      }
      if(this.currData.length < this.sizeData){
        return
      }
      if(data == "server_accept_only_one_client"){
        app.quit()
      }
      this.currData = JSON.parse(this.currData)
      if(this.currData.command == "server_closing"){
        app.quit()
      }
      else if(this.socketCommands[this.currData.command]){
        this.socketCommands[this.currData.command](this.currData)
      }
      this.currData = null
      this.sizeData = 0
    })
  }

  start(fun){
    this.init()
    this.app.on('ready', () => {
      this.createWindow()
      this.connect()
      this.listenSocket()

      if(fun)
        fun()
    })
  }

  listenSocketCommand(name, fun){
    if(!this.socketCommands[name]){
      this.socketCommands[name] = fun
    }
    else{
      throw new Error(`SocketCommand "${name}" already used`)
    }
  }

  sendSocket(data){
    data = data + ""
    this.client.write(struct.pack("i", data.length) + data)
  }

  sendSocketJson(data){
    data = JSON.stringify(data)
    this.sendSocket(data)
  }

  sendWeb(channel, ...data){
    this.window.webContents.send(channel, ...data)
  }
}