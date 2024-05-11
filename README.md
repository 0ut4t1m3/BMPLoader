# BMPLoader
## Micropython module for handling indexed bitmaps


I've noticed most image libraries for Micropython are either painfully slow or require conversion of the image to a raw format using a PC. As ESP32s often come with MBs of RAM I decided to take advantage of it. This relies heavily on built-in framebuf support for colourspace conversion.
This library will open normal 16 and 256 colour bitmap files from the filesystem and cache them so they can be drawn quickly to the display instead of needing to be reloaded.
Destination can be any framebuf based buffer or display driver.

## Features
- Written in pure Micropython
- Handles native 4 and 8-bit bitmap files
- Transparency support
- Caches loaded image in memory for fast drawing
- Supports loading indexed sprites from an atlas
- Image colourspace conversion to RGB565
- Tested on ESP32 and RP2040

## Requirements
- Requires framebuf and struct libraries so will only work on ports that include them
- Maximum size of loadable image will depend on available memory

## Supported image format
Any standard indexed bitmap should work provided you have enough RAM to load it. Most image editors will allow you to save an indexed bitmap but I would recommend an image editor designed for indexed images such as [Usenti](https://www.coranac.com/projects/usenti/) as this give you much more control of the final image.

## Commands
### Draw the entire image
```python
BMPLoader.draw(buffer,x=0,y=0,bg=-1)
```
**buffer** - framebuf based buffer to draw the image to

**x**, **y** - top left corner of image, can be neagtive

**bg** - colour to set as transparent. Pixels matching this colour will not be drawn


### Draw an indexed sprite
```python
BMPLoader.draw_index(buffer,x=0,y=0,index=0,bg=-1)
```
**buffer** - framebuf based buffer to draw the image to

**x**, **y** - top left corner of image, can be neagtive

**index** - select which sprite to draw

**bg** - colour to set as transparent. Pixels matching this colour will not be drawn


### Draw a cropped image
```python
BMPLoader.draw_xy(buffer,x=0,y=0,crop_x=0,crop_y=0,bg=-1)
```
**buffer** - framebuf based buffer to draw the image to

**x**, **y** - top left corner location on output buffer

**crop_x**, **crop_y** - top left corner of window on larger image

**bg** - colour to set as transparent. Pixels matching this colour will not be drawn


### RGB565 colour conversion
```python
BMPLoader.rgb(r,g,b)
```
**r**, **g**, **b** - RGB colour to convert

*returns* encoded colour value



## Usage
There are three different methods that can be used to draw an image to a buffer
### Full image
This will draw the entire image to the buffer based on the top left starting position.
```python
from bmploader import BMPLoader

img = BMPLoader('imgfile.bmp')

img.draw(buffer,x=0,y=0,bg=-1)
```

### Indexed sprite
Useful for stateful icons like battery level. The width of each sprite is set at load and can be selected by its index.
```python
from bmploader import BMPLoader

img = BMPLoader('imgfile.bmp',width=20)

img.draw_index(buffer,x=0,y=0,index=2,bg=-1)
```

### Windowed mode
Draw a smaller cropped section of the image. Useful for displaying a pannable image such as a map.
```python
from bmploader import BMPLoader

img = BMPLoader('imgfile.bmp',width=50,height=50)

img.draw_xy(buffer,x=0,y=0,crop_x=50,crop_y=75,bg=-1)
```

