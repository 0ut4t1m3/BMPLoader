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


from struct import unpack
import framebuf
import gc

class BMPLoader:
    def __init__(self,imgfile,width=None,height=None):
        
        self.__sprwidth  = width
        self.__sprheight = height

        with open(imgfile, 'rb') as f:
            data = f.read(14)
            BMP_id = data[0:2]
            data = f.read(4)
            DIB_len = unpack("<I", data[0:4])[0]
            data = f.read(DIB_len - 4)
            DIB_w = unpack("<I", data[0:4])[0]
            DIB_h = unpack("<I", data[4:8])[0]
            DIB_depth = unpack("<H", data[10:12])[0]
            DIB_comp = unpack("<I", data[12:16])[0]
            DIB_plt_num_info = unpack("<I", data[28:32])[0]
            self.width  = DIB_w
            self.height = DIB_h
            
            #check image is valid
            assert BMP_id == b"BM", \
                "Not a valid BMP file"
            assert DIB_comp == 0, \
                "Compression is not supported"
            assert 3 < DIB_depth < 9, \
                "Only 16 and 265 colour bitmaps are supported"
            if width:
                assert width <= DIB_w, \
                    f"Sprite width must be within image dimensions ({DIB_w})"
            if height:
                assert height <= DIB_h, \
                    f"Sprite height must be within image dimensions ({DIB_h})"
                
            if DIB_w % 8:
                padding = 8 - DIB_w % 8
            else:
                padding = 0    
                
            #set up palette
            if DIB_depth == 4:
                palette = framebuf.FrameBuffer(bytearray(32), 16, 1, framebuf.RGB565)
            else:    
                palette = framebuf.FrameBuffer(bytearray(512), 256, 1, framebuf.RGB565)
            for i in range(DIB_plt_num_info):
                    data = f.read(4)
                    palette.pixel(i,0,self.rgb(data[2],data[1],data[0]))    
            
            #set up image buffer, width aligned to 8 bits
            in_mv  = memoryview(f.read())
            out_mv = memoryview(bytearray(((DIB_w + padding) * DIB_h) // (2 if DIB_depth == 4 else 1)))
            
            #bmp format has 0,0 at the bottom right so we need to mirror the y axis
            bmplen = ((DIB_w + padding) * DIB_h) // (2 if DIB_depth == 4 else 1)
            linewid = (DIB_w + padding) // (2 if DIB_depth == 4 else 1)
            #this looks ugly but works, we use memoryview to slice the buffer into lines and remap
            for y in range(DIB_h):
                out_mv[bmplen-(y*linewid+linewid):bmplen-(y*linewid+1)] = in_mv[y*linewid:y*linewid+linewid-1]
            
            tempbuff = framebuf.FrameBuffer(out_mv, DIB_w + padding, DIB_h, framebuf.GS4_HMSB if DIB_depth == 4 else framebuf.GS8)
            
            #initilise buffer to the proper frame size and colourspace
            self.__imgbuff = framebuf.FrameBuffer(bytearray(DIB_w * DIB_h * 2), DIB_w, DIB_h, framebuf.RGB565)
            self.__imgbuff.blit(tempbuff,0,0,-1,palette)
            
            #if we're using the sprite functions set up a buffer to handle the sprite
            if width:
                self.__tile = framebuf.FrameBuffer(bytearray(width * (height if height else DIB_h) * 2), width, height if height else DIB_h, framebuf.RGB565)
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

