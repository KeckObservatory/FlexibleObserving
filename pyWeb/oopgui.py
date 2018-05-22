import matplotlib.pyplot as plt
import matplotlib.patches as pch
import matplotlib.ticker as tkr
import shutil
import pandas as pd
import numpy as np
from pymongo import MongoClient as mc

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
        self.measurement = 'arcsec'
        self.aomode = 'NGS'
        self.queueDir = '~/'
        self.ddfname = 'test.ddf'
        self.gridScale = 4.0 #0.8
        self.boxWidth = 0.32
        self.boxHeight = 1.28
        self.filters = SpecFilters()

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
        self.imagY = 15.138
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
                'Opn','Jbb','Hbb','Kbb','Zbb',
                'Jn1','Jn2','Jn3','Hn1','Hn2',
                'Hn3','Hn4','Hn5','Kn1','Kn2',
                'Kn3','Kn4','Kn5','Zn3','Drk'
            ]
        self.imgFilter = 'Opn'
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

        # Set up plot graphic
        self.draw_fig()
        self.ax.grid()

    # End __init__()

    def set_queue_dir(self, qdir):
        """
        Sets the directory of the queue to where
        the observing tool pulls config files from.

        @type qdir: string
        @param qdir: absolute directory of the queue folder
        """
        self.queueDir = qdir

    def send_to_queue(self):
        """
        Moves the file to the directory set in queueDir
        """
        pass

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
            self.xMin = minX - 1.0*float(self.scale)/0.02
            self.xMax = maxX + 1.0*float(self.scale)/0.02
            self.yMin = minY - 1.0*float(self.scale)/0.02
            self.yMax = maxY + 1.0*float(self.scale)/0.02
        elif self.mode == 'imag':
            self.xMin = minX + self.imagX - 14.3
            self.xMax = maxX + self.imagX + 14.3
            self.yMin = minY + self.imagY - 14.3
            self.yMax = maxY + self.imagY + 14.3
        else: # self.mode == both
            xMinSpec = minX - 1.0*float(self.scale)/0.02
            xMaxSpec = maxX + 1.0*float(self.scale)/0.02
            yMinSpec = minY - 1.0*float(self.scale)/0.02
            yMaxSpec = maxY + 1.0*float(self.scale)/0.02

            xMinImag = minX + self.imagX - 14.3
            xMaxImag = maxX + self.imagX + 14.3
            yMinImag = minY + self.imagY - 14.3
            yMaxImag = maxY + self.imagY + 14.3

            self.xMin = xMinSpec if xMinSpec < xMinImag else xMinImag
            self.xMax = xMaxSpec if xMaxSpec > xMaxImag else xMaxImag
            self.yMin = yMinSpec if yMinSpec < yMinImag else yMinImag
            self.yMax = yMaxSpec if yMaxSpec > yMaxImag else yMaxImag

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
        self.draw[self.objPattern]()
        self.draw[self.skyPattern]()
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

    def add_obj_box(self, xpos, ypos):
        """
        Creates an object box around the given x and y positions

        @type xpos: float
        @param xpos: x position around which to draw the object box
        @typp ypos: float
        @param ypos: y position around which to draw the object box
        """
        return pch.Rectangle(
            (self.specX+self.initOffX+xpos*self.objLenX,
            self.specY+self.initOffY+ypos*self.objHgtY),
            self.boxWidth,
            self.boxHeight,
            fill = False,
            linewidth = 3
        )

    def add_sky_box(self, xpos, ypos):
        """
        Creates a sky box around the given x and y positions

        @type xpos: float
        @param xpos: x position around which to draw the sky box
        @type ypos: float
        @param ypos: y position around which to draw the sky box
        """
        return pch.Rectangle(
            (self.specX+self.initOffX+self.nodOffX+xpos*self.skyLenX,
            self.specY+self.initOffY+self.nodOffY+ypos*self.skyHgtY),
            self.boxWidth,
            self.boxHeight,
            fill = False,
            linewidth = 3
        )

    def add_obj_diamond(self, xpos, ypos):
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
        return pch.Polygon(
            np.array(
                [
                    [self.imagX - 14.3 + self.initOffX
                            + xoff + xpos*self.objLenX,
                        self.imagY + 0 + self.initOffY
                            - yoff + ypos*self.objHgtY],
                    [self.imagX + 0 + self.initOffX
                            - xoff + xpos*self.objLenX,
                        self.imagY + 14.3 + self.initOffY
                            - yoff + ypos*self.objHgtY],
                    [self.imagX + 14.3 + self.initOffX
                            - xoff + xpos*self.objLenX,
                        self.imagY + 0 + self.initOffY
                            + yoff + ypos*self.objHgtY],
                    [self.imagX + 0 + self.initOffX
                            + xoff + xpos*self.objLenX,
                        self.imagY -14.3 + self.initOffY
                            + yoff + ypos*self.objHgtY]
                ]
            ),
            fill = False,
            linewidth = 3
        )

    def add_sky_diamond(self, xpos, ypos):
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
        return pch.Polygon(
            np.array(
                [
                    [self.imagX -14.3 + self.initOffX
                        + self.nodOffX + xoff + xpos*self.skyLenX,
                    self.imagY +0 + self.initOffY + self.nodOffY
                        - yoff + ypos*self.skyHgtY],
                    [self.imagX + 0 + self.initOffX
                        + self.nodOffX - xoff + xpos*self.skyLenX,
                    self.imagY + 14.3 + self.initOffY + self.nodOffY
                        - yoff + ypos*self.skyHgtY],
                    [self.imagX + 14.3 + self.initOffX + self.nodOffX
                        - xoff + xpos*self.skyLenX,
                    self.imagY +0 + self.initOffY + self.nodOffY
                        + yoff + ypos*self.skyHgtY],
                    [self.imagX + 0 + self.initOffX + self.nodOffX
                        + xoff + xpos*self.skyLenX,
                    self.imagY - 14.3 + self.initOffY + self.nodOffY
                        + yoff + ypos*self.skyHgtY]
                ]
            ),
            fill = False,
            linewidth = 3
        )

    def draw_none(self):
        """
        Placeholder function to prevent problems where one of the
        dither patterns is 'None'
        """
        pass

    def draw_stare(self):
        """
        Draws a stare pattern on the figure depending on the
        selected mode of the instrument and the stored values
        """
        # Check if the mode takes a spec integration
        if self.mode in ['spec','both']:
            # Check if the object or sky box pattern is Stare
            if self.objPattern == 'Stare':
                self.ax.add_patch(self.add_obj_box(
                    self.offDefs[self.objPattern][0][0],
                    self.offDefs[self.objPattern][0][1]))
            if self.skyPattern == 'Stare':
                self.ax.add_patch(self.add_sky_box(
                    self.offDefs[self.skyPattern][0][0],
                    self.offDefs[self.skyPattern][0][1]))
        # Check if the mode takes an imager integration
        if self.mode in ['imag','both']:
            # Check if the object or sky diamond pattern is Stare
            if self.objPattern == 'Stare':
                self.ax.add_patch(self.add_obj_diamond(
                        self.offDefs[self.objPattern][0][0],
                        self.offDefs[self.objPattern][0][1]))
            if self.skyPattern == 'Stare':
                self.ax.add_patch(self.add_sky_diamond(
                        self.offDefs[self.skyPattern][0][0],
                        self.offDefs[self.skyPattern][0][1]))

    def draw_box4(self):
        """
        Draws a box4 pattern on the figure using the stored values
        """
        # Check if the mode takes a spec integration
        if self.mode in ['spec','both']:
            # check if the object or sky box pattern is Box4
            if self.objPattern == 'Box4':
                self.ax.add_patch(self.add_obj_box(
                    self.offDefs[self.objPattern][0][0],
                    self.offDefs[self.objPattern][0][1]))
                self.ax.add_patch(self.add_obj_box(
                    self.offDefs[self.objPattern][1][0],
                    self.offDefs[self.objPattern][1][1]))
                self.ax.add_patch(self.add_obj_box(
                    self.offDefs[self.objPattern][2][0],
                    self.offDefs[self.objPattern][2][1]))
                self.ax.add_patch(self.add_obj_box(
                    self.offDefs[self.objPattern][3][0],
                    self.offDefs[self.objPattern][3][1]))
            if self.skyPattern == 'Box4':
                self.ax.add_patch(self.add_sky_box(
                    self.offDefs[self.skyPattern][0][0],
                    self.offDefs[self.skyPattern][0][1]))
                self.ax.add_patch(self.add_sky_box(
                    self.offDefs[self.skyPattern][1][0],
                    self.offDefs[self.skyPattern][1][1]))
                self.ax.add_patch(self.add_sky_box(
                    self.offDefs[self.skyPattern][2][0],
                    self.offDefs[self.skyPattern][2][1]))
                self.ax.add_patch(self.add_sky_box(
                    self.offDefs[self.skyPattern][3][0],
                    self.offDefs[self.skyPattern][3][1]))
        # Check if the mode takes an imager integration
        if self.mode in ['imag','both']:
            # Check if the object or sky diamond pattern is Box4
            if self.objPattern == 'Box4':
                self.ax.add_patch(self.add_obj_diamond(
                        self.offDefs[self.objPattern][0][0],
                        self.offDefs[self.objPattern][0][1]))
                self.ax.add_patch(self.add_obj_diamond(
                        self.offDefs[self.objPattern][1][0],
                        self.offDefs[self.objPattern][1][1]))
                self.ax.add_patch(self.add_obj_diamond(
                        self.offDefs[self.objPattern][2][0],
                        self.offDefs[self.objPattern][2][1]))
                self.ax.add_patch(self.add_obj_diamond(
                        self.offDefs[self.objPattern][3][0],
                        self.offDefs[self.objPattern][3][1]))
            if self.skyPattern == 'Box4':
                self.ax.add_patch(self.add_sky_diamond(
                        self.offDefs[self.skyPattern][0][0],
                        self.offDefs[self.skyPattern][0][1]))
                self.ax.add_patch(self.add_sky_diamond(
                        self.offDefs[self.skyPattern][1][0],
                        self.offDefs[self.skyPattern][1][1]))
                self.ax.add_patch(self.add_sky_diamond(
                        self.offDefs[self.skyPattern][2][0],
                        self.offDefs[self.skyPattern][2][1]))
                self.ax.add_patch(self.add_sky_diamond(
                        self.offDefs[self.skyPattern][3][0],
                        self.offDefs[self.skyPattern][3][1]))

    def draw_box5(self):
        """
        Draws a box5 pattern on the figure using the stored values
        """
        # Check if the mode takes a spec integration
        if self.mode in ['spec','both']:
            # Check if the obj or sky box pattern is Box5
            if self.objPattern == 'Box5':
                self.ax.add_patch(self.add_obj_box(
                    self.offDefs[self.objPattern][0][0],
                    self.offDefs[self.objPattern][0][1]))
                self.ax.add_patch(self.add_obj_box(
                    self.offDefs[self.objPattern][1][0],
                    self.offDefs[self.objPattern][1][1]))
                self.ax.add_patch(self.add_obj_box(
                    self.offDefs[self.objPattern][2][0],
                    self.offDefs[self.objPattern][2][1]))
                self.ax.add_patch(self.add_obj_box(
                    self.offDefs[self.objPattern][3][0],
                    self.offDefs[self.objPattern][3][1]))
                self.ax.add_patch(self.add_obj_box(
                    self.offDefs[self.objPattern][4][0],
                    self.offDefs[self.objPattern][4][1]))
            if self.skyPattern == 'Box5':
                self.ax.add_patch(self.add_sky_box(
                    self.offDefs[self.skyPattern][0][0],
                    self.offDefs[self.skyPattern][0][1]))
                self.ax.add_patch(self.add_sky_box(
                    self.offDefs[self.skyPattern][1][0],
                    self.offDefs[self.skyPattern][1][1]))
                self.ax.add_patch(self.add_sky_box(
                    self.offDefs[self.skyPattern][2][0],
                    self.offDefs[self.skyPattern][2][1]))
                self.ax.add_patch(self.add_sky_box(
                    self.offDefs[self.skyPattern][3][0],
                    self.offDefs[self.skyPattern][3][1]))
                self.ax.add_patch(self.add_sky_box(
                    self.offDefs[self.skyPattern][4][0],
                    self.offDefs[self.skyPattern][4][1]))
        # Check if the mode takes an imager integration
        if self.mode in ['imag','both']:
            # Check if the obj or sky diamond pattern is Box5
            if self.objPattern == 'Box5':
                self.ax.add_patch(self.add_obj_diamond(
                        self.offDefs[self.objPattern][0][0],
                        self.offDefs[self.objPattern][0][1]))
                self.ax.add_patch(self.add_obj_diamond(
                        self.offDefs[self.objPattern][1][0],
                        self.offDefs[self.objPattern][1][1]))
                self.ax.add_patch(self.add_obj_diamond(
                        self.offDefs[self.objPattern][2][0],
                        self.offDefs[self.objPattern][2][1]))
                self.ax.add_patch(self.add_obj_diamond(
                        self.offDefs[self.objPattern][3][0],
                        self.offDefs[self.objPattern][3][1]))
                self.ax.add_patch(self.add_obj_diamond(
                        self.offDefs[self.objPattern][4][0],
                        self.offDefs[self.objPattern][4][1]))
            if self.skyPattern == 'Box5':
                self.ax.add_patch(self.add_sky_diamond(
                        self.offDefs[self.skyPattern][0][0],
                        self.offDefs[self.skyPattern][0][1]))
                self.ax.add_patch(self.add_sky_diamond(
                        self.offDefs[self.skyPattern][1][0],
                        self.offDefs[self.skyPattern][1][1]))
                self.ax.add_patch(self.add_sky_diamond(
                        self.offDefs[self.skyPattern][2][0],
                        self.offDefs[self.skyPattern][2][1]))
                self.ax.add_patch(self.add_sky_diamond(
                        self.offDefs[self.skyPattern][3][0],
                        self.offDefs[self.skyPattern][3][1]))
                self.ax.add_patch(self.add_sky_diamond(
                        self.offDefs[self.skyPattern][4][0],
                        self.offDefs[self.skyPattern][4][1]))

    def draw_box9(self):
        """
        Draws a Box9 pattern on the figure using the stored values
        """
        # Check if the mode takes a spec integration
        if self.mode in ['spec','both']:
            # Check if the obj or sky box pattern is Box9
            if self.objPattern == 'Box9':
                self.ax.add_patch(self.add_obj_box(
                    self.offDefs[self.objPattern][0][0],
                    self.offDefs[self.objPattern][0][1]))
                self.ax.add_patch(self.add_obj_box(
                    self.offDefs[self.objPattern][1][0],
                    self.offDefs[self.objPattern][1][1]))
                self.ax.add_patch(self.add_obj_box(
                    self.offDefs[self.objPattern][2][0],
                    self.offDefs[self.objPattern][2][1]))
                self.ax.add_patch(self.add_obj_box(
                    self.offDefs[self.objPattern][3][0],
                    self.offDefs[self.objPattern][3][1]))
                self.ax.add_patch(self.add_obj_box(
                    self.offDefs[self.objPattern][4][0],
                    self.offDefs[self.objPattern][4][1]))
                self.ax.add_patch(self.add_obj_box(
                    self.offDefs[self.objPattern][5][0],
                    self.offDefs[self.objPattern][5][1]))
                self.ax.add_patch(self.add_obj_box(
                    self.offDefs[self.objPattern][6][0],
                    self.offDefs[self.objPattern][6][1]))
                self.ax.add_patch(self.add_obj_box(
                    self.offDefs[self.objPattern][7][0],
                    self.offDefs[self.objPattern][7][1]))
                self.ax.add_patch(self.add_obj_box(
                    self.offDefs[self.objPattern][8][0],
                    self.offDefs[self.objPattern][8][1]))
            if self.skyPattern == 'Box9':
                self.ax.add_patch(self.add_sky_box(
                    self.offDefs[self.skyPattern][0][0],
                    self.offDefs[self.skyPattern][0][1]))
                self.ax.add_patch(self.add_sky_box(
                    self.offDefs[self.skyPattern][1][0],
                    self.offDefs[self.skyPattern][1][1]))
                self.ax.add_patch(self.add_sky_box(
                    self.offDefs[self.skyPattern][2][0],
                    self.offDefs[self.skyPattern][2][1]))
                self.ax.add_patch(self.add_sky_box(
                    self.offDefs[self.skyPattern][3][0],
                    self.offDefs[self.skyPattern][3][1]))
                self.ax.add_patch(self.add_sky_box(
                    self.offDefs[self.skyPattern][4][0],
                    self.offDefs[self.skyPattern][4][1]))
                self.ax.add_patch(self.add_sky_box(
                    self.offDefs[self.skyPattern][5][0],
                    self.offDefs[self.skyPattern][5][1]))
                self.ax.add_patch(self.add_sky_box(
                    self.offDefs[self.skyPattern][6][0],
                    self.offDefs[self.skyPattern][6][1]))
                self.ax.add_patch(self.add_sky_box(
                    self.offDefs[self.skyPattern][7][0],
                    self.offDefs[self.skyPattern][7][1]))
                self.ax.add_patch(self.add_sky_box(
                    self.offDefs[self.skyPattern][8][0],
                    self.offDefs[self.skyPattern][8][1]))
        # Check if the mode takes an image integration
        if self.mode in ['imag','both']:
            # Check if the obj or sky diamond pattern is Box9
            if self.objPattern == 'Box9':
                self.ax.add_patch(self.add_obj_diamond(
                        self.offDefs[self.objPattern][0][0],
                        self.offDefs[self.objPattern][0][1]))
                self.ax.add_patch(self.add_obj_diamond(
                        self.offDefs[self.objPattern][1][0],
                        self.offDefs[self.objPattern][1][1]))
                self.ax.add_patch(self.add_obj_diamond(
                        self.offDefs[self.objPattern][2][0],
                        self.offDefs[self.objPattern][2][1]))
                self.ax.add_patch(self.add_obj_diamond(
                        self.offDefs[self.objPattern][3][0],
                        self.offDefs[self.objPattern][3][1]))
                self.ax.add_patch(self.add_obj_diamond(
                        self.offDefs[self.objPattern][4][0],
                        self.offDefs[self.objPattern][4][1]))
                self.ax.add_patch(self.add_obj_diamond(
                        self.offDefs[self.objPattern][5][0],
                        self.offDefs[self.objPattern][5][1]))
                self.ax.add_patch(self.add_obj_diamond(
                        self.offDefs[self.objPattern][6][0],
                        self.offDefs[self.objPattern][6][1]))
                self.ax.add_patch(self.add_obj_diamond(
                        self.offDefs[self.objPattern][7][0],
                        self.offDefs[self.objPattern][7][1]))
                self.ax.add_patch(self.add_obj_diamond(
                        self.offDefs[self.objPattern][8][0],
                        self.offDefs[self.objPattern][8][1]))
            if self.skyPattern == 'Box9':
                self.ax.add_patch(self.add_sky_diamond(
                        self.offDefs[self.skyPattern][0][0],
                        self.offDefs[self.skyPattern][0][1]))
                self.ax.add_patch(self.add_sky_diamond(
                        self.offDefs[self.skyPattern][1][0],
                        self.offDefs[self.skyPattern][1][1]))
                self.ax.add_patch(self.add_sky_diamond(
                        self.offDefs[self.skyPattern][2][0],
                        self.offDefs[self.skyPattern][2][1]))
                self.ax.add_patch(self.add_sky_diamond(
                        self.offDefs[self.skyPattern][3][0],
                        self.offDefs[self.skyPattern][3][1]))
                self.ax.add_patch(self.add_sky_diamond(
                        self.offDefs[self.skyPattern][4][0],
                        self.offDefs[self.skyPattern][4][1]))
                self.ax.add_patch(self.add_sky_diamond(
                        self.offDefs[self.skyPattern][5][0],
                        self.offDefs[self.skyPattern][5][1]))
                self.ax.add_patch(self.add_sky_diamond(
                        self.offDefs[self.skyPattern][6][0],
                        self.offDefs[self.skyPattern][6][1]))
                self.ax.add_patch(self.add_sky_diamond(
                        self.offDefs[self.skyPattern][7][0],
                        self.offDefs[self.skyPattern][7][1]))
                self.ax.add_patch(self.add_sky_diamond(
                        self.offDefs[self.skyPattern][8][0],
                        self.offDefs[self.skyPattern][8][1]))

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

    def draw_user(self):
        """
        Uses user defined values to draw boxes and diamonds on the
        figure
        """
        # Iterate through the definitions provided by
        # the user in groups of 3
        for i in range(0,len(self.defs),3):
            if self.mode in ['spec','both']:
                if self.defs[i+2]=="false":
                    self.ax.add_patch(
                            self.add_obj_box(
                                float(self.defs[i]),
                                float(self.defs[i+1])
                            )
                        )
                elif self.defs[i+2]=="true":
                    self.ax.add_patch(
                            self.add_sky_box(
                                float(self.defs[i]),
                                float(self.defs[i+1])
                            )
                        )
            if self.mode in ['imag','both']:
                if self.defs[i+2]=="false":
                    self.ax.add_patch(
                            self.add_obj_diamond(
                                float(self.defs[i]),
                                float(self.defs[i+1])
                            )
                        )
                elif self.defs[i+2]=="true":
                    self.ax.add_patch(
                            self.add_sky_diamond(
                                float(self.defs[i]),
                                float(self.defs[i+1])
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
        self.keckID = qstr['keckID'][0]
        if qstr['imgMode'][0] == 'Disabled': self.mode = 'spec'
        elif qstr['imgMode'][0] == 'Independent': self.mode = 'imag'
        else: self.mode = 'both'
        self.dataset = qstr['dataset'][0]
        self.object = qstr['object'][0]
        self.targType = qstr['targType'][0]
        self.coordSys = qstr['coordSys'][0]
        self.aoType = qstr['aoType'][0]
        self.lgsMode = qstr['lgsMode'][0]
        self.specFilter = qstr['specFilter'][0]
        self.scale = qstr['scale'][0]
        self.specCoadds = qstr['specCoadds'][0]
        self.specItime = qstr['specItime'][0]
        self.initOffX = float(qstr['initOffX'][0])
        self.initOffY = float(qstr['initOffY'][0])
        self.objPattern = qstr['objPattern'][0]
        self.objFrames = qstr['objFrames'][0]
        self.objLenX = float(qstr['objLenX'][0])
        self.objHgtY = float(qstr['objHgtY'][0])
        self.imgFilter = qstr['imgFilter'][0]
        self.repeats = qstr['repeats'][0]
        self.imgCoadds = qstr['imgCoadds'][0]
        self.imgItime = float(qstr['imgItime'][0])
        self.nodOffX = float(qstr['nodOffX'][0])
        self.nodOffY = float(qstr['nodOffY'][0])
        self.skyPattern = qstr['skyPattern'][0]
        self.skyFrame = qstr['skyFrames'][0]
        self.skyLenX = float(qstr['skyLenX'][0])
        self.skyHgtY = float(qstr['skyHgtY'][0])
        self.defs = qstr['defs'][0].split(',')

        # Update spec values based on specfilter
        self.boxWidth = self.filters[self.specFilter][self.scale][0]
        self.boxHeight = self.filters[self.specFilter][self.scale][1]
        self.specX = -self.filters[self.specFilter][self.scale][0]/2.0
        self.specY = -self.filters[self.specFilter][self.scale][1]/2.0
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
        print('frames:',self.objFrames)
        print('oblenx:',self.objLenX)
        print('obhgty:',self.objHgtY)
        print('ifiltr:',self.imgFilter)
        print('repeat:',self.repeats)
        print('icoadd:',self.imgCoadds)
        print('iitime:',self.imgItime)
        print('nodx  :',self.nodOffX)
        print('nody  :',self.nodOffY)
        print('skypat:',self.skyPattern)
        print('sframe:',self.skyFrame)
        print('slenx :',self.skyLenX)
        print('shgty :',self.skyHgtY)
        print('defs  :',self.defs)
        print('xmin  :',self.xMin)
        print('xmax  :',self.xMax)
        print('ymin  :',self.yMin)
        print('ymax  :',self.yMax)
        print('gscale:',self.gridScale)

    def obj_dither_out(self):
        """
        """
        out = ''.join((' type="', self.objPattern, ' '))
    def save_to_file(self):
        """
        Save the current configuration as a DDF (XML) file
        locally
        """
        with open(self.ddfname, 'w') as ddf:
            ddf.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            ddf.write('<ddf version="1.0" type="target">\n')
            ddf.write('\t<dataset name="', self.dataset, '" setnum="0" aomode=',
                      self.aomode, ' status="', self.status, '">\n')
            ddf.write('\t\t<object>', self.object,'</object>\n')
            ddf.write('\t\t<spec filter="', self.filter, '" scale=',
                      self.scale, '" / lenslet" itime="', self.itime,
                      '" coadds="', self.coadds,'" />\n')
            ddf.write('\t\t<imag mode="', self.immode, '">\n')
            ddf.write('\t\t\t<imagFrame filter="', self.filter, '" itime="',
                      self.itime, '" coadds="', self.coadds, '" repeats="',
                      self.repeats, '/>\n')
            ddf.write('\t\t</imag>\n')
            ddf.write('\t\t<objectDither', self.obj_dither_out(), '/>\n')
            ddf.write()
        print('File saved')

    def save_to_db(self):
        """
        Save the current configuration to the database
        """
        piID = 
        client = mc('dev-vm-www1',27017)
        db = client['osiris']
        os = db[piID]
        ins = { 'progname':progname,
                'semester':semester,
                'progtitl':progtitl,
                'submitter':self.keckid
            }
        ins.update(qry)
        os.insert(ins)

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
