#!/usr/bin/python

# by svsd_val
# jabber : svsd_val@jabber.ru
# mail to: svsdval@gmail.com

import math;
import cv2;
from midiutil.MidiFile import MIDIFile;
import os;
import sys;
import ntpath;

import pygame;
from pygame.locals import *;

from OpenGL.GL import *;
from OpenGL.GLU import *;


width=640;
height=480;

mpos = [0,0];

xoffset_whitekeys = 60;
yoffset_whitekeys = 673;

yoffset_blackkeys = -30;

keygrab=0;
keygrabid=-1;

whitekey_width=24.6;

if ( len(sys.argv) < 2 ):
  print "halt, no args";
  sys.exit( 0 ) ;

filepath = sys.argv[1];
if os.path.exists( filepath ):
  print "open file " + filepath;
  vidcap = cv2.VideoCapture( filepath );
else:
  print "file not exists " + filepath;
  sys.exit( 0 ) ;

outputmid= ntpath.basename( filepath ) + "_output.mid";
fileid=0;
while os.path.exists( outputmid ):
 outputmid = ntpath.basename( filepath ) + "_"+str(fileid)+ "_output.mid";
 fileid+=1;
 if ( fileid > 99 ): break;

frame= 0;
resize= 0;
convertCvtColor=0;

vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame);
success,image = vidcap.read();


# set start frame;
def getFrame( framenum =-1 ):
  global resize;
  global image;
  global success;
  global width;
  global height;
  global convertCvtColor;

  if ( framenum != -1 ):
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, framenum);

  if ( resize == 1 ):
    image=cv2.resize(image, (width , height));

  if ( convertCvtColor == 1 ):
    cv2.cvtColor(image,cv2.COLOR_BGR2RGB)

  success,image = vidcap.read();

getFrame();

debug = 0;
debug_keys = 0;

length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT));
width  = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH));
height = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT));
fps    = float(vidcap.get(cv2.CAP_PROP_FPS));

startframe = 0;
endframe = length;

#;
print "video " + str(width) + "x" + str(height) +" fps: " + str(fps);

# add some notes;
channel = 0;
volume = 100;
basenote = 35;


notes=[];
notes_db=[];
notes_de=[];
notes_channel=[];

keys_pos=[];

keyp_colors = [ [241,173,64], [216,57,77], [218,52,64], [105,150,192], [39,87,149], [166,250,103], [102,185,43] ];
keyp_delta = 90;
keyp_colors_channel = [ 0, 1, 2, 3, 4, 5, 6 ];
#;
minimal_duration = 0.6;
bgImgGL=-1;

experimental = 0;

for i in range(127):
  notes.append(0);
  notes_db.append(0);
  notes_de.append(0);
  notes_channel.append(0);
#;
resize= 0;

if ( resize == 1 ):
  width=1280;
  height=720;


def updatekeys( append=0 ):
 global keys_pos;
 xx=0;
 for i in range(8):
  for j in range(12):
   if (append == 1):
    keys_pos.append( [0,0] );
   keys_pos[i*12+j][0] = int(round( xx ));
   keys_pos[i*12+j][1] = 0;
   if (j == 1) or ( j ==3 ) or ( j == 6 ) or ( j == 8) or ( j == 10 ):
    xx += -whitekey_width;
    keys_pos[i*12+j][0] = int(round( xx  + whitekey_width *0.5 ));
    keys_pos[i*12+j][1] = yoffset_blackkeys;
   xx += whitekey_width;


def loadImage(idframe=130):
  global image;
  getFrame(idframe);

  print "video " + str(width) + "x" + str(height) + " frame: "+ str(frame) ;
  glPixelStorei(GL_UNPACK_ALIGNMENT,1)

  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
  glTexImage2D(GL_TEXTURE_2D, 0, 3, width, height, 0, GL_BGR, GL_UNSIGNED_BYTE, image );
#  glTexImage2D(GL_TEXTURE_2D, 0, 3, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
  glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)



def DrawQuad(x,y,x2,y2, texx=1, texy=-1):
  glBegin(GL_QUADS);
  glTexCoord2f(0, texy);
  glVertex2f(x, y);
  glTexCoord2f(texx, texy);
  glVertex2f(x2, y);
  glTexCoord2f(texx, 0);
  glVertex2f(x2, y2);
  glTexCoord2f(0, 0);
  glVertex2f(x, y2);
  glEnd();

updatekeys( 1 );

