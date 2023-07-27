PLUGIN_ID = "gitago.websockets"



TP_PLUGIN_INFO = {
    "sdk": 6,
    "version": 102,
    "name": "Websockets",
    "id": PLUGIN_ID,
    "plugin_start_cmd_windows": "%TP_PLUGIN_FOLDER%Websocket Plugin\\Websockets_TP.exe",
    "configuration": {
        "colorDark": "#222423",
        "colorLight": "#43a047"
    },
    "plugin_start_cmd": "%TP_PLUGIN_FOLDER%Websocket Plugin\\Websockets_TP.exe",
    "plugin_start_cmd_linux": "sh %TP_PLUGIN_FOLDER%TwitchExtras//start.sh Websockets_TP",
    "plugin_start_cmd_mac": "sh %TP_PLUGIN_FOLDER%TwitchExtras//start.sh Websockets_TP",
}



TP_PLUGIN_SETTINGS = {
    "1": {
        "name": "Debug",
        "default": "False",
        "type": "text"
    }
}



TP_PLUGIN_CATEGORIES = {
    "main": {
        "id": PLUGIN_ID + ".main",
        "name": "Websockets Main Category",
        "imagepath": "%TP_PLUGIN_FOLDER%Websocket Plugin\\Websockets_Logo.png"
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


