# ytpmvbot
sony vegas killer

## Available commands:
- ytpmvbot help - send help message

- ytpmvbot pitch/duration pitch/duration pitch/duration [...] -bpm 160
  - optionally set bpm: -bpm 123
  - add pause by leaving pitch field empty, example: /1
  - example: ytpmvbot 0/0.5 2/0.5 4/0.5 5/0.5 7/0.5 9/0.5 11/0.5 12/0.5 0/0.33 4/0.33 7/0.34 12/0.33 7/0.33 4/0.34 0/1
  - reply to the message that has video attached to it or attach it directly to your 'command' message
  
- ytpmvbot trim start end
  - example: ytpmvbot trim 2 3
  
- ytpmvbot volume multiplier
  - example: ytpmvbot volume 0.5
  
- ytpmvbot add - add this video to be merged
  - to use, reply to the message with attached video
  - currently you can only merge 2 or 4 videos
  
- ytpmvbot merge - merge chosen videos into amazing multi track pyp

- ytpmvbot reset - clear 'videos to be merged' list
  
## Setup:
Not tested on Windows, probably won't work (todo docker)
- clone this repo
- go into its directory
- install required python libraries
  - pip install -r requirements.txt
- install ffmpeg
  - sudo apt update
  - sudo apt install ffmpeg
- create file named 'key' and put your bot's token inside
- run ytpmv.py with python
### Bot permissions:
When adding your bot to a server set following permissions:
  - send messages
  - attach files
  - read message history
  - add reactions

## FAQ:
### Wait so now I can make bad YTPMVs on my phone?
- yes
### Do i need RAM to run this?
- yes, 4 or 8 should be ok
### Wow why is your code shit?
- idk feel free to fork this project or just make your own
- or if you actually want to help hmu on discord efpacito#0659
