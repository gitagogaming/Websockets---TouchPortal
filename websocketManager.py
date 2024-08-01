## Websockets Manager
import json
import websocket
import socketio 
from typing import Dict

import TouchPortalAPI as TP
from TPPEntry import PLUGIN_ID

     
      
class WebSocketClient:
    def __init__(self, plugin:TP.Client):
        self.plugin = plugin
        self.websockets: Dict[str, WebSocketWrapper] = {}

    def handle_message(self, socket_name:str, message:str):
        try:
            message = json.loads(message)
            if message['op'] == 0:  # Hello message
                self.plugin.log.info(f"Received Hello message on '{socket_name}'")
            
            self.plugin.stateUpdate(stateId=PLUGIN_ID + f".state.response.{socket_name}", stateValue=str(message))
        except json.JSONDecodeError:
            self.plugin.log.error(f"Received non-JSON message on '{socket_name}': {message}")
            self.plugin.stateUpdate(stateId=PLUGIN_ID + f".state.response.{socket_name}", stateValue=str(message))

        
    def connect(self, socket_name:str, websocket_url:str):
        if socket_name not in self.websockets:
            self.plugin.createState(stateId=PLUGIN_ID + f".state.response.{socket_name}", value="", description=f"WS | {socket_name} Websocket Response", parentGroup=socket_name)
            self.plugin.createState(stateId=PLUGIN_ID + f".state.socket.{socket_name}.status", value="", description=f"WS | {socket_name} Websocket Status", parentGroup=socket_name)   

            try:
                ws_wrapper = WebSocketWrapper(socket_name, websocket_url, self)
                self.websockets[socket_name] = ws_wrapper
                ws_wrapper.run_forever()
                return ws_wrapper
            
            except ConnectionRefusedError:
                self.plugin.stateUpdate(stateId=PLUGIN_ID + f".state.socket.{socket_name}.status", stateValue="Disconnected")
                self.plugin.stateUpdate(stateId=PLUGIN_ID + f".state.response.{socket_name}", stateValue="Failed to Connect, Connection Refused")
                self.plugin.log.error("Connection was actively refused by the target machine.")
                return "Connection was actively refused by the target machine."
            except Exception as e:
                self.plugin.log.error(f"Failed to open WebSocket '{socket_name}' due to: {str(e)}")
                return
        else:
            self.plugin.log.error(f"WebSocket connection '{socket_name}' already open.")
            return "WebSocket connection already open."

    def send_command(self, socket_name:str, socket_url:str, command:str):
        if (socket := self.websockets.get(socket_name)) is None:
            self.connect(socket_name, socket_url)
            socket = self.websockets.get(socket_name)
            
        if socket:
            try:
                socket.ws.send(command)
                self.plugin.log.debug(f"Message sent to '{socket_name}': {command}")
            except websocket.WebSocketConnectionClosedException:
                self.plugin.log.error(f"Failed to send message to '{socket_name}' because the connection is already closed.")
        else:
            self.plugin.log.error(f"No WebSocket connection found for '{socket_name}'.")

    def disconnect(self, socket_name:str):
        if socket_name in self.websockets:
            socket = self.websockets[socket_name]
            socket.ws.close()
        else:
            self.plugin.log.error(f"No WebSocket connection found for '{socket_name}'.")
            
    def disconnect_all(self):
        for socket_name in list(self.websockets.keys()):
            self.disconnect(socket_name)
        self.plugin.log.info("All WebSocket connections closed successfully.")
        return "All WebSocket connections closed successfully."
     


class WebSocketWrapper:
    def __init__(self, socket_name, websocket_url, client: WebSocketClient):
        self.socket_name = socket_name
        self.websocket_url = websocket_url
        self.client = client
        self.ws = websocket.WebSocketApp(
            websocket_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )

    def on_open(self, ws):
        self.client.plugin.log.info(f"WebSocket connection '{self.socket_name}' opened successfully.")
        self.client.plugin.stateUpdate(stateId=PLUGIN_ID + ".state.sockets_open", stateValue=str(len(self.client.websockets)))
        self.client.plugin.stateUpdate(stateId=PLUGIN_ID + f".state.socket.{self.socket_name}.status", stateValue="Connected")
        

    def on_message(self, ws, message):
        self.client.handle_message(self.socket_name, message)

    def on_error(self, ws, error):
        self.client.plugin.log.error(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        self.client.plugin.log.info(f"WebSocket '{self.socket_name}' closed with status: {close_status_code}, message: {close_msg}")
        if self.socket_name in self.client.websockets:
            del self.client.websockets[self.socket_name]
            self.client.plugin.stateUpdate(stateId=PLUGIN_ID + ".state.sockets_open", stateValue=str(len(self.client.websockets)))
            self.client.plugin.stateUpdate(stateId=PLUGIN_ID + f".state.socket.{self.socket_name}.status", stateValue="Disconnected")

    def run_forever(self):
        self.ws.run_forever()
        
        
        
        
        
        
        
class IOSocketWrapper:
    def __init__(self, plugin:TP.Client):
        self.plugin = plugin
        self.event_handlers = {}  # Dictionary to store event names and their corresponding event handler functions
        self.sio = socketio.Client()
        self.servers = {}
        self.websockets = {}

    def get_server_details(self):
        """
        Return server details in dictionary format.
        """
        return self.servers

    def process_message(self, event_name, data):
        """
        Method to process the received WebSocket message based on the event name.
        - unused currently
        """
        if event_name in self.event_handlers:
            event_handler = self.event_handlers[event_name]
            event_handler(data)

    def send_message(self, server_name:str, data:str, event_name:str='update_event'):
        """
        Method to send a message to the server.

        - need to create an action for this.. socketio specicially as we will need to specify event name, server url & data message
        """
        ws = self.websockets.get(server_name)
        ws.emit(event_name, data)
        #self.sio.emit(event_name, data)

    def create_event(self, server_url:str, event_name:str, server_name:str, eventParse:str):
        """
        Function to create event handlers dynamically based on the server name, event name, and response key.
        """
        @self.sio.on(event_name)
        def dynamic_event_handler(data):
            if eventParse != "":
                self.plugin.stateUpdate(stateId=PLUGIN_ID + f".state.response.{server_name}.{event_name}",
                                stateValue=str(data[eventParse]))
            else:
                self.plugin.stateUpdate(stateId=PLUGIN_ID + f".state.response.{server_name}.{event_name}",
                                stateValue=str(data))
            self.plugin.log.debug(f"Received event '{event_name}' from server '{server_name}'.")
            
    def connect(self, websocket_url:str, server_name:str):
        ws = self.websockets.get(server_name)
        if ws is None:
            ws = self.sio.connect(websocket_url)
            self.websockets[server_name] = ws

    def disconnect(self):
        self.sio.disconnect()

        
   