def processmidi():
 global frame;
 global xoffset_whitekeys;
 global yoffset_whitekeys;
 global whitekey_width;
 global bgImgGL;
 global width;
 global height;
 global length;
 global fps;

 global notes;
 global notes_db;
 global notes_de;
 global notes_channel;
 global keyp_colors_channel;

 global success,image;
 global startframe;
 global experimental;

 print "video " + str(width) + "x" + str(height);

 # create  MIDI object;
 mf = MIDIFile(1) # only 1 track;
 track = 0 # the only track;

 time = 0 # start at the beginning;

 mf.addTrackName(track, time, "Sample Track");
 mf.addTempo(track, time, 60 );

# vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame);
# success,image = vidcap.read();
 getFrame( startframe );

 while success:

  if (frame % 100 == 0):
   glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
   glTexImage2D(GL_TEXTURE_2D, 0, 3, width, height, 0, GL_BGR, GL_UNSIGNED_BYTE, image );
   glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
   glEnable(GL_TEXTURE_2D);

   glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);
   glViewport (0, 0, width, height);
   glMatrixMode (GL_PROJECTION);
   glLoadIdentity ();
   glOrtho(0, width, height, 0, -1, 100);
   glMatrixMode(GL_MODELVIEW);
   glLoadIdentity();

   #glScale(scale,scale,1);
   glColor4f(1.0, 1.0, 1.0, 1.0);

   glEnable(GL_TEXTURE_2D);
   DrawQuad(0,0,width,height);
   glEnable(GL_BLEND);
   glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
   glColor4f(1.0, 0.5, 1.0, 0.5);
   glDisable(GL_TEXTURE_2D);
 #  glPushMatrix();
 #  glTranslatef(0,height*0.5 - 20,0);
   p= frame / float( length );
   DrawQuad(0,height *0.5 -10, p  * width ,height *0.5 +10);
 #  glPopMatrix();
   pygame.display.flip();

#  if (frame % 100 == 0):
   print "processing frame: " + str(frame) + " / " + str(length) + " % " + str( math.trunc(p * 100));

  if ( resize == 1 ):
    image=cv2.resize(image, (width , height));

  # processing white keys;
  for i in range( len(keys_pos) ):
    pixx=xoffset_whitekeys + keys_pos[i][0];
    pixy=yoffset_whitekeys + keys_pos[i][1];

    if ( pixx >= width ) or ( pixy >= height ) or ( pixx < 0 ) or ( pixy < 0 ): continue;

    keybgr=image[pixy,pixx];
    key= [ keybgr[2], keybgr[1],keybgr[0] ];

    note=(i+1);

    keypressed=0;
    note_channel=0;

    for j in range(len(keyp_colors)):
      if ( abs( int(key[0]) - keyp_colors[j][0] ) < keyp_delta ) and ( abs( int(key[1]) - keyp_colors[j][1] ) < keyp_delta ) and ( abs( int(key[2]) - keyp_colors[j][2] ) < keyp_delta ):
       keypressed=1;
       note_channel=keyp_colors_channel[j];


    if ( debug == 1 ):
      if (keypressed == 1 ):
        cv2.rectangle(image, (pixx-5,pixy-5), (pixx+5,pixy+5), (128,128,255), -1 );
        cv2.putText(image, str(note_channel), (pixx-5,pixy-10), 0, 0.3, (64,128,255));
      cv2.rectangle(image, (pixx-5,pixy-5), (pixx+5,pixy+5), (255,0,255));
      cv2.rectangle(image, (pixx-1,pixy-1), (pixx+1,pixy+1), (255,0,255));
      cv2.putText(image, str(note), (pixx-5,pixy+20), 0, 0.5, (255,0,255));


    # reg pressed key;
    if keypressed==1:
      # if key is not pressed;
      if ( notes[note] == 0 ):
        if ( debug_keys == 1 ):
          print "white keys, note pressed on :" + str( note );
        notes[ note ] = 1;
        notes_db[ note ] = frame;
        notes_channel[ note ] = note_channel;
      if ( notes[note] == 1 ) and ( notes_channel[ note ] != note_channel ) and ( experimental == 1 ):
        # case if one key over other
        time = notes_db[note] / fps;
        duration = ( frame - notes_db[note] ) / fps;
        if ( duration < minimal_duration ): duration = minimal_duration;

        if ( debug_keys == 1 ):
          print "keys (one over other), note released :" + str(note) + " de = " + str(notes_de[note]) + "- db =" + str(notes_db[note]);
          print "midi add white keys, note : " +str(note) + " time:" +str(time) + " duration:" + str(duration);
        mf.addNote(track, notes_channel[note] , basenote+ note, time , duration , volume );

        notes_db[ note ] = frame;
        notes_channel[ note ] = note_channel;
    else:
      # if key been presed and released:
      if ( notes[note] == 1 ):
        notes[ note ] = 0;
        notes_de[ note ] = frame;
        time = notes_db[note] / fps;
        duration = ( notes_de[note] - notes_db[note] ) / fps;
        if ( duration < minimal_duration ): duration = minimal_duration;

        if ( debug_keys == 1 ):
          print "keys, note released :" + str(note ) + " de = " + str(notes_de[note]) + "- db =" + str(notes_db[note]);
          print "midi add white keys, note : " +str(note) + " time:" +str(time) + " duration:" + str(duration);
        mf.addNote(track, notes_channel[note] , basenote+ note, time , duration , volume );

  xapp=0;
  if ( debug == 1 ):
    cv2.imwrite("/tmp/frame%d.jpg" % frame, image)  # save frame as JPEG file

