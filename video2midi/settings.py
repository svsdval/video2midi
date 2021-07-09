try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0

from video2midi.prefs import prefs

def savesettings():
 global minimal_duration,keyp_colors_channel,keyp_colors_channel_prog,xoffset_whitekeys,yoffset_whitekeys,yoffset_blackkeys,whitekey_width,keyp_colors,keys_pos,ignore_minimal_duration,keyp_delta,screen,tempo,width,height;
 global colorBtns,colorWindow_colorBtns_channel_labels;
 global keyp_colors_alternate_sensetivity, keyp_colors_alternate,keyp_spark_y_pos,use_sparks;
 global rollcheck;

 print("save settings to file")
 config = ConfigParser();
 section='options';
 config.add_section(section);
 config.set(section, 'midi_track_name', prefs.miditrackname);
 config.set(section, 'debug', str(int(prefs.debug)));
 config.set(section, 'notes_overlap', str(int(prefs.notes_overlap)));
 config.set(section, 'resize', str(int(prefs.resize)));
 config.set(section, 'resize_width', str(prefs.resize_width));
 config.set(section, 'resize_height', str(prefs.resize_height));
 config.set(section, 'minimal_note_duration', str(prefs.minimal_duration));
 config.set(section, 'ignore_notes_with_minimal_duration', str(int(prefs.ignore_minimal_duration)));
 config.set(section, 'sensitivity', str(int(prefs.keyp_delta)));
 config.set(section, 'output_midi_tempo', str(int(prefs.tempo)));
 config.set(section, 'blackkey_relative_position', str(float(prefs.blackkey_relative_position)));
 #Sparks 
 config.set(section, 'keyp_spark_y_pos', str(int(prefs.keyp_spark_y_pos)));
 config.set(section, 'use_sparks', str( int(prefs.use_sparks) ));
 # Roll Check
 config.set(section, 'rollcheck', str( int(prefs.rollcheck) ));
 
 
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
 config.set(section, 'yoffset_blackkeys',str(int(yoffset_blackkeys)));
 config.set(section, 'whitekey_width',str(int(whitekey_width)));

 skeyp_colors="";
 for i in keyp_colors:
  skeyp_colors+= str(int(i[0]))+":"+str(int(i[1]))+":"+str(int(i[2]))+",";
 config.set(section, 'keyp_colors', skeyp_colors[0:-1]);

 skeyp_colors_sparks_sensitivity="";
 for i in keyp_colors_sparks_sensitivity:
  skeyp_colors_sparks_sensitivity += str(round(i,2))+",";
 config.set(section, 'keyp_colors_sparks_sensitivity', skeyp_colors_sparks_sensitivity[0:-1]);

 skeys_pos="";
 for i in keys_pos:
  skeys_pos+= str(int(i[0]))+":"+str(int(i[1]))+",";
 config.set(section, 'keys_pos', skeys_pos[0:-1]);
  
 s="";
 for i in keyp_colors_alternate:
  s+= str(int(i[0]))+":"+str(int(i[1]))+":"+str(int(i[2]))+",";
 config.set(section, 'keyp_colors_alternate', s[0:-1]);
 # 
 s="";
 for i in keyp_colors_alternate_sensetivity:
  s+= str(int(i))+",";
 config.set(section, 'keyp_colors_alternate_sensetivity', s[0:-1]);
  
 with open(settingsfile, 'w') as configfile:
    config.write(configfile);
 pass;