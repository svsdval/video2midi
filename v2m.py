#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import time;

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
resize= 0;
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

resize_width=1280;
resize_height=720;
tempo = 120;

debug = 0;
debug_keys = 0;

length = int(vidcap.get(CAP_PROP_FRAME_COUNT));
video_width  = int(vidcap.get(CAP_PROP_FRAME_WIDTH));
video_height = int(vidcap.get(CAP_PROP_FRAME_HEIGHT));
fps    = float(vidcap.get(CAP_PROP_FPS));

width = video_width;
height = video_height;

startframe = 1;
endframe = length;

# set start frame;
def getFrame( framenum =-1 ):
  global resize;
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
[0  ,  0,  0], [  0,  0,  0],
[0  ,  0,  0], [  0,  0,  0],
[0  ,  0,  0], [  0,  0,  0],
[0  ,  0,  0], [  0,  0,  0]
# .....
];

keyp_delta = 90; # sensitivity
#
keyp_colors_channel =      [ 0,0, 1,1, 2,2, 3,3, 4,4, 5,5, 6,6, 7,7, 8,8 ]; # MIDI channel per color
keyp_colors_channel_prog = [ 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0 ]; # MIDI program ID per channel

colorWindow_colorBtns_channel_labels=[];
colorWindow_colorBtns_channel_btns=[];


#
minimal_duration = 0.1;
ignore_minimal_duration = False;

bgImgGL=-1;

notes_overlap = False;
keyp_colormap_id=-1;

separate_note_id=-1;

miditrackname="Sample Track";

Label_v_spacer=21;
fontSize=24;
glDrawPixelsText = 0;
fontTexture = -1;
fontChars = u''' !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz'''

screen=0;
colorBtns = []

#

#cfg
home = expanduser("~")
inifile = os.path.join( home, '.v2m.ini');
if os.path.exists( 'v2m.ini' ):
  inifile="v2m.ini";
  print("local config file exists.")

def loadsettings( cfgfile ):
 global miditrackname,debug,notes_overlap,resize,resize_width,resize_height,minimal_duration,keyp_colors_channel,keyp_colors_channel_prog,xoffset_whitekeys,yoffset_whitekeys,keyp_colors,keys_pos,ignore_minimal_duration,keyp_delta,screen,tempo,width,height;
 global colorBtns,colorWindow_colorBtns_channel_labels;

 if not os.path.exists( cfgfile ):
  print("cannot find setings file: "+cfgfile);
 else:  
  print("reading settings from file: "+cfgfile);
  config = ConfigParser()
  config.read( cfgfile )
  section = 'options';
  if config.has_option(section, 'midi_track_name'):
   miditrackname = config.get(section, 'midi_track_name')
  if config.has_option(section, 'debug'):
   debug = config.getboolean(section, 'debug')
  if config.has_option(section, 'notes_overlap'):
   notes_overlap = config.getboolean(section, 'notes_overlap')
  if config.has_option(section, 'resize'):
   resize = config.getboolean(section, 'resize')
  if config.has_option(section, 'resize_width'):
   resize_width = config.getint(section, 'resize_width')
  if config.has_option(section, 'resize_height'):
   resize_height = config.getint(section, 'resize_height')
  if config.has_option(section, 'minimal_note_duration'):
   minimal_duration = config.getfloat(section, 'minimal_note_duration')
  if config.has_option(section, 'color_channel_accordance'):
   clr_chnls = config.get(section, 'color_channel_accordance')
  if config.has_option(section, 'channel_prog_accordance'):
   clr_chnls_prog = config.get(section, 'channel_prog_accordance')
  if config.has_option(section, 'ignore_notes_with_minimal_duration'):
   ignore_minimal_duration = config.getboolean(section, 'ignore_notes_with_minimal_duration')
  if config.has_option(section, 'notes_overlap'):
   notes_overlap = config.getboolean(section, 'notes_overlap')
  if config.has_option(section, 'sensitivity'):
   keyp_delta = config.getint(section, 'sensitivity')
  if config.has_option(section, 'output_midi_tempo'):
   tempo = config.getint(section, 'output_midi_tempo')


  if ( clr_chnls != "" ):
#    keyp_colors_channel = map(int, clr_chnls.split(","))
    keyp_colors_channel = [ int(x) for x in clr_chnls.split(",") ]
    print("readed color = channel", keyp_colors_channel);

  if ( clr_chnls_prog != "" ):
