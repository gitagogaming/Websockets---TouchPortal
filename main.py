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
import logging

### Local Imports
from update_check import plugin_update_check, GITHUB_PLUGIN_NAME, GITHUB_USER_NAME, PLUGIN_NAME


TP_PATH = os.path.expandvars(rf'%APPDATA%\TouchPortal\plugins\{PLUGIN_NAME}')

class SendMessage_Socket:
    """
    Sending Messages via Websocket.
    Args:
        websocket_url (str, optional): The URL of the WebSocket server. Defaults to "ws://localhost:9000".

    Attributes:
        websocket_url (str): The URL of the WebSocket server.
        ws (websocket._core.WebSocket): The WebSocket connection object.
        logger (logging.Logger): The logger object for logging messages.
    """

    def __init__(self):
        self.ws = None
        self.logger = logging.getLogger(__name__)
    

    def connect(self, websocket_url):
        try:
            self.ws = websocket.create_connection(websocket_url)
            self.logger.info("WebSocket connection opened successfully.")
            return self.ws
        except ConnectionRefusedError:
            self.logger.error("Connection was actively refused by the target machine.")
            return "Connection was actively refused by the target machine."
        except Exception as e:
            self.logger.error(f"Failed to open WebSocket due to: {str(e)}")
            return
 

    def disconnect(self):
        if self.ws is not None:
            self.ws.close()
            self.ws = None
            self.logger.info("WebSocket connection closed successfully.")
            return "WebSocket connection closed successfully."
        else:
            self.logger.error("No WebSocket connection to close.")
            return "No WebSocket connection to close."

    def send_command(self, websocket_url, command):
            WS.connect(websocket_url)
            command_json = json.loads(command)
            try:
                if self.ws is None:
                    self.logger.error("WebSocket connection is not open. Must connect first.")
                    self.connect(websocket_url)
                    return
    
                self.ws.send(json.dumps(command_json))
                response = self.ws.recv()
                return json.loads(response)
            except Exception as e:
                self.logger.error('Failed to send command due to: ' + str(e))




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
        self.log.debug(f"Connection: {data}")
        self.plugin_settings = self.settingsToDict(data["settings"])
            
        ## Checking for Updates
        try:
            github_check, message = plugin_update_check(str(data['pluginVersion']))
            if github_check == True:
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
        G_LOG.debug(f"Action: {data}")
        if not (action_data := data.get('data')) or not (aid := data.get('actionId')):
            return
        
        if aid == PLUGIN_ID + ".act.send_message":
          response = WS.send_command(data['data'][0]['value'], data['data'][1]['value'])
          plugin.stateUpdate(PLUGIN_ID + ".state.response", str(response))
          G_LOG.debug(f"Response: {response}")
          WS.disconnect()


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
        


  #  def onError(self, data):
  #      self.error(f'Error in TP Client event handler: {repr(data)}')



if __name__ == "__main__":

    G_LOG = Logger(name = PLUGIN_ID)
    
    WS = SendMessage_Socket()
    plugin = ClientInterface()
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
        plugin.disconnect()
        del plugin
        exit(ret)

