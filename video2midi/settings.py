try:
  from configparser import ConfigParser
except ImportError:
  from ConfigParser import ConfigParser  # ver. < 3.0

from video2midi.prefs import prefs
import os

def savesettings(settingsfile):
  print("save settings to "+settingsfile)
  config = ConfigParser()
  section='options'
  config.add_section(section)
  config.set(section, 'midi_track_name', prefs.miditrackname)
  config.set(section, 'debug', str(int(prefs.debug)))
  config.set(section, 'notes_overlap', str(int(prefs.notes_overlap)))
  config.set(section, 'resize', str(int(prefs.resize)))
  config.set(section, 'resize_width', str(prefs.resize_width))
  config.set(section, 'resize_height', str(prefs.resize_height))
  config.set(section, 'minimal_note_duration', str(prefs.minimal_duration))
  config.set(section, 'ignore_notes_with_minimal_duration', str(int(prefs.ignore_minimal_duration)))
  config.set(section, 'sensitivity', str(int(prefs.keyp_delta)))
  config.set(section, 'octave', str(int(prefs.octave)))
  config.set(section, 'output_midi_tempo', str(int(prefs.tempo)))
  config.set(section, 'frame_start', str(int(prefs.startframe)))
  config.set(section, 'blackkey_relative_position', str(float(prefs.blackkey_relative_position)))
  #Sparks
  config.set(section, 'keyp_spark_y_pos', str(int(prefs.keyp_spark_y_pos)))
  config.set(section, 'use_sparks', str( int(prefs.use_sparks) ))
  # extra
  config.set(section, 'rollcheck', str( int(prefs.rollcheck) ))
  config.set(section, 'rollcheck_priority', str( int(prefs.rollcheck_priority) ))
  config.set(section, 'use_alternate_keys', str( int(prefs.use_alternate_keys) ))

  skeyp_colors_channel = ""
  for i in prefs.keyp_colors_channel:
    skeyp_colors_channel+= str(i)+","
  skeyp_colors_channel_prog = ""
  for i in prefs.keyp_colors_channel_prog:
    skeyp_colors_channel_prog+= str(i)+","
  config.set(section, 'color_channel_accordance',skeyp_colors_channel[0:-1])
  config.set(section, 'channel_prog_accordance', skeyp_colors_channel_prog[0:-1])

  config.set(section, 'xoffset_whitekeys',str(int(prefs.xoffset_whitekeys)))
  config.set(section, 'yoffset_whitekeys',str(int(prefs.yoffset_whitekeys)))
  config.set(section, 'yoffset_blackkeys',str(int(prefs.yoffset_blackkeys)))
  config.set(section, 'whitekey_width',str(int(prefs.whitekey_width)))

  skeyp_colors=""
  for i in prefs.keyp_colors:
    skeyp_colors+= str(int(i[0]))+":"+str(int(i[1]))+":"+str(int(i[2]))+","
  config.set(section, 'keyp_colors', skeyp_colors[0:-1])

  skeyp_colors_sparks_sensitivity=""
  for i in prefs.keyp_colors_sparks_sensitivity:
    skeyp_colors_sparks_sensitivity += str(round(i,2))+","
  config.set(section, 'keyp_colors_sparks_sensitivity', skeyp_colors_sparks_sensitivity[0:-1])

  spercolor_sensitivity=""
  for i in prefs.percolor_delta:
    spercolor_sensitivity += str(round(i,2))+","
  config.set(section, 'percolor_sensitivity', spercolor_sensitivity[0:-1])
  config.set(section, 'use_percolor_sensitivity', str( int(prefs.use_percolor_delta) ))

  skeys_pos=""
  for i in prefs.keys_pos:
    skeys_pos+= str(int(i[0]))+":"+str(int(i[1]))+","
  config.set(section, 'keys_pos', skeys_pos[0:-1])

  s=""
  for i in prefs.keyp_colors_alternate:
    s+= str(int(i[0]))+":"+str(int(i[1]))+":"+str(int(i[2]))+","
  config.set(section, 'keyp_colors_alternate', s[0:-1])
  #
  s=""
  for i in prefs.keyp_colors_alternate_sensitivity:
    s+= str(int(i))+","
  config.set(section, 'keyp_colors_alternate_sensitivity', s[0:-1])

  with open(settingsfile, 'w') as configfile:
    config.write(configfile)
  pass





