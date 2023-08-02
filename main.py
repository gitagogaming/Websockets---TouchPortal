## Websockets 
import TouchPortalAPI
from TouchPortalAPI import TYPES
from TouchPortalAPI.logger import Logger
from TPPEntry import TP_PLUGIN_ACTIONS, TP_PLUGIN_STATES, TP_PLUGIN_EVENTS, PLUGIN_ID
import os
import webbrowser
import time
import json
import websocket
import toml
#from socketioWrapper import IOSocketWrapper
import socketio
import toml

from sys import exit

### Local Imports
from update_check import plugin_update_check, GITHUB_PLUGIN_NAME, GITHUB_USER_NAME, PLUGIN_NAME


TP_PATH = os.path.expandvars(rf'%APPDATA%\TouchPortal\plugins\{PLUGIN_NAME}')



class WebSocketWrapper:
    """
    Sending Messages via Websocket.

    Attributes:
        websockets (dict): A dictionary of WebSocket connection objects.
        logger (logging.Logger): The logger object for logging messages.
    """

    def __init__(self):
        self.websockets = {}
      #  GLOG = logging.getLogger(__name__)

    def connect(self, socket_name, websocket_url):
         ## creating state for new socket
        ws = self.websockets.get(socket_name)
        if ws is None:
            plugin.createState(stateId=PLUGIN_ID + f".state.response.{socket_name}", value="", description=f"WS | {socket_name} Websocket Response", parentGroup=socket_name)
            plugin.createState(stateId=PLUGIN_ID + f".state.socket.{socket_name}.status", value="", description=f"WS | {socket_name} Websocket Status", parentGroup=socket_name)   

            try:
                ws = websocket.create_connection(websocket_url)
               # for OBS, dont think people need thistry:
               # for OBS, dont think people need this    self.server_hello = json.loads(ws.recv())
               # for OBS, dont think people need thisexcept:
               # for OBS, dont think people need this    pass

                self.websockets[socket_name] = ws
                plugin.log.info(f"WebSocket connection '{socket_name}' opened successfully.")
                plugin.stateUpdate(stateId=PLUGIN_ID + ".state.sockets_open", stateValue=str(len(self.websockets)))

                plugin.stateUpdate(stateId=PLUGIN_ID + f".state.socket.{socket_name}.status", stateValue="Connected")
                return ws
            except ConnectionRefusedError:
                plugin.stateUpdate(stateId=PLUGIN_ID + f".state.socket.{socket_name}.status", stateValue="Disconnected")
                plugin.stateUpdate(stateId=PLUGIN_ID + f".state.response.{socket_name}", stateValue="Failed to Connect, Connection Refused")
                plugin.log.error("Connection was actively refused by the target machine.")
                return "Connection was actively refused by the target machine."
            except Exception as e:
                plugin.log.error(f"Failed to open WebSocket '{socket_name}' due to: {str(e)}")
                return
        else:
            plugin.log.error(f"WebSocket connection '{socket_name}' already open.")
            return "WebSocket connection already open."

    def disconnect(self, socket_name):
        ws = self.websockets.get(socket_name)
        if ws is not None:
            ws.close()
            del self.websockets[socket_name]
            plugin.log.info(f"WebSocket connection '{socket_name}' closed successfully.")
            plugin.stateUpdate(stateId=PLUGIN_ID + ".state.sockets_open", stateValue=str(len(self.websockets)))

            ## updating and or creating state for socket status
            plugin.stateUpdate(stateId=PLUGIN_ID + f".state.response.{socket_name}", stateValue="Socket Closed")
            plugin.stateUpdate(stateId=PLUGIN_ID + f".state.socket.{socket_name}.status", stateValue="Disconnected")
            return "WebSocket connection closed successfully."
        else:
            plugin.log.error(f"No WebSocket connection '{socket_name}' to close.")
            return "No WebSocket connection to close."
        
    def disconnect_all(self):
        for socket_name in list(self.websockets.keys()):
            self.disconnect(socket_name)
        plugin.log.info("All WebSocket connections closed successfully.")
        return "All WebSocket connections closed successfully."

    def send_command(self, socket_name, socket_url, command):
        ws = self.websockets.get(socket_name)
        if ws is None:
          #  print(socket_name, socket_url)
            self.connect(socket_name, socket_url)
            ws = self.websockets.get(socket_name)

        command_json = json.loads(command)
        try:
            ws.send(json.dumps(command_json))
            response = ws.recv()
            return json.loads(response)
        except Exception as e:
            plugin.log.error(f"Failed to send command via WebSocket '{socket_name}' due to: {str(e)}")





