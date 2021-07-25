import ffmpeg
import os
import shutil


if os.path.exists('assets'):
	shutil.rmtree('assets')
	os.mkdir('assets')
	shutil.copy('samp1.mp4', 'assets')

inFlip = ffmpeg.input('samp1.mp4')
inFlipVid = inFlip.video.hflip()
inFlipAudio = inFlip.audio
outFlip = ffmpeg.output(inFlipVid, inFlipAudio, 'assets/samp-1.mp4')
outFlip.run()


bpm = 120

notes = ['0/1', '0/1', '0/1', '0/1', '0/0.5', '0/0.5', '0/1', '0/1', '0/1', '0/1', '0/0.5', '0/0.5', '2/0.25', '/0.25', '4/0.25', '6/0.25', '8/0.25', '10/0.25']

uniqueNotes = []
for i in notes:
	notePitch = i.split('/')[0]
	if notePitch != '' and int(notePitch) not in uniqueNotes:
		uniqueNotes.append(int(notePitch))
print(uniqueNotes)

for i in uniqueNotes:
	pitchedSample = ffmpeg.input('samp1.mp4').audio.filter('rubberband', pitch=1*2**(i/12))
	out = ffmpeg.output(pitchedSample, f'assets/samp{i}.mp3')
	out.run()


timeline = []
flipSwitch = 1

for i in range(len(notes)):

	length = float(notes[i].split('/')[1])
	pitch = notes[i].split('/')[0]

	if pitch == '':
		inAudio = ffmpeg.input('samp1.mp4', t=length*60/bpm).audio.filter('volume', 0)

	else:
		inVid = ffmpeg.input(f'assets/samp{flipSwitch}.mp4', t=length*60/bpm).video
		flipSwitch *= -1
		inAudio = ffmpeg.input(f'assets/samp{pitch}.mp3', t=length*60/bpm).audio

	timeline.append(inVid)
	timeline.append(inAudio)

joined = ffmpeg.concat(*timeline, v=1, a=1).node
video = joined[0]
audio = joined[1]

out = ffmpeg.output(video, audio, 'assets/out.mp4')
out.run()

