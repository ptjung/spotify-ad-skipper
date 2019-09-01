"""Spotify Ad Skipper

  Author: Patrick Jung
    Date: 2019-08-31
 Version: 1.0

This script runs in the background to automatically skip Spotify ads. Note that
both PowerShell and CMD will be used to manipulate the Spotify app.

There are edge cases for what is considered a Spotify ad. This script watches
the title of the Spotify app for text such as "Spotify Free" or "Spotify"; any
local files without any author that hold these names will reciprocate those 
features and will be considered Spotify ads.

Please ensure that the following dependencies are installed before running:
    - keyboard
        To simulate key-presses for automated song playing
    - pywinauto
        To manipulate the focused window
    - win32gui
        To retrieve the title information of the focused window

Look to README.md for extra information.
"""

import keyboard
import os
import subprocess
import time
import win32gui

from pywinauto.application import Application

def proc_exists(proc_name):
    """Gets the running state of a given process using CMD
    
    Params:
        proc_name : string
            The file name of the process
    
    Returns:
        bool
            A value representing whether the process is currently running or not
    """
    proc_str_call = os.popen('TASKLIST /FI "imagename eq %s"' % (proc_name)).read()
    proc_exist = (proc_str_call.find(proc_name) >= 0)
    
    # Returns the running state
    return proc_exist
        
def proc_get_path(proc_name):
    """Gets the full file path of a given process using CMD
    
    Params:
        proc_name : string
            The file name of the process
    
    Returns:
        string
            A file path to a process, which includes double backslashes to
            represent directories
    """
    proc_str_list = os.popen('wmic process where "name=\'%s\'" get ProcessID, \
    ExecutablePath /FORMAT:LIST' % (proc_name)).read()
    index_i = proc_str_list.find('ExecutablePath=') + len('ExecutablePath=')
    index_f = index_i + proc_str_list[index_i:].find('\n')
    
    # Returns the file path
    return proc_str_list[index_i:index_f]

def proc_reload(proc_name, spotify_is = ('Spotify Free', 'Spotify')):
    """Reloads a given process and records the window open state of Spotify;
    assumes that Spotify can have any of the given titles
    
    Params:
        proc_name : string
            The file name of the process
        spotify_is : tuple, optional
            A tuple of strings that represent aliases of Spotify
            (default includes simple Spotify aliases)
    
    Returns:
        bool
            A value representing if Spotify was open by the time of execution
    """
    spotify_is_open = False
    if proc_exists(proc_name):
        # Records the process file path and window title before being killed
        proc_file_path = proc_get_path(proc_name)
        focus_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())        
        os.system('taskkill /f /im %s > NUL' % (proc_name))
    
        # Runs the process file path, minimzed
        window_info = subprocess.STARTUPINFO()
        window_info.dwFlags = subprocess.STARTF_USESHOWWINDOW
        window_info.wShowWindow = 6
        subprocess.Popen(proc_file_path, startupinfo = window_info)
        
        # Pipe the Spotify open state (before kill) into a variable
        for title_segment in spotify_is:
            print('Log (Notif.): "%s" == "%s": %s' % \
                  (title_segment, focus_title, str(title_segment == focus_title)))
            if (title_segment == focus_title) or (' - ' in focus_title):
                spotify_is_open = True
                break
    
    # Returns the open state of Spotify
    return spotify_is_open
        
def get_curr_song(key_string = ': Spotify\\r'):
    """Gets the name of the current song being played on the user's Spotify app;
    assumes that PowerShell will output processes in a specific list manner
    
    Params:
        key_string : string, optional
            The string to be found in a PowerShell output line, which indicates
            that the next output line includes the current Spotify song
    
    Returns:
        string
            The name of the current song being played on Spotify; this is also
            the title of the Spotify window
    """
    window_list = subprocess.Popen(['powershell.exe', 'Get-Process | where \
    {$_.mainWindowTitle} | format-list name, mainwindowtitle'], stdout = subprocess.PIPE)
    
    current_song = ''
    while (not current_song):
        # Iterates line-by-line throughout PowerShell output
        iter_song_raw = str(window_list.stdout.readline())
        
        if (key_string in iter_song_raw):
            # Extracts raw song string from the output and polishes it
            song_raw = str(window_list.stdout.readline())
            current_song = song_raw[song_raw.find(':') + 2:].replace('\\r\\n\'', '').strip()
            
        elif (len(iter_song_raw) <= 3):
            # Reached the end of PowerShell output, break out of loop
            break
            
    # Returns the current song
    return current_song

def play_next_song(spfy_open, window_names = ('Spotify Free', 'Spotify')):
    """Plays the next song on Spotify in an automated manner; assumes that the
    Spotify window is minimized and has any of the specific window names
    
    Params:
        spfy_open : bool
            The value representing if Spotify should stay open or closed after
            the time of this function's execution
        window_names : tuple, optional
            A tuple of strings that represent possible titles the Spotify app
            window can take
    """
    for potential_title in window_names:
        # Try for any of the given window names
        try:
            # Focus on Spotify app and simulate [SPACE] to resume the song
            curr_focus_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
            spfy_app = Application().connect(title = potential_title)
            spfy_win = spfy_app.window()
            spfy_win.set_focus()
            keyboard.press_and_release('space')
            
            if (spfy_open):
                # For Spotify to stay open, the focus does not change
                print("Log (Notif.): Spotify is open")
            else:
                # For Spotify to stay hidden, the focus must be set elsewhere
                print("Log (Notif.): Spotify is hidden")
                spfy_app = Application().connect(title = curr_focus_title)
                spfy_win = spfy_app.window()
                spfy_win.set_focus()
            
            # Try-clause successful
            return
        
        except Exception as e:
            # Deal with duplicate app connections and inappropriate window titles
            print('Log (Notif.): play_next_song() not okay with "%s": %s' % (potential_title, e))

def main():
    """This is the main-line logic of the program."""
    
    # This list of advertisement titles may change in the future
    ADVERT_TITLES = ['Spotify', 'Advertisement']
    
    # These constants may vary, especially for slower computers (yet to be tested)
    TEST_INTERVAL, SPOTIFY_LOAD_TIME, SONG_SAVE_TIME, REFSH_COOLDOWN = 0.5, 1.25, 2.25, 10.0
    
    while True:
        # Check for Spotify ads on an infinite time loop
        curr_song = get_curr_song()
        print('Log (Notif.): Now playing "%s"' % (curr_song))
        
        if proc_exists('Spotify.exe') and (curr_song in ADVERT_TITLES):
            # Upon ad detection, reload Spotify and play the next song in queue
            time.sleep(SONG_SAVE_TIME)
            spfy_open = proc_reload('Spotify.exe')
            time.sleep(SPOTIFY_LOAD_TIME)
            play_next_song(spfy_open)
            time.sleep(REFSH_COOLDOWN)
        
        time.sleep(TEST_INTERVAL)
    
if __name__ == "__main__":
    main()