class IOSocketWrapper:
    def __init__(self):
        self.event_handlers = {}  # Dictionary to store event names and their corresponding event handler functions
        self.sio = socketio.Client()
        self.servers = {}
        self.websockets = {}

    def get_server_details(self):
        """
        Return server details in dictionary format.
        """
        return self.servers

    # def process_message(self, event_name, data):
    #     """
    #     Method to process the received WebSocket message based on the event name.
    #     """
    #     if event_name in self.event_handlers:
    #         event_handler = self.event_handlers[event_name]
    #         event_handler(data)

    def send_message(self, server_name, data, event_name='update_event',):
        """
        Method to send a message to the server.

        - need to create an action for this.. socketio specicially as we will need to specify event name, server url & data message
        """
      #  sio.emit('update_event', {'data': 'Hello from client'})
        ws = self.websockets.get(server_name)
        ws.emit(event_name, data)
        #self.sio.emit(event_name, data)

    def create_event(self, server_url, event_name, server_name, eventParse):
        """
        Function to create event handlers dynamically based on the server name, event name, and response key.
        """
        @self.sio.on(event_name)
        def dynamic_event_handler(data):
            if eventParse != "":
                plugin.stateUpdate(stateId=PLUGIN_ID + f".state.response.{server_name}.{event_name}",
                                stateValue=str(data[eventParse]))
            else:
                plugin.stateUpdate(stateId=PLUGIN_ID + f".state.response.{server_name}.{event_name}",
                                stateValue=str(data))
            plugin.log.debug(f"Received event '{event_name}' from server '{server_name}'.")
            
    def connect(self, websocket_url, server_name):
        ws = self.websockets.get(server_name)
        if ws is None:
            ws = self.sio.connect(websocket_url)
            # dont need this? but why.. im so confused...   because of when auto loads? for event_name in self.event_handlers:
            # dont need this? but why.. im so confused...   because of when auto loads?     ws.on(event_name, self.event_handlers[event_name])  # Register event handlers with SocketIO
            # dont need this? but why.. im so confused...   because of when auto loads?     plugin.log.debug(f"Registered event handler for event '{event_name} at {websocket_url}.")

            self.websockets[server_name] = ws

    def disconnect(self):
        self.sio.disconnect()



class ClientInterface(TouchPortalAPI.Client):
    def __init__(self):
        super().__init__(self)
        
        
        self.pluginId = PLUGIN_ID
        self.TPHOST = "127.0.0.1"
        self.TPPORT = 12136
        self.RCV_BUFFER_SZ = 4096 
        self.SND_BUFFER_SZ = 1048576

        # Log settings
        self.logLevel = "INFO"

        self.setLogFile(PLUGIN_ID + "_LOG")
    
        # Register events
        self.add_listener(TYPES.onConnect, self.onConnect)
        self.add_listener(TYPES.onAction, self.onAction)
        self.add_listener(TYPES.onShutdown, self.onShutdown)
        self.add_listener(TYPES.onListChange, self.onListChange)
        self.add_listener(TYPES.onNotificationOptionClicked, self.onNoticationClicked)
        self.add_listener(TYPES.onSettingUpdate, self.onSettings)






    """
    Custom Method/Functions
    """
    def settingsToDict(self, settings):
        """ 
        Convert a list of settings to a dictionary
        """
        return { list(settings[i])[0] : list(settings[i].values())[0] for i in range(len(settings)) }

    def load_config(self, config_file):
        """
        Load server configurations from the socketconfig.ini file.
        """
        try:
            config = toml.load(config_file)
            for server_name, server_info in config.items():
                server_url = server_info.get("socketURL", None)
                if server_url and server_url.startswith("http"):
                    events = server_info['events']
                    for eventnumber, event_config in events.items():
                        socketIO.create_event(server_url, event_config['eventName'], server_name, event_config['eventParse'])
                        ## create a state using the stateUpdate key
                        plugin.createState(stateId=PLUGIN_ID + f".state.response.{server_name}.{event_config['eventName']}",
                                            value="", description=f"WS | {server_name} {event_config['eventName']} socketIO Response", parentGroup=server_name)

                    plugin.log.debug(f"Connecting: '{server_name}' at '{server_url}' and events '{events}'.")
                    socketIO.connect(websocket_url=server_url, server_name=server_name)


                elif server_url and server_url.startswith("ws"):
                    events = server_info.get('events')
                    plugin.log.debug(f"Connecting: '{server_name}' at '{server_url}' and events '{events}'.")
                    WS.connect(socket_name=server_name,
                            websocket_url=server_url)

            socketIO.servers = config
            #try:
            #    socketIO.sio.wait()
            #except KeyboardInterrupt:
            #    socketIO.disconnect()
            return config
        except FileNotFoundError:
            plugin.log.debug(f"Error: Configuration file '{config_file}' not found.")


    """
    Events
    """
    def onConnect(self, data):
        self.log.info(f"Connected to TP v{data.get('tpVersionString', '?')}, plugin v{data.get('pluginVersion', '?')}.")
        self.plugin_settings = self.settingsToDict(data["settings"])

        if self.plugin_settings['Debug'].lower() == "true":
            self.setLogLevel("DEBUG")
        else:
            self.setLogLevel("INFO")


        if os.path.exists(self.plugin_settings['Config File Location']):
            print("Config File Exists")
            self.load_config(self.plugin_settings['Config File Location'])
