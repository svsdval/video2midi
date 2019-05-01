#!/usr/bin/python

import math;
import cv2
from PIL import Image
from midiutil.MidiFile import MIDIFile
import os
import sys
import ntpath

if ( len(sys.argv) < 2 ):
  print "halt, no args";
  sys.exit( 0 ) 

filepath = sys.argv[1];
if os.path.exists( filepath ):
  print "open file " + filepath;
  vidcap = cv2.VideoCapture( filepath )
else:
  print "file not exists " + filepath;
  sys.exit( 0 ) 

outputmid= ntpath.basename( filepath ) + "_output.mid";

success,image = vidcap.read()
frame = 0

debug = 0;
debug_keys = 0;

length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
width  = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps    = float(vidcap.get(cv2.CAP_PROP_FPS))

# set start frame
vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame)

success,image = vidcap.read()
#
print "video fps: %d" % fps;

xoffset_whitekeys = 5 # 40 for avengers, else 5

yoffset_whitekeys = 673

yoffset_blackkeys = 637
xoffset_blackkeys = xoffset_whitekeys + 10

# create  MIDI object
mf = MIDIFile(1) # only 1 track
track = 0 # the only track

time = 0 # start at the beginning

mf.addTrackName(track, time, "Sample Track")
mf.addTempo(track, time, 60 )

# add some notes
channel = 0
volume = 100
basenote=35;

notes=[];
notes_db=[];
notes_de=[];

keyp_colors = [ [241,173,64], [216,57,77], [218,52,64] ];
keyp1d = 90;
#
minimal_duration = 0.1;

for i in range(88):
  notes.append(0)
  notes_db.append(0);
  notes_de.append(0);

#
while success:
  if (frame % 100 == 0):
    print "processing frame: " + str(frame) + " / " + str(length);

  # processing white keys
  for i in range(48):
	# generate key position:
    pixx=xoffset_whitekeys + i * 28 -i;
    pixy=yoffset_whitekeys

    if ( pixx > width ) or ( pixy > height ): break;
    if ( pixx < 0 ) or ( pixy < 0 ): continue;

    keybgr=image[pixy,pixx]
    key= [ keybgr[2], keybgr[1],keybgr[0] ];

    # generate note ID
    nk = (i+1)  % 7;
    nko= math.trunc( (i+1) / 7 );
    if ( nk == 0 ): addk =+ addk + 5;
    note = nko;

    addk = 0;
    if nk == 2 : addk=1;
    if (nk == 3) or (nk == 4) : addk=2;
    if nk >= 5 : addk=nk-2;

    note = nko * 12 + nk+addk;

    if ( debug == 1 ):
      cv2.rectangle(image, (pixx-5,pixy-5), (pixx+5,pixy+5), (255,0,255));
      cv2.rectangle(image, (pixx-1,pixy-1), (pixx+1,pixy+1), (255,0,255));
      cv2.putText(image, str(note), (pixx-5,pixy+20), 0, 0.5, (255,0,255));
 
    keypressed=0;
    for keyc in keyp_colors:
      if ( abs( int(key[0]) - keyc[0] ) < keyp1d ) and ( abs( int(key[1]) - keyc[1] ) < keyp1d ) and ( abs( int(key[2]) - keyc[2] ) < keyp1d ):
       keypressed=1;

    # reg pressed key
    if keypressed==1:
      # if key is not pressed
      if ( notes[note] == 0 ):
        if ( debug_keys == 1 ):
          print "white keys, note pressed on :" + str( note );
        notes[ note ] = 1;
        notes_db[ note ] = frame;

    else:
      # if key been presed and released:
      if ( notes[note] == 1 ):
        notes[ note ] = 0;
        notes_de[ note ] = frame;
        time = notes_db[note] / fps;
        duration = ( notes_de[note] - notes_db[note] ) / fps ;
        if ( duration < minimal_duration ): duration = minimal_duration;

        if ( debug_keys == 1 ):
          print "white keys, note released :" + str( note ) + " de = " + str(notes_de[note]) + "- db =" + str(notes_db[note]);
          print "midi add white keys, note : " +str(note) + " time:" +str(time) + " duration:" + str(duration);
        mf.addNote(track, channel, basenote+ note, time , duration , volume )

  xapp=0;

  # processing black keys
  for i in range(34):
    if (i % 5 == 2) or ((i % 5 == 0) and (i != 0)):
      xapp=xapp + 15;
	# generate key position:
    pixx=xoffset_blackkeys + i * 32 + xapp;
    pixy=yoffset_blackkeys;

    if ( pixx > width ) or ( pixy > height ): break;
    if ( pixx < 0 ) or ( pixy < 0 ): continue;

    keybgr=image[pixy,pixx] 
    key= [ keybgr[2], keybgr[1],keybgr[0] ];
    image[pixy:pixy+10,pixx:pixx] = (255,0,255)

    nk= (i+1) % 5;
    note = i + (i / 5) * 7 + (i % 5)+3;

    if ( nk == 1 ) or ( nk == 2 ): note += -1

    if ( debug == 1 ):
      cv2.rectangle(image, (pixx-5,pixy-5), (pixx+5,pixy+5), (255,0,255));
      cv2.rectangle(image, (pixx-1,pixy-1), (pixx+1,pixy+1), (255,0,255));
      cv2.putText(image, str(note), (pixx-5,pixy-10), 0, 0.5, (255,0,255));

    keypressed=0;
    for keyc in keyp_colors:
      if ( abs( key[0] - keyc[0] ) < keyp1d ) and ( abs( key[1] - keyc[1] ) < keyp1d ) and ( abs( key[2] - keyc[2] ) < keyp1d ):
       keypressed=1;

    if keypressed==1:
      if ( notes[note] == 0 ):
        if ( debug_keys == 1 ):
          print "black keys, note pressed on [" +str(i) + "] =" + str( note );
        notes[ note ] = 1;
        notes_db[ note ] = frame;
    else:
      if ( notes[note] == 1 ):
        notes[ note ] = 0;
        notes_de[ note ] = frame;
        if ( debug_keys == 1 ):
          print "black keys, note released :" + str( note ) + " de = " + str(notes_de[note]) + "- db =" + str(notes_db[note]);
        duration = ( notes_de[note] - notes_db[note] ) / fps;
        time = notes_db[note] / fps;
        if ( duration < minimal_duration ): duration = minimal_duration;

        if ( debug_keys == 1 ):
          print "midi add black keys, note: " +str(note) + " time:" +str(time) + " duration:" + str(duration);
        mf.addNote(track, channel, basenote+note, time , duration , volume )

#  os.remove("/tmp/frame%d.jpg" % frame)

#  if frame > 60: 
#    break;

  if ( debug == 1 ):
    cv2.imwrite("/tmp/frame%d.jpg" % frame, image)  # save frame as JPEG file
  success,image = vidcap.read()
  frame += 1

# write midi to disk
with open(outputmid, 'wb') as outf:
    mf.writeFile(outf)
