#BMPLoader - Micropython module for handling indexed bitmaps
#Copyright (C) 2024 0ut4t1m3

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <https://www.gnu.org/licenses/>.

import framebuf
import gc

class BMPLoader:
    def __init__(self,imgfile,width=None,height=None):
        
        self.__sprwidth  = width
        self.__sprheight = height

        with open(imgfile, 'rb') as f:
            b=bytearray(54)
            b=f.read(54)
            bmp_id = b[0:2]
            self.width = b[18] + (b[19]<<8) + (b[20]<<16) +(b[21]<<24)
            self.height = b[22] + (b[23]<<8) + (b[24]<<16) +(b[25]<<24)
            bits_per_pixel = b[28] + (b[29]<<8)
            compression = b[30] + (b[31]<<8) + (b[32]<<16) +(b[33]<<24)
            total_cols = b[46] + (b[47]<<8) + (b[48]<<16) +(b[49]<<24)
            
            #check image is valid
            assert bmp_id == b"BM", \
                "Not a valid BMP file"
            assert compression == 0, \
                "Compression is not supported"
            assert 3 < bits_per_pixel < 9, \
                f"Only 16 and 265 colour bitmaps are supported"
            if width:
                assert width <= self.width, \
                    f"Sprite width must be within image dimensions ({self.width})"
            if height:
                assert height <= self.height, \
                    f"Sprite height must be within image dimensions ({self.height})"
                
            if self.width % 8:
                padding = 8 - self.width % 8
            else:
                padding = 0    
                
            #set up palette
            if bits_per_pixel == 4:
                palette = framebuf.FrameBuffer(bytearray(32), 16, 1, framebuf.RGB565)
            else:    
                palette = framebuf.FrameBuffer(bytearray(512), 256, 1, framebuf.RGB565)
            b = bytearray(4)
            for i in range(total_cols):
                b = f.read(4)
                palette.pixel(i,0,self.rgb(b[2],b[1],b[0]))    
            
            #set up image buffer, width aligned to 8 bits
            in_mv  = memoryview(f.read())
            out_mv = memoryview(bytearray(((self.width + padding) * self.height) // (2 if bits_per_pixel == 4 else 1)))
            
            #bmp format has 0,0 at the bottom right so we need to mirror the y axis
            bmplen = ((self.width + padding) * self.height) // (2 if bits_per_pixel == 4 else 1)
            linewid = (self.width + padding) // (2 if bits_per_pixel == 4 else 1)
            #this looks ugly but works, we use memoryview to slice the buffer into lines and remap
            for y in range(self.height):
                out_mv[bmplen-(y*linewid+linewid):bmplen-(y*linewid)] = in_mv[y*linewid:y*linewid+linewid]
            
            tempbuff = framebuf.FrameBuffer(out_mv, self.width + padding, self.height, framebuf.GS4_HMSB if bits_per_pixel == 4 else framebuf.GS8)
            
            #initilise buffer to the proper frame size and colourspace
            self.__imgbuff = framebuf.FrameBuffer(bytearray(self.width * self.height * 2), self.width, self.height, framebuf.RGB565)
            self.__imgbuff.blit(tempbuff,0,0,-1,palette)
            
            #if we're using the sprite functions set up a buffer to handle the sprite
            if width:
                self.__tile = framebuf.FrameBuffer(bytearray(width * (height if height else self.height) * 2), width, height if height else self.height, framebuf.RGB565)
        gc.collect()
        
    #RGB565 conversion
    def rgb(self,r,g,b):
        return ((r & 0xf8) << 5) | ((g & 0x1c) << 11) | (b & 0xf8) | ((g & 0xe0) >> 5)
        
    #draw image to given framebuffer
    def draw(self,buffer,x=0,y=0,bg=-1):
        buffer.blit(self.__imgbuff,x,y,bg)
        
    #draw image sprite in index mode
    def draw_index(self,buffer,x=0,y=0,index=0,bg=-1):
        assert self.__sprwidth, f"Index mode called without correct initilisation"
        self.__tile.blit(self.__imgbuff, -self.__sprwidth * index, 0)
        buffer.blit(self.__tile,x,y,bg)
        
    #draw image sprite in xy mode
    def draw_xy(self,buffer,x=0,y=0,crop_x=0,crop_y=0,bg=-1):
        assert self.__sprheight, f"XY mode called without correct initilisation"
        self.__tile.blit(self.__imgbuff, -crop_x, -crop_y)
        buffer.blit(self.__tile,x,y,bg)