def loadsettings( cfgfile ):
  print("starting read settings...")

  if not os.path.exists( cfgfile ):
    print("cannot find settings file: "+cfgfile)
    return

  print("reading settings from file: "+cfgfile)
  config = ConfigParser()
  config.read( cfgfile )
  section = 'options'
  if config.has_option(section, 'midi_track_name'):
    prefs.miditrackname = config.get(section, 'midi_track_name')
  if config.has_option(section, 'debug'):
    prefs.debug = config.getboolean(section, 'debug')
  if config.has_option(section, 'notes_overlap'):
    prefs.notes_overlap = config.getboolean(section, 'notes_overlap')
  if config.has_option(section, 'resize'):
    prefs.resize = config.getboolean(section, 'resize')
  if config.has_option(section, 'resize_width'):
    prefs.resize_width = config.getint(section, 'resize_width')
  if config.has_option(section, 'resize_height'):
    prefs.resize_height = config.getint(section, 'resize_height')
  if config.has_option(section, 'minimal_note_duration'):
    prefs.minimal_duration = config.getfloat(section, 'minimal_note_duration')
  if config.has_option(section, 'color_channel_accordance'):
    clr_chnls = config.get(section, 'color_channel_accordance')
  else:
    clr_chnls = ""

  if config.has_option(section, 'channel_prog_accordance'):
    clr_chnls_prog = config.get(section, 'channel_prog_accordance')
  else:
    clr_chnls_prog = ""

  if config.has_option(section, 'ignore_notes_with_minimal_duration'):
    prefs.ignore_minimal_duration = config.getboolean(section, 'ignore_notes_with_minimal_duration')
  if config.has_option(section, 'notes_overlap'):
    prefs.notes_overlap = config.getboolean(section, 'notes_overlap')
  if config.has_option(section, 'sensitivity'):
    prefs.keyp_delta = config.getint(section, 'sensitivity')
  if config.has_option(section, 'octave'):
    prefs.octave = config.getint(section, 'octave')
  #
  if config.has_option(section, 'midi_file_format'):
    midi_file_format = config.getint(section, 'midi_file_format')
    print(midi_file_format)
  if config.has_option(section, 'output_midi_tempo'):
    prefs.tempo = config.getint(section, 'output_midi_tempo')
  if config.has_option(section, 'frame_start'):
    prefs.startframe = config.getint(section, 'frame_start')
  if config.has_option(section, 'blackkey_relative_position'):
    prefs.blackkey_relative_position = config.getfloat(section, 'blackkey_relative_position')

  # Sparks
  if config.has_option(section, 'keyp_spark_y_pos'):
    prefs.keyp_spark_y_pos = config.getint(section, 'keyp_spark_y_pos')

  if config.has_option(section, 'use_sparks'):
    prefs.use_sparks = config.getint(section, 'use_sparks')
  if config.has_option(section, 'use_alternate_keys'):
    prefs.use_alternate_keys = config.getboolean(section, 'use_alternate_keys')

  if ( clr_chnls != "" ):
    prefs.keyp_colors_channel = [ int(x) for x in clr_chnls.split(",") ]
    print("readed color = channel", prefs.keyp_colors_channel)

  if ( clr_chnls_prog != "" ):
    prefs.keyp_colors_channel_prog = [ int(x) for x in clr_chnls_prog.split(",") ]

    print("readed color channel = prog ", prefs.keyp_colors_channel_prog)

  if config.has_option(section, 'xoffset_whitekeys'):
    prefs.xoffset_whitekeys = config.getint(section, 'xoffset_whitekeys')
  if config.has_option(section, 'yoffset_whitekeys'):
    prefs.yoffset_whitekeys = config.getint(section, 'yoffset_whitekeys')
  if config.has_option(section, 'yoffset_blackkeys'):
    prefs.yoffset_blackkeys = config.getint(section, 'yoffset_blackkeys')
  if config.has_option(section, 'whitekey_width'):
    prefs.whitekey_width = config.getint(section, 'whitekey_width')

  if config.has_option(section, 'keyp_colors'):
    skeyp_colors = config.get(section, 'keyp_colors')
    if ( skeyp_colors.strip() != "" ):
      prefs.keyp_colors[:] = []
      for cur in skeyp_colors.split(","):
        c = cur.split(":")
        prefs.keyp_colors.append( [ int(c[0]), int(c[1]),int(c[2]) ])

  if config.has_option(section, 'keyp_colors_sparks_sensitivity'):
    skeyp_colors_sparks_sensitivity = config.get(section, 'keyp_colors_sparks_sensitivity')
    if ( skeyp_colors_sparks_sensitivity.strip() != "" ):
      prefs.keyp_colors_sparks_sensitivity[:] = []
      for cur in skeyp_colors_sparks_sensitivity.split(","):
        prefs.keyp_colors_sparks_sensitivity.append( float(cur) )


  if config.has_option(section, 'keys_pos'):
    skeys_pos = config.get(section, 'keys_pos')
    if ( skeys_pos.strip() != "" ):
      prefs.keys_pos = []
      for cur in skeys_pos.split(","):
        c = cur.split(":")
        prefs.keys_pos.append( [ int(c[0]), int(c[1])  ])
      print( len(prefs.keyp_colors) )
      print( len(prefs.keyp_colors_channel))

  if config.has_option(section, 'keyp_colors_alternate'):
    s = config.get(section, 'keyp_colors_alternate')
    if ( s.strip() != "" ):
      prefs.keyp_colors_alternate[:] = []
      for cur in s.split(","):
        c = cur.split(":")
        print(" Append :" + str(cur))
        prefs.keyp_colors_alternate.append( [ int(c[0]), int(c[1]),int(c[2]) ])
  #
  if config.has_option(section, 'keyp_colors_alternate_sensitivity'):
    s = config.get(section, 'keyp_colors_alternate_sensitivity')
    if ( s.strip() != "" ):
      prefs.keyp_colors_alternate_sensitivity[:] = []
      for cur in s.split(","):
        prefs.keyp_colors_alternate_sensitivity.append( int(cur) )
  if config.has_option(section, 'rollcheck'):
    prefs.rollcheck = config.getboolean(section, 'rollcheck')
  if config.has_option(section, 'rollcheck_priority'):
    prefs.rollcheck_priority = config.getboolean(section, 'rollcheck_priority')

  if config.has_option(section, 'use_percolor_sensitivity'):
    prefs.use_percolor_delta = config.getboolean(section, 'use_percolor_sensitivity')

  if config.has_option(section, 'percolor_sensitivity'):
    s = config.get(section, 'percolor_sensitivity')
    prefs.percolor_delta = [ float(x) for x in s.split(",") ]
    print("percolor_sensitivity", prefs.percolor_delta)
  pass


