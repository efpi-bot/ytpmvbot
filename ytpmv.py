import ffmpeg
import os
import shutil
from moviepy.editor import *


if os.path.exists('assets'):
	shutil.rmtree('assets')
os.mkdir('assets')
shutil.copy('samp1.mp4', 'assets')

inFlip = ffmpeg.input('samp1.mp4')
inFlipVid = inFlip.video.hflip()
outFlip = ffmpeg.output(inFlipVid, 'assets/samp-1.mp4')
outFlip.run()

bpm = 120

notes = ['0/0.5', '0/0.5', '0/0.5', '2/0.5', '5/0.5', '7/10', '4/1', '4/0.5', '4/0.5', '9/0.5']

uniqueNotes = []
for i in notes:
	notePitch = i.split('/')[0]
	if notePitch != '' and int(notePitch) not in uniqueNotes:
		uniqueNotes.append(int(notePitch))

for i in uniqueNotes:
	pitchedSample = ffmpeg.input('samp1.mp4').audio.filter('rubberband', pitch=2**(i/12))
	out = ffmpeg.output(pitchedSample, f'assets/samp{i}.mp3')
	out.run()


timelineV = []
timelineA = []
flipSwitch = 1
timer = 0.0
for i in range(len(notes)):

	length = float(notes[i].split('/')[1])*60/bpm
	pitch = notes[i].split('/')[0]


	audio = AudioFileClip(f'assets/samp{pitch}.mp3')
	clip = VideoFileClip(f"assets/samp{flipSwitch}.mp4")

	clip.start = timer
	audio.start = timer
	if length < clip.duration:
		clip.end = timer+length
		audio.end = timer+length
	else:
		clip.end = timer+clip.duration
		audio.end = timer+clip.duration

	timer += length
	flipSwitch *= -1

	timelineV.append(clip)
	timelineA.append(audio)

final_Vclip = CompositeVideoClip(timelineV)
final_Aclip = CompositeAudioClip(timelineA)
final_Vclip.audio = final_Aclip
final_Vclip.resize(width=320).write_videofile("mudzinmv.mp4")