#    keyp_colors_channel_prog = map(int, clr_chnls_prog.split(","))
    keyp_colors_channel_prog = [ int(x) for x in clr_chnls_prog.split(",") ]

    print("readed color channel = prog ", keyp_colors_channel_prog);
    
  if config.has_option(section, 'xoffset_whitekeys'):
   xoffset_whitekeys = config.getint(section, 'xoffset_whitekeys')
  if config.has_option(section, 'yoffset_whitekeys'):
   yoffset_whitekeys = config.getint(section, 'yoffset_whitekeys')

  if config.has_option(section, 'keyp_colors'):
   skeyp_colors = config.get(section, 'keyp_colors')
   if ( skeyp_colors.strip() != "" ):
    keyp_colors[:] = [];
    for cur in skeyp_colors.split(","):
     c = cur.split(":")
     keyp_colors.append( [ int(c[0]), int(c[1]),int(c[2]) ]);

  while ( len(keyp_colors) < len(colorBtns) ):  
    print("Warning, append array keyp_colors", len(keyp_colors));
    keyp_colors.append( [0,0,0] );
    
  if config.has_option(section, 'keys_pos'):
   skeys_pos = config.get(section, 'keys_pos')
   if ( skeys_pos.strip() != "" ):
    keys_pos = [];
    for cur in skeys_pos.split(","):
     c = cur.split(":")
     keys_pos.append( [ int(c[0]), int(c[1])  ]);
    print( len(keyp_colors) );
    print( len(keyp_colors_channel));
 while ( len(keyp_colors_channel) < len(keyp_colors) ):  
    print("Warning, append array keyp_colors_channel", len(keyp_colors_channel));
    keyp_colors_channel.append( len(keyp_colors_channel) // 2 ); 
 while ( len(keyp_colors_channel_prog) < len(keyp_colors) ):  
    print("Warning, append array keyp_colors_channel_prog", len(keyp_colors_channel_prog));
    keyp_colors_channel_prog.append(0);

 if len(colorWindow_colorBtns_channel_labels) > 0:
   for i in range(len(colorBtns)):
     colorWindow_colorBtns_channel_labels[i].text = "Ch:" + str(keyp_colors_channel[i]+1);

 if ( resize == 1 ):
    width = resize_width;
    height = resize_height;

 pass;
 
###
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
 for i in range(9):
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
  pass;


def savesettings():
 print("save settings to file")
 config = ConfigParser();
 #config = configparser.RawConfigParser()
 section='options';
 config.add_section(section);
 config.set(section, 'midi_track_name', miditrackname);
 config.set(section, 'debug', str(int(debug)));
 config.set(section, 'notes_overlap', str(int(notes_overlap)));
 config.set(section, 'resize', str(int(resize)));
 config.set(section, 'resize_width', str(resize_width));
 config.set(section, 'resize_height', str(resize_height));
 config.set(section, 'minimal_note_duration', str(minimal_duration));
 config.set(section, 'ignore_notes_with_minimal_duration', str(int(ignore_minimal_duration)));
 config.set(section, 'notes_overlap', str(int(notes_overlap)));
 config.set(section, 'sensitivity', str(int(keyp_delta)));
 config.set(section, 'output_midi_tempo', str(int(tempo)));
 
 
 skeyp_colors_channel = "";
 for i in keyp_colors_channel:
  skeyp_colors_channel+= str(i)+",";
 skeyp_colors_channel_prog = "";
 for i in keyp_colors_channel_prog:
  skeyp_colors_channel_prog+= str(i)+",";
 config.set(section, 'color_channel_accordance',skeyp_colors_channel[0:-1]);
 config.set(section, 'channel_prog_accordance', skeyp_colors_channel_prog[0:-1]);

 config.set(section, 'xoffset_whitekeys',str(int(xoffset_whitekeys)));
 config.set(section, 'yoffset_whitekeys',str(int(yoffset_whitekeys)));

 skeyp_colors="";
 for i in keyp_colors:
  skeyp_colors+= str(int(i[0]))+":"+str(int(i[1]))+":"+str(int(i[2]))+",";
  config.set(section, 'keyp_colors', skeyp_colors[0:-1]);

 skeys_pos="";
 for i in keys_pos:
  skeys_pos+= str(int(i[0]))+":"+str(int(i[1]))+",";
  config.set(section, 'keys_pos', skeys_pos[0:-1]);
 
 with open(settingsfile, 'w') as configfile:
    config.write(configfile);
 pass;

updatekeys( 1 );

loadsettings(inifile);

glListQuad1=-1;
glListRect1=-1;

tStart = t0 = time.time()-1;
frames = 0;

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

def DrawQuad(vx,vy,vx2,vy2,):
  global glListQuad1;
  if glListQuad1 == -1 :
    glListQuad1 = glGenLists(1)
    glNewList(glListQuad1, GL_COMPILE)
    #
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(0, 0)
    glTexCoord2f(1, 0)
    glVertex2f(1, 0)
    glTexCoord2f(1, 1)
    glVertex2f(1, 1)
    glTexCoord2f(0, 1)
    glVertex2f(0, 1)
    glEnd()
    #
    glEndList()
    glCallList(glListQuad1);
  else :
    glPushMatrix();
    glTranslatef(vx,vy,0);
    glScalef(vx2-vx,vy2-vy,1);
    glCallList(glListQuad1);
    glPopMatrix();
  #
  pass;
def DrawQuad_old(x,y,x2,y2, texx=1, texy=-1):
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
  pass;

def DrawRect(vx,vy,vx2,vy2,w=1):
  global glListRect1;
  glLineWidth(w);
  if glListRect1 == -1 :
    glListRect1 = glGenLists(1)
    glNewList(glListRect1, GL_COMPILE)
    x=0;
    y=0;
    x2=1;
    y2=1;

    glBegin(GL_LINE_LOOP);
    glVertex2f(x, y);
    glVertex2f(x2, y);
    glVertex2f(x2, y2);
    glVertex2f(x, y2);
    glEnd();
    glEndList()
    glCallList(glListRect1);
  else :
    glPushMatrix();
    glTranslatef(vx,vy,0);
    glScalef(vx2-vx,vy2-vy,1);
    glCallList(glListRect1);
    glPopMatrix();
  #
  pass;


def DrawRect_old(x,y,x2,y2,w=1):
   glLineWidth(w);
   glBegin(GL_LINE_LOOP);
   glVertex2f(x, y);
   glVertex2f(x2, y);
   glVertex2f(x2, y2);
   glVertex2f(x, y2);
   glEnd();
   pass;

def DrawQuadT(x,y,x2,y2):
   glBegin(GL_QUADS)
   glTexCoord2i(0, 1)
   glVertex2f(x, y)
   glTexCoord2i(1, 1)
   glVertex2f(x2, y)
   glTexCoord2i(1, 0)
   glVertex2f(x2, y2)
   glTexCoord2i(0, 0)
   glVertex2f(x, y2)
   glEnd()
   pass;

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
  glEnd();
  pass

class GLFont:
  def __init__(self,tx,ty,tx2,ty2, fw,fh, char):
    self.tx = tx;
    self.ty = ty;
    self.tx2 = tx2;
    self.ty2 = ty2;
    self.fw = fw;
    self.fh = fh;
    self.char = char;
    self.gllistid = -1;
    pass;

fonts = []

def RenderText(x,y, text):
  global fontChars;
  global fonts;
  glPushAttrib(GL_ENABLE_BIT);

  glDisable(GL_DEPTH_TEST);
  glDisable(GL_CULL_FACE);

  glEnable(GL_TEXTURE_2D);
  glEnable(GL_BLEND);

  glEnable(GL_ALPHA_TEST);
  glAlphaFunc(GL_GEQUAL, 0.1);

  #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
  glBlendFunc(GL_ONE, GL_SRC_ALPHA);
  #
  glBindTexture(GL_TEXTURE_2D,fontTexture);
  
  glPushMatrix();
  

  glTranslatef(x,y-21,0);
  glColor4f(1.0, 1.0, 1.0, 1.0);
  for i in text:
    fid=0;  
    #Is this really so terribly slow to find the need charset O_o ?!
    #
    #for fid in range(len(fonts)):
    #  if i == fonts[fid].char :
    #    break;
    
    fid = int(ord( i )) - 32;
    if fid < 0 and fid > len(fonts): continue;
    j = fonts[ fid ];
    if i == ' ' :
      glTranslatef(j.fw,0,0);
      continue;
      
    if j.gllistid == -1 :

     #PyOpenGL terribly slow =( so... trying to optimize ...
     gllist = glGenLists(1)
     glNewList(gllist, GL_COMPILE)
     glBegin(GL_QUADS)
     glTexCoord2f(j.tx, j.ty)
     glVertex2f(0, 0)
     glTexCoord2f(j.tx2, j.ty)
     glVertex2f(j.fw, 0)
     glTexCoord2f(j.tx2, j.ty2)
     glVertex2f(j.fw, j.fh)
     glTexCoord2f(j.tx, j.ty2)
     glVertex2f(0, j.fh)
     glEnd()
     
     glEndList()
     fonts[fid].gllistid = gllist;
     glCallList(gllist);
#     print "new list created : ", gllist;
    else:
#     print "calling list : ", j.vbo;
     glCallList(j.gllistid);
         
    glTranslatef(j.fw,0,0);
  glPopMatrix();
  glPopAttrib();
  pass;


def GenFontTexture():
  global fontChars;
  global fonts;
  global fontSize;
  global fontTexture;
  
  #surface
  texture_buffer_surf = pygame.Surface((512, 512))
  texture_buffer_surf.fill(pygame.Color('black'))  
  
  font = pygame.font.Font(None, fontSize )
  x = 2;
  y = 0;
  for i in range(len(fontChars)):
    y = i // 32;
    #
    textSurface = font.render( fontChars[i] , True, (255,255,255,255))
    #
    ix, iy = textSurface.get_width(), textSurface.get_height()
    texture_buffer_surf.blit(textSurface, (x, y*fontSize, 0, 0))
    fnt =  GLFont(x / 512.0 ,1 - (y*fontSize -2) / 512.0, (x+ix) / 512.0,1 - (y*fontSize+fontSize-2) / 512.0, ix,fontSize, fontChars[i]);
   
    fonts.append( fnt );
    
    x += ix + 2;
    if (i % 32 == 31 ) and (i != 0): x=2;
    
  tex_data = pygame.image.tostring(texture_buffer_surf, "RGBA", 1)
  
  # fix alpha ...
  l = list( tex_data );
  #
  for y in range(512):
   for x in range(512):
       l[ (y*512+x) * 4 +3 ] =  l[ (y*512+x) * 4 +0 ]
       
  if sys.version_info >= (3, 0):
    tex_data4 = l;
  else:
    tex_data4 = ''.join(l);
  #
  glBindTexture(GL_TEXTURE_2D, fontTexture)
    
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
  glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

  glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_data4 );
  pass;


