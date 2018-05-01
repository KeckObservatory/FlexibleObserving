import matplotlib.pyplot as plt
import matplotlib.patches as pch
import matplotlib.ticker as tkr
import shutil
import pandas as pd
import numpy as np

class Oopgui:
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
                'User':[]
            }
        self.filters = [
                'Opn','Jbb','Hbb','Kbb','Zbb',
                'Jn1','Jn2','Jn3','Hn1','Hn2',
                'Hn3','Hn4','Hn5','Kn1','Kn2',
                'Kn3','Kn4','Kn5','Zn3','Drk'
            ]
        self.filter = 'Opn'
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
        self.queueDir = qdir

    def send_to_queue(self):
        pass

    def rescale(self):
        minX = 0
        maxX = 0
        minY = 0
        maxY = 0
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

        if self.mode == 'spec':
            self.xMin = minX - 1.0
            self.xMax = maxX + 1.0
            self.yMin = minY - 1.0
            self.yMax = maxY + 1.0
        elif self.mode == 'imag':
            self.xMin = minX + self.imagX - 14.3
            self.xMax = maxX + self.imagX + 14.3
            self.yMin = minY + self.imagY - 14.3
            self.yMax = maxY + self.imagY + 14.3
        else: # self.mode == both
            xMinSpec = minX - 1.0
            xMaxSpec = maxX + 1.0
            yMinSpec = minY - 1.0
            yMaxSpec = maxY + 1.0

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
        self.ax.add_patch(
            pch.Circle(
                (0,0),
                radius=0.025,
                fill=False,
                color='red'
            )
        )

    def add_ref(self):
        self.ax.add_patch(
            pch.Rectangle(
                (-0.015,-0.015),
                0.03,
                0.03,
                fill=False
            )
        )

    def add_obj_box(self, xpos, ypos):
        return pch.Rectangle(
            (self.specX+self.initOffX+xpos*self.objLenX,
            self.specY+self.initOffY+ypos*self.objHgtY),
            self.boxWidth,
            self.boxHeight,
            fill = False,
            linewidth = 3
        )

    def add_sky_box(self, xpos, ypos):
        return pch.Rectangle(
            (self.specX+self.initOffX+self.nodOffX+xpos*self.skyLenX,
            self.specY+self.initOffY+self.nodOffY+ypos*self.skyHgtY),
            self.boxWidth,
            self.boxHeight,
            fill = False,
            linewidth = 3
        )

    def add_obj_diamond(self, xpos, ypos):
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
        pass

    def draw_stare(self):
        if self.mode in ['spec','both']:
            if self.objPattern == 'Stare':
                self.ax.add_patch(self.add_obj_box(
                    self.offDefs[self.objPattern][0][0],
                    self.offDefs[self.objPattern][0][1]))
            if self.skyPattern == 'Stare':
                self.ax.add_patch(self.add_sky_box(
                    self.offDefs[self.skyPattern][0][0],
                    self.offDefs[self.skyPattern][0][1]))
        if self.mode in ['imag','both']:
            if self.objPattern == 'Stare':
                self.ax.add_patch(self.add_obj_diamond(
                        self.offDefs[self.objPattern][0][0],
                        self.offDefs[self.objPattern][0][1]))
            if self.skyPattern == 'Stare':
                self.ax.add_patch(self.add_sky_diamond(
                        self.offDefs[self.skyPattern][0][0],
                        self.offDefs[self.skyPattern][0][1]))

    def draw_box4(self):
        if self.mode in ['spec','both']:
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
        if self.mode in ['imag','both']:
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
        if self.mode in ['spec','both']:
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
        if self.mode in ['imag','both']:
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
        if self.mode in ['spec','both']:
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
        if self.mode in ['imag','both']:
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
        pass

    def draw_raster(self):
        pass

    def draw_user(self):
        for i in range(0,len(self.defs),3):
            if self.mode in ['spec','both']:
                if self.defs[i+2]=="false":
                    self.ax.add_patch(
                            self.add_obj_box(
                                float(self.defs[i]),float(self.defs[i+1])))
                elif self.defs[i+2]=="true":
                    self.ax.add_patch(
                            self.add_sky_box(
                                float(self.defs[i]),float(self.defs[i+1])))
            if self.mode in ['imag','both']:
                if self.defs[i+2]=="false":
                    self.ax.add_patch(
                            self.add_obj_diamond(
                                float(self.defs[i]),float(self.defs[i+1])))
                elif self.defs[i+2]=="true":
                    self.ax.add_patch(
                            self.add_sky_diamond(
                                float(self.defs[i]),float(self.defs[i+1])))

    def update(self, qstr):
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

        self.gridScale = self.rescale()
        self.print_all()
        self.draw_fig()
        self.ax.grid()

    def print_all(self):
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
        out = ''.join((' type="', self.objPattern, ' '))
    def save_to_file(self):
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
    FOV.02:  Field of View in 0.02" Scale
    FOV.035: Field of View in 0.035" Scale
    FOV.05:  Field of View in 0.05" Scale
    FOV.10:  Field of View in 0.10" Scale
    """
    return {
            'Zbb':{'SEL':999,'LEL':1176,'NoSC':1476, 'NoCS':1019,
                'ALG':(16,64), 'FOV.02':(0.32,1.28), 'FOV.035':(0.56,2.24),
                'FOV.05':(0.8,3.2), 'FOV.10':(1.6,6.4)},
            'Jbb':{'SEL':1180,'LEL':1416,'NoSC':1574, 'NoCS':1019,
                'ALG':(16,64), 'FOV.02':(0.32,1.28), 'FOV.035':(0.56,2.24),
                'FOV.05':(0.8,3.2), 'FOV.10':(1.6,6.4)},
            'Hbb':{'SEL':1473,'LEL':1803,'NoSC':1651, 'NoCS':1019,
                'ALG':(16,64), 'FOV.02':(0.32,1.28), 'FOV.035':(0.56,2.24),
                'FOV.05':(0.8,3.2), 'FOV.10':(1.6,6.4)},
            'Kbb':{'SEL':1965,'LEL':2381,'NoSC':1665, 'NoCS':1019,
                'ALG':(16,64), 'FOV.02':(0.32,1.28), 'FOV.035':(0.56,2.24),
                'FOV.05':(0.8,3.2), 'FOV.10':(1.6,6.4)},
            'Kcb':{'SEL':1965,'LEL':2381,'NoSC':1665, 'NoCS':1019,
                'ALG':(16,64), 'FOV.02':None, 'FOV.035':None,
                'FOV.05':None, 'FOV.10':(1.6,6.4)},
            'Zn4':{'SEL':1103,'LEL':1158,'NoSC':459, 'NoCS':2038,
                'ALG':(32,64), 'FOV.02':(0.64,1.28), 'FOV.035':(1.12,2.24),
                'FOV.05':(1.6,3.2), 'FOV.10':(3.2,6.4)},
            'Jn1':{'SEL':1174,'LEL':1232,'NoSC':388, 'NoCS':2038,
                'ALG':(32,64), 'FOV.02':(0.64,1.28), 'FOV.035':(1.12,2.24),
                'FOV.05':(1.6,3.2), 'FOV.10':(3.2,6.4)},
            'Jn2':{'SEL':1228,'LEL':1289,'NoSC':408, 'NoCS':2678,
                'ALG':(42,64), 'FOV.02':(0.84,1.28), 'FOV.035':(1.47,2.24),
                'FOV.05':(2.1,3.2), 'FOV.10':(4.2,6.4)},
            'Jn3':{'SEL':1275,'LEL':1339,'NoSC':428, 'NoCS':3063,
                'ALG':(48,64), 'FOV.02':(0.96,1.28), 'FOV.035':(1.68,2.24),
                'FOV.05':(2.4,3.2), 'FOV.10':(4.8,6.4)},
            'Jn4':{'SEL':1323,'LEL':1389,'NoSC':441, 'NoCS':2678,
                'ALG':(42,64), 'FOV.02':(0.84,1.28), 'FOV.035':(1.47,2.24),
                'FOV.05':(2.1,3.2), 'FOV.10':(4.2,6.4)},
            'Hn1':{'SEL':1466,'LEL':1541,'NoSC':376, 'NoCS':2292,
                'ALG':(36,64), 'FOV.02':(0.72,1.28), 'FOV.035':(1.26,2.24),
                'FOV.05':(1.8,3.2), 'FOV.10':(3.6,6.4)},
            'Hn2':{'SEL':1532,'LEL':1610,'NoSC':391, 'NoCS':2868,
                'ALG':(45,64), 'FOV.02':(0.90,1.28), 'FOV.035':(1.58,2.24),
                'FOV.05':(2.25,3.2), 'FOV.10':(4.5,6.4)},
            'Hn3':{'SEL':1594,'LEL':1676,'NoSC':411, 'NoCS':3063,
                'ALG':(48,64), 'FOV.02':(0.96,1.28), 'FOV.035':(1.68,2.24),
                'FOV.05':(2.4,3.2), 'FOV.10':(4.8,6.4)},
            'Hn4':{'SEL':1652,'LEL':1737,'NoSC':426, 'NoCS':2671,
                'ALG':(42,64), 'FOV.02':(0.84,1.28), 'FOV.035':(1.47,2.24),
                'FOV.05':(2.1,3.2), 'FOV.10':(4.2,6.4)},
            'Hn5':{'SEL':1721,'LEL':1808,'NoSC':436, 'NoCS':2038,
                'ALG':(32,64), 'FOV.02':(0.64,1.28), 'FOV.035':(1.12,2.24),
                'FOV.05':(1.6,3.2), 'FOV.10':(3.2,6.4)},
            'Kn1':{'SEL':1955,'LEL':2055,'NoSC':401, 'NoCS':2292,
                'ALG':(36,64), 'FOV.02':(0.72,1.28), 'FOV.035':(1.26,2.24),
                'FOV.05':(1.8,3.2), 'FOV.10':(3.6,6.4)},
            'Kn2':{'SEL':2036,'LEL':2141,'NoSC':421, 'NoCS':2868,
                'ALG':(45,64), 'FOV.02':(0.90,1.28), 'FOV.035':(1.58,2.24),
                'FOV.05':(2.25,3.2), 'FOV.10':(4.5,6.4)},
            'Kn3':{'SEL':2121,'LEL':2229,'NoSC':433, 'NoCS':3063,
                'ALG':(48,64), 'FOV.02':(0.96,1.28), 'FOV.035':(1.68,2.24),
                'FOV.05':(2.4,3.2), 'FOV.10':(4.8,6.4)},
            'Kc3':{'SEL':2121,'LEL':2229,'NoSC':443, 'NoCS':3063,
                'ALG':(48,64), 'FOV.02':None, 'FOV.035':None,
                'FOV.05':None, 'FOV.10':(4.8,6.4)},
            'Kn4':{'SEL':2208,'LEL':2320,'NoSC':449, 'NoCS':2671,
                'ALG':(42,64), 'FOV.02':(0.84,1.28), 'FOV.035':(1.47,2.24),
                'FOV.05':(2.1,3.2), 'FOV.10':(4.2,6.4)},
            'Kc4':{'SEL':2208,'LEL':2320,'NoSC':449, 'NoCS':2671,
                'ALG':(42,64), 'FOV.02':None, 'FOV.035':None,
                'FOV.05':None, 'FOV.10':(4.2,6.4)},
            'Kn5':{'SEL':2292,'LEL':2408,'NoSC':465, 'NoCS':2038,
                'ALG':(32,64), 'FOV.02':(0.64,1.28), 'FOV.035':(1.12,2.24),
                'FOV.05':(1.6,3.2), 'FOV.10':(3.2,6.4)},
            'Kc5':{'SEL':2292,'LEL':2408,'NoSC':465, 'NoCS':2038,
                'ALG':(32,64), 'FOV.02':None, 'FOV.035':None,
                'FOV.05':None, 'FOV.10':(3.2,6.4)},
        }
