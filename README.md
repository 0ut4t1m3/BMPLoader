# BMPLoader
## Micropython module for handling indexed bitmaps


I've noticed most image libraries for Micropython are either painfully slow or require conversion of the image to a raw format using a PC. As ESP32s often come with MBs of RAM I decided to take advantage of it. This relies heavily on built-in framebuf support for colourspace conversion.
This library will open normal 16 and 256 colour bitmap files from the filesystem and cache them so they can be drawn quickly to the display instead of needing to be reloaded.
Destination can be any framebuf based buffer or display driver.

## Features
- Written in pure Micropython
- Handles native 4 and 8-bit bitmap files
- Transparency support
- Caches image in memory for fast drawing
- Supports loading indexed sprites from an atlas
- Image colourspace conversion to RGB565
- Tested on ESP32 and RP2040

## Requirements
- Requires framebuf so will only work on ports that include it
- Maximum size of loadable image will depend on available memory

## Supported image format
Any standard indexed bitmap should work provided you have enough RAM to load it. Most image editors will allow you to save an indexed bitmap but I would recommend an image editor designed for indexed images such as [Usenti](https://www.coranac.com/projects/usenti/) as this will give you much more control of the final image.

## Functions
### Draw the entire image
```python
BMPLoader.draw(buffer,x=0,y=0,bg=-1)
```
**buffer** - framebuf based buffer to draw the image to

**x**, **y** - image top left corner location on output buffer

**bg** - RGB565 encoded colour to set as transparent. Pixels matching this colour will not be drawn


### Draw an indexed sprite
```python
BMPLoader.draw_index(buffer,x=0,y=0,index=0,bg=-1)
```
**buffer** - framebuf based buffer to draw the image to

**x**, **y** - image top left corner location on output buffer

**index** - select which sprite to draw

**bg** - RGB565 encoded colour to set as transparent. Pixels matching this colour will not be drawn


### Draw a cropped image
```python
BMPLoader.draw_xy(buffer,x=0,y=0,crop_x=0,crop_y=0,bg=-1)
```
**buffer** - framebuf based buffer to draw the image to

**x**, **y** - image top left corner location on output buffer

**crop_x**, **crop_y** - top left corner of window on larger image

**bg** - RGB565 encoded colour to set as transparent. Pixels matching this colour will not be drawn


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

![img1](https://github.com/0ut4t1m3/BMPLoader/assets/12528193/15dc8117-c775-4b84-974f-03715bea5b4b)
```python
from bmploader import BMPLoader

img = BMPLoader('imgfile.bmp')

img.draw(buffer,x=0,y=0,bg=-1)
```

### Indexed sprite
Useful for stateful icons like battery level. The width of each sprite is set at load and can be selected by its index.

![img2](https://github.com/0ut4t1m3/BMPLoader/assets/12528193/7a64e60e-c4fe-4cd5-951f-cda1b7c72173)
```python
from bmploader import BMPLoader

img = BMPLoader('imgfile.bmp',width=20)

img.draw_index(buffer,x=0,y=0,index=2,bg=-1)
```

### Windowed mode
Draw a smaller cropped section of the image. Useful for displaying a pannable image such as a map.

![img3](https://github.com/0ut4t1m3/BMPLoader/assets/12528193/3452f9f8-d3d0-4b72-9b2f-d99b54b146bf)
```python
from bmploader import BMPLoader

img = BMPLoader('imgfile.bmp',width=300,height=300)

img.draw_xy(buffer,x=0,y=0,crop_x=50,crop_y=75,bg=-1)
```

