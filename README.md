# video2midi
youtube synthesia video to midi, just for fun )

# dependency 
- python-opencv
- midiutil

# install dependency
  ```
  sudo apt install python-opencv
  pip install midiutil
  ```

# usage 
  ```
  ./v2m.py ./test_video/Not\ Evil\ -\ The\ LEGO\ Movie\ 2\ -\ The\ Second\ Part\ _\ Piano\ Tutorial\ \(Synthesia\)-9mv_hKwCzUo.mkv
  ./v2m.py ./test_video/Gotham\ City\ Guys\ -\ The\ LEGO\ Movie\ 2\ -\ The\ Second\ Part\ _\ Piano\ Tutorial\ \(Synthesia\)-y_aBUQrp5vY.webm
  ```

# in v2m.py parameters

xoffset_whitekeys = 5 # 40 for avengers, else 5

yoffset_whitekeys = 673

yoffset_blackkeys = 637
xoffset_blackkeys = xoffset_whitekeys + 10

# how it works

frame by frame we scan the virtual keyboard and write the keys to the midi file...

![Alt text](docs/image47.jpg?raw=true "input from image")

# todo

- gui to configure keyboard layauts