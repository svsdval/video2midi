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
frame = 308

debug = 0;
resize= 1;
debug_keys = 1;

length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
width  = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps    = float(vidcap.get(cv2.CAP_PROP_FPS))

# set start frame
vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame)

success,image = vidcap.read()
#
print "video fps: %d" % fps;


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
keys_pos=[];

keyp_colors = [ [241,173,64], [216,57,77], [218,52,64], [105,150,192], [39,87,149], [166,250,103], [102,185,43] ];
keyp1d = 90;
#
minimal_duration = 0.1;

for i in range(96):
  notes.append(0)
  notes_db.append(0);
  notes_de.append(0);
  #

xoffset_whitekeys = 5 # 40 for avengers, else 5
xoffset_whitekeys = 60

yoffset_whitekeys = 603

yoffset_blackkeys = yoffset_whitekeys - 30
xoffset_blackkeys = xoffset_whitekeys + 10
#
width=1280;
height=720;
whitekey_width=24.6;
debug= 0;
resize= 0;

xx=0
for i in range(8):
 for j in range(12):
  keys_pos.append( [0,0] )
  keys_pos[i*12+j][0] = int(round(xoffset_whitekeys + xx ));
  keys_pos[i*12+j][1] = yoffset_whitekeys;
  if (j == 1) or ( j ==3 ) or ( j == 6 ) or ( j == 8) or ( j == 10 ):
   xx += -whitekey_width;
   keys_pos[i*12+j][0] = int(round(xoffset_whitekeys + xx  + whitekey_width *0.5 ));
   keys_pos[i*12+j][1] = yoffset_blackkeys;
  xx += whitekey_width

while success:
  if (frame % 100 == 0):
    print "processing frame: " + str(frame) + " / " + str(length);
  if ( resize == 1 ):
    image=cv2.resize(image, (width , height));

  # processing white keys
  for i in range( 96 ):
    pixx=keys_pos[i][0]
    pixy=keys_pos[i][1]

    if ( pixx > width ) or ( pixy > height ): break;
    if ( pixx < 0 ) or ( pixy < 0 ): continue;

    keybgr=image[pixy,pixx]
    key= [ keybgr[2], keybgr[1],keybgr[0] ];

    note=i;

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


#  os.remove("/tmp/frame%d.jpg" % frame)

  #cv2.imwrite("/tmp/frame%d.jpg" % frame, image)  # save frame as JPEG file

  if ( debug == 1 ):
    cv2.imwrite("/tmp/frame%d.jpg" % frame, image)  # save frame as JPEG file

#  if frame > 0: 
#    break;
  success,image = vidcap.read()
  frame += 1

# write midi to disk
with open(outputmid, 'wb') as outf:
    mf.writeFile(outf)
