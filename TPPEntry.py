PLUGIN_ID = "gitago.websockets"
PLUGIN_NAME = "Websockets_TP"
PLUGIN_FOLDER = "Websocket Plugin"
PLUGIN_ICON ="websockets_logo.png"



TP_PLUGIN_INFO = {
    "sdk": 6,
    "version": 107,
    "name": "Websockets",
    "id": PLUGIN_ID,
    "plugin_start_cmd_windows": f"%TP_PLUGIN_FOLDER%{PLUGIN_FOLDER}\\{PLUGIN_NAME}.exe",
    "configuration": {
        "colorDark": "#222423",
        "colorLight": "#43a047"
    },
    "plugin_start_cmd": f"%TP_PLUGIN_FOLDER%{PLUGIN_FOLDER}\\{PLUGIN_NAME}.exe",
    "plugin_start_cmd_linux": f"sh %TP_PLUGIN_FOLDER%{PLUGIN_FOLDER}//start.sh {PLUGIN_NAME}",
    "plugin_start_cmd_mac": f"sh %TP_PLUGIN_FOLDER%{PLUGIN_FOLDER}//start.sh {PLUGIN_NAME}",
}



TP_PLUGIN_SETTINGS = {
    "1": {
        "name": "Debug",
        "default": "False",
        "type": "text"
    },
    "2": {
        "name": "Config File Location",
        "default": "",
        "type": "text"
    },
}



TP_PLUGIN_CATEGORIES = {
    "main": {
        "id": PLUGIN_ID + ".main",
        "name": "Websockets",
        "imagepath": f"%TP_PLUGIN_FOLDER%Websocket Plugin\\{PLUGIN_ICON}.png"
    }
}

TP_PLUGIN_CONNECTORS = {}



TP_PLUGIN_ACTIONS = {
    "1": {
        "id": PLUGIN_ID + ".act.send_message",
        "name": "Send Websocket Message",
        "prefix": "Prefix",
        "type": "communicate",
        "tryInline": True,
        "description": "Connect & Send a Message to specified Websocket. Example URL:  ws://localhost:9000",
        "format": "Websocket URL:$[1] Message:$[2] with Socket Name:$[3]",
        "data": {
            "1": {
                "id": PLUGIN_ID + ".act.send_message.url",
                "type": "text",
                "label": "The IP and Port of the Websocket",
                "default": "ws://localhost:9000"
            },
            "2": {
                "id": PLUGIN_ID + ".act.send_message.content",
                "type": "text",
                "label": "The Code or Message to Send",
                "default": ""
            },
            "3": {
                "id": PLUGIN_ID + ".act.send_message.socket",
                "type": "text",
                "label": "The Socket Name",
                "default": ""
            }   
        },
        "category": "main"
    },
    "2": {
        "id": PLUGIN_ID + ".act.disconnect",
        "name": "Disconnect Websocket",
        "prefix": "Prefix",
        "type": "communicate",
        "tryInline": True,
        "description": "Disconnect a Websocket.",
        "format": "Websocket with Socket Name:$[1]",
        "data": {
            "1": {
                "id": PLUGIN_ID + ".act.disconnect.socket",
                "type": "text",
                "label": "The Socket Name",
                "default": ""
            }
        },
        "category": "main"
    },
    ## register socketio event
    "3": {
        "id": PLUGIN_ID + ".act.register_event",
        "name": "Register SocketIO Event",
        "prefix": "Prefix",
        "type": "communicate",
        "tryInline": True,
        "description": "Register a SocketIO Event - URL ",
        "format": "Websocket Event Name:$[1] with Socket Name:$[2], Socket URL:$[3] and ParseData:$[4]",
        "data": {
            "1": {
                "id": PLUGIN_ID + ".act.register_event.event",
                "type": "text",
                "label": "The Event Name",
                "default": ""
            },
            "2": {
                "id": PLUGIN_ID + ".act.register_event.socket",
                "type": "text",
                "label": "The Socket Name",
                "default": ""
            },
            "3": {
                "id": PLUGIN_ID + ".act.register_event.url",
                "type": "text",
                "label": "The IP and Port of the Websocket",
                "default": "http://192.168.0.100:9000"
            },
            "4": {
                "id": PLUGIN_ID + ".act.register_event.parseData",
                "type": "text",
                "label": "Parse Event",
                "default": ""
            }
        }
    },

  #  ## socket IO connect
  # "3": {
  #     "id": PLUGIN_ID + ".act.connectIO",
  #     "name": "Connect SocketIO",
  #     "prefix": "Prefix",
  #     "type": "communicate",
  #     "tryInline": True,
  #     "description": "Connect to a SocketIO.",
  #     "format": "SocketIO URL:$[1] with Socket Name:$[2]",
  #     "data": {
  #         "1": {
  #             "id": PLUGIN_ID + ".act.connectIO.url",
  #             "type": "text",
  #             "label": "The IP and Port of the SocketIO",
  #             "default": "http://localhost:9000"
  #         },
  #         "2": {
  #             "id": PLUGIN_ID + ".act.connectIO.socket",
  #             "type": "text",
  #             "label": "The Socket Name",
  #             "default": ""
  #         }
  #     },
  #     "category": "main"
  # },

    "4": {
        ## connect to websocket
        "id": PLUGIN_ID + ".act.connect",
        "name": "Connect Websocket",
        "prefix": "Prefix",
        "type": "communicate",
        "tryInline": True,
        "description": "Connect to a Websocket.",
        "format": "Websocket URL:$[1] with Socket Name:$[2]",
        "data": {
            "1": {
                "id": PLUGIN_ID + ".act.connect.url",
                "type": "text",
                "label": "The IP and Port of the Websocket",
                "default": "ws://localhost:9000"
            },
            "2": {
                "id": PLUGIN_ID + ".act.connect.socket",
                "type": "text",
                "label": "The Socket Name",
                "default": ""
            }
        }
    }
}



TP_PLUGIN_STATES = {
    "0": {
        "id": PLUGIN_ID + ".state.sockets_open",
        "type": "text",
        "desc": "WS | Total Websockets Open",
        "default": "",
        "category": "main"
    }
}



TP_PLUGIN_EVENTS = {
 #  "0": {
 #      'id': PLUGIN_ID + ".event.socket.closed",
 #      'name':"WS | Socket Closed",
 #      'category': "main",
 #      "format":"When Socket Closes for $val",
 #      "type":"communicate",
 #      "valueType":"choice",
 #      "valueChoices": [],
 #      "valueStateId": PLUGIN_ID + ".state.socket.closed",
 #		},
 #  "1": {
 #      'id': PLUGIN_ID + ".event.socket.opened",
 #      'name':"WS | Socket Opened",
 #      'category': "main",
 #      "format":"When Socket Opens for $val",
 #      "type":"communicate",
 #      "valueType":"choice",
 #      "valueChoices": [],
 #      "valueStateId": PLUGIN_ID + ".state.socket.opened",
 #      }
}


