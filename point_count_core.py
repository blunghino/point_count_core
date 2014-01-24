# -*- coding: utf-8 -*-
"""
point_count_core.py

Software to make regular manual measurements of grains in an image of sediment

dependencies:
    - python 3.x
    - numpy
    - matplotlib
    - PIL (Pillow) <https://pypi.python.org/pypi/Pillow/2.3.0>
    
to run from the command line:
    
python point_count_core.py [-i image_file]
                           [-h]
                           [-s {csv,pkl,none}]
                           [--sf {png,pdf,none}]
                           [--nax {1,2}]
                           [--gs GS]
                     
optional arguments:
  -h, --help           show this help message and exit
  -i image_file        image file to use
  -s {csv,pkl,none}    file type to save to (default="csv")
  --sf {png,pdf,none}  file type to save figure to (default="png")
  --nax {1,2}          number of axes to measure for each grain (default=2)
  --gs GS              grid spacing in pixels (default=100)
  
Measurements must be made on grid nodes progressing from left to right, top to 
bottom along the image. At each grid node two measurements are made, for the 
major axis and the minor axis of the grain. The grid node to be measured is 
highlighted by a small dot on the grid.

Grid spacing specifies the distance in pixels between each grid node. 
The plot window automatically zooms to show the single row of grid nodes that 
are actively being measured.

After all measurements are completed, the measurements and their pixel 
locations can be saved as a .csv or .pkl. The figure, showing the line 
measurements, can be saved saved as a .png or .pdf.

Created on Wed Jan 22 15:38:52 2014

Brent Lunghino
blunghino@usgs.gov
"""
import os
import csv
import pickle
import tkinter
import warnings
import argparse
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
from tkinter import filedialog as tkfiledialog
from PIL import Image

def full_screen_figure():
    """
    create a full screen pyplot figure
    """
    root = tkinter.Tk()
    pix2in = root.winfo_fpixels('1i')
    width = root.winfo_screenwidth() / pix2in
    height = root.winfo_screenheight() / pix2in
    fig = plt.figure(figsize=(width, height), dpi=pix2in)
    return fig

def draw_line(color='r'):
    """
    interactively draw a line on a pyplot axis
    return the coordinates of the endpoints
    """
    ax = plt.gca()
    ## get 2 input clicks
    xy = plt.ginput(2, timeout=0)
    ## extract x and y values
    x = [p[0] for p in xy]
    y = [p[1] for p in xy]
    ## plot and draw preserving original limits
    limits = ax.axis()
    line = plt.plot(x, y, color=color)
    ax.axis(limits)
    ax.figure.canvas.draw()
    return xy
        
def distance(xy1, xy2):
    """calculate the distance between two points"""
    return np.sqrt((xy2[0]-xy1[0])**2 + (xy2[1]-xy1[1])**2)
        
