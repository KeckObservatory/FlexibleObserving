import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as pch
import matplotlib.ticker as tkr
import shutil as sh
import pandas as pd
import numpy as np
import urllib.request as url
import db_conn_mongo as dcm
import json
from datetime import datetime as dt
from datetime import date
from random import random

class Oopgui:
    """
    Contains all the values to be used in image generation for
    the web tool as well as the values to be stored in database
    and DDF (XML) file for local storage. It can be used in place
    of the java tool.

    @type fig: matplotlib figure
    @param fig: stores the canvas on which the figure is drawn
    @type ax: matplotlib axis
    @param ax: the current plot axis which is modified to produce
        the appropriate scale and markings
    @type mode: string
    @param mode: which CCD the tool will use (spec, imag, both)
    @type object: string
    @param object: name of the object being observed
    @type objPattern: string
    @param objPattern: Mode of the dither pattern being used
        for the object frame
    @type skyPattern: string
    @param skyPattern: Mode of the dither pattern being used
        for the sky frame
    @type measurement: string
    @param measurement: Unit the movement of the frame should be
        measured (arcsec or lenslet)
    @type aomode: string
    @param aomode: Type of AO being used (NGS or LGS)
    @type queueDir: string
    @param queueDir: Location of queue directory to move DDFs to
        when they are to be used for observation
    @type ddfname: string
    @param ddfname: name of the file
    @type gridScale: float
    @param gridScale: Scale at which to place tick marks
    @type boxWidth: float
    @param boxWidth: width of the CCD on the screen
    @type boxHeight: float
    @param boxHeight: height of the CCD on the screen
    @type filters: dictionary
    @param filters: collection of filters and their physical
        characteristics. See the function for the specifics
    @type oriX: float
    @param oriX: x-coordinate of the origin
    @type oriY: float
    @param oriY: y-coordinate of the origin
    @type xMin: float
    @param xMin: Minimum x-value of the grid
    @type xMax: float
    @param xMax: Maximum x-value of the grid
    @type yMin: float
    @param yMin: Minimum y-value of the grid
    @type yMax: float
    @param yMax: Maximum y-value of the grid
    @type scale: float
    @param scale: arcsec-to-lenslet ratio
    @type specX: float
    @param specX: spec x-offset for drawing the box on the grid
    @type specY: float
    @param specY: spec y-offset for drawing the box on the grid
    @type imagX: float
    @param imagX: imager x-offset for the center of the diamond
    @type imagY: float
    @param imagY: imager y-offset for the center of the diamond
    @type initOffX: float
    @param initOffX: Initial x-offset given by the user
    @type initOffY: float
    @param initOffY: Initial y-offset given by the user
    @type nodOffX: float
    @param nodOffX: Additional x-offset for sky frames given by user
    @type nodOffY: float
    @param nodOffY: Additional y-offset for sky frames given by user
    @type objLenX: float
    @param objLenX: X-Distance to move additional frames in the dither
        pattern as defined by the user. Used for BoxN and Raster Scan
    @type objHgtY: float
    @param objHgtY: Y-Distance to move additional frames in the dither
        pattern as defined by the user. Used for BoxN and Raster Scan
    @type offDefs: dictionary
    @param offDefs: Directions to move the frames for BoxN when additional
        offsets are given by the user.
    @type draw: dictionary
    @param draw: collection of the draw functions to be called using
        the spec and image mode
    @type 
    """
    def __init__(self):
        # Initial planning params
        self.mode = 'spec'
        self.object = 'none'
        self.objPattern = 'Stare'
        self.skyPattern = 'None'
        self.coordSys = 'arcsec'
        self.unitScale = 1.0
        self.pa = 0.0
        self.aomode = 'NGS'
        self.queueDir = '~/'
        self.ddfname = 'webtest.ddf'
        self.gridScale = 4.0 #0.8
        self.boxWidth = 0.32
        self.boxHeight = 1.28
        self.filters = SpecFilters()
        self.colorList = self.gen_color(1)
        self.schedurl = 'https://www.keck.hawaii.edu/software/db_api/telSchedule.php?'
        self.propurl = 'https://www.keck.hawaii.edu/software/db_api/proposalsAPI.php?'

        # Observing Parameters
        self.oriX = 0.0
        self.oriY = 0.0
        self.xMin = -16.0
        self.xMax = 16.1
        self.yMin = -16.0
        self.yMax = 16.1

        self.scale = 1.0
        self.specX = -0.16
        self.specY = -0.64
        self.imagX = -14.388
        self.imagY = -15.138
        self.initOffX = 0.0
        self.initOffY = 0.0
        self.nodOffX = 0.0
        self.nodOffY = 0.0
        self.objLenX = 0.0
        self.objHgtY = 0.0
        self.skyLenX = 0.0
        self.skyHgtY = 0.0
        self.offDefs = {
                'Stare':[(0,0)],
                'Box4':[(0,0), (1,0), (1,-1), (0,-1)],
                'Box5':[(0,0),(-1,1),(1,1),(1,-1),(-1,-1)],
                'Box9':[(0,0),(-1,1),(-1,-1),(1,1),(1,-1),
                        (-1,0),(1,0),(0,1),(0,-1)],
                'Dither':{'frames':1, 'length':1.0, 'height':1.0},
                'Raster':{'frames':9,'rows':1,'xstep':1.0, 'ystep':1.0},
            }
        self.imgFilters = [
                'Opn','Y','J','Hbb','Kp','Zbb',
                'Jn1','Jn2','Jn3','Hn1','Hn2',
                'Hn3','Hn4','Hn5','Kn1','Kn2',
                'Kn3','Kn4','Kn5','Zn3','Brγ',
                'Kcnt','HeIB','Paγ','FeII',
                'Hcnt','Drk'
            ]
        self.fullMask = {
                'O':'Open Circ',
                'P':'Pupil View',
                'A':'Large Ann',
                'a':'Small Ann',
                'H':'Large Hex',
                'h':'Small Hex'
            }
        self.imgFilter = 'Opn'
        self.mask = 'Open Circ'
        self.draw = {
                'None':self.draw_none,
                'Stare':self.draw_stare,
                'Box4':self.draw_box4,
                'Box5':self.draw_box5,
                'Box9':self.draw_box9,
                'Statistical Dither':self.draw_stat,
                'Raster Scan':self.draw_raster,
                'User Defined':self.draw_user
            }

    # End __init__()

    def hsv_to_rgb(self, h, s, v):
        """
        Martin Ankerl's hsv to rgb converter
        from https://martin.ankerl.com/2009/12/09/
        how-to-create-random-colors-programmatically

        @type  h: double
        @param h: hue
        @type  s: double
        @param s: saturation
        @type  v: double
        @param v: value
        """
        h_i = int(h*6)
        f = h*6 - h_i
        p = v * (1 - s)
        q = v * (1 - f*s)
        t = v * (1 - (1 - f) * s)
        if h_i == 0: rgb = (v, t, p)
        elif h_i == 1: rgb = (q, v, p)
        elif h_i == 2: rgb = (p, v, t)
        elif h_i == 3: rgb = (p, q, v)
        elif h_i == 4: rgb = (t, p, v)
        elif h_i == 5: rgb = (v, p, q)
        return rgb

    def gen_color(self, num):
        """
        Martin Ankerl's color generator based on Phi distributions

        @type num: int
        @param num: Number of colors to produce

        @return returns a list of rgb tuples with values [0,1)
        """
        PHI = 0.618033988749895
        s = 0.5
        v = 0.95
        h = random()
        colorList = []
        for i in range(num):
            h += PHI
            h %= 1
            rgb = self.hsv_to_rgb(h,s,v)
            colorList.append(rgb)
        return colorList

    def set_queue_dir(self, qdir):
        """
        Sets the directory of the queue to where
        the observing tool pulls config files from.

        @type qdir: string
        @param qdir: absolute directory of the queue folder
        """
        self.queueDir = qdir

    def rescale(self):
        """
        Looks at the coordinates of the objects being drawn
        to figure out what the grid tick scale should be.
        """
        # Initialize some variables to keep track of the current
        # min and max x values
        minX = 0
        maxX = 0
        minY = 0
        maxY = 0

        # Look at the object pattern to determine an initial
        # min and max based off of initOffX and initOffY given
        # by the user
        if self.objPattern != 'None':
            if self.initOffX < 0:
                minX -= self.initOffX
                maxX -= self.initOffX
            elif self.initOffX > 0:
                minX += self.initOffX
                maxX += self.initOffX
            if self.initOffY < 0:
                minY -= self.initOffY
                maxY -= self.initOffY
            elif self.initOffX > 0:
                minY += self.initOffY
                maxY += self.initOffY
            if self.objPattern != 'User Defined':
                minX -= abs(self.objLenX)
                maxX += abs(self.objLenX)
                minY -= abs(self.objHgtY)
                maxY += abs(self.objHgtY)
            elif self.objPattern == 'User Defined':
                for i in range(0, len(self.defs), 3):
                    if float(self.defs[i]) < minX:
                        minX = float(self.defs[i])
                    if float(self.defs[i]) > maxX:
                        maxX = float(self.defs[i])
                    if float(self.defs[i+1]) < minY:
                        minY = float(self.defs[i+1])
                    if float(self.defs[i+1]) > maxY:
                        maxY = float(self.defs[i+1])
        # Check if the skyPattern changes any min or max
        if self.skyPattern not in ['None', 'User Defined']:
            if self.initOffX + self.nodOffX - abs(self.skyLenX) < minX:
                minX = self.initOffX + self.nodOffX - abs(self.skyLenX)
            if self.initOffX + self.nodOffX + abs(self.skyLenX) > maxX:
                maxX = self.initOffX + self.nodOffX + abs(self.skyLenX)
            if self.initOffY + self.nodOffY - abs(self.skyHgtY) < minY:
                minY = self.initOffY + self.nodOffY - abs(self.skyHgtY)
            if self.initOffY + self.nodOffY + abs(self.skyHgtY) > maxY:
                maxY = self.initOffY + self.nodOffY + abs(self.skyHgtY)
        elif self.skyPattern == 'User Defined':
            for i in range(0, len(self.defs), 3):
                if self.initOffX + self.nodOffX + float(self.defs[i]) < minX:
                    minX = self.initOffX + self.nodOffX + float(self.defs[i])
                if self.initOffX + self.nodOffX + float(self.defs[i]) > maxX:
                    maxX = self.initOffX + self.nodOffX + float(self.defs[i])
                if self.initOffY + self.nodOffY + float(self.defs[i+1]) < minY:
                    minY = self.initOffY + self.nodOffY + float(self.defs[i+1])
                if self.initOffY + self.nodOffY + float(self.defs[i+1]) > maxY:
                    maxY = self.initOffY + self.nodOffY + float(self.defs[i+1])

        # Set the min and max based on the determined value from above
        # and the scale of the filter selected.
        if self.mode == 'spec':
            self.xMin = minX - 1.0*self.scale/0.02
            self.xMax = maxX + 1.0*self.scale/0.02
            self.yMin = minY - 1.0*self.scale/0.02
            self.yMax = maxY + 1.0*self.scale/0.02
        elif self.mode == 'imag':
            self.xMin = minX + self.imagX - 14.3
            self.xMax = maxX + self.imagX + 14.3
            self.yMin = minY + self.imagY - 14.3
            self.yMax = maxY + self.imagY + 14.3
        else: # self.mode == both
            xMinSpec = minX - 1.0*self.scale/0.02
            xMaxSpec = maxX + 1.0*self.scale/0.02
            yMinSpec = minY - 1.0*self.scale/0.02
            yMaxSpec = maxY + 1.0*self.scale/0.02

            xMinImag = minX + self.imagX - 14.3
            xMaxImag = maxX + self.imagX + 14.3
            yMinImag = minY + self.imagY - 14.3
            yMaxImag = maxY + self.imagY + 14.3

            self.xMin = xMinSpec if xMinSpec < xMinImag else xMinImag
            self.xMax = xMaxSpec if xMaxSpec > xMaxImag else xMaxImag
            self.yMin = yMinSpec if yMinSpec < yMinImag else yMinImag
            self.yMax = yMaxSpec if yMaxSpec > yMaxImag else yMaxImag

        self.xMin = int(self.xMin)-1
        self.xMax = int(self.xMax)+1
        self.yMin = int(self.yMin)-1
        self.yMax = int(self.yMax)+1

        # Calculate the difference between min and max
        xDiff = self.xMax - self.xMin
        yDiff = self.yMax - self.yMin

        # Make both ranges the same as the larger one
        if xDiff > yDiff:
            self.yMin -= 0.5*(xDiff-yDiff)
            self.yMax += 0.5*(xDiff-yDiff)
        elif yDiff > xDiff:
            self.xMin -= 0.5*(yDiff-xDiff)
            self.xMax += 0.5*(yDiff-xDiff)

        gridScale = (self.xMax - self.xMin)/8.0

        # Add a scale increment to the max so that
        # they don't get cut off by a section
        self.xMax += gridScale
        self.yMax += gridScale

        return gridScale

    def draw_fig(self):
        """
        Draws a figure based on the values set in the object variables
        """
        # create a mathplotlib figure that's 8in x 8in
        self.fig = plt.figure(figsize=(8,8))
        self.ax = self.fig.gca()
        self.ax.xaxis.set_major_formatter(tkr.FormatStrFormatter('%10.1f"'))
        self.ax.yaxis.set_major_formatter(tkr.FormatStrFormatter('%10.1f"'))
        self.ax.set_xticks(np.arange(self.xMin, self.xMax, self.gridScale))
        self.ax.set_yticks(np.arange(self.yMin, self.yMax, self.gridScale))

        # Activate the draw function for the correct pattern
        self.draw[self.objPattern]('obj')
        self.draw[self.skyPattern]('sky')
        self.add_origin()
        self.add_ref()

    def add_origin(self):
        """
        Creates the circle at the origin of the object frame
        """
        self.ax.add_patch(
            pch.Circle(
                (self.oriX,self.oriY),
                radius=0.025*self.gridScale,
                fill=False,
                color='red'
            )
        )

    def add_ref(self):
        """
        Creates a box at the centroid reference
        """
        self.ax.add_patch(
            pch.Rectangle(
                (-0.015*self.gridScale,-0.015*self.gridScale),
                0.03*self.gridScale,
                0.03*self.gridScale,
                fill=False
            )
        )

    def add_obj_box(self, xpos, ypos, index):
        """
        Creates an object box around the given x and y positions

        @type xpos: float
        @param xpos: x position around which to draw the object box
        @typp ypos: float
        @param ypos: y position around which to draw the object box
        """
        if self.objPattern == 'User Defined':
            initOffX = 0
            initOffY = 0
        else:
            initOffX = self.initOffX
            initOffY = self.initOffY
        return pch.Rectangle(
            (self.specX+initOffX+xpos*self.objLenX,
            self.specY+initOffY+ypos*self.objHgtY),
            self.boxWidth,
            self.boxHeight,
            fill = False,
            linewidth = 3,
            color = self.colorList[index]
        )

    def add_sky_box(self, xpos, ypos, index):
        """
        Creates a sky box around the given x and y positions

        @type xpos: float
        @param xpos: x position around which to draw the sky box
        @type ypos: float
        @param ypos: y position around which to draw the sky box
        """
        if self.skyPattern == 'User Defined':
            initOffX = 0
            initOffY = 0
            nodOffX = 0
            nodOffY = 0
        else:
            initOffX = self.initOffX
            initOffY = self.initOffY
            nodOffX = self.nodOffX
            nodOffY = self.nodOffY
        return pch.Rectangle(
            (self.specX+initOffX+nodOffX+xpos*self.skyLenX,
            self.specY+initOffY+nodOffY+ypos*self.skyHgtY),
            self.boxWidth,
            self.boxHeight,
            fill = False,
            linewidth = 3,
            color = self.colorList[index]
        )

    def add_obj_diamond(self, xpos, ypos, index):
        """
        Creates an object diamond around the given x and y positions

        @type xpos: float
        @param xpos: x position around which to draw the object diamond
        @type ypos: float
        @param ypos: y position around which to draw the object diamond
        """
        # Tilt offset for the image CCD
        xoff = np.cos(np.radians(47.5))
        yoff = np.sin(np.radians(47.5))
        if self.objPattern == 'User Defined':
            initOffX = 0
            initOffY = 0
        else:
            initOffX = self.initOffX
            initOffY = self.initOffY
        return pch.Polygon(
            np.array(
                [
                    [self.imagX - 14.3 + initOffX
                            + xoff + xpos*self.objLenX,
                        self.imagY + 0 + initOffY
                            - yoff + ypos*self.objHgtY],
                    [self.imagX + 0 + initOffX
                            - xoff + xpos*self.objLenX,
                        self.imagY + 14.3 + initOffY
                            - yoff + ypos*self.objHgtY],
                    [self.imagX + 14.3 + initOffX
                            - xoff + xpos*self.objLenX,
                        self.imagY + 0 + initOffY
                            + yoff + ypos*self.objHgtY],
                    [self.imagX + 0 + initOffX
                            + xoff + xpos*self.objLenX,
                        self.imagY -14.3 + initOffY
                            + yoff + ypos*self.objHgtY]
                ]
            ),
            fill = False,
            linewidth = 3,
            color = self.colorList[index]
        )

    def add_sky_diamond(self, xpos, ypos, index):
        """
        Creates a sky diamond around the given x and y positions

        @type xpos: float
        @param xpos: x position around which to draw the sky diamond
        @type ypos: float
        @param ypos: y position around which to draw the sky diamond
        """
        # Tilt offset for the imager CCD
        xoff = np.cos(np.radians(47.5))
        yoff = np.sin(np.radians(47.5))
        if self.skyPattern == 'User Defined':
            initOffX = 0
            initOffY = 0
            nodOffX = 0
            nodOffY = 0
        else:
            initOffX = self.initOffX
            initOffY = self.initOffY
            nodOffX = self.nodOffX
            nodOffY = self.nodOffY
        return pch.Polygon(
            np.array(
                [
                    [self.imagX -14.3 + initOffX
                        + nodOffX + xoff + xpos*self.skyLenX,
                    self.imagY +0 + initOffY + nodOffY
                        - yoff + ypos*self.skyHgtY],
                    [self.imagX + 0 + initOffX
                        + nodOffX - xoff + xpos*self.skyLenX,
                    self.imagY + 14.3 + initOffY + nodOffY
                        - yoff + ypos*self.skyHgtY],
                    [self.imagX + 14.3 + initOffX + nodOffX
                        - xoff + xpos*self.skyLenX,
                    self.imagY +0 + initOffY + nodOffY
                        + yoff + ypos*self.skyHgtY],
                    [self.imagX + 0 + initOffX + nodOffX
                        + xoff + xpos*self.skyLenX,
                    self.imagY - 14.3 + initOffY + nodOffY
                        + yoff + ypos*self.skyHgtY]
                ]
            ),
            fill = False,
            linewidth = 3,
            color = self.colorList[index]
        )

    def draw_none(self, ditherType):
        """
        Placeholder function to prevent problems where one of the
        dither patterns is 'None'
        """
        pass

    def draw_stare(self, ditherType):
        """
        Draws a stare pattern on the figure depending on the
        selected mode of the instrument and the stored values
        """
        # Check if the mode takes a spec integration
        if self.mode in ['spec','both']:
            # Check if the object or sky box pattern is Stare
            if self.objPattern == 'Stare' and ditherType=='obj':
                self.ax.add_patch(self.add_obj_box(
                        self.offDefs[self.objPattern][0][0],
                        self.offDefs[self.objPattern][0][1],
                        0))
            if self.skyPattern == 'Stare' and ditherType=='sky':
                self.ax.add_patch(self.add_sky_box(
                        self.offDefs[self.skyPattern][0][0],
                        self.offDefs[self.skyPattern][0][1],
                        self.objFrames1*self.objFrames2+0))
        # Check if the mode takes an imager integration
        if self.mode in ['imag','both']:
            # Check if the object or sky diamond pattern is Stare
            if self.objPattern == 'Stare' and ditherType=='obj':
                self.ax.add_patch(self.add_obj_diamond(
                        self.offDefs[self.objPattern][0][0],
                        self.offDefs[self.objPattern][0][1],
                        0))
            if self.skyPattern == 'Stare' and ditherType=='sky':
                self.ax.add_patch(self.add_sky_diamond(
                        self.offDefs[self.skyPattern][0][0],
                        self.offDefs[self.skyPattern][0][1],
                        self.objFrames1*self.objFrames2+0))

    def draw_box4(self, ditherType):
        """
        Draws a box4 pattern on the figure using the stored values
        """
        # Check if the mode takes a spec integration
        if self.mode in ['spec','both']:
            # check if the object or sky box pattern is Box4
            if self.objPattern == 'Box4' and ditherType=='obj':
                for i in range(4):
                    self.ax.add_patch(self.add_obj_box(
                            self.offDefs[self.objPattern][i][0],
                            self.offDefs[self.objPattern][i][1],
                            i))
            if self.skyPattern == 'Box4' and ditherType=='sky':
                for i in range(4):
                    self.ax.add_patch(self.add_sky_box(
                            self.offDefs[self.skyPattern][i][0],
                            self.offDefs[self.skyPattern][i][1],
                            self.objFrames1*self.objFrames2+i))
        # Check if the mode takes an imager integration
        if self.mode in ['imag','both']:
            # Check if the object or sky diamond pattern is Box4
            if self.objPattern == 'Box4' and ditherType=='obj':
                for i in range(4):
                    self.ax.add_patch(self.add_obj_diamond(
                            self.offDefs[self.objPattern][i][0],
                            self.offDefs[self.objPattern][i][1],
                            i))
            if self.skyPattern == 'Box4' and ditherType=='sky':
                for i in range(4):
                    self.ax.add_patch(self.add_sky_diamond(
                            self.offDefs[self.skyPattern][i][0],
                            self.offDefs[self.skyPattern][i][1],
                            self.objFrames1*self.objFrames2+i))

    def draw_box5(self, ditherType):
        """
        Draws a box5 pattern on the figure using the stored values
        """
        # Check if the mode takes a spec integration
        if self.mode in ['spec','both']:
            # Check if the obj or sky box pattern is Box5
            if self.objPattern == 'Box5' and ditherType=='obj':
                for i in range(5):
                    self.ax.add_patch(self.add_obj_box(
                            self.offDefs[self.objPattern][i][0],
                            self.offDefs[self.objPattern][i][1],
                            i))
            if self.skyPattern == 'Box5' and ditherType=='sky':
                for i in range(5):
                    self.ax.add_patch(self.add_sky_box(
                            self.offDefs[self.skyPattern][i][0],
                            self.offDefs[self.skyPattern][i][1],
                            self.objFrames1*self.objFrames2+i))
        # Check if the mode takes an imager integration
        if self.mode in ['imag','both']:
            # Check if the obj or sky diamond pattern is Box5
            if self.objPattern == 'Box5' and ditherType=='obj':
                for i in range(5):
                    self.ax.add_patch(self.add_obj_diamond(
                            self.offDefs[self.objPattern][i][0],
                            self.offDefs[self.objPattern][i][1],
                            i))
            if self.skyPattern == 'Box5' and ditherType=='sky':
                for i in range(5):
                    self.ax.add_patch(self.add_sky_diamond(
                            self.offDefs[self.skyPattern][i][0],
                            self.offDefs[self.skyPattern][i][1],
                            self.objFrames1*self.objFrames2+i))

    def draw_box9(self, ditherType):
        """
        Draws a Box9 pattern on the figure using the stored values
        """
        # Check if the mode takes a spec integration
        if self.mode in ['spec','both']:
            # Check if the obj or sky box pattern is Box9
            if self.objPattern == 'Box9' and ditherType=='obj':
                for i in range(9):
                    self.ax.add_patch(self.add_obj_box(
                            self.offDefs[self.objPattern][i][0],
                            self.offDefs[self.objPattern][i][1],
                            i))
            if self.skyPattern == 'Box9' and ditherType=='sky':
                for i in range(9):
                    self.ax.add_patch(self.add_sky_box(
                            self.offDefs[self.skyPattern][i][0],
                            self.offDefs[self.skyPattern][i][1],
                            self.objFrames1*self.objFrames2+i))
        # Check if the mode takes an image integration
        if self.mode in ['imag','both']:
            # Check if the obj or sky diamond pattern is Box9
            if self.objPattern == 'Box9' and ditherType=='obj':
                for i in range(9):
                    self.ax.add_patch(self.add_obj_diamond(
                            self.offDefs[self.objPattern][i][0],
                            self.offDefs[self.objPattern][i][1],
                            i))
            if self.skyPattern == 'Box9' and ditherType=='sky':
                for i in range(9):
                    self.ax.add_patch(self.add_sky_diamond(
                            self.offDefs[self.skyPattern][i][0],
                            self.offDefs[self.skyPattern][i][1],
                            self.objFrames1*self.objFrames2+i))

    def draw_stat(self):
        """
        To be done in the future... Creates a randomly generated
        statistical dither pattern based on user input
        """
        pass

    def draw_raster(self):
        """
        To be done in the future... Uses an iterative Raster Scan
        approach to take methodical integrations over the sky
        """
        pass

    def draw_user(self, ditherType):
        """
        Uses user defined values to draw boxes and diamonds on the
        figure
        """
        # Iterate through the definitions provided by
        # the user in groups of 3
        for i in range(0,len(self.defs),3):
            if self.mode in ['spec','both']:
                if self.defs[i+2]=="false" and ditherType=='obj':
                    self.ax.add_patch(
                            self.add_obj_box(
                                float(self.defs[i]),
                                float(self.defs[i+1]),
                                int(i/3)
                            )
                        )
                elif self.defs[i+2]=="true" and ditherType=='sky':
                    self.ax.add_patch(
                            self.add_sky_box(
                                float(self.defs[i]),
                                float(self.defs[i+1]),
                                int(i/3)
                            )
                        )
            if self.mode in ['imag','both']:
                if self.defs[i+2]=="false" and ditherType=='obj':
                    self.ax.add_patch(
                            self.add_obj_diamond(
                                float(self.defs[i]),
                                float(self.defs[i+1]),
                                int(i/3)
                            )
                        )
                elif self.defs[i+2]=="true" and ditherType=='sky':
                    self.ax.add_patch(
                            self.add_sky_diamond(
                                float(self.defs[i]),
                                float(self.defs[i+1]),
                                int(i/3)
                            )
                        )

    def update(self, qstr):
        """
        Takes the values sent from the webform and stores them in
        the object then produces a new graphic to be returned to the
        webpage.

        @type qstr: dictionary
        @param qstr: Contains the values from the webform to update
            the oopgui object and then creates a new figure to be
            returned to the webpage
        """
        # Extract the values from the JSON object and store it in
        # the proper member variables

        self.keckID = qstr['keckID']
        self.ddfname = qstr['ddfname']
        if '.ddf' not in self.ddfname:
            self.ddfname = ''.join((self.ddfname, '.ddf'))
        self.imgMode = qstr['imgMode']
        if self.imgMode == 'Disabled':
            self.mode = 'spec'
            self.imgMode = 'Disabled (Spec only)'
        elif self.imgMode == 'Independent':
            self.mode = 'imag'
            self.imgMode = 'Independent (Imager only)'
        else:
            self.mode = 'both'
            if self.imgMode == 'Slave1': self.imgMode = 'Slave 1: Maximum Repeats'
            elif self.imgMode == 'Slave2': self.imgMode = 'Slave 2: Maximum Itime'
            elif self.imgMode == 'Slave4': self.imgMode = 'Slave 4: Filter Sets'
        self.dataset = qstr['dataset']
        self.object = qstr['object']
        self.targType = qstr['targType']
        self.coordSys = qstr['coordSys']
        self.units = qstr['units']
        self.pa = qstr['pa']
        self.aoType = qstr['aoType']
        self.lgsMode = qstr['lgsMode']
        self.specFilter = qstr['specFilter']
        self.scale = float(qstr['scale'])
        self.specCoadds = qstr['specCoadds']
        self.specItime = qstr['specItime']
        self.initOffX = float(qstr['initOffX'])
        self.initOffY = float(qstr['initOffY'])
        self.objPattern = qstr['objPattern']
        self.objFrames1 = int(qstr['objFrames1'])
        self.objFrames2 = int(qstr['objFrames2'])
        self.objLenX = float(qstr['objLenX'])
        self.objHgtY = float(qstr['objHgtY'])
        self.imgFilter = qstr['imgFilter']
        self.repeats = qstr['repeats']
        self.imgCoadds = qstr['imgCoadds']
        if self.imgMode == 'Slave 4: Filter Sets': self.imgItime = qstr['imgItime']
        else: self.imgItime = float(qstr['imgItime'])
        self.nodOffX = float(qstr['nodOffX'])
        self.nodOffY = float(qstr['nodOffY'])
        self.skyPattern = qstr['skyPattern']
        self.skyFrames1 = int(qstr['skyFrames1'])
        self.skyFrames2 = int(qstr['skyFrames2'])
        self.skyLenX = float(qstr['skyLenX'])
        self.skyHgtY = float(qstr['skyHgtY'])
        self.defs = qstr['defs'][0].split(',')

        # Use the proper unitScale depending on the lenslet size
        if self.coordSys == 'lenslet':
            self.unitScale = self.scale
        else:
            self.unitScale = 1.0
        
        # Generate a color list based on the number of frames
        numFrames = self.objFrames1*self.objFrames2+self.skyFrames1*self.skyFrames2
        self.colorList = self.gen_color(numFrames)

        # Update spec values based on specfilter
        self.boxWidth = self.filters[self.specFilter][str(self.scale)][0]
        self.boxHeight = self.filters[self.specFilter][str(self.scale)][1]
        self.specX = -self.filters[self.specFilter][str(self.scale)][0]/2.0
        self.specY = -self.filters[self.specFilter][str(self.scale)][1]/2.0
        if self.specFilter == 'Zn4':
            self.oriX = -self.boxWidth / 4.0
        elif self.specFilter == 'Jn1':
            self.oriX = self.boxWidth / 4.0
        elif self.specFilter == 'Jn2':
            self.oriX = self.boxWidth / 10.0
        elif self.specFilter in ['Jn4','Hn4','Kn4','Kc4']:
            self.oriX = -self.boxWidth / 10.0
        elif self.specFilter in ['Hn1','Kn1']:
            self.oriX = self.boxWidth / 6.0
        elif self.specFilter in ['Hn2','Kn2']:
            self.oriX = self.boxWidth / 18.0
        elif self.specFilter == 'Hn5':
            self.oriX = self.boxWidth / 4.0
        elif self.specFilter in ['Kn5','Kc5']:
            self.oriX = -9.0*self.boxWidth / 32.0
        else:
            self.oriX = 0.0

        # Rescale the gridScale based on the extracted values
        self.gridScale = self.rescale()
        #self.print_all()
        # Redraw the figure based on the extracted values
        self.draw_fig()
        #self.fig.tight_layout()
        # draw the arrow in the upper right corner
        #quivx = self.xMax - 0.1*(self.xMax + abs(self.xMin))
        #quivy = self.yMax - 0.1*(self.yMax + abs(self.yMin))
        #a = self.ax.quiver(quivx, quivy, [0,-1], [1,0], units='inches',
        #        pivot='tail', minlength=3)
        #self.ax.quiverkey(a,.8,.8,2,'N',coordinates='figure')
        # Apply the grid for visual scale
        self.ax.grid()

    def print_all(self):
        print('keckID:',self.keckID)
        print('mode  :',self.mode)
        print('fname :',self.dataset)
        print('object:',self.object)
        print('target:',self.targType)
        print('coords:',self.coordSys)
        print('aotype:',self.aoType)
        print('lgsmod:',self.lgsMode)
        print('sfiltr:',self.specFilter)
        print('scale :',self.scale)
        print('coadds:',self.specCoadds)
        print('itime :',self.specItime)
        print('offX  :',self.initOffX)
        print('offY  :',self.initOffY)
        print('pattrn:',self.objPattern)
        print('frames:',self.objFrames1)
        print('oblenx:',self.objLenX)
        print('obhgty:',self.objHgtY)
        print('ifiltr:',self.imgFilter)
        print('repeat:',self.repeats)
        print('icoadd:',self.imgCoadds)
        print('iitime:',self.imgItime)
        print('nodx  :',self.nodOffX)
        print('nody  :',self.nodOffY)
        print('skypat:',self.skyPattern)
        print('sframe:',self.skyFrames1)
        print('slenx :',self.skyLenX)
        print('shgty :',self.skyHgtY)
        print('defs  :',self.defs)
        print('xmin  :',self.xMin)
        print('xmax  :',self.xMax)
        print('ymin  :',self.yMin)
        print('ymax  :',self.yMax)
        print('gscale:',self.gridScale)

    def dither_out(self):
        """

        """
        out = ''
        line1 = ''
        line2 = ''
        # Determine the object portion of the dither pattern
        if 'Stare' == self.objPattern:
            line1 = ''.join(('\t\t\t<ditherPosition sky="false" xOff="',
                str(self.initOffX+self.offDefs["Stare"][0][0]*self.objLenX), 
                '" yOff="',
                str(self.initOffY+self.offDefs["Stare"][0][1]*self.objHgtY),
                '" />\n'))
        elif 'Box4' == self.objPattern:
            for i in range(4):
                line1 = ''.join((line1, '\t\t\t<ditherPosition sky="false" xOff="',
                        str(self.initOffX+self.offDefs["Box4"][i][0]*self.objLenX),
                        '" yOff="',
                        str(self.initOffY+self.offDefs["Box4"][i][1]*self.objHgtY),
                        '" />\n'))
        elif 'Box5' == self.objPattern:
            for i in range(5):
                line1 = ''.join((line1, '\t\t\t<ditherPosition sky="false" xOff="',
                        str(self.initOffX+self.offDefs["Box5"][i][0]*self.objLenX),
                        '" yOff="',
                        str(self.initOffY+self.offDefs["Box5"][i][1]*self.objHgtY),
                        '" />\n'))
        elif 'Box9' == self.objPattern:
            for i in range(9):
                line1 = ''.join((line1, '\t\t\t<ditherPosition sky="false" xOff="',
                        str(self.initOffX+self.offDefs["Box9"][i][0]*self.objLenX),
                        '" yOff="',
                        str(self.initOffY+self.offDefs["Box9"][i][1]*self.objHgtY),
                        '" />\n'))
        elif 'User Defined' in self.objPattern:
            for i in range(0, self.objFrames1*3, 3):
                line1 = ''.join((line1, '\t\t\t<ditherPosition sky="false" xOff="', 
                        self.defs[i],'" yOff="', self.defs[i+1], '" />\n'))
        elif 'Raster Scan' == self.objPattern:
            pass
        elif 'Statistical Dither' == self.objPattern:
            pass

        # Determine the sky portion of the dither pattern
        if 'Stare' == self.skyPattern:
            line2 = ''.join(('\t\t\t<ditherPosition sky="true" xOff="',
                str(self.initOffX+self.nodOffX+self.offDefs["Stare"][0][0]*self.skyLenX),
                '" yOff="',
                str(self.initOffY+self.nodOffY+self.offDefs["Stare"][0][1]*self.skyHgtY),
                '" />\n'))
        elif 'Box4' == self.skyPattern:
            for i in range(4):
                line2 = ''.join((line2, '\t\t\t<ditherPosition sky="true" xOff="',
                        str(self.initOffX+self.nodOffX+self.offDefs["Box4"][i][0]*self.skyLenX),
                        '" yOff="',
                        str(self.initOffY+self.nodOffY+self.offDefs["Box4"][i][1]*self.skyHgtY),
                        '" />\n'))
        elif 'Box5' == self.skyPattern:
            for i in range(5):
                line2 = ''.join((line2, '\t\t\t<ditherPosition sky="true" xOff="',
                        str(self.initOffX+self.nodOffX+self.offDefs["Box5"][i][0]*self.skyLenX),
                        '" yOff="',
                        str(self.initOffY+self.nodOffY+self.offDefs["Box5"][i][1]*self.skyHgtY),
                        '" />\n'))
        elif 'Box9' == self.skyPattern:
            for i in range(9):
                line2 = ''.join((line2, '\t\t\t<ditherPosition sky="true" xOff="',
                        str(self.initOffX+self.nodOffX+self.offDefs["Box9"][i][0]*self.skyLenX),
                        '" yOff="',
                        str(self.initOffY+self.nodOffY+self.offDefs["Box9"][i][1]*self.skyHgtY),
                        '" />\n'))
        elif 'User Defined' in self.skyPattern:
            for i in range(self.objFrames1*3, (self.objFrames1+self.skyFrames1)*3, 3):
                line2 = ''.join((line2, '\t\t\t<ditherPosition sky="true" xOff="',
                        self.defs[i],'" yOff="', self.defs[i+1], '" />\n'))
        elif 'Raster Scan' == self.skyPattern:
            pass
        elif 'Statistical Dither' == self.skyPattern:
            pass
        out = ''.join((line1, line2))
        return out

    def imgFrameOut(self):
        """
        Function that reads the imgMode and returns the output for image frames
        """
        out = ''
        filters = self.imgFilter.split(',')
        repeats = self.repeats.split(',')
        coadds = self.imgCoadds.split(',')
        itime = self.imgItime.split(',')

        for i in range(len(filters)):
            print(filters[i])
            fil, mask = filters[i].split('-')
            out = ''.join([out, '\t\t\t<imagFrame',
                ' filter="', fil,
                '" mask="', self.fullMask[mask],
                '" itime="', itime[i],
                '" coadds="', coadds[i],
                '" repeats="', repeats[i],
                '" />\n'])
        print('output of imgFrameOut: ', out)
        return out

    def save_to_file(self):
        """
        Save the current configuration as a DDF (XML) file
        locally
        """
        if '.ddf' not in self.ddfname:
            ''.join((self.ddfname, '.ddf'))
        ddfdir = ''.join(('docs/',self.ddfname))
        with open(ddfdir, 'w') as ddf:
            ddf.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            ddf.write(''.join(('<ddf version="1.0" type="', self.targType,'">\n')))
            self.dataset = self.dataset.replace('<','&lt;').replace('>','&gt;')
            if self.aoType == 'LGS': aoVal = ''.join((self.aoType, '_', self.lgsMode))
            else: aoVal = self.aoType
            ddf.write(''.join(('\t<dataset name="', self.dataset,
                    '" setnum="0" aomode="', aoVal, '" status="Modified">\n')))
            self.object = self.object.replace('<','&lt;').replace('>','&gt;')
            ddf.write(''.join(('\t\t<object>', self.object,'</object>\n')))
            ddf.write(''.join(('\t\t<spec filter="', self.specFilter, '" scale="',
                    str(self.scale), '&quot; / lenslet" itime="', self.specItime,
                    '" coadds="', self.specCoadds,'" />\n')))
            if 'Disabled' in self.imgMode:
                ddf.write(''.join(('\t\t<imag mode="', self.imgMode, '" />\n')))
            elif 'Slave 4' in self.imgMode:
                ddf.write(''.join(('\t\t<imag mode="', self.imgMode, '">\n')))
                ddf.write(self.imgFrameOut())
            else:
                ddf.write(''.join(('\t\t<imag mode="', self.imgMode, '">\n')))
                ddf.write(''.join(('\t\t\t<imagFrame filter="', self.imgFilter,
                        '" mask="', self.mask,
                        '" itime="', str(self.imgItime),
                        '" coadds="', str(self.imgCoadds),
                        '" repeats="', str(self.repeats), '" />\n')))
                ddf.write('\t\t</imag>\n')
            ddf.write(''.join(('\t\t<objectDither type="', self.objPattern,'" ',
                    'frames1="', str(self.objFrames1), '" ',
                    'frames2="', str(self.objFrames2), '" ',
                    'param1="', str(self.objLenX), '" ',
                    'param2="', str(self.objHgtY), '" ',
                    'xOffset="', str(self.initOffX), '" ',
                    'yOffset="', str(self.initOffY), '" />\n')))
            ddf.write(''.join(('\t\t<skyDither type="', self.skyPattern, '" ',
                    'frames1="', str(self.skyFrames1), '" ',
                    'frames2="', str(self.skyFrames2), '" ',
                    'param1="', str(self.skyLenX), '" ',
                    'param2="', str(self.skyHgtY), '" ',
                    'nodXOffset="', str(self.nodOffX), '" ',
                    'nodYOffset="', str(self.nodOffY), '"/>\n')))
            ddf.write(''.join(('\t\t<ditherPattern coords="', self.coordSys,'" ',
                    'units="', self.units, '" skyPA="', self.pa,'" >\n')))
            ddf.write(self.dither_out())
            ddf.write('\t\t</ditherPattern>\n')
            ddf.write('\t\t<reduction>\n')
            ddf.write(''.join(('\t\t\t<reductionParameter ',
                    'name="Spatially Rectify Spectrum" instrument="spec" ',
                    'doStep="true" filechoice="Use instrument default" />\n')))
            ddf.write(''.join(('\t\t\t<reductionParameter ',
                    'name="Divide by Flat Field" instrument="spec" ',
                    'doStep="true" filechoice="Use instrument default" />\n')))
            ddf.write(''.join(('\t\t\t<reductionParameter ',
                    'name="Interpolate 1D" instrument="spec" ',
                    'doStep="true" filechoice="Use instrument default" />\n')))
            ddf.write(''.join(('\t\t\t<reductionParameter ',
                    'name="Wavelength Solution" instrument="spec" ',
                    'doStep="true" filechoice="Use instrument default" />\n')))
            ddf.write(''.join(('\t\t\t<reductionParameter ',
                    'name="Interpolate 3D" instrument="spec" ',
                    'doStep="true" filechoice="Not Applicable" />\n')))
            ddf.write(''.join(('\t\t\t<reductionParameter ',
                    'name="Subtract Sky" instrument="spec" ',
                    'doStep="true" filechoice="Use instrument default" />\n')))
            ddf.write(''.join(('\t\t\t<reductionParameter ',
                    'name="Make Data Cube" instrument="spec" ',
                    'doStep="true" filechoice="Not Applicable" />\n')))
            ddf.write(''.join(('\t\t\t<reductionParameter ',
                    'name="Correct Dispersion" instrument="spec" ',
                    'doStep="true" filechoice="Use instrument default" />\n')))
            ddf.write(''.join(('\t\t\t<reductionParameter ',
                    'name="Correct Telluric Lines" instrument="spec" ',
                    'doStep="true" filechoice="Use instrument default" />\n')))
            ddf.write(''.join(('\t\t\t<reductionParameter ',
                    'name="Correct OH Lines" instrument="spec" ',
                    'doStep="true" filechoice="Not Applicable" />\n')))
            ddf.write(''.join(('\t\t\t<reductionParameter ',
                    'name="Calibrate Flux" instrument="spec" ',
                    'doStep="true" filechoice="Not Applicable" />\n')))
            ddf.write(''.join(('\t\t\t<reductionParameter ',
                    'name="Clean PSF" instrument="spec" doStep="true" ',
                    'filechoice="Use instrument default" />\n')))
            ddf.write(''.join(('\t\t\t<reductionParameter ',
                    'name="Mosaic Dithered Frames" instrument="spec" ',
                    'doStep="true" filechoice="Not Applicable" />\n')))
            ddf.write('\t\t</reduction>\n')
            ddf.write('\t</dataset>\n')
            ddf.write('</ddf>\n')
        print('File saved')
        return True

    def get_p_codes(self, keckid):
        codes = []
        currDate = dt.now()
        currDate = date(currDate.year, currDate.month, currDate.day)
        currSem = self.get_semester(currDate)
        URL = ''.join((self.schedurl,'cmd=getScheduleByUser&obsid=',
                keckid))
        obsURL = ''.join((URL,'&type=observer&semester=',currSem))
        try:
            res = url.urlopen(obsURL).read().decode('utf-8')
        except:
            print('not in obs list')
        try:
            res = json.loads(res)
            #print(res)
            for prog in res:
                #print(prog['Instrument'])
                if 'OSIRIS' in prog['Instrument']:
                    pcode = prog['ProjCode']
                    yr,mo,dy = prog['Date'].split('-')
                    obsDate = date(int(yr),int(mo),int(dy))
                    sem = self.get_semester(obsDate)
                    semid = ''.join((sem,"_",pcode))
                    if semid not in codes:
                        codes.append(semid)
        except:
            print('no data to extract')

        piURL = ''.join((URL, '&type=pi&semester=', currSem)) 
        try:
            res = url.urlopen(piURL).read().decode('utf-8')
        except:
            print('Not in pi list')
        try:
            res = json.loads(res)
            for prog in res:
                if 'OSIRIS' in prog['Instrument']:
                    pcode = prog['ProjCode']
                    yr,mo,dy = prog['Date'].split('-')
                    obsDate = date(int(yr),int(mo),int(dy))
                    sem = self.get_semester(obsDate)
                    semid = ''.join((sem,"_",pcode))
                    if semid not in codes:
                        codes.append(semid)
        except:
            print('No pi data to extract')

        tooURL = ''.join((self.schedurl, 'cmd=getToO&obsid=', keckid,
                '&semester=', currSem)) 
        #print(tooURL)
        try:
            res = url.urlopen(tooURL).read().decode('utf-8')
        except:
            print('Not in ToO list')
        try:
            res = json.loads(res)
            for prog in res:
                if 'OSIRIS' in prog['InstrumentList']:
                    pcode = prog['ProjCode']
                    semid = ''.join((currSem,"_",pcode))
                    if semid not in codes:
                        codes.append(semid)
        except:
            print('No too data to extract')
        return codes

    def save_to_db(self, qry):
        """
        Save the current configuration to the database

        @type qry: dictionary
        @param qry: list of user input values from interface
        """
        piID = ''
        semid = qry['semid']
        semester, progname = semid.split('_')
        URL = ''.join((self.schedurl,'cmd=getPI&semid=',
                semid))
        try:
            res = url.urlopen(URL).read().decode()
            res = json.loads(res)
            piID = res[0]['Principal']
            #print(piID)
        except:
            print('not in telschedule, checking ToO')
            try:
                URL = ''.join((self.schedurl, 'cmd=getToO&obsid=',
                qry['keckID'], '&semester=', semester))
                res = url.urlopen(URL).read().decode()
                res = json.loads(res)
                piID = res[0]['PiId']
            except Exception as e:
                print(e)

        URL = ''.join((self.propurl, 'ktn=', semid,
                '&cmd=getTitle'))
        try:
            res = url.urlopen(URL).read().decode()
            print(res)
        except:
            print(e)
            res = "Blank Title"
        title = res
        try:
            mc = dcm.db_conn_mongo('OSIRIS')
            mc.db_connect()
            mc.db = mc.client[mc.database]
            mc.col = mc.db['Configurations']
            qry.pop('Cmd',None)
            #for key in qry:
            #    qry[key] = qry[key]
            qry['piID'] = piID
            qry['progname'] = progname
            qry['semester'] = semester
            qry['progtitl'] = title
            qry['statenam'] = qry['ddfname']
            try:
                mc.col.insert(qry)
            except:
                return False
            else:
                return True
            finally:
                mc.db_close()
        except:
            print('broke in the mongo cnnection')

    def send_to_queue(self):
        """
        Moves the file to the directory set in queueDir
        """
        if '.ddf' not in self.ddfname: ''.join((self.ddfname, '.ddf'))
        try:
            sh.copy(self.ddfname, self.queueDir)
        except:
            print('File was not transferred')

    def load_from_db(self, qstr):
        """
        """
        try:
            keckid = qstr['keckID']
            #print('oopgui keckid: ', keckid)
        except:
            keckid = 0
        semid = qstr.get('semid', '2019A_K999')
        qry = {'keckID':keckid, 'semid':semid}
        #print(qry)

        mc = dcm.db_conn_mongo('OSIRIS')
        mc.db_connect()
        mc.db = mc.client[mc.database]
        mc.col = mc.db['Configurations']

        try:
            result = mc.col.find(qry)
        except:
            print("in except")
            return False
        else:
            print("in else")
            res = []
            for record in result:
                record.pop("_id", None)
                res.append(record)
            return res
        finally:
            mc.db_close()

    def get_semester(self, obsDate=None):
        if obsDate is None: obsDate = date.today()
        sem = str(obsDate.year)
        if obsDate.month > 7 or obsDate.month < 2: sem += 'B'
        else: sem += 'A'
        return sem

