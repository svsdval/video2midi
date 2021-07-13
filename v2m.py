#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# by svsd_val
# jabber : svsd_val@jabber.ru
# mail to: svsdval@gmail.com

import math;
import cv2;
from midiutil.MidiFile import MIDIFile;
import os;
import ntpath;

import pygame;
from pygame.locals import *;

from OpenGL.GL import *;
from OpenGL.GLU import *;
import time;

from os.path import expanduser


import video2midi.settings as settings
from video2midi.prefs import prefs
from video2midi.gl import *


width=640;
height=480;

mpos = [0,0];

keygrab=0;
keygrabid=-1;
lastkeygrabid=-1;

if ( len(sys.argv) < 2 ):
  print("halt, no args");
  sys.exit( 0 ) ;

filepath = sys.argv[1];
if not os.path.exists( filepath ):
  print("file not exists [" + filepath +"]");
  sys.exit( 0 ) ;

print("open file " + filepath);
vidcap = cv2.VideoCapture( filepath );

outputmid= ntpath.basename( filepath ) + "_output.mid";
fileid=0;
while os.path.exists( outputmid ):
 outputmid = ntpath.basename( filepath ) + "_"+str(fileid)+ "_output.mid";
 fileid+=1;
 if ( fileid > 99 ): break;
#
settingsfile= filepath + ".ini";
#
frame= 0;
printed_for_frame=0;
convertCvtColor=1;
# For OpenCV 2.X ..
CAP_PROP_FRAME_COUNT =0;
CAP_PROP_POS_FRAMES  =0;
CAP_PROP_POS_MSEC    =0;
CAP_PROP_FRAME_WIDTH =0;
CAP_PROP_FRAME_HEIGHT=0;
CAP_PROP_FPS         =0;
COLOR_BGR2RGB        =0;
print("OpenCV version:" + cv2.__version__ );

if cv2.__version__.startswith('2.'):
 CAP_PROP_FRAME_COUNT  = cv2.cv.CV_CAP_PROP_FRAME_COUNT;
 CAP_PROP_POS_FRAMES   = cv2.cv.CV_CAP_PROP_POS_FRAMES;
 CAP_PROP_POS_MSEC     = cv2.cv.CV_CAP_PROP_POS_MSEC;
 CAP_PROP_FRAME_WIDTH  = cv2.cv.CV_CAP_PROP_FRAME_WIDTH;
 CAP_PROP_FRAME_HEIGHT = cv2.cv.CV_CAP_PROP_FRAME_HEIGHT;
 CAP_PROP_FPS          = cv2.cv.CV_CAP_PROP_FPS;
else:
 # 3, 4 , etc ...
 CAP_PROP_FRAME_COUNT  = cv2.CAP_PROP_FRAME_COUNT;
 CAP_PROP_POS_FRAMES   = cv2.CAP_PROP_POS_FRAMES;
 CAP_PROP_POS_MSEC     = cv2.CAP_PROP_POS_MSEC;
 CAP_PROP_FRAME_WIDTH  = cv2.CAP_PROP_FRAME_WIDTH;
 CAP_PROP_FRAME_HEIGHT = cv2.CAP_PROP_FRAME_HEIGHT;
 CAP_PROP_FPS          = cv2.CAP_PROP_FPS;
 
COLOR_BGR2RGB         = cv2.COLOR_BGR2RGB;

#

vidcap.set(CAP_PROP_POS_FRAMES, frame);
success,image = vidcap.read();

debug_keys = 0;

length = int(vidcap.get(CAP_PROP_FRAME_COUNT));
video_width  = int(vidcap.get(CAP_PROP_FRAME_WIDTH));
video_height = int(vidcap.get(CAP_PROP_FRAME_HEIGHT));
fps    = float(vidcap.get(CAP_PROP_FPS));

width = video_width;
height = video_height;

startframe = 1;
endframe = length;

def resize_window():
  global screen,  width, height

  if prefs.resize:
    width = prefs.resize_width;
    height = prefs.resize_height;
  else:
    width = video_width
    height = video_height;
  screen = pygame.display.set_mode((width,height), DOUBLEBUF|OPENGL);
  #
  doinit();

# set start frame;
def getFrame( framenum =-1 ):
  global image;
  global success;
  global width;
  global height;
  global convertCvtColor;
  global fps;


  if ( fps == 0 ):
   return;

  if ( framenum != -1 ):
    #vidcap.set(CAP_PROP_POS_FRAMES, int(framenum) );
    # problems with mpeg formats ...
    oldframenum = int(round(vidcap.get(1)));

    frametime =  framenum * 1000.0 / fps;
    print("go to frame time :" + str(frametime));
    success = vidcap.set(CAP_PROP_POS_MSEC, frametime);
    if not success:
      print("Cannot set frame position from video file at " + str(framenum));
      success = vidcap.set(CAP_PROP_POS_FRAMES, int(oldframenum) );
    curframe = vidcap.get(CAP_PROP_POS_FRAMES);
    if (curframe != framenum ):
     print("OpenCV bug, Requesting frame " + str(framenum) + " but get position on " +str(curframe));


  success,image = vidcap.read();
#  if ( resize == 1 ):
#    image = cv2.resize(image, (resize_width , resize_height));
#    print "resize to "+str(resize_width) + "x"+ str(resize_height);
  pass

getFrame();


#;
print("video " + str(width) + "x" + str(height) +" fps: " + str(fps));

# add some notes;
channel = 0;
volume = 100;
octave = 3;
basenote = octave * 12;


notes=[];
notes_db=[];
notes_de=[];
notes_channel=[];
notes_tmp=[];

colorWindow_colorBtns_channel_labels=[];
colorWindow_colorBtns_channel_btns=[];



separate_note_id=-1;



screen=0;
colorBtns = []

#quantized notes to the grid.
use_snap_notes_to_grid = False;
notes_grid_size=32;
#
midi_file_format = 0;
#
line_height = 20;

#cfg
home = expanduser("~")
inifile = os.path.join( home, '.v2m.ini');
if os.path.exists( 'v2m.ini' ):
  inifile="v2m.ini";
  print("local config file exists.")

def update_size():
  global width, height
  if ( prefs.resize == 1 ):
    width = prefs.resize_width;
    height = prefs.resize_height;

def loadsettings(cfgfile):
  global colorBtns, colorWindow_colorBtns_channel_labels

  settings.loadsettings(cfgfile)
  settings.compatibleColors(colorBtns)

  if len(colorWindow_colorBtns_channel_labels) > 0:
   for i in range(len(colorBtns)):
     colorWindow_colorBtns_channel_labels[i].text = "Ch:" + str(prefs.keyp_colors_channel[i]+1);

  update_size

  if 'glwindows' in globals():
    settingsWindow_slider1.setvalue(prefs.keyp_delta);
    settingsWindow_slider2.setvalue(prefs.minimal_duration * 100);
    settingsWindow_slider3.setvalue(prefs.tempo);
    sparks_switch.switch_status = prefs.use_sparks;
    sparks_slider_delta.value = 0;
    sparks_slider_delta.id =-1;
    extraWindow_rollcheck_button.switch_status = prefs.rollcheck;
  pass;

