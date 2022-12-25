# AvPCharacters
## Dependencies
You need python to run this application.

## How to run:
The GUI Way:
Right click on the MergeCharacters.py and click on open with -> python.

The CLI way:
Open  the command prompt or windows powershell. Write the following:
```
python c:/users/username/downloads/AvPCharacters/MergeCharacters.py
```
Where instead of c:/users/username/downloads/AvPCharacters/MergeCharacters.py you write your own path to the MergeCharacters.py

Then when prompted, enter the avp folder, which is usually C:/Program Files(x86)/Steam/steamapps/common/Aliens vs. Predator/

## How to configure
The game can load the textures of at most 3 missions. You can select these by editing Multiplayer.lst to include the respective files in the "mission" folder.
By default A01_Lab and M04_Ruins are included, as they contain the textures for all characters and cause few conflicts.

## How to disable
In Multiplayer.lst remove everything except Characters/Multiplayer.en

