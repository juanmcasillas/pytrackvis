##!/usr/bin/env bash
# -*- coding: utf-8 -*-
# /////////////////////////////////////////////////////////////////////////////
# //
# // altitude.py 
# //
# // 
# //
# // 03/12/2024 12:17:56  
# // (c) 2024 Juan M. Casillas <juanm.casillas@gmail.com>
# //
# /////////////////////////////////////////////////////////////////////////////

from PIL import Image, ImageDraw, ImageFont

from .appenv import *
from .rainbowvis import  SlopeGradient
from .helpers import distancePoints3D


class PNGFactory():
    def __init__(self,outputfname=None, config=None, size=(800,100)):

        self.size = size
        self.color = (102,204,153,255) #rgba (a>255 solid)
        self.fillcolor = (0,153,51,255) # green
        self.fillcolor = (210,210,210,255) # grey
        self.outlinecolor = (51,102,51,255)
        self.bordercolor = (0,0,0,255)
        self.fontcolor = (255,255,255,255)
        self.tickcolor = (255,255,255,255)

        self.outputfname = outputfname
        if config:
            self.size = config.size
            self.color= config.color #RGBA
            self.fillcolor = config.fillcolor
            self.outlinecolor = config.outlinecolor
            self.bordercolor = config.bordercolor
            self.fontcolor = config.fontcolor
            self.tickcolor = config.tickcolor

        # fixed colors

        
        self.fontname = "webapp/static/webfonts/BebasNeue-Regular.otf"
        self.fontsize = 16
        self.gap = (5,5) # space in the sides (padding)


    def CreatePNG(self, gpx, distance=None, elevation=None, optimize=False, full_featured=True, draw_border=True):

        points = gpx.tracks[0].segments[0].points
        
        # remove al 0,0 points
        points = list(filter(lambda x: x.latitude!=0.0 and x.longitude!=0.0 and x.elevation!=0.0, points))
        
        # start working. Create a PNG with the given size, with the altitude profile for the track.

        img = Image.new("RGBA", self.size, color=self.fillcolor)

        xgap,ygap = self.gap

        (min_elevation, max_elevation) = gpx.get_elevation_extremes()
        # to fix THEORIC tracks (no elevation)
        if min_elevation == None: min_elevation = 0.0
        if max_elevation == None: max_elevation = 0.0
  
        
        if elevation == None:
            delta_elevation = (max_elevation - min_elevation + (ygap*2))
        else:
            ##delta_elevation = elevation
            delta_elevation = (max_elevation - min_elevation + (ygap*2))
            
        if distance == None:
            track_length = float(gpx.tracks[0].segments[0].length_3d())
        else:
            track_length = distance

        # empty
        if track_length == 0:
            return img
        
        
        xincr = 0
        yincr = 0
        
        if track_length >0:
            xincr = (self.size[0]-(2*xgap)) / float(track_length)
        
        if delta_elevation > 0:
            yincr = (self.size[1]-(2*ygap)) / float(delta_elevation)


        fill_points = []
        ticks = []

        y = 0
        x = 0
        d = 0
        slope = 0.0
        rainbow = SlopeGradient()
        dm = ImageDraw.Draw(img)
    
        for i in range(len(points)):

            distance_delta = 0.0 
            elevation_delta = 0.0
            slope = 0.0
            
            if i > 0:
                
                elevation_delta = points[i].elevation - points[i-1].elevation
                distance_delta = distancePoints3D(points[i-1], points[i])
                slope = points[i].slope_avg
                
                d += distance_delta
     
            x = (d*xincr)+xgap

            if i == 0:
                if points[0].elevation == None: points[0].elevation = 0.0
                
                y = (self.size[1]-ygap) - (yincr * (points[0].elevation - min_elevation + (ygap*2)))
                #y = (self.size[1]-ygap) - (yincr * (min_elevation)) 
            else:
                if points[i-1].elevation == None: points[i-1].elevation = 0.0
                
                y = (self.size[1]-ygap) - (yincr * (points[i-1].elevation - min_elevation + (ygap*2)))
                #y = (self.size[1]-ygap) - (yincr * (points[i-1].elevation - min_elevation + (ygap*2)))
                #y = (self.size[1]-ygap) - (yincr * (min_elevation)) 

            if distance_delta > 0.0:
                fill_points.append((x,y, slope))
            ticks.append( (x, self.size[1]-ygap))
        
        fill_points = [ (xgap, self.size[1]-ygap, 0.0 ) ] + fill_points # bottom left (first)
        
        if x < self.size[0]-xgap:
            x = self.size[0]-xgap
        fill_points.append( (x, self.size[1]-ygap, 0.0)  ) # bottom right (last)
            
        fill_points_clean = []
        #draw the polygons
        
        for i in range(len(fill_points)-1):
            px,py,ps = fill_points[i]
            qx,qy,qs = fill_points[i+1]
        
            poly = [ (px, self.size[1]-ygap), (px, py), (qx, qy), (qx, self.size[1]-ygap) ]  
            #dm.polygon(poly, fill="#%s" % rainbow.colourAt(ps), outline=(0,0,0))
            dm.polygon(poly, fill="#%s" % rainbow.colourAt(ps))
            
            # clean the top line.
            fill_points_clean.append( (px, py) )
        # the last one
       
        px,py,ps = fill_points[i+1]
        fill_points_clean.append( (px, py) )
        
        fill_points = fill_points_clean
    
        
        ###remove-me for line-based draw
        #dm.polygon(fill_points, fill=self.fillcolor, outline=self.outlinecolor)
        dm.polygon(fill_points, outline=self.outlinecolor)
        
        
        #dm.polygon(ticks,fill=self.fontcolor, outline=self.f)


        if full_featured:
            # draw ticks, axis and so on

            d = 0.0
            scaleh = (self.size[0]-2*xgap) / float(track_length) # pixel -> 1m
            scalev = (self.size[1]-2*xgap) / float(delta_elevation) # pixel -> 1m

            while d <= self.size[0]-2*xgap:
                dm.line( [ d+xgap, self.size[1]-ygap, d+xgap, self.size[1]-ygap-3 ], fill=self.tickcolor )
                d+= (scaleh*500)

            d = self.size[1]-ygap
            while d >= xgap:
                dm.line( [ xgap, d, xgap+3, d ], fill=self.tickcolor )
                d-= (scalev*50)

            dm.line( [ (xgap, self.size[1]-ygap ), (x, self.size[1]-ygap ) ], fill=self.tickcolor) # horizontal tick
            dm.line( [ (xgap, self.size[1]-ygap ), (xgap, ygap ) ], fill=self.tickcolor) # vertical tick

        #fill_points = fill_points[1:-1]
        #pygame.draw.lines( self.mapimg, self.config.colors.line.colortuple, False, fill_points, 3)
        if draw_border:
            dm.rectangle( [ (0,0), (self.size[0]-1, self.size[1]-1)], outline=self.bordercolor )
        #pygame.draw.rect(self.mapimg, self.config.colors.border.colortuple, (0,0,self.mapimg.get_rect().width, self.mapimg.get_rect().height),1)



        if full_featured:
            max_r_v = "%3.2f m (max)" % max_elevation
            min_r_v = "%3.2f m (min)" % min_elevation
            len_r_v = "%3.2f Km distance" % (int(track_length)/1000.0)
            alt_r_v = "%3.2f m Climb" % (elevation if elevation is not None else 0.0)
            scale_h_v   = "1:500h/1:50v"

            font = ImageFont.truetype(self.fontname, self.fontsize)
            dm.text((self.gap[0]+2,self.gap[1]+2), max_r_v, self.fontcolor, font=font)
            dm.text((self.gap[0]+2,self.size[1]-25), min_r_v, self.fontcolor, font=font)
            dm.text((self.size[0]-len(len_r_v)*6,self.gap[1]+2), len_r_v, self.fontcolor, font=font)
            dm.text((self.size[0]-len(alt_r_v)*6,self.gap[1]+20), alt_r_v, self.fontcolor, font=font)
            dm.text((self.size[0]-len(scale_h_v)*6,self.size[1]-25), scale_h_v, self.fontcolor, font=font)
        else:
            # don't show anything
            self.fontname = "www/css/fonts/MyriadPro-Regular.otf"
            self.fontsize=13
            self.fontcolor = (20,20,20,255)
            font = ImageFont.truetype(self.fontname, self.fontsize-3)
            lab_v = "%3.2f Km / %3.2f m" % ((int(track_length)/1000.0), elevation)
            #dm.text((self.gap[0]+5,self.size[1]-20), lab_v, self.fontcolor, font=font)
            dm.text((5,2), lab_v, self.fontcolor, font=font)


        if self.outputfname:
            fp = open(self.outputfname,"wb+")
            img.save(fp, "PNG")
            fp.close()
        return img

