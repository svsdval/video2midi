# video2midi
youtube synthesia video to midi, just for fun )

Воссоздание midi с видео роликов synthesia и ей подобным..
![Alt text](docs/mainwindow.png?raw=true "main window")

[Video example on YouTube](https://youtu.be/AY0wME73Z98)

# dependency / зависимости

- python-opencv
- python-pygame
- python-midiutil

# install dependency / установка зависимостей.

```bash
sudo apt install python-opencv python-pygame python-midiutil
```

# usage / использование

##### RU:
 Скачиваем видео с понравившейся мелодией ( рекомендую 720p ) , запускаем программу, в ней регулируем клавиши жмём Q и после завершения работы будет создан midi файл.
 
##### EN:
 Download the video with your favorite melody (I recommend 720p), launch the program, adjust the keys in it, press Q and after the completion of the work a midi file will be created.

  ```
  ./v2m.py ./synthesia_video.mkv
  ```
  RU:
  Управление:
  * **h** - показать/спрятать помощь
  * **q** - приступить к воссозданию midi
  * **s** - Установить начальный кадр обработки (модификатор: shift, сброс на начальный кадр видео)
  * **e** - Установить конечный кадр обработки (модификатор: shift, сброс на конечный кадр видео), на некоторых форматах, не работает корректно, похоже на баг OpenCV
  * **Mouse wheel** - подстройка клавиш
  * **Левая кнопка мыши** - перетаскивание выбранной клавиши / выбор цвета из карты цветов.
  * **CTRL + Левая кнопка мыши** - обновить выбранный цвет к карте цветов.
  * **Правая кнопка мыши** - перетаскивание всех клавиш, если клавиша выбрана, перенос осуществляется относительно неё 
  * **CTRL + 0** - Выключить выбранный цвет.
  * **Стрелки** - подстройка клавиш  (модификатор: shift)
  * **PageUp/PageDown** - прокрутка видео (модификатор: shift, шаг по кадру)
  * **Home/End** - переход в начало или конец видео
  * **[ / ]** - изменить базовую октаву
  * **ESCAPE** - выход / quit
  * **SPACE** - прервать воссоздание и записать midi файл на диск / abort re-creation and save midi file to disk
  
  EN:
  Control:
  * **h** - show/hide this help
  * **q** - begin to recreate midi
  * **s** - set start frame, (mods : shift, set processing start frame to the beginning)
  * **e** - set end frame, (mods : shift, set processing end frame to the ending), on some formats, it does not work correctly, it seems like an OpenCV bug
  * **Mouse wheel** - keys adjustment
  * **Left mouse button** - dragging the selected key / select color from the color map
  * **CTRL + Left mouse button** - update selected color in the color map
  * **CTRL + 0** - disable selected color in the color map
  * **Right mouse button** - dragging all keys, if the key is selected, the transfer is carried out relative to it.
  * **Arrows** - keys adjustment (mods : shift)
  * **PageUp/PageDown** - scrolling video (mods : shift)
  * **Home/End** - go to the beginning or end of the video
  * **[ / ]** - change base octave
  * **Escape** - quit
  * **Space** - abort re-creation and save midi file to disk

  
# how it works / как это работает

##### RU:
Кадр за кадром сканируется видео поток отслеживая изменения виртуальной клавиатуры после всё что зафиксировано дампим на винт.

##### EN:
Frame by frame we scan the virtual keyboard and write the keys to the midi file...

![Alt text](docs/frame47.jpg?raw=true "input from image")

# Дополнительные возможности / Additional features

##### RU:
Вы можете настроить разбиение на каналы в зависимости от цвета клавиши. Для этого в файле v2m.py нужно поправить соответствие цвета каналу midi трека. 
По умолчанию каждый цвет активирующий клавишу будет записан в собственный канал, таким образом если хотите объединить каналы просто укажите для разных цветов одинаковые номера.

##### EN:
You can also customize the separation into channels depending on the color of the key. To do this, in the v2m.py file, you need to modify the color matching to the midi channel of the track.
By default, each color key will be recorded in its own channel, so if you want to combine the channels, simply specify the same numbers for different colors.

```python
keyp_colors_channel = [ 0,0, 1,1, 2,2, 3,3, 4,4, 5,5 ]; # MIDI channel per color
```

![Alt text](docs/multichannel.png?raw=true "multi channel midi export")

##### RU:
Вы можете настроить соотнесение канала к MIDI инструменту. Для этого в файле v2m.py нужно поправить соответствие канала midi инструменту. 
По умолчанию канал равен 0 midi инструменту

##### EN:
You can customize the channel mapping to a MIDI instrument. To do this, in the v2m.py file, you need to modify the correspondence of the midi channel to the instrument.
The default all channels is 0 midi instrument.

```python
keyp_colors_channel_prog = [ 0,0, 0,0, 0,0, 0,0, 0,0, 0,0 ]; # MIDI program ID per channel

```

##### RU:
Вы так же можете указать минимальную длительность нот, ноты длительность которых будет меньше указанной будут автоматически приравнены минимальной длительности.
Для этого в файле v2m.py необходимо изменить переменные "minimal_duration".

##### EN:
You can also specify the minimum duration of the notes, the notes whose duration will be less than that specified will be automatically equated to the minimum duration.
To do this, in the v2m.py file, you need to modify variables "minimal_duration".

```python
minimal_duration = 0.6;
```

# Экспериментальные возможности / Experimental features:

##### RU:
Добавил возможность распознавать перекрытие клавиш друг другом. В данном случае в момент перекрытия будет создано окончание одной ноты и начало другой. По умолчанию данная функция выключена, в файле v2m.py можно включить её, изменив состояние переменной experimental в 1

##### EN:
Added the ability to recognize the overlap of keys with each other. In this case, at the moment of overlapping, the end of one note and the beginning of another will be created. By default, this function is disabled; in the v2m.py file, you can enable it by changing the state of the experimental variable "experimental" to 1

```python
experimental = 0;
```