#  success,image = vidcap.read();
  getFrame();

  frame += 1;
  for event in pygame.event.get():
   if event.type == pygame.QUIT: 
     success = False;
     pygame.quit();
     quit();
   elif event.type == pygame.KEYDOWN:
    if event.key == pygame.K_SPACE:
     success = False;

# write midi to disk;
 with open(outputmid, 'wb') as outf:
  mf.writeFile(outf);


def GenHelpTexture(text):
  font = pygame.font.Font(None, 64)
  textSurface = font.render(text, True, (255,255,255,255), (0,0,0,255))
  ix, iy = textSurface.get_width(), textSurface.get_height()
  img = pygame.image.tostring(textSurface, "RGBX", True)
  glPixelStorei(GL_UNPACK_ALIGNMENT,1)
  i = glGenTextures(1)
  glBindTexture(GL_TEXTURE_2D, i)
  glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, img)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
  glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
  return i


def main():
  global xoffset_whitekeys;
  global yoffset_whitekeys;
  global yoffset_blackkeys;
  global whitekey_width;
  global bgImgGL;
  global pyfont;
  running=1;
  keygrab=0;
  keygrabid=-1;
  keygrabaddx=0;

  scale=1.0;
  pygame.init();
  pyfont = pygame.font.SysFont('Sans', 20)
  display = (width,height);
  screen = pygame.display.set_mode(display, DOUBLEBUF|OPENGL);

  glPixelStorei(GL_UNPACK_ALIGNMENT,1)
  bgImgGL = glGenTextures(1);
  glBindTexture(GL_TEXTURE_2D, bgImgGL);
  loadImage();
  #
  helptext = GenHelpTexture("Q - for process, Mouse wheel & arrows to adjust keys, Right mouse button - to move all keys");

  frame= 0;
  # set start frame;
  vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame);

  display = (width,height);
  pygame.display.set_mode(display, DOUBLEBUF|OPENGL);
  while running==1:
    mousex, mousey = pygame.mouse.get_pos();

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);
    glViewport (0, 0, width, height);
    glMatrixMode (GL_PROJECTION);
    glLoadIdentity ();
    glOrtho(0, width, height, 0, -1, 100);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

    glScale(scale,scale,1);
    glColor4f(1.0, 1.0, 1.0, 1.0);

    glBindTexture(GL_TEXTURE_2D, bgImgGL);
    glEnable(GL_TEXTURE_2D);
    DrawQuad(0,0,width,height);
    glColor4f(1.0, 1.0, 1, 0.7);
    glBindTexture(GL_TEXTURE_2D, helptext);
    DrawQuad(0,0,width,height *0.05, texy=1);


    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glColor4f(1.0, 0.5, 1.0, 0.5);
    glPushMatrix();
    glTranslatef(xoffset_whitekeys,yoffset_whitekeys,0);
    glDisable(GL_TEXTURE_2D);
    for i in range( len( keys_pos) ):

     pixx=xoffset_whitekeys + keys_pos[i][0];
     pixy=yoffset_whitekeys + keys_pos[i][1];

     if ( pixx >= width ) or ( pixy >= height ) or ( pixx < 0 ) or ( pixy < 0 ): continue;

     keybgr=image[pixy,pixx];
     key= [ keybgr[2], keybgr[1],keybgr[0] ];
     note=(i+1);
     keypressed=0;

     for keyc in keyp_colors:
        if ( abs( int(key[0]) - keyc[0] ) < keyp_delta ) and ( abs( int(key[1]) - keyc[1] ) < keyp_delta ) and ( abs( int(key[2]) - keyc[2] ) < keyp_delta ):
         keypressed=1;

     glPushMatrix();
     glTranslatef(keys_pos[i][0],keys_pos[i][1],0);

     if ( keypressed == 1 ):
       glColor4f(1.0, 0.5, 1.0, 0.9);
       DrawQuad(-5,-7,5,7);
     else:
       glColor4f(0.5, 1, 1.0, 0.5);
       DrawQuad(-5,-5,5,5);
     DrawQuad(-1,-1,1,1);
     glPopMatrix();
     glColor4f(0.0, 1.0, 1.0, 0.5);
    glPopMatrix();

    glPushMatrix();
    glTranslatef(mousex,mousey,0);
    glScalef(0.5,0.5,0.5);
    DrawQuad(-5,-5,5,5);
    glPopMatrix();

    for event in pygame.event.get():
     if event.type == pygame.QUIT: 
      running = 0;
      pygame.quit();
      quit();
     elif event.type == pygame.KEYDOWN:
