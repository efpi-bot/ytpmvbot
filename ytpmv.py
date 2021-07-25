import ffmpeg
import os
import shutil


if os.path.exists('assets'):
	shutil.rmtree('assets')
	os.mkdir('assets')

inFlip = ffmpeg.input('samp.mp4')
inFlipVid = inFlip.video.hflip()
inFlipAudio = inFlip.audio
outFlip = ffmpeg.output(inFlipVid, inFlipAudio, 'assets/sampflip.mp4')
outFlip.run()


bpm = 120

notes = ['0-1', '0-1', '8-0.5', '8-0.5', '8-0.1', '2-0.2', '-15', '0-2', '0-2']


uniqueNotes = []
for i in notes:
	notePitch = i.split('-')[0]
	if notePitch != '' and int(notePitch) not in uniqueNotes:
		uniqueNotes.append(int(notePitch))
print(uniqueNotes)

for i in uniqueNotes:
	pitchedSample = ffmpeg.input('samp.mp4').audio.filter('rubberband', pitch=1*2**(i/12))
	out = ffmpeg.output(pitchedSample, f'assets/samp{i}.mp3')
	out.run()


clipList = []
for i in range(len(notes)):

	length = float(notes[i].split('-')[1])

	pitch = notes[i].split('-')[0]
	if pitch == '':
		inAudio = ffmpeg.input('samp.mp4', t=length*60/bpm).audio.filter('volume', 0)
	else:
		if i % 2 == 0:
			inVid = ffmpeg.input('samp.mp4', t=length*60/bpm).video
		else:
			inVid = ffmpeg.input('assets/sampflip.mp4', t=length*60/bpm).video

		inAudio = ffmpeg.input(f'assets/samp{pitch}.mp3', t=length*60/bpm).audio

	clipList.append(inVid)
	clipList.append(inAudio)

joined = ffmpeg.concat(*clipList, v=1, a=1).node
video = joined[0]
audio = joined[1]

out = ffmpeg.output(video, audio, 'assets/out.mp4')
out.run()

