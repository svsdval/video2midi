#!/usr/bin/env python

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

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0

from os.path import expanduser


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
if not os.path.exists( filepath ):
  print "file not exists [" + filepath +"]";
  sys.exit( 0 ) ;

print "open file " + filepath;
vidcap = cv2.VideoCapture( filepath );

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

resize_width=1280;
resize_height=720;

# set start frame;
def getFrame( framenum =-1 ):
  global resize;
  global image;
  global success;
  global width;
  global height;
  global convertCvtColor;

  if ( framenum != -1 ):
    #vidcap.set(cv2.CAP_PROP_POS_FRAMES, int(framenum) );
    # problems with mpeg formats ...
    oldframenum = int(round(vidcap.get(1)));
    frametime =  framenum * 1000.0 / fps;
    print "go to frame time :" + str(frametime);
    success = vidcap.set(cv2.CAP_PROP_POS_MSEC, frametime);
    if not success:
      print "Cannot set frame position from video file at " + str(framenum)
      success = vidcap.set(cv2.CAP_PROP_POS_FRAMES, int(oldframenum) );
    curframe = vidcap.get(cv2.CAP_PROP_POS_FRAMES);
    if (curframe != framenum ):
     print "OpenCV bug, Requesting frame " + str(curFrame) + " but get position on " +str(curframe);

  if ( convertCvtColor == 1 ):
    cv2.cvtColor(image,cv2.COLOR_BGR2RGB)

  success,image = vidcap.read();
#  if ( resize == 1 ):
#    image = cv2.resize(image, (resize_width , resize_height));
#    print "resize to "+str(resize_width) + "x"+ str(resize_height);
  pass

getFrame();

debug = 0;
debug_keys = 0;

length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT));
video_width  = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH));
video_height = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT));
fps    = float(vidcap.get(cv2.CAP_PROP_FPS));

width = video_width;
height = video_height;


startframe = 0;
endframe = length;

#;
print "video " + str(width) + "x" + str(height) +" fps: " + str(fps);

# add some notes;
channel = 0;
volume = 100;
octave = 3;
basenote = octave * 12;


notes=[];
notes_db=[];
notes_de=[];
notes_channel=[];

keys_pos=[];

keyp_colors = [
#L.GREEN         D.GREEN
[166,250,103], [ 58,146,  0],
#L.BLUE          D.BLUE
[102,185,207], [  8,113,174],
#L.YELLOW        D.YELLOW
[255,255,85 ], [254,210,  0],
#L.ORANGE        D.ORANGE
[255,212,85 ], [255,138,  0],
#L.RED           D.RED
[253,125,114], [255, 37,  9],
#EMPTY 
[0  ,  0,  0], [  0,  0,  0]
# .....
];

keyp_delta = 90; # sensitivity
#
keyp_colors_channel = [ 0,0, 1,1, 2,2, 3,3, 4,4, 5,5 ]; # MIDI channel per color
keyp_colors_channel_prog = [ 0,0, 0,0, 0,0, 0,0, 0,0, 0,0 ]; # MIDI program ID per channel

#
minimal_duration = 0.6;
bgImgGL=-1;
drawhelp=1;

experimental = 0;


keyp_colormap_colors_pos=[];
keyp_colormap_pos=[32,16];
keyp_colormap_id=-1;

keyp_delta_slider_pos=[132,16];
keyp_delta_slider_size=[120,20];

separate_note_id=-1;

miditrackname="Sample Track";
#

#cfg
home = expanduser("~")
inifile = os.path.join( home, '.v2m.ini');
if os.path.exists( 'v2m.ini' ):
  inifile="v2m.ini";
  print "local config file exists."


if os.path.exists( inifile ):
  print "Loading config from:"+inifile;
  config = ConfigParser()
  config.read( inifile )
  miditrackname = config.get('options', 'midi_track_name')
  debug = config.getboolean('options', 'debug')
  experimental = config.getboolean('options', 'experimental')
  resize = config.getboolean('options', 'resize')
  resize_width = config.getint('options', 'resize_width')
  resize_height = config.getint('options', 'resize_height')
  minimal_duration = config.getfloat('options', 'minimal_note_duration')
  clr_chnls = config.get('options', 'color_channel_accordance')
  clr_chnls_prog = config.get('options', 'channel_prog_accordance')

  if ( clr_chnls != "" ):
    keyp_colors_channel = map(int, clr_chnls.split(","))
    print "readed color = channel", keyp_colors_channel;

  if ( clr_chnls_prog != "" ):
    keyp_colors_channel_prog = map(int, clr_chnls_prog.split(","))
    print "readed color channel = prog ", keyp_colors_channel_prog;

