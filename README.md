# ytpmvbot
sony vegas killer

## How to use

### Basic usage
ytpmvbot pitch/duration pitch/duration pitch/duration pitch/duration

- ytpmvbot 0/0.5 3/0.5 5/0.5 6/0.5 5/0.5 3/0.5 0/1.5 -2/0.25 2/0.25 0/2

### Pauses
Add pause by leaving pitch field empty

ytpmvbot pitch/duration **/duration** pitch/duration

- ytpmvbot 0/1 **/1** 2/1 4/1

### BPM
Default BPM is 120
To change it simply add -bpm 123 to your command
- ytpmvbot 0/0.5 3/0.5 5/0.5 6/0.5 5/0.5 3/0.5 0/1.5 -2/0.25 2/0.25 0/2 -bpm 100

### Pitch offset
Just add -pitchoffset 12 to pitch whole vid an octave up (or -12 for an octave down)

### Repetition
To add repetition put some notes into square brackets followed by number of repeats
- ytpmvbot [ 0/0.25 3/0.25 7/0.25 12/0.25 ]4

Repetitions are nestable so you can put one inside of another
- ytpmvbot [ [ 0/0.25 3/0.25 7/0.25 12/0.25 ]4 [ -7/0.25 -4/0.25 0/0.25 5/0.25 ]4 ]2

### Merging
Merge up to 4 vids to make amazing multi-track pyp

- reply with **ytpmvbot add** to choose videos
- send **ytpmvbot reset** if you want to start over

Then you have three possibilities:
1) ytpmvbot merge - fit all vids on screen and play them at the same time
2) ypmvbot vmerge - stands for vertical merge and works only for 2 vids
3) ytpmvbot concat - concatenate vids (play them one after another)

If you need more tracks just merge again

### Registering patterns
- ytpmvbot register title, instrument, pattern
- ytpmvbot search title (leave title blank for all)
- ytpmvbot show title
- ytpmvbot delete title, instrument
- ytpmvbot make title, instrument

### Trim
Trim your samples with **ytpmvbot trim start end**

This command will create clip from 00:03 to 00:05
- ytpmvbot trim 3 5

### Volume
Change volume of your samples with **ytpmvbot volume multiplier**
- ytpmvbot volume 0.5
- ytpmvbot volume 2
- ytpmvbot volume 0 (silence)
  
## Setup
### Linux
- clone this repo and cd to it  
- install required python libraries
  - pip install -r requirements.txt
- install ffmpeg with your system's package manager (apt, pacman, yum, dnf, zypper, etc.)
- create file named 'key' and put your bot's token inside
- run ytpmv.py with python
### Windows
- install Windows Subsystem for Linux [How to install WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10)  
- install Docker Desktop  [How to install Docker Desktop](https://docs.docker.com/docker-for-windows/install/)
- follow Docker instructions below
### Docker
This is available on all platforms - Windows, macOS and Linux  
Install Docker and run this on the terminal:
```bash
$ docker run -dit -e TOKEN=<your-bot-token> efpibot/ytpmvbot
```
### Bot permissions
When adding your bot to a server set following permissions:
  - send messages
  - attach files
  - read message history
  - add reactions
## FAQ
### It's not working please help!
- sure, hmu on discord efpee#0659
### Wait so now I can make bad YTPMVs on my phone?
- yes
### Do i need RAM to run this?
- yes, 4 or 8 should be ok
### Wow why is your code shit?
- idk feel free to fork this project or just make your own
- or if you actually want to help hmu on discord efpee#0659
