import os
import base64
import requests
from tempfile import gettempdir
from tkinter import Tk, Label, Button, ttk, PhotoImage, Frame, BOTH
from threading import Thread
import TouchPortalAPI as TP
import time
from typing import Union, Dict, Tuple, Callable
import subprocess
import platform

USER_SYSTEM = platform.system()

if USER_SYSTEM == "Linux":
    from Xlib import X, display
elif USER_SYSTEM == "Windows":
    # import win32gui
    import ctypes
    from ctypes import wintypes

elif USER_SYSTEM == "Darwin":
    pass


class GitHubUpdater:
    def __init__(self, owner: str, repo: str, icon_path: str, TPClient:TP.Client, pre_releases:bool = False):
        self.owner = owner
        self.repo = repo
        self.icon_name = icon_path
        self.update_info = None
        self.TPClient = TPClient
        self.pre_releases = pre_releases
        self.file_name = ""
        self.locater = WindowLocater()


    def _fetch_patch_notes(self) -> str:
        """Fetches and decodes patch notes from GitHub."""
        patch_notes_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/recent_patchnotes.txt"
        response = requests.get(patch_notes_url)
        if response.status_code == 404:
            print("No Patch Notes Found")
            return ""
        try:
            content = response.json()['content']
            decoded_bytes = base64.b64decode(content)
            return decoded_bytes.decode('ascii')
        except Exception as e:
            print(f"Error fetching patch notes: {e}")
            return None

    def _get_release_info(self) -> Tuple[str, str, str]:
        """Fetches release information from GitHub based on the pre_releases flag."""
        
        system_suffixes = {
            'Windows': 'Windows',
            'Linux': 'Linux',
            'Darwin': 'MacOS'
            }
        
        # Get the suffix for the current system
        system_suffix = system_suffixes.get(USER_SYSTEM, "")
        
        if not system_suffix:
            raise ValueError(f'Unsupported system: {USER_SYSTEM}')
        url = f'https://api.github.com/repos/{self.owner}/{self.repo}/releases'
        response = requests.get(url)
        
        if response.ok:
            releases = response.json()
            for release in releases:
                # Check for pre-release status based on pre_releases flag
                if not self.pre_releases and release.get('prerelease'):
                    continue
                if self.pre_releases or not release.get('prerelease'):
                    assets = release.get('assets', [])
                    if assets:
                        ## Matching the correct system and download based on end prefix of file.
                        for asset in assets:
                            download_url = asset.get('browser_download_url', "")
                            if system_suffix.lower() in download_url.lower():
                                release_version = release.get('tag_name', "")
                                html_url = release.get('html_url', "")
                                return release_version, download_url, html_url

                        # Fallback if no matching asset is found
                        download_url = assets[0].get('browser_download_url', "")
                        release_version = release.get('tag_name', "")
                        html_url = release.get('html_url', "")
                        return release_version, download_url, html_url
                                
            # Raise error if no suitable release found
            raise ValueError(f'No suitable release found in repository: {url}')
        else:
            raise ValueError(f'Invalid repository URL or response: {url}')

    def check_for_updates(self, current_version: str) -> Union[Dict[str, str], bool, None]:
        """Checks GitHub for the latest version of the plugin."""
        try:
            github_version, download_url, html_url = self._get_release_info()
            github_version = github_version.replace('v', '').replace(".", "")
            if github_version > current_version:
                patch_notes = self._fetch_patch_notes()
                self.update_info = {"version": github_version, "patchnotes": patch_notes, "downloadURL": download_url, "htmlURL": html_url}
                return self.update_info
            else:
                return False
        except Exception as e:
            print(f"Error checking for updates: {e}")
            return None

    def show_update_notification(self, notification_id, title: str, msg: str = None):
        """Display a custom notification with title and message.

        Args:
            title (str): The title of the notification.
            msg (str): The message of the notification.
            notification_id (str, optional): A unique ID for the notification.
        """

        # Defining our options for the notification, perhaps give more control over title etc if we build this out  more
        self.options = [
            {
                "id": f"{notification_id}.update.download",
                "title": "(Automatic Install)"
            },
            {
                "id": f"{notification_id}.update.manual",
                "title": "(Manual Install)"
            }
        ]
        
        # Show the notification
        self.TPClient.showNotification(
            notificationId=notification_id,
            title=title,
            msg=msg,
            options=self.options
        )


    def download_update(self, download_url: str, progress_callback: Callable[[int, int], None] = None) -> Union[str, None]:
        """Downloads the update and returns the path to the downloaded file."""
        temp_file_path = os.path.join(gettempdir(), self.file_name)
        
        response = requests.get(download_url, stream=True)
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            with open(temp_file_path, 'wb') as file:
                downloaded_size = 0
                for data in response.iter_content(chunk_size=1024):
                    file.write(data)
                    downloaded_size += len(data)
                    if progress_callback:
                        progress_callback(downloaded_size, total_size)
            return temp_file_path
        return None

    def _update_gui(self, root, progress_bar, progress_label, file_name, download_url):
        """Updates the GUI with the progress of the download."""
        def progress_callback(downloaded_size, total_size):
            # Convert bytes to megabytes
            downloaded_mb = downloaded_size / (1024 * 1024)
            total_mb = total_size / (1024 * 1024)
            progress_percentage = (downloaded_size / total_size) * 100
            
            # Update progress bar and label
            progress_bar['value'] = progress_percentage
            progress_label.config(text=f"{downloaded_mb:.2f} MB / {total_mb:.2f} MB")

        def download_thread():
            temp_file_path = self.download_update(download_url, progress_callback)
            if temp_file_path:
                progress_label.config(text=f"Downloaded Complete!")
                time.sleep(0.5)
                progress_label.config(text=f"Installing Plugin....")
                time.sleep(0.7)
                os.startfile(temp_file_path)
            root.after(0, root.destroy)
            
        Thread(target=download_thread).start()
        
    def resize_image(self, image, size):
        # Resize the image to the desired size
        width, height = image.width(), image.height()
        new_width, new_height = size

        # Create a new image with the desired size
        resized_image = PhotoImage(width=new_width, height=new_height)
        for x in range(new_width):
            for y in range(new_height):
                # Calculate corresponding position in the original image
                orig_x = int(x * width / new_width)
                orig_y = int(y * height / new_height)
                color = image.get(orig_x, orig_y)
                resized_image.put(color, (x, y))
        
        return resized_image
    
    def run_gui(self, download_url):
        """Runs a Tkinter GUI to show the download progress."""
        
        script_dir = os.path.dirname(os.path.abspath(self.icon_name))
        # icon_path = os.path.join(script_dir, "src", self.icon_name)

        # Finding the TouchPortal Window to appear on top where user would expect...
        touchportal_window = self.locater.get_window_info("Touch Portal")
        if touchportal_window:
            touchportal_left = touchportal_window['left']
            touchportal_top = touchportal_window['top']
            touchportal_width = touchportal_window['width']
            touchportal_height = touchportal_window['height']
        else:
            # Default to center of the screen if TouchPortal is not found, which shouldnt be a thing but who knows...
            touchportal_left = 0
            touchportal_top = 0
            touchportal_width = Tk().winfo_screenwidth()
            touchportal_height = Tk().winfo_screenheight()

        root = Tk()
        root.attributes('-topmost', True)
        root.overrideredirect(True)  # Remove title bar
        root.geometry("400x150")
        root.resizable(False, False)

        # Styling
        bg_color = "#1E1E1E"  # Dark gray
        fg_color = "white"
        border_color = "#727272"  # Light gray for border
        border_width = 2

        # Create a frame with a border
        border_frame = Frame(root, bg=border_color)
        border_frame.pack(fill=BOTH, expand=True)

        # Create an inner frame for content
        content_frame = Frame(border_frame, bg=bg_color)
        content_frame.pack(fill=BOTH, expand=True, padx=border_width, pady=border_width)

        # Position window based on TouchPortal location
        window_width = 400
        window_height = 150
        x = touchportal_left + (touchportal_width // 2) - (window_width // 2)
        y = touchportal_top + (touchportal_height // 2) - (window_height // 2)
        root.geometry(f'{window_width}x{window_height}+{x}+{y}')
        root.tk.call('font', 'create', 'RobotoNormal', '-family', 'Roboto', '-size', 12)
        root.tk.call('font', 'create', 'RobotoBold', '-family', 'Roboto', '-size', 16, '-weight', 'bold')
            
        self.file_name = download_url.split('/')[-1]
        file_label = Label(content_frame, text=f"DOWNLOADING: {self.file_name}", font=("RobotoNormal", 10), bg=bg_color, fg=fg_color, justify="left", anchor='w')
        file_label.pack(pady=10, padx=10, fill='x')

        style = ttk.Style()
        style.theme_use('default')
        style.configure("TProgressbar", thickness=20, troughcolor=bg_color, background="#4CAF50")

        progress_bar = ttk.Progressbar(content_frame, orient='horizontal', mode='determinate', length=300, style="TProgressbar")
        progress_bar.pack(pady=20, padx=20, fill='x')
        progress_bar['maximum'] = 100
        

        progress_label = Label(content_frame, text="Starting download...", bg=bg_color, fg=fg_color)
        progress_label.pack(pady=0)

        # Close button
        close_button = Button(content_frame, text="×", command=root.destroy, font=("RobotoBold", 16, "bold"),
                            bg=bg_color, fg=fg_color, activebackground="#3E3E3E", activeforeground=fg_color,
                            bd=0, width=2, height=1)
        close_button.place(x=window_width-border_width-40, y=5)

        self._update_gui(root, progress_bar, progress_label, self.file_name, download_url)
        root.mainloop()



class WindowLocater:
    def __init__(self):
        self.USER_SYSTEM = platform.system()

    def get_window_info(self, title):
        if self.USER_SYSTEM == "Windows":
            return self.get_window_info_windows(title)
        elif self.USER_SYSTEM == "Linux":
            return self.get_window_info_linux(title)
        elif self.USER_SYSTEM == "Darwin":
            return self.get_window_info_mac(title)
        else:
            return None

    def get_window_info_linux(self, title):
        """ Retrieves window information on Linux using xwininfo """
        try:
            # Run xwininfo to get window details
            result = subprocess.run(['xwininfo', '-name', title], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = result.stdout

            if result.returncode != 0:
                raise ValueError("Failed to get window info")

            # Extract window details
            left = int(next(line.split(':')[1].strip()) for line in output.splitlines() if "Absolute upper-left X:" in line)
            top = int(next(line.split(':')[1].strip()) for line in output.splitlines() if "Absolute upper-left Y:" in line)
            width = int(next(line.split(':')[1].strip()) for line in output.splitlines() if "Width:" in line)
            height = int(next(line.split(':')[1].strip()) for line in output.splitlines() if "Height:" in line)

            return {"left": left, "top": top, "width": width, "height": height}
        
        except Exception as e:
            print(f"Error: {e}")
            return None

    # def get_window_info_windows(self, title):
    #     """ Retrieves window information on Windows using win32gui """
    #     hwnd = win32gui.FindWindow(None, title)
    #     if hwnd:
    #         rect = win32gui.GetWindowRect(hwnd)
    #         if rect:
    #             left = rect[0]
    #             top = rect[1]
    #             width = rect[2] - rect[0]
    #             height = rect[3] - rect[1]
    #             return {"left": left, "top": top, "width": width, "height": height}
    #         else:
    #             return None
    #     else:
    #         return None
    def get_window_info_windows(self, title: str):
        """ Retrieves window information on Windows using ctypes """
        
        # Define necessary ctypes structures and functions
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        
        # Define the RECT structure
        class RECT(ctypes.Structure):
            _fields_ = [
                ('left', wintypes.LONG),
                ('top', wintypes.LONG),
                ('right', wintypes.LONG),
                ('bottom', wintypes.LONG)
            ]
        
        # Define FindWindow and GetWindowRect functions
        FindWindow = user32.FindWindowW
        FindWindow.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
        FindWindow.restype = wintypes.HWND
        
        GetWindowRect = user32.GetWindowRect
        GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
        GetWindowRect.restype = wintypes.BOOL
        
        # Find the window handle
        hwnd = FindWindow(None, title)
        if hwnd:
            rect = RECT()
            if GetWindowRect(hwnd, ctypes.byref(rect)):
                left = rect.left
                top = rect.top
                width = rect.right - rect.left
                height = rect.bottom - rect.top
                return {"left": left, "top": top, "width": width, "height": height}
            else:
                return None
        else:
            return None
            

    def get_window_info_mac(self, title):
        """ Retrieves window information on macOS using AppleScript """
        script = f'''
        tell application "System Events"
            set windowInfo to ""
            set theWindows to windows of (first process whose name is "{title}")
            repeat with win in theWindows
                set windowInfo to windowInfo & "left:" & (position of win's window 1)'s item 1 & ", top:" & (position of win's window 1)'s item 2 & ", width:" & (size of win's window 1)'s item 1 & ", height:" & (size of win's window 1)'s item 2
            end repeat
            return windowInfo
        end tell
        '''
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            output = result.stdout.strip()
            
            if result.returncode != 0:
                raise ValueError("Failed to retrieve window info")

            # Parse output
            info = {}
            for line in output.split(", "):
                key, value = line.split(":")
                info[key.strip()] = int(value.strip())

            return info
        except Exception as e:
            return None




if __name__ == "__main__":
    locater = WindowLocater()
    updater = GitHubUpdater(owner='gitagogaming', repo='Websockets---TouchPortal', icon_path="websockets_logo.png", TPClient=None, pre_releases=False)

    update_info = updater.check_for_updates('1.0')
    if update_info:
        updater.run_gui(update_info['downloadURL'])