def resize_window():
  global resize, screen,  width, height, bgImgGL, fontTexture;

  if resize:
    width = resize_width;
    height = resize_height;
  else:
    width = video_width
    height = video_height;
  screen = pygame.display.set_mode((width,height), DOUBLEBUF|OPENGL);
  #
  doinit();
  
  

def drawText(position, color, textString, size=24):
  global glDrawPixelsText;
  if not glDrawPixelsText :
    RenderText(position[0],position[1], textString);
  else:
    glEnable(GL_BLEND);
    glBlendFunc(GL_ONE, GL_SRC_ALPHA);
    font = pygame.font.Font (None, size)
    textSurface = font.render(textString, True, (color[0],color[1],color[2],255), (0,0,0,0))
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glRasterPos3d(*position)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)
  pass

class GLSlider:
  def __init__(self,x,y,w,h, vmin,vmax, value):
    self.w = float(w);
    self.h = float(h);
    self.x = float(x);
    self.y = float(y);
    self.vmin = vmin;
    self.vmax = vmax;
    self.value = value;

    if (vmax - vmin) != 0:
      self.percent = (value / float(vmax - vmin)) * 100;
    self.mousegrab = 0;
    self.mousepos = [0,0];
    self.mouseclickpos = [0,0];
    pass;

  def draw(self):
    self.update();
    glDisable(GL_TEXTURE_2D);
    glEnable(GL_BLEND);
    glPushMatrix()
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glColor4f(0.2, 0.2, 0.2, 0.9);

    glTranslatef( self.x , self.y ,0);
    glColor4f(0.8, 0.8, 0.8, 1);
    DrawQuad(0,0,self.w+2,self.h+2);
    glColor4f(0.5, 0.5, 1.0, 1);
    DrawQuad(2,2,self.percent * self.w * 0.01, self.h );

