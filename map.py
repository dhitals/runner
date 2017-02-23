# class for each run
import numpy as np
import matplotlib.pyplot as plt

import fiona
import folium

import cartopy.crs as ccrs
from cartopy.io import shapereader
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.io.img_tiles as cimgt

class map(object):
    def __init__():
        pass

    def map(self, file):
        layer = fiona.open(file, layer='tracks')

        coords = layer[0]['geometry']['coordinates'][0]
        # folium uses (lat, lon) instead of (lon, lat) :-(
        fCoords = [ (coords[i][1], coords[i][0]) for i in range(len(coords)) ]

        fCenter = [np.mean([coords[0][1], coords[-1][1]]),
                   np.mean([coords[0][0], coords[-1][0]])]
        
        m = folium.Map(location=fCenter, zoom_start=13, tiles='OpenStreetMap')
        
        kw = dict(opacity=1.0, weight=5)
        
        m.add_child(folium.PolyLine(locations=fCoords, color='blue', **kw))

        return m
    
    def make_map(projection=ccrs.PlateCarree()):
        fig, ax = plt.subplots(figsize=(9, 13),
                               subplot_kw=dict(projection=projection))
        gl = ax.gridlines(draw_labels=True)
        gl.xlabels_top = gl.ylabels_right = False
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        
        return fig, ax

    def get_static_map():
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
