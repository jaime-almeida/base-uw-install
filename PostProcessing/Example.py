#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 13:46:18 2019

@author: jaime
"""

import pandas as pd
from uw_model import uw_model
import h5py as h5
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


path =  '/media/jaime/FCUL_BACKUP/3D_AgeTest/model_results/3D_block_S'
#path = '/media/jaime/FCUL_BACKUP/AgeTest/model_results/Peierls900/50OP_50DP'

test = uw_model(path)
test.set_scaling_factor(1e22)
test.set_current_ts(1e3)
test.get_mesh()
#test.get_viscosity()
test.get_material()

test.set_slice('y', test.output['mesh']['y'].iloc[-1])
#test.set_slice('x', 1.8e6)
#test.extract_by_material(3)

#
#Test plotting
fig, ax = plt.subplots(figsize=[20,20])

#ax = Axes3D(fig)

# 2D:

ax.scatter(test.output['mesh']['x'],
           test.output['mesh']['z'],
           c = test.output['material']['mat'],
           linewidth=0,
           cmap = 'RdYlBu_r')

# 3D:
#temp = ax.scatter(test.output['mesh']['x'],
#                  test.output['mesh']['z'],
#                  test.output['mesh']['y'],
#                  c=test.output['material']['mat'],
#                  cmap='RdYlBu_r')
#
#ax.set_xlim(test.boundary['x'][0], test.boundary['x'][1])
#ax.set_ylim(test.boundary['z'][0], test.boundary['z'][1])
#ax.set_zlim(test.boundary['y'][0], test.boundary['y'][1])
#
#fig.colorbar(temp)
