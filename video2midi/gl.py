import pygame;
import sys;

from OpenGL.GL import *;
from OpenGL.GLU import *;

from .prefs import prefs;

Label_v_spacer=21;
fontSize=24;
fontChars = u''' !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz'''

class GlConstants:
  fontTexture = -1
  bgImgGL=-1


glListQuad1=-1;
glListRect1=-1;
glDrawPixelsText = 0;

keyp_colormap_id=-1;

def doinitGl():
  global glListQuad1,glListRect1;
  glListQuad1=-1;
  glListRect1=-1;
  for fnt in  fonts:
    fnt.gllistid = -1;
  glPixelStorei(GL_UNPACK_ALIGNMENT,1)
  GlConstants.bgImgGL = glGenTextures(1);
  GlConstants.fontTexture = glGenTextures(1);
  glBindTexture(GL_TEXTURE_2D, GlConstants.bgImgGL);


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
   glVertex2f(x + s,y);range
   glVertex2f(x + s*0.5, y-s);
  glEnd();
  pass

class GLFont:
  def __init__(self,tx,ty,tx2,ty2, fw,fh, char):
    self.ty2 = ty2;
    self.tx2 = tx2;
    self.tx = tx;
    self.ty = ty;
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

  glEnable(GL_ALPHA_TEST)
  glAlphaFunc(GL_GEQUAL, 0.1);

  #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
  glBlendFunc(GL_ONE, GL_SRC_ALPHA);
  #
  glBindTexture(GL_TEXTURE_2D,GlConstants.fontTexture);
  
  glPushMatrix();
  

  glTranslatef(x,y-21,0);
  glColor4f(1.0, 1.0, 1.0, 1.0);
  for i in text:
    fid=0;  
    #Is this really so terribly slow to find the need charset O_o ?!
    #
    #for fid in range(len(fonts)):
    #  if i == fonts[fid].char 
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
  glBindTexture(GL_TEXTURE_2D, GlConstants.fontTexture)
    
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
  glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

  glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_data4 );
  pass;



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
  def __init__(self,x,y,w,h, vmin,vmax, value, update_func = None, label = "", color = [128, 128, 255] ):
    self.w = float(w);
    self.h = float(h);
    self.x = float(x);
    self.y = float(y);
    self.vmin = vmin;
    self.vmax = vmax;
    self.value = value;
    self.update_func = update_func;

#    if ( (vmax+ abs(vmin)) - vmin) != 0:
    if ((vmax - vmin) != 0):
      self.percent = ( (value + abs(vmin)) / float(vmax - vmin)) * 100;

    self.mousegrab = 0;
    self.mousepos = [0,0];
    self.mouseclickpos = [0,0];
    self.showvalue= False;
    self.label = label;
    self.showlabel = label != "";
    self.showvaluesinlabel = 1;
    self.round = 2;
    self.color = color;
    self.id    = -1;
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
    glColor4ub( self.color[0], self.color[1], self.color[2], 255);
    DrawQuad(2,2,self.percent * self.w * 0.01, self.h );

    if (self.showvalue):
      glPushMatrix();
      glTranslatef(self.w *0.5 , self.h *0.5 + Label_v_spacer *0.5 ,0);
      drawText( (0,0,1), (128,0,255), str(round(self.value,2)));
      glPopMatrix()
    if (self.showlabel):
      labeltext = self.label;
      if (self.showvaluesinlabel):
        if (self.round == 0):
         value = str(int(self.value));
        else:
         value = str(self.value);
        labeltext = labeltext + ": " + value;
      glPushMatrix();
      drawText( (0,0,1),(255,255,255), labeltext );
      glPopMatrix()
        
    
    glPopMatrix();
    pass;
#
  def update(self):
    pass;
  def setvalue(self,value):
#
    self.value = round(value, self.round );
    #value;
    if (self.vmax - self.vmin) != 0:
      self.percent = ((self.value + abs(self.vmin)) / float(self.vmax - self.vmin)) * 100;
    pass;
    
  def update_mouse_move(self, mpx, mpy ):
    self.mousepos[0] = mpx - self.x;
    self.mousepos[1] = mpy;
    if (self.mousegrab == 1):
      self.percent = (self.mousepos[0] / self.w) * 100.0;

      if ( self.percent > 100.0 ) : self.percent = 100;
      if ( self.percent < 0 ) : self.percent = 0;
      if (self.vmax-self.vmin) == 0:
        self.value = 0;
      else:
        self.value = round( self.percent * (self.vmax-self.vmin) * 0.01 + self.vmin, self.round );
      if ( self.update_func != None ):
        self.update_func(self, self.value);
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
        if keyp_colormap_id < len(prefs.keyp_colors) :
         sparks_slider_delta.id    = keyp_colormap_id;
         sparks_slider_delta.color = prefs.keyp_colors[keyp_colormap_id];
         sparks_slider_delta.setvalue( prefs.keyp_colors_sparks_sensitivity[keyp_colormap_id] );
 #       print "color button: update_mouse_up set index = " + str(keyp_colormap_id);
    pass;

  def update_key_down(self, keycode ):
    pass;

  def update_key_up(self, keycode ):
    pass;


class GLButton:
  def __init__(self,x,y,w,h, index, color = [128,128,128], text="", procedure=None, upcolor=[128,128,128], downcolor=[80,80,80], switch =0, switch_status =0, switch_on= [128,128,255], switch_off = [128,128,128]):
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
    self.switch = switch;
    self.switch_status = switch_status;
    self.switch_on  = switch_on;
    self.switch_off = switch_off;
    self.downcolor = downcolor;
    self.upcolor = upcolor;
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
    if (self.switch) and (self.mousegrab == 0):
      if self.switch_status:
        self.color = self.switch_on;
      else:
        self.color = self.switch_off;
    #
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
        self.color = self.downcolor;
    self.update();
    pass;

  def update_mouse_up(self,mpx,mpy,btn):
    global keyp_colormap_id
    self.mousegrab = 0;
    self.mouseclickpos[0] = mpx - self.x;
    self.mouseclickpos[1] = mpy - self.y;

    if (( mpx > self.x ) and ( mpx < self.x+self.w ) and
        ( mpy > self.y ) and ( mpy < self.y+self.h )):
        self.color = self.upcolor;
        if (self.switch):
          self.switch_status = not self.switch_status;
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