#    glTranslatef(self.w *0.5 , self.h *0.5 + Label_v_spacer *0.5 ,0);
#    drawText( (0,0,1), (128,0,255), str(int(self.value)));

    glPopMatrix();
    pass;
#
  def update(self):
    pass;
  def setvalue(self,value):
#
    self.value = value;
    if (self.vmax - self.vmin) != 0:
      self.percent = (value / float(self.vmax - self.vmin)) * 100;
    pass;
    
  def update_mouse_move(self, mpx, mpy ):
    self.mousepos[0] = mpx;
    self.mousepos[1] = mpy;
    if (self.mousegrab == 1):
      self.percent = (mpx / self.w) * 100.0;

      if ( self.percent > 100.0 ) : self.percent = 100;
      if ( self.percent < 0 ) : self.percent = 0;
      if (self.vmax-self.vmin) == 0:
        selv.value = 0;
      else:
        self.value = self.percent * (self.vmax-self.vmin) * 0.01 + self.vmin
#      print "update_mouse_move on slider x:" + str( mpx ) + " y:" + str(mpy) + " self.x:" + str( self.x ) + " self.y:" + str(self.y) + " value : " +str(self.value) ;
#      if ( self.value > self.vmax ) : self.value = self.vmax;
#      if ( self.value < self.vmin ) : self.value = self.vmin;
      
    pass;
    
  def update_mouse_down(self,mpx,mpy,btn):
    self.mouseclickpos[0] = mpx - self.x;
    self.mouseclickpos[1] = mpy - self.y;
    #print "update_mouse_down on slider x:" + str( mpx ) + " y:" + str(mpy) + " self.x:" + str( self.x ) + " self.y:" + str(self.y);
    
    if (( mpx > self.x ) and ( mpx < self.x+self.w ) and
        ( mpy > self.y ) and ( mpy < self.y+self.h )):
        #print "update_mouse_down grab on slider x:" + str( mpx ) + " y:" + str(mpy) + " self.x:" + str( self.x ) + " self.y:" + str(self.y);
        self.mousegrab = 1;
    self.update();
    pass;
    
  def update_mouse_up(self,mpx,mpy,btn):
    self.mousegrab = 0;
    self.mouseclickpos[0] = mpx - self.x;
    self.mouseclickpos[1] = mpy - self.y;
    #print "update_mouse_up on slider x:" + str( mpx ) + " y:" + str(mpy) + " self.x:" + str( self.x ) + " self.y:" + str(self.y);
    pass;
    
  def update_key_down(self, keycode ):
    pass;
    
  def update_key_up(self, keycode ):
    pass;

class GLColorButton:
  def __init__(self,x,y,w,h, index, color):
    self.w = float(w);
    self.h = float(h);
    self.x = float(x);
    self.y = float(y);
    self.color = color;
    self.index = index;
    self.mousegrab = 0;
    self.mousepos = [0,0];
    self.mouseclickpos = [0,0];
    pass;

  def draw(self):
    self.update();
    glDisable(GL_TEXTURE_2D);
    glEnable(GL_BLEND);
    glPushMatrix()
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glColor4f(0.2, 0.2, 0.2, 0.9);

    glTranslatef( self.x, self.y ,0);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
 
    if ( keyp_colormap_id == self.index ):
      glColor4f(1.0, 1.0, 1.0, 1);
      
      DrawQuad(0,0,self.w,self.h);
    else:
      glColor4f(0.5, 0.5, 0.5, 1);
      DrawQuad(2,2,self.w-2,self.h-2);
 
    glColor4f(0.0, 0.0, 0.0, 1);
    DrawQuad(3,3,self.w-3,self.h-3);

    glColor4ub(self.color[0],self.color[1],self.color[2], 255);
    DrawQuad(5,5,self.w-5,self.h-5);
    glPopMatrix();
    pass;


  def update(self):
    pass;

  def update_mouse_move(self, mpx, mpy ):
    self.mousepos[0] = mpx;
    self.mousepos[1] = mpy;
    if (self.mousegrab == 1):
      pass;
    pass;
    
  def update_mouse_down(self,mpx,mpy,btn):
    global keyp_colormap_id
    self.mouseclickpos[0] = mpx - self.x;
    self.mouseclickpos[1] = mpy - self.y;
#    if (( mpx > self.x ) and ( mpx < self.x+self.w ) and
#        ( mpy > self.y ) and ( mpy < self.y+self.h )):
#        keyp_colormap_id = self.index
#        print "color button: update_mouse_down set index = " + str(keyp_colormap_id);
    
    if (( mpx > self.x ) and ( mpx < self.x+self.w ) and
        ( mpy > self.y ) and ( mpy < self.y+self.h )):
        self.mousegrab = 1;
    self.update();
    pass;

  def update_mouse_up(self,mpx,mpy,btn):
    global keyp_colormap_id
    self.mousegrab = 0;
    self.mouseclickpos[0] = mpx - self.x;
    self.mouseclickpos[1] = mpy - self.y;

    if (( mpx > self.x ) and ( mpx < self.x+self.w ) and
        ( mpy > self.y ) and ( mpy < self.y+self.h )):
        keyp_colormap_id = self.index
 #       print "color button: update_mouse_up set index = " + str(keyp_colormap_id);
    pass;

  def update_key_down(self, keycode ):
    pass;

  def update_key_up(self, keycode ):
    pass;


