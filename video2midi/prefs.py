
class prefs:
    debug = 0
    miditrackname="Sample Track"
    notes_overlap = False

    resize= 0
    resize_width=1280
    resize_height=720

    minimal_duration = 0.1
    ignore_minimal_duration = False

    keyp_delta = 90 # sensitivity

    octave = 3
    tempo = 120
    startframe = 1

    blackkey_relative_position = 0.4

    keyp_spark_y_pos = -110
    use_sparks= False

    use_alternate_keys = False
    rollcheck = False
    rollcheck_priority = 0

    keyp_colors_channel =      [ 0,0, 1,1, 2,2, 3,3, 4,4, 5,5, 6,6, 7,7, 8,8, 9,9, 10,10, 11,11 ] # MIDI channel per color
    keyp_colors_channel_prog = [ 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0,  0, 0,  0, 0 ] # MIDI program ID per channel

    xoffset_whitekeys = 60
    yoffset_whitekeys = 673
    yoffset_blackkeys = -30
    whitekey_width=24.6

    keyp_colors_alternate = []
    keyp_colors_alternate_sensitivity = []
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
    [0  ,  0,  0], [  0,  0,  0],
    [0  ,  0,  0], [  0,  0,  0],
    [0  ,  0,  0], [  0,  0,  0],
    [0  ,  0,  0], [  0,  0,  0]
    # .....
    ]
    keyp_colors_sparks_sensitivity = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50]

    keys_pos=[]
    keys_angle = 90
    #
    use_percolor_delta=False
    #
    percolor_delta=[90]*20
    autoclose = 1
    sync_notes_start_pos = False
    sync_notes_start_pos_time_delta = 1000
    save_to_disk_message = ""
    save_to_disk_per_channel = False
