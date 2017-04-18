import numpy as np
#import matplotlib.pyplot as plt

#import fiona
import folium
import branca.colormap as cm

#import cartopy.crs as ccrs
#from cartopy.io import shapereader
#from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
#import cartopy.io.img_tiles as cimgt

def get_map(activity_id, coords, z=None):
    """ Get a folium map of the activity given the coords 
        Input should be a list of tuples: (lat, lon)

        If specified, uses the third variable (e.g. pace) as plot color
    """
    
    ctr = tuple(np.mean(coords, axis=0))

    m = folium.Map(location=ctr, zoom_start=13, tiles='OpenStreetMap')
    
    if z is None:
        kw = dict(opacity=1.0, weight=3)
        line = folium.PolyLine(locations=coords, color='r', **kw)
    else:
        zcolors = ['r', 'g', 'c', 'b', 'm']
        line = folium.features.ColorLine(coords, #list(zip(lat, lon)),
                                         colors=z,
                                         colormap=cm.LinearColormap(zcolors, vmin=2, vmax=5),
                                         weight=3)
            
    m.add_child(line)

    # add markers for start and end
    folium.Marker(coords[0], icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(coords[-1], icon=folium.Icon(color='black')).add_to(m)

    m.save('./app/static/maps/{0}.html'.format(activity_id))    
    return


# class map(object):
#     def __init__():
#         pass

   
#     def make_map(projection=ccrs.PlateCarree()):
#         fig, ax = plt.subplots(figsize=(9, 13),
#                                subplot_kw=dict(projection=projection))
#         gl = ax.gridlines(draw_labels=True)
#         gl.xlabels_top = gl.ylabels_right = False
#         gl.xformatter = LONGITUDE_FORMATTER
#         gl.yformatter = LATITUDE_FORMATTER
        
#         return fig, ax

#     def get_static_map():
#         data = {'type': 'MultiLineString',
#                 'coordinates': layer[0]['geometry']['coordinates']}
        
#         # get OSM tiles
#         request = cimgt.OSM()
        
#         x = [layer.bounds[0], layer.bounds[2]]
#         y = [layer.bounds[1], layer.bounds[3]]
#         delta = 0.025
#         extent = [np.min(x) - delta, np.max(x) + delta, 
#                   np.min(y) - delta, np.max(y) + delta]

        
#         fig, ax = make_map(projection=request.crs)
        
#         ax.set_extent(extent)
        
#         img = ax.add_image(request, 14)
#         s = ax.add_geometries(shape(data), ccrs.PlateCarree(),
#                               facecolor='none',
#                               edgecolor='crimson',
#                               linewidth=2)

#         return
