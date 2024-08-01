## Websockets 
import os
import webbrowser
import toml
from sys import exit

import TouchPortalAPI
from TouchPortalAPI import TYPES
from TouchPortalAPI.logger import Logger
from TPPEntry import PLUGIN_ID
from update_check import plugin_update_check, GITHUB_PLUGIN_NAME, GITHUB_USER_NAME, PLUGIN_NAME
from websocketManager import WebSocketClient, IOSocketWrapper


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

        self.setLogFile(PLUGIN_ID + "_LOG.log")
    
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
    def settingsToDict(self, settings:dict):
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

            return config
        except FileNotFoundError:
            plugin.log.debug(f"Error: Configuration file '{config_file}' not found.")


    """
    Events
    """
    def onConnect(self, data:dict):
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



    def onSettings(self, data:dict):
        self.plugin_settings = self.settingsToDict(data['values'])
        self.log.debug(f"Connection: {data}")


    def onAction(self, data:dict):
        self.log.debug(f"Connection: {data}")
        plugin.log.debug(f"Action: {data}")

        if not (action_data := data.get('data')) or not (aid := data.get('actionId')):
            return
        
        if aid == PLUGIN_ID + ".act.send_message":
            WS.send_command(socket_name = data['data'][2]['value'], socket_url = data['data'][0]['value'], command = data['data'][1]['value'])
            
        elif aid == PLUGIN_ID + ".act.disconnect":
            WS.disconnect(data['data'][0]['value'])

        elif aid == PLUGIN_ID + ".act.connect":
            if data['data'][0]['value'].startswith("http"):
                socketIO.connect(websocket_url=data['data'][0]['value'])
            elif data['data'][0]['value'].startswith("ws"):
                WS.connect(socket_name=data['data'][1]['value'], websocket_url=data['data'][0]['value'])

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
    plugin = ClientInterface()
    WS = WebSocketClient(plugin)
    socketIO = IOSocketWrapper(plugin)

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


