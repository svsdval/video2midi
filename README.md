# video2midi
youtube synthesia video to midi, just for fun )

Воссоздание midi с видео роликов synthesia и ей подобным..

# dependency / зависимости

- python-opencv
- python-pygame
- midiutil

# install dependency / установка зависимостей.
  ```
  sudo apt install python-opencv python-pygame
  pip install midiutil
  ```

# usage / использование
 RU:
 Скачиваем видео с понравившейся милодией ( рекомендую 720p ) , запускаем программу, в ней регулируем клавиши жмём Q и после завершения работы будет создан midi файл.
 
 EN:
 Download the video with your favorite melody (I recommend 720p), launch the program, adjust the keys in it, press Q and after the completion of the work a midi file will be created.

  ```
  ./v2m.py ./test_video/Not\ Evil\ -\ The\ LEGO\ Movie\ 2\ -\ The\ Second\ Part\ _\ Piano\ Tutorial\ \(Synthesia\)-9mv_hKwCzUo.mkv
  ./v2m.py ./test_video/Gotham\ City\ Guys\ -\ The\ LEGO\ Movie\ 2\ -\ The\ Second\ Part\ _\ Piano\ Tutorial\ \(Synthesia\)-y_aBUQrp5vY.webm
  ```

  Управление:
  * **Стрелки** - подстройка клавиш / keys adjustment
  * **PageUp/PageDown** - прокрутка видео / scrolling video 
  * **Q** - приступить к воссозданию midi / begin to recreate midi
  * **ESCAPE** - выход / quit
  * **Левая кнопка мыши** - перетаскивание выбранной клавиши / dragging the selected key
  * **Правая кнопка мыши** - перетаскивание всех клавиш, если клавиша выбрана, перенос осуществляется относительно неё / dragging all keys, if the key is selected, the transfer is carried out relative to it.

# how it works / как это работает

frame by frame we scan the virtual keyboard and write the keys to the midi file...

Кадр за кадром сканируется видео поток отслеживая изменения виртуальной клавиатуры после всё что зафиксировано дампим на винт.

![Alt text](docs/frame47.jpg?raw=true "input from image")