class GLButton:
  def __init__(self,x,y,w,h, index, color, text, procedure):
    self.w = float(w);
    self.h = float(h);
    self.x = float(x);
    self.y = float(y);
    self.color = color;
    self.index = index;
    self.text = text;
    self.procedure = procedure;
    self.mousegrab = 0;
    self.mousepos = [0,0];
    self.mouseclickpos = [0,0];
    pass;

  def draw(self):
    self.update();
    glDisable(GL_TEXTURE_2D);
    glEnable(GL_BLEND);
    glPushMatrix()
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glColor4f(0.2, 0.2, 0.2, 0.9);

    glTranslatef( self.x, self.y ,0);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
 
    glColor4f(0.5, 0.5, 0.5, 1);
    DrawQuad(1,1,self.w-1,self.h-1);

    glColor4f(1.0, 1.0, 1.0, 1);
    DrawQuad(2,2,self.w-2,self.h-2);

    glColor4ub(self.color[0],self.color[1],self.color[2], 255);
    DrawQuad(3,3,self.w-3,self.h-3);
    glPopMatrix();
    
    glPushMatrix()
    glTranslatef( self.x+5, self.y ,0);
    glColor4f(1.0, 1.0, 1, 0.0);
    #glScalef(0.7,0.7,0.7);
    r = self.text.splitlines();
    for i in r:
      drawText( (0,Label_v_spacer,1),(255,255,255), i);
      glTranslatef(0,Label_v_spacer,0);
    glPopMatrix()
    
    pass;


  def update(self):
    pass;

  def update_mouse_move(self, mpx, mpy ):
    self.mousepos[0] = mpx;
    self.mousepos[1] = mpy;
    if (self.mousegrab == 1):
      pass;
    pass;
    
  def update_mouse_down(self,mpx,mpy,btn):
    global keyp_colormap_id
    self.mouseclickpos[0] = mpx - self.x;
    self.mouseclickpos[1] = mpy - self.y;
#    if (( mpx > self.x ) and ( mpx < self.x+self.w ) and
#        ( mpy > self.y ) and ( mpy < self.y+self.h )):
#        keyp_colormap_id = self.index
#        print "color button: update_mouse_down set index = " + str(keyp_colormap_id);
    
    if (( mpx > self.x ) and ( mpx < self.x+self.w ) and
        ( mpy > self.y ) and ( mpy < self.y+self.h )):
        self.mousegrab = 1;
    self.update();
    pass;

  def update_mouse_up(self,mpx,mpy,btn):
    global keyp_colormap_id
    self.mousegrab = 0;
    self.mouseclickpos[0] = mpx - self.x;
    self.mouseclickpos[1] = mpy - self.y;

    if (( mpx > self.x ) and ( mpx < self.x+self.w ) and
        ( mpy > self.y ) and ( mpy < self.y+self.h )):
        self.procedure(self);
        #keyp_colormap_id = self.index
 #       print "color button: update_mouse_up set index = " + str(keyp_colormap_id);
    pass;

  def update_key_down(self, keycode ):
    pass;

  def update_key_up(self, keycode ):
    pass;