update_size

for i in range(127):
  notes.append(0);
  notes_db.append(0);
  notes_de.append(0);
  notes_channel.append(0);
  notes_tmp.append(0);
  #
  prefs.keyp_colors_alternate.append([0,0,0]);
  prefs.keyp_colors_alternate_sensetivity.append(0);
#;



def updatekeys( append=0 ):
 xx=0;
 for i in range(9):
  for j in range(12):
   if (append == 1) or (i*12+j > len(prefs.keys_pos)-1):
    prefs.keys_pos.append( [0,0] );
   
   prefs.keys_pos[i*12+j][0] = int(round( xx ));
   prefs.keys_pos[i*12+j][1] = 0;
   if (j == 1) or ( j ==3 ) or ( j == 6 ) or ( j == 8) or ( j == 10 ):
     prefs.keys_pos[i*12+j][1] = prefs.yoffset_blackkeys;
     xx += -prefs.whitekey_width;
#     keys_pos[i*12+j][0] = int(round( xx  + whitekey_width *0.5 ));
   # tune by wuzhuoqing  
   if (j == 1) or ( j == 6 ):
     prefs.keys_pos[i*12+j][0] = int(round( xx  + prefs.whitekey_width * prefs.blackkey_relative_position ));
   if (j == 8 ):
     prefs.keys_pos[i*12+j][0] = int(round( xx  + prefs.whitekey_width * 0.5 ));
   if ( j ==3 ) or ( j == 10 ):
     prefs.keys_pos[i*12+j][0] = int(round( xx  + prefs.whitekey_width * (1.0 - prefs.blackkey_relative_position) ));
     
   xx += prefs.whitekey_width;
  pass;




updatekeys( 1 );

loadsettings(inifile);

tStart = t0 = time.time()-1;
frames = 0;

def snap_to_grid( input_value , input_grid_size ):
    quantized = int( (input_value - int(input_value)) * input_grid_size ) / input_grid_size;
    result = (quantized + int(input_value));
    #print ("value before:", input_value , " after :", result);
    return result;



def framerate():
    global t0, frames
    t = time.time();
    frames += 1
    if t - t0 >= 1.0:
        seconds = t - t0
        if ( seconds != 0) :
          fps = frames / seconds
          print("%.0f frames in %3.1f seconds = %6.3f FPS" % (frames,seconds,fps))
        t0 = t
        frames = 0


def loadImage(idframe=130):
  global image;
  global convertCvtColor;
  getFrame(idframe);

  print("load image from video " + str(width) + "x" + str(height) + " frame: "+ str(idframe));
  glPixelStorei(GL_UNPACK_ALIGNMENT,1)

  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
  glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
  if ( convertCvtColor == 1 ):
    #print ("Loading RGB texture");
    glTexImage2D(GL_TEXTURE_2D, 0, 3, video_width, video_height, 0, GL_RGB, GL_UNSIGNED_BYTE, cv2.cvtColor(image,COLOR_BGR2RGB) );
  else:
    #print ("Loading BGR texture");
    glTexImage2D(GL_TEXTURE_2D, 0, 3, video_width, video_height, 0, GL_BGR, GL_UNSIGNED_BYTE, image );
  pass;

def update_channels(sender):
   print( 'update_channels...' +str(sender.index));
   i=abs(sender.index) -1;
   if (sender.index > 0):
     prefs.keyp_colors_channel[i]= prefs.keyp_colors_channel[i] + 1;
   else:
     prefs.keyp_colors_channel[i]= prefs.keyp_colors_channel[i] - 1;
   if (prefs.keyp_colors_channel[i] > 15):
     prefs.keyp_colors_channel[i] = 15;
   if (prefs.keyp_colors_channel[i] < 0):
     prefs.keyp_colors_channel[i] = 0;
   colorWindow_colorBtns_channel_labels[i].text = "Ch:" + str(prefs.keyp_colors_channel[i]+1);

def readkeycolor(i):
   pixx=int(prefs.xoffset_whitekeys + prefs.keys_pos[i][0]);
   pixy=int(prefs.yoffset_whitekeys + prefs.keys_pos[i][1]);

   if ( pixx >= width ) or ( pixy >= height ) or ( pixx < 0 ) or ( pixy < 0 ): return;
   if ( prefs.resize == 1 ):
     pixxo=pixx;
     pixyo=pixy;

     pixx= int(round( pixx * ( video_width / float(prefs.resize_width) )))
     pixy= int(round( pixy * ( video_height / float(prefs.resize_height) )))
     if ( pixx > video_width -1 ): pixx = video_width-1;
     if ( pixy > video_height-1 ): pixy= video_height-1;
    #      print "original x:"+str(pixxo) + "x" +str(pixyo) + " mapped :" +str(pixx) +"x"+str(pixy);

   keybgr=image[pixy,pixx];
   key=[ keybgr[2], keybgr[1],keybgr[0] ];

   prefs.keyp_colors_alternate[i] = key;
    

def readcolors(sender):
   for i in range( len(prefs.keys_pos) ):
    readkeycolor(i);

def update_alternate_sensetivity(sender,value):
   global lastkeygrabid;
   if ( lastkeygrabid != -1 ):
     prefs.keyp_colors_alternate_sensetivity[ lastkeygrabid ] = value;
     
def update_sparks_delta(sender,value):
   if (sender.id == -1):
     return;
   if (sender.id < len(prefs.keyp_colors))  :
    prefs.keyp_colors_sparks_sensitivity[sender.id] = sender.value
    #print("keyp_colors_sparks_sensitivity["+str(sender.id)+"] = "+ str(sender.value) );
     
def update_blackkey_relative_position(sender,value):
  prefs.blackkey_relative_position = value * 0.001;
  updatekeys();

def change_use_alternate_keys(sender):
   global extra_label1;
   prefs.use_alternate_keys = not prefs.use_alternate_keys
   update_alternate_label()

def update_alternate_label():
  extra_label1.text = "Use alternate:"+str(prefs.use_alternate_keys)

def change_use_sparks(sender):
   prefs.use_sparks = sender.switch_status;
#   sender.text = "use sparks:"+str(use_sparks);
def change_rollcheck(sender):
   prefs.rollcheck = sender.switch_status;


def updatecolor(sender):
   if (lastkeygrabid != -1):
    readkeycolor(lastkeygrabid);