#      print event.key;
      if event.key == pygame.K_q:
       running = 0;
      if event.key == pygame.K_ESCAPE:
       running = 0;
       pygame.quit();
       quit();
      if event.key == pygame.K_UP:
       yoffset_blackkeys -= 1;
       updatekeys( );
      if event.key == pygame.K_DOWN:
       yoffset_blackkeys += 1;
       updatekeys( );
      if event.key == pygame.K_LEFT:
       whitekey_width-=0.5;
       updatekeys( );
      if event.key == pygame.K_RIGHT:
       whitekey_width+=0.5;
       updatekeys( );
      if event.key == pygame.K_PAGEUP:
       frame+=100;
       if (frame > length *0.98):
        frame=math.trunc(length *0.98);

       glBindTexture(GL_TEXTURE_2D, bgImgGL);
       loadImage(frame);
      if event.key == pygame.K_PAGEDOWN:
       frame-=100;
       if (frame < 1):
        frame=1;
       glBindTexture(GL_TEXTURE_2D, bgImgGL);
       loadImage(frame);

     elif event.type == pygame.MOUSEBUTTONUP:
      if ( event.button == 1 ):
        keygrab = 0;
        keygrabid = -1;
      if ( event.button == 3 ):
        keygrab = 0;

     elif event.type == pygame.MOUSEBUTTONDOWN:
#      print event.button;
      if ( event.button == 4 ):
        whitekey_width+=0.05;
#        print "whitekey_width="+str(whitekey_width);
        updatekeys( );
#        scale+=0.1;
      if ( event.button == 5 ):
        whitekey_width-=0.05;
#        print "whitekey_width="+str(whitekey_width);
        updatekeys( );
#        scale-=0.1;
      if (scale >2): scale=2;
      if (scale <1): scale=1;

      if ( event.button == 1 ):
        size=5;
        print "x offset " + str(xoffset_whitekeys) + " y offset: " +str(yoffset_whitekeys);
        for i in range( len( keys_pos) ):
         if (abs( mousex - (keys_pos[i][0] + xoffset_whitekeys) )< size) and (abs( mousey - (keys_pos[i][1] + yoffset_whitekeys) )< size):
          keygrab=1;
          keygrabid=i;
          print "ok click found on : "+str(keygrabid);
          break;
        pass;
      if ( event.button == 3 ):
        keygrab = 2;
        size=5;
        print "x offset " + str(xoffset_whitekeys) + " y offset: " +str(yoffset_whitekeys);
        keygrabaddx=0
        for i in range( len( keys_pos) ):
         if (abs( mousex - (keys_pos[i][0] + xoffset_whitekeys) )< size) and (abs( mousey - (keys_pos[i][1] + yoffset_whitekeys) )< size):
          keygrab=2;
          keygrabaddx=keys_pos[i][0];
          print "ok click found on : "+str(keygrabid);
          break;

    if ( keygrab == 1) and ( keygrabid >-1 ):
#     print "moving keyid = " + str(keygrabid);
     keys_pos[ keygrabid ][0] = mousex - xoffset_whitekeys;
     keys_pos[ keygrabid ][1] = mousey - yoffset_whitekeys;
    if ( keygrab == 2):
#      print "moving offsets : "+ str(mousex) + " x " + str(mousey);
      xoffset_whitekeys = mousex - keygrabaddx;
      yoffset_whitekeys = mousey;

    pygame.display.flip();

main();

frame=0;
processmidi();

print "done...";