def pointcount(im, grid_spacing=100, savefig=None, n_axes=2):
    """
    draw lines on image of sediment to point count grains
    
    im is a PIL Image object
    grid_spacing determines the spacing in pixels for the sampling grid
    savefig specifies the file name to save to (doesn't save if None)
    n_axes specifies whether 1 or 2 axes will be measured on each grain
    
    returns a numpy array recording each measurement and the position of the 
    node where the measurement was made
    """
    ## create figure and axis instances
    fig = full_screen_figure()
    ax = plt.subplot(111)
    ## calculate number of grid nodes and preallocate numpy array
    w_im, h_im = im.size
    n_nodes = (w_im//grid_spacing) * (h_im//grid_spacing)
    sizes = np.zeros((n_nodes, 2+n_axes))
    ## plot image and text
    implot = plt.imshow(im)
    limits = ax.axis()
    plt.xlabel('Location (pixels)')
    plt.ylabel('Location (pixels)')
    htext = fig.text(.5, .02, '', size=10)
    dot = plt.plot(0, 0, 'm.', ms=2, zorder=15)[0]
    ax.axis(limits)
    ## set up grid
    ax.grid(b=1, which='minor', color='c', linestyle='-', zorder=10)
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(base=grid_spacing))
    ax.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(base=grid_spacing))
    ## display figure and keep running the program
    plt.show(block=False)
    ## loop through grid nodes

    ctr = -1
    for r in range(grid_spacing, h_im, grid_spacing):
        ## zoom to current row of nodes
        plt.ylim([r+grid_spacing, r-grid_spacing])
        for c in range(grid_spacing, w_im, grid_spacing):
            ctr += 1
            htext.set_text('x = %i , y = %i \nnodes remaining = %i' % (c, r, n_nodes-ctr))
            dot.set_data(c, r)
            ax.figure.canvas.draw()
            ## draw lines and calculate distances
            try:
                xy1, xy2 = draw_line()
                sizes[ctr,2] = distance(xy1, xy2)
                if n_axes == 2:
                    xy3, xy4 = draw_line(color='b')
                    sizes[ctr,3] = distance(xy3, xy4)
                sizes[ctr,:2] = c, r
            ## ValueError: too many values too unpack (clicked too fast)
            except ValueError as e:
                print('\nValueError: %s' % e)
                print('(You probably clicked too quickly)')
                print('\nFailed at %s, %s' % (r, c))
                return sizes
            ## Other errors... perhaps from closing the figure window
            except Exception as e:
                print('\n%s' % e)
                print('\nFailed at %s, %s' % (r, c))
                return sizes
    ## draw full image extent
    ax.axis(limits)
    ax.figure.canvas.draw()
    ## save figure
    if savefig:    
        plt.savefig(savefig, dpi=300)
        print('\nFigure saved as %s' % savefig)
    return sizes
    
def create_save_file_name(root, ext, add_text='_point_count_'):
    """create a file name that will not overwrite an existing file"""
    if ext == 'none':
        return None
    root = root.split('.')[0]
    save_file_name = root + add_text + '%i.' % 1 + ext
    for ii in range(2, 1000):
        if os.path.isfile(save_file_name):
            save_file_name = root + add_text + '%i.' % ii + ext
        else:
            break
    return save_file_name
    
if __name__ == '__main__':
    ## set up argument parser
    parser = argparse.ArgumentParser(description='Software to make regular manual measurements of grains in an image of sediment')
    parser.add_argument('-i', type=str, dest='image_file', default='',
                        metavar='image_file', help='image file to use')
    parser.add_argument('-s', type=str, default='csv', 
                        choices=('csv','pkl','none'), 
                        help='file type to save to (default="csv")')
    parser.add_argument('--sf', type=str, default='png', 
                        choices=('png', 'pdf', 'none'),
                        help='file type to save figure to (default="png")')
    parser.add_argument('--nax', type=int, default=2, choices=(1, 2),
                        help='number of axes to measure for each grain (default=2)')
    parser.add_argument('--gs', type=int, default=100, 
                        help='grid spacing in pixels (default=100)')
    ## parse arguments
    args = parser.parse_args()
    ## get image_file if none passed in arguments
    if not args.image_file:
        args.image_file = tkfiledialog.askopenfilename()
    ## open image_file as a PIL Image
    im = Image.open(args.image_file)
    ## create file name to save figure
    save_fig_name = create_save_file_name(args.image_file, args.sf)
    ## run point count program with MatplotlibDeprecationWarning disabled
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", 
                                category=mpl.MatplotlibDeprecationWarning)
        sizes = pointcount(im, grid_spacing=args.gs, n_axes=args.nax,
                           savefig=save_fig_name)
    ## save point count data
    if args.s == 'none':
        print('\nData not saved')
    else:
        save_file_name = create_save_file_name(args.image_file, args.s)
        ## save as a .pkl file
        if args.s == 'pkl':
            with open(save_file_name, 'wb') as file:
                pickle.dump(sizes, file)
        ## save as a .csv file
        else:
            with open(save_file_name, 'w', newline='') as file:
                wrtr = csv.writer(file)
                if args.nax == 2:
                    wrtr.writerow(['Xlocation_pixels', 'Ylocation_pixels', 'Ax1_pixels', 'Ax2_pixels'])
                else:
                    wrtr.writerow(['Xlocation_pixels', 'Ylocation_pixels', 'Ax1_pixels'])
                wrtr.writerows(sizes)
        print('\nData saved as %s' % save_file_name)                
        
