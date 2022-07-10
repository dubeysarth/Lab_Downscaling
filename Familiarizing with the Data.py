import xarray as xr
import netCDF4 as nc
import numpy as np
import pandas as pd
import itertools
import os
from tqdm import tqdm

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import seaborn as sns

from PIL import Image
import io
#%%
def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    #return buf
    img = Image.open(buf)
    return img

def render(images, image_file = 'FileName', duration = 100):
    # loop=0: loop forever, duration=1: play each frame for 1ms
    images[0].save(
        f"{image_file}.gif", save_all=True, append_images=images[1:], loop=0, duration=duration)
#%%
def get_plot(idx, date, ds, sample = 'day', show_plot = False, scatter_latlon = False, set_scale = True):
    # ds = xr.open_dataset(filepath)
    if sample == 'month':
        ds = ds.resample(time = '1MS').sum()
    try:
        temp = ds['pr']
        del temp
        var_name = 'pr'
    except:
        var_name = 'rain'
    vmin, vmax = float(ds[var_name].min()), float(ds[var_name].max())
    lons = ds.variables['lon'][:]
    lats = ds.variables['lat'][:]
    lon_0 = lons.mean()
    lat_0 = lats.mean()
    rain = ds.variables[var_name][idx,:,:]
    fig = plt.figure(dpi = 300)
    m = Basemap(resolution='l',projection='cyl',\
                llcrnrlon = 66.5, urcrnrlon = 100, llcrnrlat = 6.5, urcrnrlat = 38.5)

    # Because our lon and lat variables are 1D,
    # use meshgrid to create 2D arrays
    # Not necessary if coordinates are already in 2D arrays.
    lon, lat = np.meshgrid(lons, lats)
    xi, yi = m(lon, lat)

    # Plot Data
    if set_scale:
        cs = m.pcolor(xi,yi,np.squeeze(rain), vmin = vmin, vmax = vmax)
    else:
        cs = m.pcolor(xi,yi,np.squeeze(rain))

    if scatter_latlon: m.scatter(lon, lat, latlon=True, c = 'red', s = 0.01)

    # Add Grid Lines
    m.drawparallels(np.arange(-80., 81., 10.), labels=[1,0,0,0], fontsize=10)
    m.drawmeridians(np.arange(-180., 181., 10.), labels=[0,0,0,1], fontsize=10)
    # Add Coastlines, States, and Country Boundaries
    m.drawcoastlines()
    m.drawstates()
    m.drawcountries()
    # Add Colorbar
    cbar = m.colorbar(cs, location='right', pad="10%")
    if sample == 'month':
        cbar.set_label('mm/mon', fontsize = 16)
        plt.title(rf"Date: {date.dt.year.values} - {date.dt.month.values}")
    else:
        cbar.set_label('mm/day', fontsize = 16)
        plt.title(rf"Date: {date.dt.year.values} / {date.dt.month.values} / {date.dt.day.values}")
    if not show_plot:
        plt.close()
    else:
        plt.show()
    return fig

#%%
def get_rendering():
    Images = []

    filepath = 'MIROC-ESM.nc'
    ds = xr.open_dataset(filepath)
    for idx, date in tqdm(itertools.islice(enumerate(ds['time']),0, None,1)):
        fig = get_plot(idx, date, ds, 'month')
        im = Image.fromarray(np.array(fig2img(fig)), 'RGBA')
        Images.append(im)

    render(Images, 'GCM_MIROC-ESM_monthly', duration = 1)
#%%