def compatibleColors(colorBtns):
  while ( len(prefs.keyp_colors) < len(colorBtns) ):
    print("Warning, append array keyp_colors", len(prefs.keyp_colors))
    prefs.keyp_colors.append( [0,0,0] )

  while ( len(prefs.keyp_colors_channel) < len(prefs.keyp_colors) ):
    print("Warning, append array keyp_colors_channel", len(prefs.keyp_colors_channel))
    prefs.keyp_colors_channel.append( len(prefs.keyp_colors_channel) // 2 )

  while ( len(prefs.keyp_colors_channel_prog) < len(prefs.keyp_colors) ):
    print("Warning, append array keyp_colors_channel_prog", len(prefs.keyp_colors_channel_prog))
    prefs.keyp_colors_channel_prog.append(0)
  #
  while len( prefs.percolor_delta ) < len(prefs.keyp_colors):
    prefs.percolor_delta.append(0)
  #
  while ( len(prefs.keyp_colors_sparks_sensitivity) < len(prefs.keyp_colors) ):
    print( 'add sparks',len(prefs.keyp_colors_sparks_sensitivity) , len(prefs.keyp_colors) )
    prefs.keyp_colors_sparks_sensitivity.append(50)
  print('keyp_colors:', len(prefs.keyp_colors) )
  print('keyp_colors_channel:', len(prefs.keyp_colors_channel))

  print('percolor_delta:', len(prefs.percolor_delta))
  print('keyp_colors_sparks_sensitivity:', len(prefs.keyp_colors_sparks_sensitivity))
  pass