def update_sparks_y_pos (sender):
   if (sender.text == "y+"):
     prefs.keyp_spark_y_pos =  prefs.keyp_spark_y_pos -1;
   else:
     prefs.keyp_spark_y_pos =  prefs.keyp_spark_y_pos +1;
   pass;
   
def update_line_height(sender,value):
  global line_height;
  line_height = value;
   

def snap_notes_to_the_grid(sender):
    global use_snap_notes_to_grid;
    use_snap_notes_to_grid = sender.switch_status;
 
# 
wh = ( (len(prefs.keyp_colors) // 2)+2 ) * 24;
colorWindow = GLWindow(32, 16, 264, wh, "color map")
settingsWindow = GLWindow(32, wh, 250, 310, "Settings");
helpWindow = GLWindow(32+270, 16, 750, 475, "help");

extraWindow = GLWindow(32+270+750+6, 16, 510, 250, "extra/experimental");

sparksWindow = GLWindow(32+270+750+6, 250, 510, 125, "sparks");


glwindows = [];
glwindows.append(colorWindow);
glwindows.append(settingsWindow);
glwindows.append(helpWindow);

glwindows.append(extraWindow);
glwindows.append(sparksWindow);

#helpWindow.hidden=1;
helpWindow_label1 = GLLabel(0,0, """h - on window title, show/hide the window
q - begin to recreate midi
s - set start frame, (mods : shift, set processing start frame to the beginning)
e - set end frame, (mods : shift, set processing end frame to the ending)
p - if key is set, force separate to 2 channels (on single color video)
o - enable or disable overlap notes
i - enable or disable ignore/lengthening of notes with minimal duration
r - enable or disable resize function
Mouse wheel - keys adjustment
Left mouse button - dragging the selected key / select color from the color map
CTRL + Left mouse button - update selected color in the color map
CTRL + 0 - disable selected color in the color map
Right mouse button - dragging all keys, if the key is selected, the transfer is carried out relative to it.
Arrows - keys adjustment (mods : shift) ( Atl+Arrows UP/Down - sparks position adjustment )
PageUp/PageDown - scrolling video (mods : shift)
Home/End - go to the beginning or end of the video
[ / ] - change base octave
F2 / F3 - save / load settings
Escape - quit
Space - abort re-creation and save midi file to disk""");

helpWindow.appendChild(helpWindow_label1);

settingsWindow_label1 = GLLabel(0,0, "base octave: " + str(octave) + "\nnotes overlap: " + str(prefs.notes_overlap) + "\nignore minimal duration: " + str(prefs.ignore_minimal_duration));
settingsWindow.appendChild(settingsWindow_label1);

#settingsWindow_label2 = GLLabel(0,67,  "Sensitivity:"+str(keyp_delta)+"\n\nMinimal note duration (sec):"+str(minimal_duration) +   "\n\nOutput tempo for midi:" + str(tempo)  );
#settingsWindow.appendChild(settingsWindow_label2);

settingsWindow_slider1 = GLSlider(1,90, 240,18, 0,130,prefs.keyp_delta,label="Sensitivity");
settingsWindow_slider1.round=1;
settingsWindow.appendChild(settingsWindow_slider1);

settingsWindow_slider2 = GLSlider(1,130, 240,18, 0,200,prefs.minimal_duration*100,label="Minimal note duration (sec)");
settingsWindow_slider2.round=0;
settingsWindow.appendChild(settingsWindow_slider2);

settingsWindow_slider3 = GLSlider(1,173, 240,18, 30,240,prefs.tempo,label="Output tempo for midi");
settingsWindow_slider3.round=0;
settingsWindow.appendChild(settingsWindow_slider3);

settingsWindow_slider4 = GLSlider(1,215, 240,18, 0,2,midi_file_format,label="Output midi format");
settingsWindow_slider4.round=0;
settingsWindow.appendChild(settingsWindow_slider4);

settingsWindow_slider5 = GLSlider(1,255, 240,18, 0,1000,prefs.blackkey_relative_position * 1000, update_blackkey_relative_position, label="black key relative pos");
settingsWindow_slider5.round=0;
settingsWindow.appendChild(settingsWindow_slider5);




# for i in range( len( keyp_colors ) ):
  #keyp_colormap_colors_pos.append ([ (i % 2) * 32,  ( i // 2 ) * 20  ]);
print ('creating new colors '+str(len( prefs.keyp_colors )));

for i in range( len( prefs.keyp_colors ) ):
 cx,cy = (i % 2) * 130,  ( i // 2 ) * 20;
 offsetx,offsety=4,4;
 colorBtns.append( GLColorButton(offsetx+cx,offsety+cy ,20,20,i, prefs.keyp_colors[i] ) );
 colorWindow.appendChild(colorBtns[i]);
 colorWindow_label1 = GLLabel(offsetx+25+cx,offsety+cy , "Ch:" + str(prefs.keyp_colors_channel[i]+1) );
 
 colorWindow_colorBtns_channel_labels.append( colorWindow_label1 );
 colorWindow.appendChild(colorWindow_label1);
 #
 colorWindow_colorBtns_channel_btns.append( GLButton(offsetx+cx+80,offsety+cy ,20,20,(i+1), [128,128,128], "+" ,update_channels) );
 colorWindow.appendChild( colorWindow_colorBtns_channel_btns[i*2] );
 #
 colorWindow_colorBtns_channel_btns.append( GLButton(offsetx+cx+80+20,offsety+cy ,20,20,-(i+1), [128,128,128], "-" ,update_channels) );
 colorWindow.appendChild( colorWindow_colorBtns_channel_btns[i*2+1] );

extraWindow.appendChild( GLButton(5,20 ,128,25,1, [128,128,128], "read colors" ,readcolors) );
extraWindow.appendChild( GLButton(135,20 ,128,25,1, [128,128,128], "update color" ,updatecolor) );
extraWindow.appendChild( GLButton(265,20 ,138,25,1, [128,128,128], "enable/disable" ,change_use_alternate_keys) );
extraWindow.appendChild( GLButton(265,45 ,155,22,1, [96,96,128], "snap notes to grid" ,snap_notes_to_the_grid,switch=1, switch_status=use_snap_notes_to_grid) );


extra_label1 = GLLabel(6,0,  "Use alternate:"+str(prefs.use_alternate_keys)  );
extraWindow.appendChild( extra_label1 );
#extra_label2 = GLLabel(0,67,  "Selected key sensitivity:"+str(0) );
extra_slider1 = GLSlider(6,65, 240,18, -100,100,0,update_alternate_sensetivity, label="Selected key sensitivity");
#extra_slider1.showvalue=True;
#showvaluesinlabel=0

extraWindow.appendChild(extra_slider1);

extra_label3 = GLLabel( 6,90,  """to select the key press ctrl + left mouse button on the key rect.
to deselect the key press ctrl + left mouse button on empty space.""" );
extraWindow.appendChild( extra_label3 );

extraWindow_slider2 = GLSlider(5,155, 240,18, 0,2000, line_height, update_line_height, label="length of vertical key lines");
extraWindow_slider2.round=0;
extraWindow.appendChild(extraWindow_slider2);

extraWindow_rollcheck_button = GLButton(250,155 ,100,22,1, [128,128,128], "roll check" ,change_rollcheck,switch=1, switch_status=prefs.rollcheck );
extraWindow.appendChild(extraWindow_rollcheck_button);



sparks_slider_delta = GLSlider(6,25, 150,18, -50,150,50,update_sparks_delta, label="Sparks delta");
sparks_slider_height = GLSlider(160,25, 150,18, 1,60,1,None, label="Sparks height");
sparks_slider_height.round=0;
sparks_switch = GLButton(313,24 ,100,22,1, [128,128,128], "use sparks" ,change_use_sparks,switch=1, switch_status=prefs.use_sparks );
sparksWindow.appendChild( sparks_slider_delta );
sparksWindow.appendChild( sparks_slider_height );
sparksWindow.appendChild( sparks_switch );
#
sparksWindow.appendChild( GLButton(413   ,24 ,32,22,1, [96,96,128], "y+" ,update_sparks_y_pos) );
sparksWindow.appendChild( GLButton(413+33,24 ,32,22,1, [96,96,128], "y-" ,update_sparks_y_pos) );
sparksWindow.appendChild( GLLabel( 6,50,  "alt + up / down - move sparks label up or down " ));

#

#extra_slider2.showvalue=True;
#extra.appendChild(extra_label2);
 

#loadsettings( settingsfile );    
#frame=801

def getkeyp_pixel_pos( x, y ):
  pixx=int(prefs.xoffset_whitekeys + x);
  pixy=int(prefs.yoffset_whitekeys + y);

  if ( pixx >= width ) or ( pixy >= height ) or ( pixx < 0 ) or ( pixy < 0 ): 
    return [-1,-1];

  if ( prefs.resize == 1 ):
    pixx= int(round( pixx * ( video_width / float(prefs.resize_width) )))
    pixy= int(round( pixy * ( video_height / float(prefs.resize_height) )))
    if ( pixx > video_width -1 ): pixx = video_width-1;
    if ( pixy > video_height-1 ): pixy= video_height-1;
  return [pixx,pixy];


 
def drawframe():
 global pyfont;
 global helptext;
 global mousex, mousey;
 global keyp_colormap_colors_pos;
 global keyp_colormap_pos;
 global keyp_colormap_id;
 global octave;
 global frame;
 global printed_for_frame;
 global notes_tmp;
 #global old_spark_color;
 #global cur_spark_color;
 print_for_frame_debug = False
 if printed_for_frame != frame:
  print_for_frame_debug = True
 printed_for_frame = frame

 scale=1.0;
 mousex, mousey = pygame.mouse.get_pos();

 glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);
 glViewport (0, 0, width, height);
 glMatrixMode (GL_PROJECTION);
 glLoadIdentity ();
 glOrtho(0, width, height, 0, -1, 100);
 glMatrixMode(GL_MODELVIEW);
 glLoadIdentity();
 glDisable(GL_DEPTH_TEST);

 glScale(scale,scale,1);
 glColor4f(1.0, 1.0, 1.0, 1.0);

 glBindTexture(GL_TEXTURE_2D, GlConstants.bgImgGL);
 glEnable(GL_TEXTURE_2D);
 DrawQuad(0,0,width,height);
 
 
 glEnable(GL_BLEND);
 glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

 glColor4f(1.0, 0.5, 1.0, 0.5);
 glPushMatrix();
 glTranslatef(prefs.xoffset_whitekeys,prefs.yoffset_whitekeys,0);
 glDisable(GL_TEXTURE_2D);

 for i in range( len( prefs.keys_pos) ):
  pixpos = getkeyp_pixel_pos(prefs.keys_pos[i][0],prefs.keys_pos[i][1]);

  if (pixpos[0] == -1) and (pixpos[1] == -1):
     continue;
  
  keybgr=image[ pixpos[1], pixpos[0] ];
  key= [ keybgr[2], keybgr[1],keybgr[0] ];

  keybgr=[0,0,0];
  sparkkey=[0,0,0];
  if prefs.use_sparks:
    sh = int(sparks_slider_height.value);
    if sh == 0:
        sh = 1;
    for spark_y_add_pos in range (sh):
     sparkpixpos = getkeyp_pixel_pos(prefs.keys_pos[i][0],prefs.keyp_spark_y_pos - spark_y_add_pos );
     if not ((sparkpixpos[0] == -1) and (sparkpixpos[1] == -1)):
       keybgr   = image[ sparkpixpos[1], sparkpixpos[0] ];
       sparkkey = [ sparkkey[0] + keybgr[2], 
                    sparkkey[1] + keybgr[1],
                    sparkkey[2] + keybgr[0] ];
    sparkkey = [ sparkkey[0] / sh,  sparkkey[1] / sh,sparkkey[2] / sh];
    #cur_spark_color[i] = sparkkey;
  else:
    sparkkey = [0,0,0];

  note=i;
  if ( note > 120 ):
    print("skip note > 120");
    continue;
  keypressed=0;

  pressedcolor=[0,0,0];
  if prefs.use_alternate_keys:
    delta = prefs.keyp_delta + prefs.keyp_colors_alternate_sensetivity[i];  
    if ( abs( int(key[0]) - prefs.keyp_colors_alternate[i][0] ) > delta ) and ( abs( int(key[1]) - prefs.keyp_colors_alternate[i][1] ) > delta ) and ( abs( int(key[2]) - prefs.keyp_colors_alternate[i][2] ) > delta ):
      keypressed=1;
      pressedcolor=prefs.keyp_colors_alternate[i];
  else: 
      for key_id in range( len(prefs.keyp_colors) ):
       keyc = prefs.keyp_colors[key_id];
       spark_delta = prefs.keyp_colors_sparks_sensitivity[key_id];
       #
       if (keyc[0] != 0 ) or (keyc[1] != 0 ) or (keyc[2] != 0 ) :
         if ( abs( int(key[0]) - keyc[0] ) < prefs.keyp_delta ) and ( abs( int(key[1]) - keyc[1] ) < prefs.keyp_delta ) and ( abs( int(key[2]) - keyc[2] ) < prefs.keyp_delta ):
          keypressed=1;
          pressedcolor = keyc;
          if prefs.use_sparks:
            #unpressed_by_spark_delta = ( abs( int(sparkkey[0]) - keyc[0] ) < spark_delta ) and ( abs( int(sparkkey[1]) - keyc[1] ) < spark_delta ) and ( abs( int(sparkkey[2]) - keyc[2] ) < spark_delta );
            has_spark_delta = ((sparkkey[0] - keyc[0] ) > spark_delta ) or ((sparkkey[1] - keyc[1] ) > spark_delta ) or ((sparkkey[2] - keyc[2] ) > spark_delta );
            #unpressed_by_spark_fade = ( cur_spark_color[i][0] <  old_spark_color[i][0]) and ( cur_spark_color[i][1] <  old_spark_color[i][1]) and ( cur_spark_color[i][2] <  old_spark_color[i][2]) ;
            #unpressed_by_spark_fade_delta = ( abs( cur_spark_color[i][0] - old_spark_color[i][0]) > 20 ) 			
            if print_for_frame_debug:
             print("note %d key_id %d spark_delta %d sparkkey vs keyc %d %d, %d %d, %d %d" % (note, key_id, spark_delta, sparkkey[0], keyc[0], sparkkey[1], keyc[1], sparkkey[2], keyc[2]))
            if ( not has_spark_delta ):
             keypressed=2;
  notes_tmp[i] = keypressed;

  j = i % 12;
  if prefs.rollcheck and (i >1):

      if (j == 1) or ( j ==3 ) or ( j == 6 ) or ( j == 8) or ( j == 10 ):
        if notes_tmp[i-1] >0:
            keypressed =0;
            
  glPushMatrix();
  glTranslatef(prefs.keys_pos[i][0],prefs.keys_pos[i][1],0);

  glColor4f(1,1,1,0.5);
  if (j == 1) or ( j ==3 ) or ( j == 6 ) or ( j == 8) or ( j == 10 ):
    glColor4f(0.57,0.57,0.57,0.55);
  DrawQuad(-0.5,-line_height,0.5, line_height );
  if ( keypressed != 0 ):
    #glColor4f(1.0, 0.5, 1.0, 0.9);
    glColor4f(pressedcolor[0]/255.0,pressedcolor[1]/255.0,pressedcolor[2]/255.0,0.9);
    DrawQuad(-6,-7,6,7);
    glColor4f(0,0,0,1);
    if ( keypressed == 1):
      DrawRect(-7,-9,7,9,3);
    else:
      DrawRect(-5,-7,5,7,3);
  else:
    glColor4f(0,0,0,1);
    DrawRect(-7,-7,7,7,1);
    glColor4f(0.5, 1, 1.0, 0.7);
    DrawQuad(-5,-5,5,5);
  if ( lastkeygrabid == i ):
    glColor4f(0.0, 0.5, 1.0, 0.7);
    DrawQuad(-4,-4,4,4);
  
  if ( separate_note_id == i ):
    glColor4f(0,1,0,1);
    DrawRect(-7,-12,7,12,2);
    
  DrawQuad(-1,-1,1,1);
  glPopMatrix();
  glColor4f(0.0, 1.0, 1.0, 0.7);
  # Sparks
  if prefs.use_sparks:
    glPushMatrix();
    glTranslatef(prefs.keys_pos[i][0], prefs.keyp_spark_y_pos ,0);
    glColor4f(0.5, 1, 1.0, 0.7);
    DrawQuad(-1,-1,1,1);
    DrawQuad(-0.5,-sparks_slider_height.value ,0.5,0);
    
    glPopMatrix();

 glPopMatrix();

 glDisable(GL_BLEND);
 glDisable(GL_TEXTURE_2D);
 
 for i in range(len(glwindows)): 
   glwindows[i].draw();

 prefs.keyp_delta = int(settingsWindow_slider1.value);
 prefs.minimal_duration = settingsWindow_slider2.value *0.01;
 prefs.tempo = int(settingsWindow_slider3.value);

 settingsWindow_label1.text = "base octave: " + str(octave) + "\nnotes overlap: " + str(prefs.notes_overlap) + "\nignore minimal duration: " + str(prefs.ignore_minimal_duration);
 #settingsWindow_label2.text = "Sensitivity:"+str(keyp_delta)+"\n\nMinimal note duration (sec):"+format(minimal_duration,'.2f' ) +   "\n\nOutput tempo for midi:" + str(tempo);
 for i in range(len(prefs.keyp_colors)):
     colorBtns[i].color = prefs.keyp_colors[i];

 glPushMatrix();
 glTranslatef(mousex,mousey,0);
 glColor4f(0.2, 0.5, 1, 0.9);
 DrawQuad(-1,-1,1,1);
 glPopMatrix();


def processmidi():
 global frame;
 global width;
 global height;
 global length;
 global fps;

 global notes;
 global notes_db;
 global notes_de;
 global notes_channel;

 global success,image;
 global startframe;
 global separate_note_id;

 print("video " + str(width) + "x" + str(height));

 # create  MIDI object;
 mf = MIDIFile(1,file_format=int(midi_file_format)) # only 1 track;
 track = 0 # the only track;
 time = 0 # start at the beginning;
 

 mf.addTrackName(track, time, prefs.miditrackname);
 mf.addTempo(track, time, prefs.tempo );
 first_note_time=0;
 
 channel_has_note = [ 0 for x in range(16) ];
 for i in range(len(prefs.keyp_colors_channel)):
  mf.addProgramChange(track, prefs.keyp_colors_channel[i], 0, prefs.keyp_colors_channel_prog[i]);
  
 print("starting from frame:" + str(startframe));
 getFrame( startframe );
 notecnt=0
 while success:

  if (frame % 100 == 0):
   glBindTexture(GL_TEXTURE_2D, GlConstants.bgImgGL);
   loadImage(frame)
   #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
   #glTexImage2D(GL_TEXTURE_2D, 0, 3, video_width, video_height, 0, GL_BGR, GL_UNSIGNED_BYTE, image );
   #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
   glEnable(GL_TEXTURE_2D);
   drawframe()

   glColor4f(1.0, 0.5, 1.0, 0.5);
   glDisable(GL_TEXTURE_2D);
   p= frame / float( length );
   DrawQuad(0,height *0.5 -10, p  * width ,height *0.5 +10);
 #  glPopMatrix();
   pygame.display.flip();

#  if (frame % 100 == 0):
   print("processing frame: " + str(frame) + " / " + str(length) + " % " + str( math.trunc(p * 100)));

#  if ( resize == 1 ):
#    image=cv2.resize(image, (width , height));

  # processing white keys;
  for i in range( len(prefs.keys_pos) ):
    pixpos = getkeyp_pixel_pos(prefs.keys_pos[i][0],prefs.keys_pos[i][1]);

    if (pixpos[0] == -1) and (pixpos[1] == -1):
      continue;
    keybgr=image[ pixpos[1], pixpos[0] ];
    key= [ keybgr[2], keybgr[1],keybgr[0] ];

    keybgr=[0,0,0];
    sparkkey=[0,0,0];
    if prefs.use_sparks:
     sh = int(sparks_slider_height.value);
     if sh == 0:
        sh = 1;
     for spark_y_add_pos in range (sh):
       sparkpixpos = getkeyp_pixel_pos(prefs.keys_pos[i][0],prefs.keyp_spark_y_pos - spark_y_add_pos );
       if not ((sparkpixpos[0] == -1) and (sparkpixpos[1] == -1)):
         keybgr   = image[ sparkpixpos[1], sparkpixpos[0] ];
         sparkkey = [ sparkkey[0] + keybgr[2], 
                      sparkkey[1] + keybgr[1],
                      sparkkey[2] + keybgr[0] ];
     sparkkey = [ sparkkey[0] / sh,  sparkkey[1] / sh,sparkkey[2] / sh];
    else:
      sparkkey = [0,0,0];

    note=i;
    if ( note > 120 ): 
      print("skip note > 120");
      continue;


    keypressed=0;
    note_channel=0;

#    deltaclr = abs( int(key[0]) - keyp_colors[0][0] ) +  abs( int(key[1]) - keyp_colors[0][1] ) + abs( int(key[2]) - keyp_colors[0][2] )
    deltaclr = prefs.keyp_delta*prefs.keyp_delta*prefs.keyp_delta;

    deltaid = 0
    if prefs.use_alternate_keys:
      delta = prefs.keyp_delta + prefs.keyp_colors_alternate_sensetivity[i];  
      if ( abs( int(key[0]) - prefs.keyp_colors_alternate[i][0] ) > delta ) and ( abs( int(key[1]) - prefs.keyp_colors_alternate[i][1] ) > delta ) and ( abs( int(key[2]) - prefs.keyp_colors_alternate[i][2] ) > delta ):
        keypressed = 1;
        pressedcolor = prefs.keyp_colors_alternate[i];
    else: 
      for j in range(len(prefs.keyp_colors)):
       if (prefs.keyp_colors[j][0] != 0 ) or ( prefs.keyp_colors[j][1] != 0 ) or ( prefs.keyp_colors[j][2] != 0 ):
        if ( abs( int(key[0]) - prefs.keyp_colors[j][0] ) < prefs.keyp_delta ) and ( abs( int(key[1]) - prefs.keyp_colors[j][1] ) < prefs.keyp_delta ) and ( abs( int(key[2]) - prefs.keyp_colors[j][2] ) < prefs.keyp_delta ):
         delta = abs( int(key[0]) - prefs.keyp_colors[j][0] ) +  abs( int(key[1]) - prefs.keyp_colors[j][1] ) + abs( int(key[2]) - prefs.keyp_colors[j][2] )
         if ( delta < deltaclr ):
          deltaclr = delta;
          deltaid = j;
         keypressed=1;
         if prefs.use_sparks:
           has_spark_delta = ((sparkkey[0] - prefs.keyp_colors[j][0] ) > prefs.keyp_colors_sparks_sensitivity[j] ) or ((sparkkey[1] - prefs.keyp_colors[j][1] ) > prefs.keyp_colors_sparks_sensitivity[j] ) or ((sparkkey[2] - prefs.keyp_colors[j][2] ) > prefs.keyp_colors_sparks_sensitivity[j] );
           #if ( abs( int(sparkkey[0]) - keyp_colors[j][0] ) < keyp_colors_sparks_sensitivity[j] ) and ( abs( int(sparkkey[1]) - keyp_colors[j][1] ) < keyp_colors_sparks_sensitivity[j] ) and ( abs( int(sparkkey[2]) - keyp_colors[j][2] ) < keyp_colors_sparks_sensitivity[j] ):
           if ( not has_spark_delta ):
             keypressed=2;
         
    #
    if ( keypressed != 0 ):
       note_channel=prefs.keyp_colors_channel[ deltaid ];

    if ( prefs.debug == 1 ):
      if (keypressed == 1 ):
        cv2.rectangle(image, (pixx-5,pixy-5), (pixx+5,pixy+5), (128,128,255), -1 );
        cv2.putText(image, str(note_channel), (pixx-5,pixy-10), 0, 0.3, (64,128,255));
#      cv2.rectangle(image, (pixx-5,pixy-5), (pixx+5,pixy+5), (255,0,255));
      cv2.rectangle(image, (pixx-1,pixy-1), (pixx+1,pixy+1), (255,0,255));
#      cv2.putText(image, str(note), (pixx-5,pixy+20), 0, 0.5, (255,0,255));

    # reg pressed key; when keypressed==2 and previous keypressed state is 0 or 2 we should also goes here
    if keypressed==1 or (keypressed==2 and notes[note] != 1):
      # if key is not pressed;
      if ( notes[note] == 0 ):
        if ( debug_keys == 1 ):
          print("note pressed on :" + str( note ));
        notes_db[ note ] = frame;
        if (first_note_time == 0):
          first_note_time = frame / fps;
        notes_channel[ note ] = note_channel;
        if ( separate_note_id != -1 ):
          if ( separate_note_id < note ):
            notes_channel[ note ] = 0
          else:
            notes_channel[ note ] = 1
            

      if prefs.rollcheck and ( note >1):
          notes_tmp[ note ] = keypressed;
          j = note % 12;
          if (j == 1) or ( j ==3 ) or ( j == 6 ) or ( j == 8) or ( j == 10 ):
            if notes_tmp[ note -1] >0:
                keypressed =0;
            
      # always update to last press state
      notes[ note ] = keypressed;

      if ( notes[note] != 0 ) and ( notes_channel[ note ] != note_channel ) and ( prefs.notes_overlap == 1 ):
        # case if one key over other
        time = notes_db[note] / fps;
        duration = ( frame - notes_db[note] ) / fps;
        if (use_snap_notes_to_grid == 1):
          #print ("1 time:", time , "first_note_time:",first_note_time)
          time = snap_to_grid( time - first_note_time , notes_grid_size ) + 1;
          duration = snap_to_grid( duration , notes_grid_size );
          #print ("1 time after:", time , "after before:",duration)
          
          
        ignore = 0
        if ( duration < prefs.minimal_duration ):
          if ( debug_keys == 1 ):
            print(" duration:" + str(duration) + " < minimal_duration:" + str(prefs.minimal_duration));
          duration = prefs.minimal_duration;
          if ( prefs.ignore_minimal_duration == 1 ):
            ignore=1;
            

        if ( debug_keys == 1 ):
          print("keys (one over other), note released :" + str(note) + " de = " + str(notes_de[note]) + "- db =" + str(notes_db[note]));
          print("midi add white keys, note : " +str(note) + " time:" +str(time) + " duration:" + str(duration));

        if ( not ignore ):
          mf.addNote(track, notes_channel[note] , basenote + note, time * prefs.tempo / 60.0 , duration * prefs.tempo / 60.0 , volume );
          channel_has_note[ note_channel ] = 1;
          notecnt+=1;

        notes_db[ note ] = frame;
        notes_channel[ note ] = note_channel;
    else:
      # if key been presed and released: two cases goes here keypressed==0 or (keypressed==2 and previous state is keypressed==1)
      if ( notes[note] != 0):
        notes[ note ] = 0;
        notes_de[ note ] = frame;
        time = notes_db[note] / fps;
        duration = ( notes_de[note] - notes_db[note] ) / fps;
        
        if (use_snap_notes_to_grid):
          if (first_note_time == 0):
            first_note_time = time;
          #print ("2 time:", time , "first_note_time:",first_note_time)
          time = snap_to_grid( time - first_note_time , notes_grid_size ) + 1;
          duration = snap_to_grid( duration , notes_grid_size );
          
        ignore=0
        if ( duration < prefs.minimal_duration ):
          if ( debug_keys == 1 ):
            print(" duration:" + str(duration) + " < minimal_duration:" + str(prefs.minimal_duration));
          duration = prefs.minimal_duration;
          if ( prefs.ignore_minimal_duration == 1 ):
            ignore=1;

        if ( debug_keys == 1 ):
          print("keys, note released :" + str(note ) + " de = " + str(notes_de[note]) + "- db =" + str(notes_db[note]));
          print("midi add white keys, note : " +str(note) + " time:" +str(time) + " duration:" + str(duration));
        if ( not ignore ):
          mf.addNote(track, notes_channel[note] , basenote+ note, time * prefs.tempo / 60.0 , duration * prefs.tempo / 60.0 , volume );

          channel_has_note[ note_channel ] = 1;
          notecnt+=1;
        # coming here when use sparks is true and previous state is keypressed==1. We consider the key is released and then pressed again
        if (keypressed==2):
          notes[ note ] = keypressed;
          notes_db[ note ] = frame;
          notes_channel[ note ] = note_channel;

  xapp=0;
  if ( prefs.debug == 1 ):
    cv2.imwrite("/tmp/frame%d.jpg" % frame, image)  # save frame as JPEG file

#  success,image = vidcap.read();
  getFrame();

  frame += 1;

  if ( frame > endframe ):
    success = False;

  for event in pygame.event.get():
   if event.type == pygame.QUIT:
     success = False;
     pygame.quit();
     quit();
   elif event.type == pygame.KEYDOWN:
    if event.key == pygame.K_SPACE:
     success = False;
    if event.key == pygame.K_ESCAPE:
     running = 0;
     pygame.quit();
     quit();

 print("saved notes: " + str(notecnt));
 
# write midi to disk;
 with open(outputmid, 'wb') as outf:
  mf.writeFile(outf);


def doinit():
  doinitGl()
  loadImage()
  GenFontTexture()


def main():
  global pyfont;
  global mousex, mousey;
  global keyp_colormap_colors_pos;
  global keyp_colormap_pos;
  global keyp_colormap_id;
  global success,image;
  global startframe;
  global endframe;
  global basenote;
  global octave;
  global glwindows;
  global separate_note_id;
  global frame;
  global width,height;
  global screen;
  global lastkeygrabid;
  #global old_spark_color, cur_spark_color;

  running=1;
  keygrab=0;
  keygrabid=-1;
  keygrabaddx=0;
  lastkeygrabid=-1;

  pygame.init();
  pyfont = pygame.font.SysFont('Sans', 20)
  screen = pygame.display.set_mode( (width,height) , DOUBLEBUF|OPENGL);
  pygame.display.set_caption(filepath)

  doinit();
  
  clock = pygame.time.Clock()
  #
  # set start frame;
  vidcap.set(CAP_PROP_POS_FRAMES, frame);

  while running==1:
#    mousex, mousey = pygame.mouse.get_pos();
    drawframe();
    mods = pygame.key.get_mods();
    for event in pygame.event.get():
     if event.type == pygame.QUIT: 
      running = 0;
      pygame.quit();
      quit();
#     elif event.type == pygame.VIDEORESIZE:
#       resize = 1;
#       resize_width = event.w;
#       resize_height = event.h;
#       width = resize_width;
#       height = resize_height;
#       screen = pygame.display.set_mode( (width,height) , DOUBLEBUF|OPENGL|pygame.RESIZABLE);
       
     elif event.type == pygame.KEYUP:
      for wnd in glwindows:
       wnd.update_key_up(event.key);
     elif event.type == pygame.KEYDOWN:
      for wnd in glwindows:
       wnd.update_key_down(event.key);

#      print event.key;
      if event.key == pygame.K_q:
       running = 0;
      if event.key == pygame.K_o:
       prefs.notes_overlap = not prefs.notes_overlap;
      if event.key == pygame.K_i:
       prefs.ignore_minimal_duration = not prefs.ignore_minimal_duration;
   
      if event.key == pygame.K_s:
       if mods & pygame.KMOD_SHIFT:
        startframe = 0;
       else:
        startframe = int(round(vidcap.get(1)));
       print("set start frame = "+ str(startframe));

      if event.key == pygame.K_e:
       if mods & pygame.KMOD_SHIFT:
        endframe = length;
       else:
        endframe = int(round(vidcap.get(1)));
       print("set end frame = "+ str(endframe));

      if event.key == pygame.K_ESCAPE:
        running = 0;
        pygame.quit();
        quit();

      if event.key == pygame.K_F2:
        settings.savesettings(settingsfile)

      if event.key == pygame.K_F3:
        old_resize = prefs.resize;
        loadsettings( settingsfile )
        update_alternate_label()
        if (prefs.resize != old_resize):
          resize_window();
       

      if event.key == pygame.K_r:
        prefs.resize = not prefs.resize;
        resize_window();

      if event.key == pygame.K_RIGHTBRACKET:
        octave += 1;
        if (octave > 7): octave = 7;
        basenote = octave * 12;

      if event.key == pygame.K_LEFTBRACKET:
        octave -= 1;
        if (octave < 0): octave = 0;
        basenote = octave * 12;

      if event.key == pygame.K_UP:
       if mods & pygame.KMOD_ALT:
         prefs.keyp_spark_y_pos -= 1;
         
       else:
         if mods & pygame.KMOD_SHIFT:
          prefs.yoffset_blackkeys -= 1;
         else:
          prefs.yoffset_blackkeys -= 2;
         updatekeys( );

      if event.key == pygame.K_DOWN:
       if mods & pygame.KMOD_ALT:
         prefs.keyp_spark_y_pos += 1;
       else:
         if mods & pygame.KMOD_SHIFT:
          prefs.yoffset_blackkeys += 1;
         else:
          prefs.yoffset_blackkeys += 2;
         updatekeys( );

      if event.key == pygame.K_LEFT:
       if mods & pygame.KMOD_SHIFT:
        prefs.whitekey_width-=0.1;
       else:
        prefs.whitekey_width-=1.0;
       updatekeys( );

      if event.key == pygame.K_RIGHT:
       if mods & pygame.KMOD_SHIFT:
        prefs.whitekey_width+=0.1;
       else:
        prefs.whitekey_width+=1.0;
       updatekeys( );

      if event.key == pygame.K_HOME:
       frame=0;
       glBindTexture(GL_TEXTURE_2D, GlConstants.bgImgGL);
       loadImage(frame);

      if event.key == pygame.K_END:
       frame=length-100;
       glBindTexture(GL_TEXTURE_2D, GlConstants.bgImgGL);
       loadImage(frame);

      if event.key == pygame.K_0:
        if mods & pygame.KMOD_CTRL and keyp_colormap_id != -1:
         prefs.keyp_colors[keyp_colormap_id][0] = 0;
         prefs.keyp_colors[keyp_colormap_id][1] = 0;
         prefs.keyp_colors[keyp_colormap_id][2] = 0;

      if event.key == pygame.K_PAGEUP:
       if mods & pygame.KMOD_SHIFT:
        frame+=1;
       else:
        frame+=100;
       if (frame > length *0.99):
        frame=math.trunc(length *0.99);
       #for i in range( len(cur_spark_color)):
       #  old_spark_color[i] = cur_spark_color[i];
         
       glBindTexture(GL_TEXTURE_2D, GlConstants.bgImgGL);
       loadImage(frame);

      if event.key == pygame.K_PAGEDOWN:
       if mods & pygame.KMOD_SHIFT:
        frame-=1;
       else:
        frame-=100;
       if (frame < 1):
        frame=1;
       #for i in range( len(cur_spark_color)):
       #  old_spark_color[i] = cur_spark_color[i];
       glBindTexture(GL_TEXTURE_2D, GlConstants.bgImgGL);
       loadImage(frame);

      if event.key == pygame.K_p:
        size=5;
        separate_note_id=-1;
        for i in range( len( prefs.keys_pos) ):
         if (abs( mousex - (prefs.keys_pos[i][0] + prefs.xoffset_whitekeys) )< size) and (abs( mousey - (prefs.keys_pos[i][1] + prefs.yoffset_whitekeys) )< size):
           separate_note_id=i;
           pass
     #
     elif event.type == pygame.MOUSEBUTTONUP:
      for wnd in glwindows:
        wnd.update_mouse_up(mousex,mousey,event.button)
      #
      if ( event.button == 1 ):
        keygrab = 0;
        keygrabid = -1;
      if ( event.button == 3 ):
        keygrab = 0;
     #
     elif event.type == pygame.MOUSEBUTTONDOWN:
      for wnd in glwindows:
        wnd.update_mouse_down(mousex,mousey,event.button);

#      print event.button;
      if ( event.button == 4 ):
        prefs.whitekey_width+=0.05;
#        print "whitekey_width="+str(whitekey_width);
        updatekeys( );
#        scale+=0.1;
      if ( event.button == 5 ):
        prefs.whitekey_width-=0.05;
#        print "whitekey_width="+str(whitekey_width);
        updatekeys( );
#
      if ( event.button == 1 ):
        if mods & pygame.KMOD_CTRL and keyp_colormap_id != -1:
         pixx = int(mousex);
         pixy = int(mousey);
         if not (( pixx >= width ) or ( pixy >= height ) or ( pixx < 0 ) or ( pixy < 0 )):
           if ( prefs.resize == 1 ):
             pixx= int(round( pixx * ( video_width / float(prefs.resize_width) )))
             pixy= int(round( pixy * ( video_height / float(prefs.resize_height) )))
             if ( pixx > video_width -1 ): pixx = video_width-1;
             if ( pixy > video_height-1 ): pixy = video_height-1;
             print("original mouse x:"+str(mousex) + "x" +str(mousey) + " mapped :" +str(pixx) +"x"+str(pixy));

           keybgr=image[pixy,pixx];
           prefs.keyp_colors[keyp_colormap_id][0] = keybgr[2];
           prefs.keyp_colors[keyp_colormap_id][1] = keybgr[1];
           prefs.keyp_colors[keyp_colormap_id][2] = keybgr[0];
        else:
#        if not (mods & pygame.KMOD_CTRL):
         if not colorWindow.active:
            keyp_colormap_id = -1;
         #keyp_colormap_id = -1;
         pass
        #
        size=5;
        if (mods & pygame.KMOD_CTRL):
          lastkeygrabid=-1;
            
        for i in range( len( prefs.keys_pos) ):
         if (abs( mousex - (prefs.keys_pos[i][0] + prefs.xoffset_whitekeys) )< size) and (abs( mousey - (prefs.keys_pos[i][1] + prefs.yoffset_whitekeys) )< size):
          keygrab=1;
          if not ( mods & pygame.KMOD_CTRL ):
            keygrabid=i;
          lastkeygrabid=i;
          extra_slider1.setvalue( prefs.keyp_colors_alternate_sensetivity[i] );
          print("ok click found on : "+str(keygrabid));
          break;
        pass;
#      if ( event.button == 2 ):
#        lastkeygrabid=-1;
      if ( event.button == 3 ):
        keygrab = 2;
        size=5;
        print("x offset " + str(prefs.xoffset_whitekeys) + " y offset: " +str(prefs.yoffset_whitekeys));
        keygrabaddx=0
        for i in range( len( prefs.keys_pos) ):
         if (abs( mousex - (prefs.keys_pos[i][0] + prefs.xoffset_whitekeys) )< size) and (abs( mousey - (prefs.keys_pos[i][1] + prefs.yoffset_whitekeys) )< size):
          keygrab=2;
          keygrabaddx=prefs.keys_pos[i][0];
          print("ok click found on : "+str(keygrabid));
          break;

    if ( keygrab == 1) and ( keygrabid >-1 ):
#     print "moving keyid = " + str(keygrabid);
     prefs.keys_pos[ keygrabid ][0] = mousex - prefs.xoffset_whitekeys;
     prefs.keys_pos[ keygrabid ][1] = mousey - prefs.yoffset_whitekeys;
    if ( keygrab == 2):
#      print "moving offsets : "+ str(mousex) + " x " + str(mousey);
      prefs.xoffset_whitekeys = mousex - keygrabaddx;
      prefs.yoffset_whitekeys = mousey;
    for wnd in glwindows:
      wnd.update_mouse_move(mousex,mousey)

    pygame.display.flip();
    #framerate();
    #limit fps to 60 and get the frame time in milliseconds
    ms = clock.tick(60)
    

main();
helpWindow.hidden=1;
frame=startframe;
processmidi();

print ("done...");

