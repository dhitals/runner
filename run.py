# class for each run
import numpy as np
import matplotlib.pyplot as plt

import cartopy.crs as ccrs
from cartopy.io import shapereader
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.io.img_tiles as cimgt

class run(object):
    def __init__():
        pass

    def make_map(projection=ccrs.PlateCarree()):
        fig, ax = plt.subplots(figsize=(9, 13),
                               subplot_kw=dict(projection=projection))
        gl = ax.gridlines(draw_labels=True)
        gl.xlabels_top = gl.ylabels_right = False
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        
        return fig, ax

    def plot_run():
        data = {'type': 'MultiLineString',
                'coordinates': layer[0]['geometry']['coordinates']}
        
        # get OSM tiles
        request = cimgt.OSM()
        
        x = [layer.bounds[0], layer.bounds[2]]
        y = [layer.bounds[1], layer.bounds[3]]
        delta = 0.025
        extent = [np.min(x) - delta, np.max(x) + delta, 
                  np.min(y) - delta, np.max(y) + delta]

        
        fig, ax = make_map(projection=request.crs)
        
        ax.set_extent(extent)
        
        img = ax.add_image(request, 14)
        s = ax.add_geometries(shape(data), ccrs.PlateCarree(),
                              facecolor='none',
                              edgecolor='crimson',
                              linewidth=2)

        return
