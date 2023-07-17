PLUGIN_ID = "gitago.websockets"



TP_PLUGIN_INFO = {
    "sdk": 6,
    "version": 100,
    "name": "Websockets",
    "id": PLUGIN_ID,
    "plugin_start_cmd_windows": "%TP_PLUGIN_FOLDER%Websocket Plugin\\Websockets_TP.exe",
    "configuration": {
        "colorDark": "#222423",
        "colorLight": "#43a047"
    },
    "plugin_start_cmd": "%TP_PLUGIN_FOLDER%Websocket Plugin\\Websockets_TP.exe"
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
        "description": "Connect & Send a Message to specified Websocket. \n Example URL:  ws://localhost:9000",
        "format": "Websocket URL:$[1] Message:$[2]",
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
            }
        },
        "category": "main"
    }
}



TP_PLUGIN_STATES = {
    "0": {
        "id": PLUGIN_ID + ".state.response",
        "type": "text",
        "desc": "WS | Websocket Response",
        "default": "",
        "category": "main"
    }
}



TP_PLUGIN_EVENTS = {}


