# NotASnake                                    
## Yes, this is just Snake. The good, niche type.
To do so, write to [this email](silverballermicro47@hotmail.com) with your ideas!  
[Official Website](https://notasnake.tilda.ws) (recently updated) or [this one](notasnake.tb.ru)   
[Closed Beta Test Registration](https://notasnake.tilda.ws/closedbeta)  
Now also available at [Itch.io](skulldozeeer.itch.io/notasnake)

Game by Danil Panchuk, Russia

How to NotASnake - Source code thing
This is a quickie on how to compile the game in any versions having a source file.

Basic requirements:
 - A Windows 11/10 PC. Linux works fine if you `venv` your way on it.
 - Have Python 3.12 or 3.11 installed. With it, install pygame-ce and cx_Freeze (optional for compiling.)
(P.S. - this way you can play PhysicalV1, the broken one, by launching the sources inside. you're very welcome)

All of that alone should allow you to play the video game only using source code, which you can download above. If you want to compile it though...
1. Make a setup.py for the source file. self-explanatory. I use cx_Freeze, but anything works, really. don't trust the setup.py in Code, I'm not sure how up-to-date it is.
2. `python setup.py build`. Yup. have a /build folder with the game!
fin.
# Privacy & No-Tracking


**NotASnake does not use telemetry, analytics, advertising, or remote tracking.**

The game does **not** send gameplay data, statistics, achievements, crash reports, or system information to the developer or to any third-party service.

NotASnake does not collect or transmit:

- IP addresses
- Windows versions or build numbers
- CPU, GPU, RAM, or other hardware information
- device or machine identifiers
- usernames or account identifiers
- gameplay telemetry
- achievement telemetry
- usage statistics
- advertising identifiers
- crash reports

### What NotASnake stores locally

NotASnake does keep some information **on your own computer** so that its features work. This includes gameplay statistics, high scores, achievements, selected settings, tutorial status, and other game progress.

These files are stored locally in the game's `nasassets` directory. They are never automatically uploaded anywhere by NotASnake.

NotASnake also creates local debug logs for troubleshooting. These can contain timestamps, game/debug events, crash information, file paths - which may include your Windows username - again, only to be found if debug log itself is shared, and Python tracebacks. These logs remain on your computer and are not automatically sent to anyone.

### No "phone home"

There is no hidden telemetry endpoint, analytics service, or background reporting system in NotASnake.

There is no equivalent of secretly sending the developer your OS build number, hardware configuration, or gameplay statistics.

If NotASnake ever gains an online feature that requires collecting data, that feature will be explicitly documented rather than silently added.

**Your save file is yours. Your statistics are yours. NotASnake does not phone home.**

Oh, and very important note! With Physical Edition v1 out... most of the game versions are broken! That is because I had no choice but to use my old laptop, having to re-import all python pips. And the setup.py I used for 90% of the versions i forgot to include 'import pygame'. oops! V2 will be out soon.

### Credits
PIXXEL - https://github.com/P1XXX4L , Game Icon Art, Music maker, and a Beta tester
##  PSA on Versions:
Order of updates:
v1.0 - v1.1 - v1.2 - v1.2.1 - v1.3 (TheBigOne) - v2.0 - v2.1/2.2 - v2.3 - v2.4 - v2.5 - v2.6 - v3.0 - v3.1 - 3.2 - 3.3 - 3.3.1 - 3.4 - 3.5 - 3.5.1 - PhysicalV1 - 3.5.2-pr1 - 3.5.2

Versions 1.2.1 and under were only py files, loaded by having to launch them directly with lots of struggles. if somebody wants to compile them into .exe for availability, go for it, but dont expect me to do it (MAKE A PULL)    

Important note: you should not unpack the .rar of the game in Program Files/Windows circa v3.0, due to NotASnake's .exe file trying to write debug logs to Windows-important directories, where it cannot write due to not having the right permissions. So the game shits itself and crashes. Desktop and any other directories should work absolutely ok.

IF you compile an old version and make a pull request, please write me or something...

## Screenshots - version 3.1
### Overview of files
<img width="676" height="282" alt="image" src="https://github.com/user-attachments/assets/2dc89ffa-4654-4826-82b5-c9303e5b7549" />


### Main menu
<img width="1364" height="796" alt="image" src="https://github.com/user-attachments/assets/21b189d3-d312-4779-b5cd-d13aa08a7d8a" />


### Main menu - Light mode
<img width="1363" height="796" alt="image" src="https://github.com/user-attachments/assets/44d0bbf7-9958-4cd2-92ce-7a66ea70e900" />


### Main menu with settings open
<img width="1363" height="793" alt="image" src="https://github.com/user-attachments/assets/7a881840-bbe7-4565-94eb-6f1b671d64d4" />


### Gameplay - Hardcore mode, 50% Grid opacity
<img width="1363" height="796" alt="image" src="https://github.com/user-attachments/assets/65ee5e5b-28d6-4a9d-9560-c5f539b8fcfc" />


### Gameplay - Light mode
<img width="1363" height="796" alt="image" src="https://github.com/user-attachments/assets/dc52b094-3d8d-41c4-87f9-861b7a98ab72" />



## License
This project is licensed under the **GNU General Public License v3.0**.
See the [LICENSE](LICENSE) file for the full text.  
The music created for the game is made independently and is not allowed for distribution/selling under any circumstances and is affected by the GNU General Public License v3.0
