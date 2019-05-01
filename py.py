#!/usr/bin/python

import pyglet
from pyglet.gl import gl
from pyglet.gl import*

from pyglet.window import mouse


#Config = pyglet.gl.Config(sample_buffers=1, samples=16, double_buffer=True)
#window = pyglet.window.Window(800, 640, caption='Stencil Test Draw with mask', config=Config)

#print([i for i in dir(gl) if 'invert'.lower() in i.lower()])

window = pyglet.window.Window()

#image = pyglet.resource.image('img1.jpg')
image = pyglet.image.load('./frame1.jpg')


mpos = [0,0];

window.width = image.width;
window.height = image.height;

label = pyglet.text.Label('Hello, World!!',
                      font_name='Times New Roman',
                      font_size=36,
                      x=window.width//2, y=window.height//2,
                      anchor_x='center', anchor_y='center')



xoffset_whitekeys = 60
yoffset_whitekeys = 673

yoffset_blackkeys = -30

keys_pos=[];
keyp_colors = [ [241,173,64], [216,57,77], [218,52,64], [105,150,192], [39,87,149] ];

global keygrab;
global keygrabid;

keygrab=0;
keygrabid=-1;

#
whitekey_width=24.6;

xx=0
for i in range(8):
 for j in range(12):
  keys_pos.append( [0,0] )
  keys_pos[i*12+j][0] = int(round( xx ));
  keys_pos[i*12+j][1] = 0;
  if (j == 1) or ( j ==3 ) or ( j == 6 ) or ( j == 8) or ( j == 10 ):
   xx += -whitekey_width;
   keys_pos[i*12+j][0] = int(round( xx  + whitekey_width *0.5 ));
   keys_pos[i*12+j][1] = yoffset_blackkeys;
  xx += whitekey_width


@window.event
def on_draw():
    window.clear()
    glClear(0,0,0)
    glColor4f(1.0, 1.0, 1.0, 1.0)
    glLoadIdentity();
    image.blit(0,0)
    label.draw()

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(1.0, 0.5, 1.0, 0.5)
    glPushMatrix();
    glTranslatef(xoffset_whitekeys,-yoffset_whitekeys,0);
    for i in range( len( keys_pos) ):
      glPushMatrix();
      glTranslatef(keys_pos[i][0],image.height-keys_pos[i][1],0);
      pyglet.graphics.draw(4, GL_QUADS, ('v2f', [-5,-5, 5,-5, 5,5, -5,5]))
      pyglet.graphics.draw(4, GL_QUADS, ('v2f', [-1,-1, 1,-1, 1,1, -1,1]))
      glPopMatrix();
    glColor4f(0.0, 1.0, 1.0, 0.5)
    glPopMatrix();

    glPushMatrix();
    glTranslatef(mpos[0],mpos[1],0);
    glScalef(0.5,0.5,0.5);
    pyglet.graphics.draw(4, GL_QUADS, ('v2f', [-5,-5, 5,-5, 5,5, -5,5]))
    glPopMatrix();
    pass

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global keygrab;
    global keygrabid;
    global key_pos;
    global mpos;
    global xoffset_whitekeys;
    global yoffset_whitekeys;

    mpos[0] = x;
    mpos[1] = y;
    #keygrab=1;
    #keygrabid=1
    print " x: " + str(x) + " y: " + str(y);
    if buttons & mouse.LEFT:
     print " x: " + str(x) + " y: " + str(y) + " kg:" +str(keygrab);
     if ( keygrab == 1) and ( keygrabid >-1 ):
      print "moving keyid = " + str(keygrabid);
      keys_pos[ keygrabid ][0] = x - xoffset_whitekeys;
      keys_pos[ keygrabid ][1] = (image.height - y) - yoffset_whitekeys;
    else:
     keygrab=0;
     keygrabid=-1;
    if buttons & mouse.RIGHT:
     xoffset_whitekeys = x;
     yoffset_whitekeys = (image.height - y);
    pass

@window.event
def on_mouse_press(x, y, button, modifiers):
    global keygrab;
    global keygrabid;
    global key_pos;
    global mpos;
    global xoffset_whitekeys;
    global yoffset_whitekeys;

    mpos[0] = x;
    mpos[1] = y;
    size=5;
    keygrab=0;
    keygrabid=-1;
    print "x offset " + str(xoffset_whitekeys) + " y offset: " +str(yoffset_whitekeys);
    for i in range( len( keys_pos) ):
     if (abs( x - (keys_pos[i][0] + xoffset_whitekeys) )< size) and (abs( (image.height - y) - (keys_pos[i][1] + yoffset_whitekeys) )< size):
      keygrab=1;
      keygrabid=i;
      print "ok click found on : "+str(keygrabid);
      break;
    pass

@window.event
def on_mouse_release(x, y, button, modifiers):
#    keygrab=0;
#    keygrabid=-1;
    pass

pyglet.app.run()