def SpecFilters():
    """
    This function returns the filter specifications for all
    the spectrometer filters as a dictionary. Its keys
    are the different filter names that return a dictionary
    of values for the specified filter.

    ## Keys for Filter Value Dictionaries ##
    SEL:     Shortest Extracted Lambda (wavelength, nm)
    LEL:     Longest Extracted Lambda (wavelength, nm)
    NoSC:    Number of Spectral Channels
    NoCS:    Number of Complete Spectra
    ALG:     Approximate Lenslet Geometry
    0.02:    Field of View in 0.02" Scale
    0.035:   Field of View in 0.035" Scale
    0.05:    Field of View in 0.05" Scale
    0.10:    Field of View in 0.10" Scale
    """
    return {
            'Zbb':{'SEL':999,'LEL':1176,'NoSC':1476, 'NoCS':1019,
                'ALG':(16,64), '0.02':(0.32,1.28), '0.035':(0.56,2.24),
                '0.05':(0.8,3.2), '0.10':(1.6,6.4)},
            'Jbb':{'SEL':1180,'LEL':1416,'NoSC':1574, 'NoCS':1019,
                'ALG':(16,64), '0.02':(0.32,1.28), '0.035':(0.56,2.24),
                '0.05':(0.8,3.2), '0.10':(1.6,6.4)},
            'Hbb':{'SEL':1473,'LEL':1803,'NoSC':1651, 'NoCS':1019,
                'ALG':(16,64), '0.02':(0.32,1.28), '0.035':(0.56,2.24),
                '0.05':(0.8,3.2), '0.10':(1.6,6.4)},
            'Kbb':{'SEL':1965,'LEL':2381,'NoSC':1665, 'NoCS':1019,
                'ALG':(16,64), '0.02':(0.32,1.28), '0.035':(0.56,2.24),
                '0.05':(0.8,3.2), '0.10':(1.6,6.4)},
            'Kcb':{'SEL':1965,'LEL':2381,'NoSC':1665, 'NoCS':1019,
                'ALG':(16,64), '0.02':None, '0.035':None,
                '0.05':None, '0.10':(1.6,6.4)},
            'Zn4':{'SEL':1103,'LEL':1158,'NoSC':459, 'NoCS':2038,
                'ALG':(32,64), '0.02':(0.64,1.28), '0.035':(1.12,2.24),
                '0.05':(1.6,3.2), '0.10':(3.2,6.4)},
            'Jn1':{'SEL':1174,'LEL':1232,'NoSC':388, 'NoCS':2038,
                'ALG':(32,64), '0.02':(0.64,1.28), '0.035':(1.12,2.24),
                '0.05':(1.6,3.2), '0.10':(3.2,6.4)},
            'Jn2':{'SEL':1228,'LEL':1289,'NoSC':408, 'NoCS':2678,
                'ALG':(42,64), '0.02':(0.84,1.28), '0.035':(1.47,2.24),
                '0.05':(2.1,3.2), '0.10':(4.2,6.4)},
            'Jn3':{'SEL':1275,'LEL':1339,'NoSC':428, 'NoCS':3063,
                'ALG':(48,64), '0.02':(0.96,1.28), '0.035':(1.68,2.24),
                '0.05':(2.4,3.2), '0.10':(4.8,6.4)},
            'Jn4':{'SEL':1323,'LEL':1389,'NoSC':441, 'NoCS':2678,
                'ALG':(42,64), '0.02':(0.84,1.28), '0.035':(1.47,2.24),
                '0.05':(2.1,3.2), '0.10':(4.2,6.4)},
            'Hn1':{'SEL':1466,'LEL':1541,'NoSC':376, 'NoCS':2292,
                'ALG':(36,64), '0.02':(0.72,1.28), '0.035':(1.26,2.24),
                '0.05':(1.8,3.2), '0.10':(3.6,6.4)},
            'Hn2':{'SEL':1532,'LEL':1610,'NoSC':391, 'NoCS':2868,
                'ALG':(45,64), '0.02':(0.90,1.28), '0.035':(1.58,2.24),
                '0.05':(2.25,3.2), '0.10':(4.5,6.4)},
            'Hn3':{'SEL':1594,'LEL':1676,'NoSC':411, 'NoCS':3063,
                'ALG':(48,64), '0.02':(0.96,1.28), '0.035':(1.68,2.24),
                '0.05':(2.4,3.2), '0.10':(4.8,6.4)},
            'Hn4':{'SEL':1652,'LEL':1737,'NoSC':426, 'NoCS':2671,
                'ALG':(42,64), '0.02':(0.84,1.28), '0.035':(1.47,2.24),
                '0.05':(2.1,3.2), '0.10':(4.2,6.4)},
            'Hn5':{'SEL':1721,'LEL':1808,'NoSC':436, 'NoCS':2038,
                'ALG':(32,64), '0.02':(0.64,1.28), '0.035':(1.12,2.24),
                '0.05':(1.6,3.2), '0.10':(3.2,6.4)},
            'Kn1':{'SEL':1955,'LEL':2055,'NoSC':401, 'NoCS':2292,
                'ALG':(36,64), '0.02':(0.72,1.28), '0.035':(1.26,2.24),
                '0.05':(1.8,3.2), '0.10':(3.6,6.4)},
            'Kn2':{'SEL':2036,'LEL':2141,'NoSC':421, 'NoCS':2868,
                'ALG':(45,64), '0.02':(0.90,1.28), '0.035':(1.58,2.24),
                '0.05':(2.25,3.2), '0.10':(4.5,6.4)},
            'Kn3':{'SEL':2121,'LEL':2229,'NoSC':433, 'NoCS':3063,
                'ALG':(48,64), '0.02':(0.96,1.28), '0.035':(1.68,2.24),
                '0.05':(2.4,3.2), '0.10':(4.8,6.4)},
            'Kc3':{'SEL':2121,'LEL':2229,'NoSC':443, 'NoCS':3063,
                'ALG':(48,64), '0.02':None, '0.035':None,
                '0.05':None, '0.10':(4.8,6.4)},
            'Kn4':{'SEL':2208,'LEL':2320,'NoSC':449, 'NoCS':2671,
                'ALG':(42,64), '0.02':(0.84,1.28), '0.035':(1.47,2.24),
                '0.05':(2.1,3.2), '0.10':(4.2,6.4)},
            'Kc4':{'SEL':2208,'LEL':2320,'NoSC':449, 'NoCS':2671,
                'ALG':(42,64), '0.02':None, '0.035':None,
                '0.05':None, '0.10':(4.2,6.4)},
            'Kn5':{'SEL':2292,'LEL':2408,'NoSC':465, 'NoCS':2038,
                'ALG':(32,64), '0.02':(0.64,1.28), '0.035':(1.12,2.24),
                '0.05':(1.6,3.2), '0.10':(3.2,6.4)},
            'Kc5':{'SEL':2292,'LEL':2408,'NoSC':465, 'NoCS':2038,
                'ALG':(32,64), '0.02':None, '0.035':None,
                '0.05':None, '0.10':(3.2,6.4)},
        }