#

        plugin.stateUpdate(stateId=PLUGIN_ID + ".state.sockets_open", stateValue="0")
     #  try:
     #      if self.plugin_settings.get("Autoconnect #1 Socket Name") != "":
     #          WS.connect(socket_name=self.plugin_settings.get("Autoconnect #1 Socket Name"),
     #                      websocket_url=self.plugin_settings.get("Autoconnect #1 Socket URL"))
     #      if self.plugin_settings.get("Autoconnect #2 Socket Name") != "":
     #          WS.connect(socket_name=self.plugin_settings.get("Autoconnect #2 Socket Name"),
     #                     websocket_url=self.plugin_settings.get("Autoconnect #2 Socket URL"))
     #  except Exception as e:
     #      plugin.log.error(f"Failed to Autoconnect to Websockets due to: {str(e)}")

        ## Checking for Updates
        try:
            github_check, message = plugin_update_check(str(data['pluginVersion']))
            if github_check:
                plugin.showNotification(
                    notificationId= f"{PLUGIN_ID}.TP.Plugins.Update_Check",
                    title=f"{PLUGIN_NAME} {github_check} is available",
                    msg=f"A new version of {PLUGIN_NAME} is available and ready to Download.\nThis may include Bug Fixes and or New Features\n\nPatch Notes\n{message} ",
                    options= [{
                    "id":f"{PLUGIN_ID}.tp.update.download",
                    "title":"Click to Update!"
                }])
        except:
            print("Error Checking for Updates")



    def onSettings(self, data):
        self.plugin_settings = self.settingsToDict(data['values'])
        self.log.debug(f"Connection: {data}")


    def onAction(self, data):
        self.log.debug(f"Connection: {data}")
        plugin.log.debug(f"Action: {data}")
        print(data)
        if not (action_data := data.get('data')) or not (aid := data.get('actionId')):
            return
        
        if aid == PLUGIN_ID + ".act.send_message":
            socket_name = data['data'][2]['value']
            response = WS.send_command(socket_name=socket_name,
                                    socket_url=data['data'][0]['value'],
                                    command=data['data'][1]['value'])
         #   print("The Response", response)      
            if response:
                print("yea so why isnt it working")
                print(PLUGIN_ID + f".state.response.{socket_name}", {str(response)})
                plugin.createState(stateId=PLUGIN_ID + f".state.response.{socket_name}", value=str(response), description=f"WS | {socket_name} Websocket Response", parentGroup=data['data'][2]['value'])
            plugin.log.debug(f"Response: {response}")

        elif aid == PLUGIN_ID + ".act.disconnect":
            WS.disconnect(data['data'][0]['value'])

        elif aid == PLUGIN_ID + ".act.connect":
            print("connect to websocket", data['data'][0]['value'])
            if data['data'][0]['value'].startswith("http"):
                socketIO.connect(websocket_url=data['data'][0]['value'])
            elif data['data'][0]['value'].startswith("ws"):
                WS.connect(socket_name=data['data'][1]['value'], websocket_url=data['data'][0]['value'])

        ## elif register_event
        elif aid == PLUGIN_ID + ".act.register_event":
            socketIO.create_event(server_url=data['data'][2]['value'], 
                                  event_name=data['data'][0]['value'],
                                 server_name=data['data'][1]['value'],
                                 eventParse=data['data'][3]['value'])


    def onNoticationClicked(data):
        if data['optionId'] == f'{PLUGIN_ID}.tp.update.download':
            github_check = TouchPortalAPI.Tools.updateCheck(GITHUB_USER_NAME, GITHUB_PLUGIN_NAME)
            url = f"https://github.com/{GITHUB_USER_NAME}/{GITHUB_PLUGIN_NAME}/releases/tag/{github_check}"
            webbrowser.open(url, new=0, autoraise=True)


    ## When a Choice List is Changed in a Button Action
    def onListChange(self, data):
        self.log.info(f"Connection: {data}")


    def onShutdown(self, data):
        self.log.info('Received shutdown event from TP Client.')
        self.disconnect()
        



if __name__ == "__main__":
    WS = WebSocketWrapper()
    plugin = ClientInterface()
    socketIO = IOSocketWrapper()

    plugin.log = Logger(name = PLUGIN_ID)
    ret = 0
    try:
        plugin.connect()
    except KeyboardInterrupt:
        plugin.log.warning("Caught keyboard interrupt, exiting.")
    except Exception:
        from traceback import format_exc
        plugin.log.error(f"Exception in TP Client:\n{format_exc()}")
        ret = -1
    finally:
        WS.disconnect_all()
        plugin.disconnect()
        del plugin
        exit(ret)


