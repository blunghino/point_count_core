point_count_core
================

point_count_core.py: Software to make regular manual measurements of grains in an image of sediment

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
  -h, --help           show this help message and exit;
  -i image_file        image file to use;
  -s {csv,pkl,none}    file type to save to (default="csv");
  --sf {png,pdf,none}  file type to save figure to (default="png");
  --nax {1,2}          number of axes to measure for each grain (default=2);
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
