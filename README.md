# Spotify Ad Skipper

## Program Description

This script runs in the background to automatically skip Spotify ads.

## Features

- Spotify is checked in frequent time intervals.
- Uses a natural exploitation (of rebooting Spotify) to skip ads.
- Both PowerShell and CMD will be used to manipulate the Spotify app.
- For debugging purposes, the ad skipper regularly outputs to the screen.
- The Spotify window being minimized and the song playing after reboot are automated.

## Known Bugs

- The mouse cursor is usually displaced after rebooting Spotify.
- Greatly tampers with user work done in the moment of rebooting.
- The rebooted Spotify window uncommonly opens up a drop-down window instead of automatically playing the next song.
- Songs without an author _(usually local files)_ that are named "Spotify" or "Advertisement" are deemed ads.

## Changelog

(August 31, 2019)
- Released Spotify-Ad-Skipper version 1.0.