class GLLabel:
  def __init__(self,x,y,text):
    self.x = x;
    self.y = y;
    self.text = text;
    pass;

  def draw(self):
    self.update();
    glPushMatrix()
    glTranslatef(self.x,self.y,0);
    glColor4f(1.0, 1.0, 1, 0.0);
    r = self.text.splitlines();
    for i in r:
      drawText( (0,Label_v_spacer,1),(255,255,255), i);
      glTranslatef(0,Label_v_spacer,0);
    glPopMatrix()
    pass;

  def update(self):
    pass;
  def update_mouse_move(self, mpx, mpy ):
    pass;
  def update_mouse_down(self,mpx, mpy, btn):
    pass;
  def update_mouse_up(self, mpx, mpy, btn):
    pass;
  def update_key_down(self, keycode ):
    pass;
  def update_key_up(self, keycode ):
    pass;

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
    self.child = [];
    self.level = 0;
    self.active = 0;
    #
    self.clientrect[0] = self.x + self.borderwidth;
    self.clientrect[1] = self.y + self.borderwidth + self.titleheight;
    self.clientrect[2] = self.x + self.w - self.borderwidth;
    self.clientrect[3] = self.y + self.h - self.titleheight - self.borderwidth;
    #
  def appendChild(self,child):
    self.child.append(child);

  def draw(self):
    self.update();
    glDisable(GL_TEXTURE_2D);
    glEnable(GL_BLEND);
    glPushMatrix()
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    if self.active == 1:
      glColor4f(0.3, 0.3, 0.3, 0.9);
    else:
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
    drawText( (self.x+4,self.y+self.titleheight-2,1),(255,255,255), self.title );
    glTranslatef(self.clientrect[0],self.clientrect[1],0);
    if ( not self.hidden ):
      for i in self.child:
        if hasattr(i, 'draw'):
          i.draw();

    glPopMatrix();
    glDisable(GL_BLEND);

    pass;
    
  def update(self):
    self.titlewidth = self.w;

    self.clientrect[0] = self.x + self.borderwidth;
    self.clientrect[1] = self.y + self.borderwidth + self.titleheight;
    self.clientrect[2] = self.x + self.w - self.borderwidth;
    self.clientrect[3] = self.y + self.h - self.titleheight - self.borderwidth;
    
    if ( not self.hidden ):
      for i in self.child:
        if hasattr(i, 'update'):
          i.update();
    
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
    
    if ( not self.hidden ):
      for i in self.child:
        if hasattr(i, 'update_mouse_move'):
          i.update_mouse_move(mpx - self.x,mpy - self.y);
      
    pass;
    
  def update_mouse_down(self,mpx,mpy,btn):
    self.mouseclickpos[0] = mpx - self.x;
    self.mouseclickpos[1] = mpy - self.y;
    if ( not self.hidden ):
      if (( mpx > self.x ) and ( mpx < self.x + self.w ) and
          ( mpy > self.y ) and ( mpy < self.y + self.h - self.titleheight )):
          self.active = 1;
      else:
          self.active = 0;
    else:
      if (( mpx > self.x ) and ( mpx < self.x + self.titlewidth ) and
        ( mpy > self.y ) and ( mpy < self.y + self.titleheight )):
          self.active = 1;
      else:
          self.active = 0;
        

    if (( mpx > self.x+self.titlewidth-16 ) and ( mpx < self.x + self.w ) and
        ( mpy > self.y ) and ( mpy < self.y + self.titleheight )):
        self.hidden = not self.hidden;
        return;
        

    if (( mpx > self.x ) and ( mpx < self.x + self.titlewidth ) and
        ( mpy > self.y ) and ( mpy < self.y + self.titleheight )):
        self.mousegrab = 1;

    if ( not self.hidden ) and ( not self.mousegrab ):
      for i in self.child:
        if hasattr(i, 'update_mouse_down'):
          i.update_mouse_down(mpx - self.clientrect[0],mpy - self.clientrect[1],btn);

    self.update();
    pass;
    
    
  def update_mouse_up(self,mpx,mpy,btn):
    self.mousegrab = 0;
    self.mouseclickpos[0] = mpx - self.x;
    self.mouseclickpos[1] = mpy - self.y;

    if ( not self.hidden ):
      for i in self.child:
        if hasattr(i, 'update_mouse_up'):
          i.update_mouse_up(mpx - self.clientrect[0],mpy - self.clientrect[1] ,btn);
    pass;
    
  def update_key_down(self, keycode ):
    mpx = self.mousepos[0];
    mpy = self.mousepos[1];
    
            
    if not self.hidden:
      if (( mpx > self.x ) and ( mpx < self.x + self.w ) and
          ( mpy > self.y ) and ( mpy < self.y + self.h - self.titleheight)):
        if keycode == pygame.K_h:
          self.hidden = not self.hidden;
    else:
      if (( mpx > self.x ) and ( mpx < self.x + self.titlewidth ) and
          ( mpy > self.y ) and ( mpy < self.y + self.titleheight )):
        if keycode == pygame.K_h:
          self.hidden = not self.hidden;

    if ( not self.hidden ):
      for i in self.child:
        if hasattr(i, 'update_key_down'):
          i.update_key_down(keycode);
      
    pass;
  def update_key_up(self, keycode ):
    if ( not self.hidden ):
      for i in self.child:
        if hasattr(i, 'update_key_up'):
          i.update_key_up(keycode);
    pass;

def update_channels(sender):
 print( 'update_channels...' +str(sender.index));
 i=abs(sender.index) -1;
 if (sender.index > 0):
   keyp_colors_channel[i]= keyp_colors_channel[i] + 1;
 else:
   keyp_colors_channel[i]= keyp_colors_channel[i] - 1;
 if (keyp_colors_channel[i] > 15):
   keyp_colors_channel[i] = 15;
 if (keyp_colors_channel[i] < 0):
   keyp_colors_channel[i] = 0;
 colorWindow_colorBtns_channel_labels[i].text = "Ch:" + str(keyp_colors_channel[i]+1);
 
