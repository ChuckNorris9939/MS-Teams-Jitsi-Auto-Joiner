- [Prerequisites](#prerequisites)
- [Configuration options](#configuration-options)
- [Run the script](#run-the-script)

Python script to automatically join Microsoft Teams or Jitsi meetings.
Automatically turns off your microphone and camera before joining.



## Prerequisites  
  
 - Python3 ([Download](https://www.python.org/downloads/))  
   
## Configuration options  



  - **type:**  
The type of the Meeting SW
Valid options: `jitsi`, `teams`

  - **link_jitsi:**  
The link to the Meeting SW
Example: https://meet.jit.si/This_is_a_Jitsi_Room

  - **link_teams:**  
The link to the Meeting SW
Example: https://teams.microsoft.com/_#/pre-join-calling/19:meeting_NzdiYmNzdNzNzNzdiYmdiYmdiYmiYm5@thread.v2

- **username:**  
The username of your Guest Account.

- **run_at_time:**  
Time to start the script at. Input is a string of the hour and minute in 24h format, if you want it to start immediately leave this empty. 
If a time before the current time is given, the next day is used. Also make sure that you entered your email and password.
For example, if you want the script to start searching meetings at 6 in the morning on the next day, you would input `06:00` in the config.

- **auto_leave_after_min:**
If set to a value greater than zero, the bot leaves every meeting after the specified time (in minutes). Useful if you know the length of your meeting, if this is left a the default the bot will stay in the meeting until a new one is available.

- **headless:**
If true, runs Chrome in headless mode (does not open GUI window and runs in background).

- **mute_audio:**
If true, mutes all the sounds.

- **chrome_type:**
Valid options: `google-chrome`, `chromium`, `msedge`. By default, google chrome is used, but the script can also be used with Chromium or Microsoft Edge.


## Run the script

 1. Install dependencies:   ```pip install -r requirements.txt```
 2. Edit the "config.json" file to fit your preferences
 3. Run [auto_joiner.py](auto_joiner.py): `python auto_joiner.py`
