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
    this.window.webContents.openDevTools()
    this.window.on('closed', () => {
      this.window = null
    })
  }

  connect(){
    this.client.connect(this.port, this.host)
  }

  listenSocket(){
    this.client.on('data', (data) => {
      if(!this.currData){
        this.sizeData = struct.unpack("<i", data)
        this.currData = data.slice(struct.sizeOf("<i")).toString('utf8').substring(0, this.sizeData)
      }
      else{
        this.currData += data.toString('utf8')
        this.currData = this.currData.substring(0, this.sizeData)
      }
      if(this.currData.length < this.sizeData){
        return
      }
      if(this.currData == "server_accept_only_one_client"){
        this.app.quit()
      }
      this.currData = JSON.parse(this.currData)
      if(this.currData.command == "server_closing"){
        this.app.quit()
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
      this.window.webContents.on("did-finish-load", () => {
        let data = {
          "command": "ready"
        }
        this.sendSocketJson(data)
      })
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
    data = Buffer.from(data)
    let prefix = new Buffer(4)
    prefix.writeIntLE(data.length, 0, 4)
    this.client.write(Buffer.concat([prefix, data]))
  }

  sendSocketJson(data){
    data = JSON.stringify(data)
    this.sendSocket(data)
  }

  sendWeb(channel, ...data){
    this.window.webContents.send(channel, ...data)
  }
}