# 
wh = ( (len(keyp_colors) // 2)+2 ) * 24;
colorWindow = GLWindow(32, 16, 264, wh, "color map")
settingsWindow = GLWindow(32, wh, 250, 250, "Settings");
helpWindow = GLWindow(32+270, 16, 750, 475, "help");

glwindows = [];
glwindows.append(colorWindow);
glwindows.append(settingsWindow);
glwindows.append(helpWindow);

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
Arrows - keys adjustment (mods : shift)
PageUp/PageDown - scrolling video (mods : shift)
Home/End - go to the beginning or end of the video
[ / ] - change base octave
F2 / F3 - save / load settings
Escape - quit
Space - abort re-creation and save midi file to disk""");

helpWindow.appendChild(helpWindow_label1);

settingsWindow_label1 = GLLabel(0,0, "base octave: " + str(octave) + "\nnotes overlap: " + str(notes_overlap) + "\nignore minimal duration: " + str(ignore_minimal_duration));
settingsWindow.appendChild(settingsWindow_label1);

settingsWindow_label2 = GLLabel(0,67,  "Sensitivity:"+str(keyp_delta)+"\n\nMinimal note duration (sec):"+str(minimal_duration) +   "\n\nOutput tempo for midi:" + str(tempo)  );
settingsWindow.appendChild(settingsWindow_label2);

settingsWindow_slider1 = GLSlider(1,90, 240,18, 0,130,keyp_delta);
settingsWindow.appendChild(settingsWindow_slider1);

settingsWindow_slider2 = GLSlider(1,130, 240,18, 0,200,minimal_duration*100);
settingsWindow.appendChild(settingsWindow_slider2);

settingsWindow_slider3 = GLSlider(1,173, 240,18, 30,200,tempo);
settingsWindow.appendChild(settingsWindow_slider3);

# for i in range( len( keyp_colors ) ):
  #keyp_colormap_colors_pos.append ([ (i % 2) * 32,  ( i // 2 ) * 20  ]);
print ('creating new colors '+str(len( keyp_colors )));

for i in range( len( keyp_colors ) ):
 cx,cy = (i % 2) * 130,  ( i // 2 ) * 20;
 offsetx,offsety=4,4;
 colorBtns.append( GLColorButton(offsetx+cx,offsety+cy ,20,20,i, keyp_colors[i] ) );
 colorWindow.appendChild(colorBtns[i]);
 colorWindow_label1 = GLLabel(offsetx+25+cx,offsety+cy , "Ch:" + str(keyp_colors_channel[i]+1) );
 
 colorWindow_colorBtns_channel_labels.append( colorWindow_label1 );
 colorWindow.appendChild(colorWindow_label1);
 #
 colorWindow_colorBtns_channel_btns.append( GLButton(offsetx+cx+80,offsety+cy ,20,20,(i+1), [128,128,128], "+" ,update_channels) );
 colorWindow.appendChild( colorWindow_colorBtns_channel_btns[i*2] );
 #
 colorWindow_colorBtns_channel_btns.append( GLButton(offsetx+cx+80+20,offsety+cy ,20,20,-(i+1), [128,128,128], "-" ,update_channels) );
 colorWindow.appendChild( colorWindow_colorBtns_channel_btns[i*2+1] );


#loadsettings( settingsfile );    
#frame=801
 
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
 global resize;
 global octave;
 global keyp_delta;
 global fontTexture;
 global keyp_delta;
 global minimal_duration;
 global tempo;


 
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
    print("skip note > 120");
    continue;
  keypressed=0;

  pressedcolor=[0,0,0];
  for keyc in keyp_colors:
   if (keyc[0] != 0 ) or (keyc[1] != 0 ) or (keyc[2] != 0 ) :
     if ( abs( int(key[0]) - keyc[0] ) < keyp_delta ) and ( abs( int(key[1]) - keyc[1] ) < keyp_delta ) and ( abs( int(key[2]) - keyc[2] ) < keyp_delta ):
      keypressed=1;
      pressedcolor=keyc;

  glPushMatrix();
  glTranslatef(keys_pos[i][0],keys_pos[i][1],0);
  if ( keypressed == 1 ):
    #glColor4f(1.0, 0.5, 1.0, 0.9);
    glColor4f(pressedcolor[0]/255.0,pressedcolor[1]/255.0,pressedcolor[2]/255.0,0.9);
    DrawQuad(-6,-7,6,7);
    glColor4f(0,0,0,1);
    DrawRect(-7,-9,7,9,3);
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
 
 for i in range(len(glwindows)): 
   glwindows[i].draw();

 keyp_delta = int(settingsWindow_slider1.value);
 minimal_duration = settingsWindow_slider2.value *0.01;
 tempo = int(settingsWindow_slider3.value);

 settingsWindow_label1.text = "base octave: " + str(octave) + "\nnotes overlap: " + str(notes_overlap) + "\nignore minimal duration: " + str(ignore_minimal_duration);
 settingsWindow_label2.text = "Sensitivity:"+str(keyp_delta)+"\n\nMinimal note duration (sec):"+format(minimal_duration,'.2f' ) +   "\n\nOutput tempo for midi:" + str(tempo);
 for i in range(len(keyp_colors)):
     colorBtns[i].color = keyp_colors[i];

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
 global notes_overlap;
 global resize;
 global miditrackname;
 global separate_note_id;
 global tempo;

 print("video " + str(width) + "x" + str(height));

 # create  MIDI object;
 mf = MIDIFile(1) # only 1 track;
 track = 0 # the only track;
 time = 0 # start at the beginning;
 

 mf.addTrackName(track, time, miditrackname);
 mf.addTempo(track, time, tempo );
 
 channel_has_note = [ 0 for x in range(16) ];
 for i in range(len(keyp_colors_channel)):
  mf.addProgramChange(track, keyp_colors_channel[i], 0, keyp_colors_channel_prog[i]);
  
 print("starting from frame:" + str(startframe));
 getFrame( startframe );
 notecnt=0
 while success:

  if (frame % 100 == 0):
   glBindTexture(GL_TEXTURE_2D, bgImgGL);
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
    key=[ keybgr[2], keybgr[1],keybgr[0] ];

    note=i;
    if ( note > 120 ): 
      print("skip note > 120");
      continue;


    keypressed=0;
    note_channel=0;

#    deltaclr = abs( int(key[0]) - keyp_colors[0][0] ) +  abs( int(key[1]) - keyp_colors[0][1] ) + abs( int(key[2]) - keyp_colors[0][2] )
    deltaclr = keyp_delta*keyp_delta*keyp_delta;

    deltaid = 0
    for j in range(len(keyp_colors)):
     if (keyp_colors[j][0] != 0 ) or ( keyp_colors[j][1] != 0 ) or ( keyp_colors[j][2] != 0 ):
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
          print("note pressed on :" + str( note ));
        notes[ note ] = 1;
        notes_db[ note ] = frame;
        notes_channel[ note ] = note_channel;
        if ( separate_note_id != -1 ):
          if ( separate_note_id < note ):
            notes_channel[ note ] = 0
          else:
            notes_channel[ note ] = 1

      if ( notes[note] == 1 ) and ( notes_channel[ note ] != note_channel ) and ( notes_overlap == 1 ):
        # case if one key over other
        time = notes_db[note] / fps;
        duration = ( frame - notes_db[note] ) / fps;
        ignore = 0
        if ( duration < minimal_duration ):
          if ( debug_keys == 1 ):
            print(" duration:" + str(duration) + " < minimal_duration:" + str(minimal_duration));
          duration = minimal_duration;
          if ( ignore_minimal_duration == 1 ):
            ignore=1;
            

        if ( debug_keys == 1 ):
          print("keys (one over other), note released :" + str(note) + " de = " + str(notes_de[note]) + "- db =" + str(notes_db[note]));
          print("midi add white keys, note : " +str(note) + " time:" +str(time) + " duration:" + str(duration));

        if ( not ignore ):
          mf.addNote(track, notes_channel[note] , basenote + note, time * tempo / 60.0 , duration * tempo / 60.0 , volume );
          channel_has_note[ note_channel ] = 1;
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
        ignore=0
        if ( duration < minimal_duration ):
          if ( debug_keys == 1 ):
            print(" duration:" + str(duration) + " < minimal_duration:" + str(minimal_duration));
          duration = minimal_duration;
          if ( ignore_minimal_duration == 1 ):
            ignore=1;

        if ( debug_keys == 1 ):
          print("keys, note released :" + str(note ) + " de = " + str(notes_de[note]) + "- db =" + str(notes_db[note]));
          print("midi add white keys, note : " +str(note) + " time:" +str(time) + " duration:" + str(duration));
        if ( not ignore ):
          mf.addNote(track, notes_channel[note] , basenote+ note, time * tempo / 60.0 , duration * tempo / 60.0 , volume );
          channel_has_note[ note_channel ] = 1;
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

 print("saved notes: " + str(notecnt));
 
# write midi to disk;
 with open(outputmid, 'wb') as outf:
  mf.writeFile(outf);

def doinit():
  global bgImgGL,glListQuad1,glListRect1;
  glListQuad1=-1;
  glListRect1=-1;
  for fnt in  fonts:
    fnt.gllistid = -1;
  glPixelStorei(GL_UNPACK_ALIGNMENT,1)
  bgImgGL = glGenTextures(1);
  fontTexture = glGenTextures(1);
  glBindTexture(GL_TEXTURE_2D, bgImgGL);
  loadImage();
  GenFontTexture();



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
  global startframe;
  global endframe;
  global basenote;
  global octave;
  global glwindows;
  global separate_note_id;
  global frame;
  global notes_overlap;
  global ignore_minimal_duration;
  global fontTexture;
  global keyp_delta;
  global minimal_duration;
  global resize;
  global width,height;
  global screen;

  running=1;
  keygrab=0;
  keygrabid=-1;
  keygrabaddx=0;

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
       notes_overlap = not notes_overlap;
      if event.key == pygame.K_i:
       ignore_minimal_duration = not ignore_minimal_duration;
   
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
        savesettings()

      if event.key == pygame.K_F3:
        old_resize = resize;
        loadsettings( settingsfile )
        settingsWindow_slider1.setvalue(keyp_delta);
        settingsWindow_slider2.setvalue(minimal_duration * 100);
        settingsWindow_slider3.setvalue(tempo);
        if (resize != old_resize):
          resize_window();
       

      if event.key == pygame.K_r:
        resize = not resize;
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
        whitekey_width+=0.05;
#        print "whitekey_width="+str(whitekey_width);
        updatekeys( );
#        scale+=0.1;
      if ( event.button == 5 ):
        whitekey_width-=0.05;
#        print "whitekey_width="+str(whitekey_width);
        updatekeys( );
#
      if ( event.button == 1 ):
        if mods & pygame.KMOD_CTRL and keyp_colormap_id != -1:
         pixx = int(mousex);
         pixy = int(mousey);
         if not (( pixx >= width ) or ( pixy >= height ) or ( pixx < 0 ) or ( pixy < 0 )):
           if ( resize == 1 ):
             pixx= int(round( pixx * ( video_width / float(resize_width) )))
             pixy= int(round( pixy * ( video_height / float(resize_height) )))
             if ( pixx > video_width -1 ): pixx = video_width-1;
             if ( pixy > video_height-1 ): pixy = video_height-1;
             print("original mouse x:"+str(mousex) + "x" +str(mousey) + " mapped :" +str(pixx) +"x"+str(pixy));

           keybgr=image[pixy,pixx];
           keyp_colors[keyp_colormap_id][0] = keybgr[2];
           keyp_colors[keyp_colormap_id][1] = keybgr[1];
           keyp_colors[keyp_colormap_id][2] = keybgr[0];
        else:
#        if not (mods & pygame.KMOD_CTRL):
         if not colorWindow.active:
            keyp_colormap_id = -1;
         #keyp_colormap_id = -1;
         pass
        #
        size=5;
        for i in range( len( keys_pos) ):
         if (abs( mousex - (keys_pos[i][0] + xoffset_whitekeys) )< size) and (abs( mousey - (keys_pos[i][1] + yoffset_whitekeys) )< size):
          keygrab=1;
          keygrabid=i;
          print("ok click found on : "+str(keygrabid));
          break;
        pass;
      if ( event.button == 3 ):
        keygrab = 2;
        size=5;
        print("x offset " + str(xoffset_whitekeys) + " y offset: " +str(yoffset_whitekeys));
        keygrabaddx=0
        for i in range( len( keys_pos) ):
         if (abs( mousex - (keys_pos[i][0] + xoffset_whitekeys) )< size) and (abs( mousey - (keys_pos[i][1] + yoffset_whitekeys) )< size):
          keygrab=2;
          keygrabaddx=keys_pos[i][0];
          print("ok click found on : "+str(keygrabid));
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
    framerate();
    #limit fps to 60 and get the frame time in milliseconds
    ms = clock.tick(60)
    

main();
helpWindow.hidden=1;
frame=startframe;
processmidi();

print ("done...");

