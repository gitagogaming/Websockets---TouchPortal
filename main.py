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

### Local Imports
from update_check import plugin_update_check, GITHUB_PLUGIN_NAME, GITHUB_USER_NAME, PLUGIN_NAME


TP_PATH = os.path.expandvars(rf'%APPDATA%\TouchPortal\plugins\{PLUGIN_NAME}')



class SendMessage_Socket:
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
                self.websockets[socket_name] = ws
                plugin.log.info(f"WebSocket connection '{socket_name}' opened successfully.")
                plugin.stateUpdate(stateId=PLUGIN_ID + ".state.sockets_open", stateValue=str(len(self.websockets)))

                plugin.stateUpdate(stateId=PLUGIN_ID + f".state.socket.{socket_name}.status", stateValue="Connected")
                plugin.stateUpdate(stateId=PLUGIN_ID + f".state.response.{socket_name}", stateValue="Socket Opened")  
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
            self.connect(socket_name, socket_url)
            ws = self.websockets.get(socket_name)
        command_json = json.loads(command)
        try:
            ws.send(json.dumps(command_json))
            response = ws.recv()
            return json.loads(response)
        except Exception as e:
            plugin.log.error(f"Failed to send command via WebSocket '{socket_name}' due to: {str(e)}")




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



    """
    Events
    """
    def onConnect(self, data):
        self.log.info(f"Connected to TP v{data.get('tpVersionString', '?')}, plugin v{data.get('pluginVersion', '?')}.")
        self.plugin_settings = self.settingsToDict(data["settings"])
        plugin.stateUpdate(stateId=PLUGIN_ID + ".state.sockets_open", stateValue="0")
            

        try:
            if self.plugin_settings.get("Autoconnect #1 Socket Name") != "":
                WS.connect(socket_name=self.plugin_settings.get("Autoconnect #1 Socket Name"),
                            websocket_url=self.plugin_settings.get("Autoconnect #1 Socket URL"))
            if self.plugin_settings.get("Autoconnect #2 Socket Name") != "":
                WS.connect(socket_name=self.plugin_settings.get("Autoconnect #2 Socket Name"),
                           websocket_url=self.plugin_settings.get("Autoconnect #2 Socket URL"))
        except Exception as e:
            plugin.log.error(f"Failed to Autoconnect to Websockets due to: {str(e)}")

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
        if not (action_data := data.get('data')) or not (aid := data.get('actionId')):
            return
        
        if aid == PLUGIN_ID + ".act.send_message":
            socket_name = data['data'][2]['value']
            response = WS.send_command(socket_name=socket_name,
                                    socket_url=data['data'][0]['value'],
                                    command=data['data'][1]['value'])
            if response:
                plugin.createState(stateId=PLUGIN_ID + f".state.response.{socket_name}", value=str(response), description=f"WS | {socket_name} Websocket Response", parentGroup=data['data'][2]['value'])
            plugin.log.debug(f"Response: {response}")

        elif aid == PLUGIN_ID + ".act.disconnect":
            WS.disconnect(data['data'][0]['value'])

       # not used yet elif aid == PLUGIN_ID + ".act.connect":
       # not used yet     WS.connect(socket_name=data['data'][1]['value'], websocket_url=data['data'][0]['value'])


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
        

# Create an instance of the SendMessage_Socket class
message_socket = SendMessage_Socket()


if __name__ == "__main__":
    WS = SendMessage_Socket()
    plugin = ClientInterface()
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