if ( resize == 1 ):
  width = resize_width;
  height = resize_height;


for i in range(127):
  notes.append(0);
  notes_db.append(0);
  notes_de.append(0);
  notes_channel.append(0);
#;


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

def update_colormap():
 global keyp_colormap_colors_pos;
 for i in range( len( keyp_colors ) ):
  keyp_colormap_colors_pos.append ([ (i % 2) * 32,  ( i // 2 ) * 20  ]);


updatekeys( 1 );
update_colormap();

def loadImage(idframe=130):
  global image;
  getFrame(idframe);

  print "load image from video " + str(width) + "x" + str(height) + " frame: "+ str(idframe) ;
  glPixelStorei(GL_UNPACK_ALIGNMENT,1)

  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
  glTexImage2D(GL_TEXTURE_2D, 0, 3, video_width, video_height, 0, GL_BGR, GL_UNSIGNED_BYTE, image );
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

def DrawRect(x,y,x2,y2,w=1):
   glLineWidth(w);
   glBegin(GL_LINE_LOOP);
   glVertex2f(x, y);
   glVertex2f(x2, y);
   glVertex2f(x2, y2);
   glVertex2f(x, y2);
   glEnd();

def DrawTriangle(x,y, s,r=0):
  glBegin(GL_TRIANGLES);
  if ( r == 0 ):
   glVertex2f(x , y-s);
   glVertex2f(x + s, y-s);
   glVertex2f(x + s*0.5, y);
  else:
   glVertex2f(x , y);
   glVertex2f(x + s,y);
   glVertex2f(x + s*0.5, y-s);
  pass
  glEnd();

def drawText(position, textString, size=24):
  font = pygame.font.Font (None, size)
  textSurface = font.render(textString, True, (255,255,255,255), (0,0,0,255))
  textData = pygame.image.tostring(textSurface, "RGBA", True)
  glRasterPos3d(*position)
  glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

class GLWindow:
  def __init__(self,x,y,w,h,title):
    self.w = w;
    self.h = h;
    self.x = x;
    self.y = y;
    self.borderwidth=2;
    self.title = title;
    self.titleheight = 25;
    self.titlewidth = self.w;
    self.clientrect=[0,0,0,0];
    self.mousegrab = 0;
    self.mousepos = [0,0];
    self.mouseclickpos = [0,0];
    self.hidden = 0;
      
  def draw(self):
    self.update();
    glDisable(GL_TEXTURE_2D);
    glEnable(GL_BLEND);
    glPushMatrix()
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glColor4f(0.2, 0.2, 0.2, 0.9);
    DrawQuad(self.x,self.y,self.x+self.w,self.y+self.titleheight);
    if ( not self.hidden ):
      glColor4f(0.1, 0.1, 0.1, 0.9);
      DrawQuad(self.x,self.y+self.titleheight,self.x+self.titlewidth,self.y+self.h-self.titleheight);
    glColor4f(1.0, 1.0, 1.0, 0.9);
    DrawTriangle(self.x+self.titlewidth-16,self.y+18,10, self.hidden);

    glColor4f(0.0, 0.0, 0.0, 0.9);
    DrawRect(self.x,self.y,self.x+self.w,self.y+self.titleheight);
    if ( not self.hidden ):
      glColor4f(0.1, 0.1, 0.1, 0.9);
      DrawRect(self.x,self.y+self.titleheight,self.x+self.w,self.y+self.h-self.titleheight);
      
    glBlendFunc(GL_ONE, GL_SRC_ALPHA);
    drawText( (self.x+4,self.y+self.titleheight-2,1), self.title );

    glPopMatrix();
    glDisable(GL_BLEND);
    pass;
    
  def update(self):
    self.titlewidth = self.w;

    self.clientrect[0] = self.x + self.borderwidth;
    self.clientrect[1] = self.y + self.borderwidth + self.titleheight;
    self.clientrect[2] = self.x + self.w - self.borderwidth;
    self.clientrect[3] = self.y + self.h - self.titleheight - self.borderwidth;
    pass;
    
  def getclientrect(self):
    self.update()
    return self.clientrect;
    pass;
  def update_mouse_move(self, mpx, mpy ):
    self.mousepos[0] = mpx;
    self.mousepos[1] = mpy;

    if (self.mousegrab == 1):
      self.x = mpx - self.mouseclickpos[0];
      self.y = mpy - self.mouseclickpos[1];
    pass;
  def update_mouse_down(self,mpx,mpy,btn):
    self.mouseclickpos[0] = mpx - self.x;
    self.mouseclickpos[1] = mpy - self.y;
    
    if (( mpx > self.x ) and ( mpx < self.x + self.titlewidth ) and
        ( mpy > self.y ) and ( mpy < self.y + self.titleheight )):
        self.mousegrab = 1;
    self.update();
    pass;
  def update_mouse_up(self,mpx,mpy,btn):
    self.mousegrab = 0;
    self.mouseclickpos[0] = mpx - self.x;
    self.mouseclickpos[1] = mpy - self.y;
    pass;
  def update_key_down(self, keycode ):
    mpx = self.mousepos[0];
    mpy = self.mousepos[1];
    
    if (( mpx > self.x ) and ( mpx < self.x + self.titlewidth ) and
        ( mpy > self.y ) and ( mpy < self.y + self.titleheight )):
      if keycode == pygame.K_h:
        self.hidden = not self.hidden;
      
    pass;
  def update_key_up(self, keycode ):
    pass;
      

colorWindow = GLWindow(keyp_colormap_pos[0],keyp_colormap_pos[1],100, ( (len(keyp_colors) // 2)+2 ) * 24, "color map")
sensWindow = GLWindow(keyp_delta_slider_pos[0], keyp_delta_slider_pos[1],170, 130, "sensitivity & octave");
helpWindow = GLWindow(303,16,750,460, "help");

glwindows = [];
glwindows.append(colorWindow);
glwindows.append(sensWindow);
glwindows.append(helpWindow);

    

def drawframe():
 global xoffset_whitekeys;
 global yoffset_whitekeys;
 global yoffset_blackkeys;
 global whitekey_width;
 global bgImgGL;
 global pyfont;
 global helptext;
 global mousex, mousey;
 global keyp_colormap_colors_pos;
 global keyp_colormap_pos;
 global keyp_colormap_id;
 global keyp_delta_slider_pos;
 global keyp_delta_slider_size;
 global drawhelp;
 global resize;
 global octave;

 scale=1.0;
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


 glEnable(GL_BLEND);
 glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

 glColor4f(1.0, 0.5, 1.0, 0.5);
 glPushMatrix();
 glTranslatef(xoffset_whitekeys,yoffset_whitekeys,0);
 glDisable(GL_TEXTURE_2D);
 for i in range( len( keys_pos) ):

  pixx=int(xoffset_whitekeys + keys_pos[i][0]);
  pixy=int(yoffset_whitekeys + keys_pos[i][1]);

  if ( pixx >= width ) or ( pixy >= height ) or ( pixx < 0 ) or ( pixy < 0 ): continue;

  if ( resize == 1 ):
    pixx= int(round( pixx * ( video_width / float(resize_width) )))
    pixy= int(round( pixy * ( video_height / float(resize_height) )))
    if ( pixx > video_width -1 ): pixx = video_width-1;
    if ( pixy > video_height-1 ): pixy= video_height-1;

  keybgr=image[pixy,pixx];
  key= [ keybgr[2], keybgr[1],keybgr[0] ];

  note=i;
  if ( note > 120 ): 
    print "skip note > 120";
    continue;
  keypressed=0;

  for keyc in keyp_colors:
   if (keyc[0] != 0 ) and (keyc[1] != 0 ) and (keyc[2] != 0 ) :
     if ( abs( int(key[0]) - keyc[0] ) < keyp_delta ) and ( abs( int(key[1]) - keyc[1] ) < keyp_delta ) and ( abs( int(key[2]) - keyc[2] ) < keyp_delta ):
      keypressed=1;

  glPushMatrix();
  glTranslatef(keys_pos[i][0],keys_pos[i][1],0);

  if ( keypressed == 1 ):
    glColor4f(0,0,0,1);
    DrawRect(-7,-9,7,9,1);
    glColor4f(1.0, 0.5, 1.0, 0.9);
    DrawQuad(-5,-7,5,7);
  else:
    glColor4f(0,0,0,1);
    DrawRect(-7,-7,7,7,1);
    glColor4f(0.5, 1, 1.0, 0.7);
    DrawQuad(-5,-5,5,5);
  if ( separate_note_id == i ): 
    glColor4f(0,1,0,1);
    DrawRect(-7,-12,7,12,2);
  DrawQuad(-1,-1,1,1);
  glPopMatrix();
  glColor4f(0.0, 1.0, 1.0, 0.7);
 glPopMatrix();

 glDisable(GL_BLEND);
 glDisable(GL_TEXTURE_2D);

 helpWindow.draw(); 
  
 if ( not helpWindow.hidden ):
   rect = helpWindow.getclientrect();

 #if (drawhelp == 1):
   glEnable(GL_BLEND);
   glBlendFunc(GL_ONE, GL_SRC_ALPHA);
   glDisable(GL_TEXTURE_2D);
   glPushMatrix()
   glTranslatef(rect[0],rect[1],0);
   spaceh=25;
   glColor4f(1.0, 1.0, 1, 0.0);
   glTranslatef(0,spaceh,0);
   drawText( (0,0,1), "h - on window title, show/hide the window");
   glTranslatef(0,spaceh,0);
   drawText( (0,0,1), "q - begin to recreate midi");
   glTranslatef(0,spaceh,0);
   drawText( (0,0,1), "s - set start frame, (mods : shift, set processing start frame to the beginning)");
   glTranslatef(0,spaceh,0);
   drawText( (0,0,1), "e - set end frame, (mods : shift, set processing end frame to the ending)");
   glTranslatef(0,spaceh,0);
   drawText( (0,0,1), "p - if key is set, force separate to 2 channels (on single color video)");
   glTranslatef(0,spaceh,0);
   drawText( (0,0,1), "Mouse wheel - keys adjustment");
   glTranslatef(0,spaceh,0);
   drawText( (0,0,1), "Left mouse button - dragging the selected key / select color from the color map");
   glTranslatef(0,spaceh,0);
   drawText( (0,0,1), "CTRL + Left mouse button - update selected color in the color map");
   glTranslatef(0,spaceh,0);
   drawText( (0,0,1), "CTRL + 0 - disable selected color in the color map");
   glTranslatef(0,spaceh,0);
   drawText( (0,0,1), "Right mouse button - dragging all keys, if the key is selected, the transfer is carried out relative to it.");
   glTranslatef(0,spaceh,0);
   drawText( (0,0,1), "Arrows - keys adjustment (mods : shift)");
   glTranslatef(0,spaceh,0);
   drawText( (0,0,1), "PageUp/PageDown - scrolling video (mods : shift)");
   glTranslatef(0,spaceh,0);
   drawText( (0,0,1), "Home/End - go to the beginning or end of the video");
   glTranslatef(0,spaceh,0);
   drawText( (0,0,1), "[ / ] - change base octave");
   glTranslatef(0,spaceh,0);
   drawText( (0,0,1), "Escape - quit");
   glTranslatef(0,spaceh,0);
   drawText( (0,0,1), "Space - abort re-creation and save midi file to disk");
   glPopMatrix()

 #for wnd in glwindows:
 colorWindow.draw(); 
  
 if ( not colorWindow.hidden ):
  rect = colorWindow.getclientrect();
  glPushMatrix();
  keyp_colormap_pos[0] = rect[0]+26;
  keyp_colormap_pos[1] = rect[1]+20;
  glTranslatef( keyp_colormap_pos[0] , keyp_colormap_pos[1] ,0);
  glBlendFunc(GL_ONE, GL_SRC_ALPHA);
  #drawText( (-10,-10,1), "color map");
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
  for i in range( len( keyp_colormap_colors_pos ) ):
   glPushMatrix();
   glTranslatef(keyp_colormap_colors_pos[i][0],keyp_colormap_colors_pos[i][1],0);
   if ( keyp_colormap_id == i ):
    glColor4f(1.0, 1.0, 1.0, 1);
    DrawQuad(-9,-9,9,9);
   else:
    glColor4f(0.5, 0.5, 0.5, 1);
    DrawQuad(-8,-8,8,8);
 
   glColor4f(0.0, 0.0, 0.0, 1);
   DrawQuad(-7,-7,7,7);
   glColor4ub(keyp_colors[i][0], keyp_colors[i][1], keyp_colors[i][2], 255);
   DrawQuad(-5,-5,5,5);
   glPopMatrix();
   glColor4f(0.0, 1.0, 1.0, 0.5);
  glPopMatrix();
  glEnable(GL_BLEND);
 sensWindow.draw();
 if ( not sensWindow.hidden ):
  rect = sensWindow.getclientrect();
  keyp_delta_slider_pos[0] = rect[0]+10;
  keyp_delta_slider_pos[1] = rect[1]+10;
  glPushMatrix();
  glTranslatef( keyp_delta_slider_pos[0] , keyp_delta_slider_pos[1] ,0);
  glBlendFunc(GL_ONE, GL_SRC_ALPHA);
  drawText( (keyp_delta_slider_size[0]+10 ,20,1), str(keyp_delta));
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
  glColor4f(1.0, 1.0, 1.0, 1);
  DrawQuad(0,0,keyp_delta_slider_size[0]+2,keyp_delta_slider_size[1]+2);
  glColor4f(0.5, 0.5, 1.0, 1);
  DrawQuad(2,2,keyp_delta_slider_size[0] * ( keyp_delta / float(keyp_delta_slider_size[0])), keyp_delta_slider_size[1] );
  glPopMatrix();
  glEnable(GL_BLEND);

  glPushMatrix();
  glTranslatef( keyp_delta_slider_pos[0] , keyp_delta_slider_pos[1]+50 ,0);
  glBlendFunc(GL_ONE, GL_SRC_ALPHA);
  glColor4f(1.0, 1.0, 1, 0.0);
  drawText( (0,0,1), "base octave:" + str(octave));
  glPopMatrix();
  glEnable(GL_BLEND);


 glPushMatrix();
 glTranslatef(mousex,mousey,0);
 glColor4f(0.2, 0.5, 1, 0.9);
 DrawQuad(-1,-1,1,1);
 glPopMatrix();


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
 global keyp_colors_channel_prog;

 global success,image;
 global startframe;
 global experimental;
 global resize;
 global miditrackname;
 global separate_note_id;

 print "video " + str(width) + "x" + str(height);

 # create  MIDI object;
 mf = MIDIFile(1) # only 1 track;
 track = 0 # the only track;
 time = 0 # start at the beginning;

 mf.addTrackName(track, time, miditrackname);
 mf.addTempo(track, time, 60 );
 for i in range(len(keyp_colors_channel)):
  mf.addProgramChange(track, keyp_colors_channel[i], time, keyp_colors_channel_prog[i]);

 print "starting from frame:" + str(startframe);
 getFrame( startframe );
 notecnt=0

 while success:

  if (frame % 100 == 0):
   glBindTexture(GL_TEXTURE_2D, bgImgGL);
   glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
   glTexImage2D(GL_TEXTURE_2D, 0, 3, video_width, video_height, 0, GL_BGR, GL_UNSIGNED_BYTE, image );
   glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
   glEnable(GL_TEXTURE_2D);
   drawframe()

   glColor4f(1.0, 0.5, 1.0, 0.5);
   glDisable(GL_TEXTURE_2D);
   p= frame / float( length );
   DrawQuad(0,height *0.5 -10, p  * width ,height *0.5 +10);
 #  glPopMatrix();
   pygame.display.flip();

#  if (frame % 100 == 0):
   print "processing frame: " + str(frame) + " / " + str(length) + " % " + str( math.trunc(p * 100));

#  if ( resize == 1 ):
#    image=cv2.resize(image, (width , height));

  # processing white keys;
  for i in range( len(keys_pos) ):
    pixx=int(xoffset_whitekeys + keys_pos[i][0]);
    pixy=int(yoffset_whitekeys + keys_pos[i][1]);

    if ( pixx >= width ) or ( pixy >= height ) or ( pixx < 0 ) or ( pixy < 0 ): continue;
    if ( resize == 1 ):
      pixxo=pixx;
      pixyo=pixy;

      pixx= int(round( pixx * ( video_width / float(resize_width) )))
      pixy= int(round( pixy * ( video_height / float(resize_height) )))
      if ( pixx > video_width -1 ): pixx = video_width-1;
      if ( pixy > video_height-1 ): pixy= video_height-1;
#      print "original x:"+str(pixxo) + "x" +str(pixyo) + " mapped :" +str(pixx) +"x"+str(pixy);

    keybgr=image[pixy,pixx];
    key= [ keybgr[2], keybgr[1],keybgr[0] ];

    note=i;
    if ( note > 120 ): 
      print "skip note > 120";
      continue;


    keypressed=0;
    note_channel=0;

    deltaclr = abs( int(key[0]) - keyp_colors[0][0] ) +  abs( int(key[1]) - keyp_colors[0][1] ) + abs( int(key[2]) - keyp_colors[0][2] )
    deltaid = 0
    for j in range(len(keyp_colors)):
     if (keyp_colors[j][0] != 0 ) and ( keyp_colors[j][1] != 0 ) and ( keyp_colors[j][2] != 0 ):
      if ( abs( int(key[0]) - keyp_colors[j][0] ) < keyp_delta ) and ( abs( int(key[1]) - keyp_colors[j][1] ) < keyp_delta ) and ( abs( int(key[2]) - keyp_colors[j][2] ) < keyp_delta ):
       delta = abs( int(key[0]) - keyp_colors[j][0] ) +  abs( int(key[1]) - keyp_colors[j][1] ) + abs( int(key[2]) - keyp_colors[j][2] )
       if ( delta < deltaclr ):
        deltaclr = delta;
        deltaid = j;
       keypressed=1;

    if ( keypressed==1 ):
       note_channel=keyp_colors_channel[ deltaid ];

    if ( debug == 1 ):
      if (keypressed == 1 ):
        cv2.rectangle(image, (pixx-5,pixy-5), (pixx+5,pixy+5), (128,128,255), -1 );
        cv2.putText(image, str(note_channel), (pixx-5,pixy-10), 0, 0.3, (64,128,255));
#      cv2.rectangle(image, (pixx-5,pixy-5), (pixx+5,pixy+5), (255,0,255));
      cv2.rectangle(image, (pixx-1,pixy-1), (pixx+1,pixy+1), (255,0,255));
#      cv2.putText(image, str(note), (pixx-5,pixy+20), 0, 0.5, (255,0,255));

    # reg pressed key;
    if keypressed==1:
      # if key is not pressed;
      if ( notes[note] == 0 ):
        if ( debug_keys == 1 ):
          print "white keys, note pressed on :" + str( note );
        notes[ note ] = 1;
        notes_db[ note ] = frame;
        notes_channel[ note ] = note_channel;
        if ( separate_note_id != -1 ):
          if ( separate_note_id < note ):
            notes_channel[ note ] = 0
          else:
            notes_channel[ note ] = 1
        
      if ( notes[note] == 1 ) and ( notes_channel[ note ] != note_channel ) and ( experimental == 1 ):
        # case if one key over other
        time = notes_db[note] / fps;
        duration = ( frame - notes_db[note] ) / fps;
        if ( duration < minimal_duration ): duration = minimal_duration;

        if ( debug_keys == 1 ):
          print "keys (one over other), note released :" + str(note) + " de = " + str(notes_de[note]) + "- db =" + str(notes_db[note]);
          print "midi add white keys, note : " +str(note) + " time:" +str(time) + " duration:" + str(duration);
                 
        mf.addNote(track, notes_channel[note] , basenote+ note, time , duration , volume );
        notecnt+=1;

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
        notecnt+=1;

  xapp=0;
  if ( debug == 1 ):
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

 print "saved notes: " + str(notecnt);
# write midi to disk;
 with open(outputmid, 'wb') as outf:
  mf.writeFile(outf);



def main():
  global xoffset_whitekeys;
  global yoffset_whitekeys;
  global yoffset_blackkeys;
  global whitekey_width;
  global bgImgGL;
  global pyfont;
  global mousex, mousey;
  global keyp_colormap_colors_pos;
  global keyp_colormap_pos;
  global keyp_colormap_id;
  global success,image;
  global keyp_colors;
  global keyp_delta;
  global keyp_delta_slider_pos;
  global keyp_delta_slider_size;
  global drawhelp;
  global startframe;
  global endframe;
  global basenote;
  global octave;
  global glwindows;
  global separate_note_id;
  running=1;
  keygrab=0;
  keygrabid=-1;
  keygrabaddx=0;

  pygame.init();
  pyfont = pygame.font.SysFont('Sans', 20)
  display = (width,height);
  screen = pygame.display.set_mode(display, DOUBLEBUF|OPENGL);

  glPixelStorei(GL_UNPACK_ALIGNMENT,1)
  bgImgGL = glGenTextures(1);
  glBindTexture(GL_TEXTURE_2D, bgImgGL);
  loadImage();
  #
  frame= 0;
  # set start frame;
  vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame);

  display = (width,height);
  pygame.display.set_mode(display, DOUBLEBUF|OPENGL);
  while running==1:
#    mousex, mousey = pygame.mouse.get_pos();
    drawframe();
    mods = pygame.key.get_mods();
    for event in pygame.event.get():
     if event.type == pygame.QUIT: 
      running = 0;
      pygame.quit();
      quit();
     elif event.type == pygame.KEYUP:
      for wnd in glwindows:
       wnd.update_key_up(event.key);
     elif event.type == pygame.KEYDOWN:
      for wnd in glwindows:
       wnd.update_key_down(event.key);
         
#      print event.key;
      if event.key == pygame.K_q:
       running = 0;
      if event.key == pygame.K_s:
       if mods & pygame.KMOD_SHIFT:
        startframe = 0;
       else:
        startframe = int(round(vidcap.get(1)));
       print "set start frame = "+ str(startframe);

      if event.key == pygame.K_e:
       if mods & pygame.KMOD_SHIFT:
        endframe = length;
       else:
        endframe = int(round(vidcap.get(1)));
       print "set end frame = "+ str(endframe);
      if event.key == pygame.K_h:
       drawhelp = not drawhelp;

      if event.key == pygame.K_ESCAPE:
       running = 0;
       pygame.quit();
       quit();

      if event.key == pygame.K_RIGHTBRACKET:
        octave += 1;
        if (octave > 7): octave = 7;
        basenote = octave * 12;

      if event.key == pygame.K_LEFTBRACKET:
        octave -= 1;
        if (octave < 0): octave = 0;
        basenote = octave * 12;

      if event.key == pygame.K_UP:
       if mods & pygame.KMOD_SHIFT:
        yoffset_blackkeys -= 1;
       else:
        yoffset_blackkeys -= 2;
       updatekeys( );
      if event.key == pygame.K_DOWN:
       if mods & pygame.KMOD_SHIFT:
        yoffset_blackkeys += 1;
       else:
        yoffset_blackkeys += 2;
       updatekeys( );
      if event.key == pygame.K_LEFT:
       if mods & pygame.KMOD_SHIFT:
        whitekey_width-=0.1;
       else:
        whitekey_width-=1.0;
       updatekeys( );
      if event.key == pygame.K_RIGHT:
       if mods & pygame.KMOD_SHIFT:
        whitekey_width+=0.1;
       else:
        whitekey_width+=1.0;
       updatekeys( );

      if event.key == pygame.K_HOME:
       frame=0;
       glBindTexture(GL_TEXTURE_2D, bgImgGL);
       loadImage(frame);

      if event.key == pygame.K_END:
       frame=length-100;
       glBindTexture(GL_TEXTURE_2D, bgImgGL);
       loadImage(frame);

      if event.key == pygame.K_0:
        if mods & pygame.KMOD_CTRL and keyp_colormap_id != -1:
         keyp_colors[keyp_colormap_id][0] = 0;
         keyp_colors[keyp_colormap_id][1] = 0;
         keyp_colors[keyp_colormap_id][2] = 0;

      if event.key == pygame.K_PAGEUP:
       if mods & pygame.KMOD_SHIFT:
        frame+=1;
       else:
        frame+=100;
       if (frame > length *0.99):
        frame=math.trunc(length *0.99);

       glBindTexture(GL_TEXTURE_2D, bgImgGL);
       loadImage(frame);
      if event.key == pygame.K_PAGEDOWN:
       if mods & pygame.KMOD_SHIFT:
        frame-=1;
       else:
        frame-=100;
       if (frame < 1):
        frame=1;
       glBindTexture(GL_TEXTURE_2D, bgImgGL);
       loadImage(frame);

      if event.key == pygame.K_p:
        size=5;
        separate_note_id=-1;
        for i in range( len( keys_pos) ):
         if (abs( mousex - (keys_pos[i][0] + xoffset_whitekeys) )< size) and (abs( mousey - (keys_pos[i][1] + yoffset_whitekeys) )< size):
           separate_note_id=i;
           pass


     elif event.type == pygame.MOUSEBUTTONUP:
      for wnd in glwindows:
        wnd.update_mouse_up(mousex,mousey,event.button)
      if ( event.button == 1 ):
        keygrab = 0;
        keygrabid = -1;
      if ( event.button == 3 ):
        keygrab = 0;

     elif event.type == pygame.MOUSEBUTTONDOWN:
      for wnd in glwindows:
        wnd.update_mouse_down(mousex,mousey,event.button);
         
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
#      if (scale >2): scale=2;
#      if (scale <1): scale=1;

      if ( event.button == 1 ):
        if mods & pygame.KMOD_CTRL and keyp_colormap_id != -1:
         pixx = int(mousex);
         pixy = int(mousey);
         if not (( pixx >= width ) or ( pixy >= height ) or ( pixx < 0 ) or ( pixy < 0 )):
           if ( resize == 1 ):
             pixx= int(round( pixx * ( video_width / float(resize_width) )))
             pixy= int(round( pixy * ( video_height / float(resize_height) )))
             if ( pixx > video_width -1 ): pixx = video_width-1;
             if ( pixy > video_height-1 ): pixy= video_height-1;
             print "original mouse x:"+str(mousex) + "x" +str(mousey) + " mapped :" +str(pixx) +"x"+str(pixy);

           keybgr=image[pixy,pixx];
           keyp_colors[keyp_colormap_id][0] = keybgr[2];
           keyp_colors[keyp_colormap_id][1] = keybgr[1];
           keyp_colors[keyp_colormap_id][2] = keybgr[0];
        else:
#        if not (mods & pygame.KMOD_CTRL):
         keyp_colormap_id = -1;
        #
        if ( not sensWindow.hidden ):
         if (( mousex > keyp_delta_slider_pos[0] ) and ( mousex < keyp_delta_slider_pos[0] + keyp_delta_slider_size[0] ) and
             ( mousey > keyp_delta_slider_pos[1] ) and ( mousey < keyp_delta_slider_pos[1] + keyp_delta_slider_size[1] )):
          keyp_delta = (mousex - keyp_delta_slider_pos[0] );
          if (keyp_delta > keyp_delta_slider_size[0] ): keyp_delta = keyp_delta_slider_size[0];
          if (keyp_delta <   1): keyp_delta = 1;
          print "click on slider " + str(keyp_delta)
        #
        size=7;
        if ( not colorWindow.hidden ):
         for i in range( len( keyp_colormap_colors_pos  ) ):
          if (abs( mousex - ( keyp_colormap_colors_pos[i][0] + keyp_colormap_pos[0] ) )< size) and (abs( mousey - ( keyp_colormap_colors_pos[i][1] + keyp_colormap_pos[1]) )< size):
           keyp_colormap_id = i;
#        print "x offset " + str(xoffset_whitekeys) + " y offset: " +str(yoffset_whitekeys);
        size=5;
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
    for wnd in glwindows:
      wnd.update_mouse_move(mousex,mousey)

    pygame.display.flip();

main();

frame=startframe;
drawhelp=0;
processmidi();

print "done...";
