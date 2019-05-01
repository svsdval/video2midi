# video2midi
youtube synthesia video to midi, just for fun )

Воссоздание midi с видео роликов synthesia и ей подобным..

# dependency / зависимости
- python-opencv
- midiutil

# install dependency / установка зависимостей 
  ```
  sudo apt install python-opencv
  pip install midiutil
  ```

# usage / использование
  ```
  ./v2m.py ./test_video/Not\ Evil\ -\ The\ LEGO\ Movie\ 2\ -\ The\ Second\ Part\ _\ Piano\ Tutorial\ \(Synthesia\)-9mv_hKwCzUo.mkv
  ./v2m.py ./test_video/Gotham\ City\ Guys\ -\ The\ LEGO\ Movie\ 2\ -\ The\ Second\ Part\ _\ Piano\ Tutorial\ \(Synthesia\)-y_aBUQrp5vY.webm
  ```

# in v2m.py parameters / параметры для изменения в исполняемом файле


xoffset_whitekeys - начальное положение (на видео) клавиатуры по X
yoffset_whitekeys - начальное положение (на видео) клавиатуры по Y

# how it works / как это работает

frame by frame we scan the virtual keyboard and write the keys to the midi file...

Кадр за кадром сканируется видео поток отслеживая изменения виртуальной клавиатуры после всё что зафиксировано дампим на винт.

![Alt text](docs/frame47.jpg?raw=true "input from image")

# todo / что сделать

- gui to configure keyboard layouts / добавить гуи для управления виртуальной раскладкой клавиатуры ...
