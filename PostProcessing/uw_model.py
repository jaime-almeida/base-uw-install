#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 13:34:51 2019

@author: jaime
#"""
#import re as re
#import os as os
import h5py as h5
import numpy as np
import pandas as pd
from multiprocessing import  Pool 
#import dask.dataframe as dd
import gc as gc

cmy = 365*24*60*60.*100

def parallelize_dataframe(df, func, n_cores=4):
    df_split = np.array_split(df, n_cores)
    pool = Pool(n_cores)
    df = pd.concat(pool.map(func, df_split))
    pool.close()
    pool.join()
    return df

def velocity_rescale(df, scf):    
    df = df/scf*cmy
    return df

def viscosity_rescale(df, scf):
    df = np.log10(df*scf)
    return df

def dim_eval(res):
    # Not likely to be a 1D model.
    if len(res) > 2:
        return 3
    else: 
        return 2

def get_res(model_dir):
    # Make  the file path
    filename = model_dir + 'Mesh.linearMesh.00000.h5'
    
    # Read everything
    data = h5.File(filename, 'r')
    res = data.attrs['mesh resolution']
    
    # Get the dimensions:
    ndims = dim_eval(res)
    
    return np.array(res), ndims

def ts_writer(ts_in):
    # Making the timestep text:
    if ts_in <= 9:
        ts_usable = '0000' + str(ts_in)
    elif 9 < ts_in <= 99:
        ts_usable = '000' + str(ts_in)
    elif 99 < ts_in <= 999:
        ts_usable = '00' + str(ts_in)
    elif 999 < ts_in <= 9999:
        ts_usable = '0' + str(ts_in)
    else:
        ts_usable = str(ts_in)
    return ts_usable
        
# %% 
class uw_model:
    
    def __init__(self, model_dir):
        if model_dir[-1] != '/':
            self.model_dir = model_dir + '/'
        else:
            self.model_dir = model_dir

        self.res, self.dim = get_res(self.model_dir)
        # Cores are not needed for now.
        
        # Initiate a dictionary output
        self.output = {}
        
        # Initiate a boundary coordinate 
        self.boundary = {}
        
    def set_current_ts(self, step):
        # Set the timestep for further processes
        if step > 1e5:
            raise Exception('Max timestep is 10,000.')
            
         # If a previous iteration of the model exists:
        try:
            if self.current_step:
                print('A previous iteration was detected, removing the output.')
                
                # Clean the output dictionary:
                self.output = {}
                
                # Supposedly help clean further
                gc.collect()
        except:
            pass
        
        # Set the current TS
        self.current_step = ts_writer(int(step))   
            
        
       
        
    def set_scaling_factor(self, scf):
        # Set the timestep for further processes
        self.scf = float(scf)
                
    def set_slice(self, direction, value):
        # This makes unlimited slices of the model. Use with care
        if np.all(direction != 'x' and direction != 'y' and direction != 'z'):
            raise Exception('The slice direction must be: ''x'', ''y'' or ''z''!')
        
        # verify we got the mesh already
        try:
            self.output['mesh']
        except:
            raise Exception('No mesh read yet!')
        
        # Limit the mesh:
        mesh_sorted = self.output['mesh'].loc[self.output['mesh'][direction] == value]

        # If empty:
        if mesh_sorted.shape[0] == 0: 
            raise Exception('Invalid slice value, check mesh dataframe for possible slice index.')
#       
        # Recreate the output files, resetting the index:
        for key in self.output:
            self.output[key] = self.output[key].iloc[mesh_sorted.index].reset_index(drop=True)
            
    ##################################################
    #              RETRIEVING INFORMATION            #
    ##################################################
    # Get mesh information:
    
    def get_mesh(self):
         # Set the file path:
        filename = self.model_dir + 'Mesh.linearMesh.' + \
                                    self.current_step + '.h5'
    
        # Read the h5 file:
        data = h5.File(filename, 'r')
        
        # Get the information from the file:
        mesh_info = data['vertices'][()]
        
        # Write the info accordingly:
        if self.dim == 2:
            self.output['mesh'] = pd.DataFrame(data=mesh_info, \
                                                  columns= ['x', 'y'], \
                                                  dtype='float')
        else:
            # in 3D:
            self.output['mesh'] = pd.DataFrame(data=mesh_info, \
                                                  columns= ['x', 'y', 'z'], \
                                                  dtype='float')
        
        # Save the model dimensions:
        axes    = self.output['mesh'].columns.values
        max_dim = self.output['mesh'].max().values
        min_dim = self.output['mesh'].min().values
        
        for axis, min_val, max_val in zip(axes, min_dim, max_dim):
            self.boundary[axis] = [min_val, max_val]
        
        
    def get_velocity(self):
        try:
            self.scf
        except:
            raise ValueError('No Scaling Factor detected!')
            
         # Set the file path:
        filename = self.model_dir + 'VelocityField.' + \
                                    self.current_step + '.h5'
    
        # Read the h5 file:
        data = h5.File(filename, 'r')
        
        # Get the information from the file:
        vel_info = data['data'][()]
        
        # Write the info accordingly:
        if self.dim == 2:
            self.output['velocity'] = pd.DataFrame(data=vel_info, \
                                                  columns= ['vx', 'vy'])
        else:
            # in 3D:
            self.output['velocity'] = pd.DataFrame(data=vel_info, \
                                                  columns= ['vx', 'vy', 'vz'])
       
        # Rescale
        self.output['velocity'] = velocity_rescale(self.output['velocity'], \
                                                   self.scf)
        
    def get_viscosity(self):
        try:
            self.scf
        except:
            raise ValueError('No Scaling Factor detected!')        
        
         # Set the file path:
        filename = self.model_dir + 'ViscosityField.' + \
                                    self.current_step + '.h5'
    
        # Read the h5 file:
        data = h5.File(filename, 'r')
        
        # Get the information from the file:
        mat_info = data['data'][()]
        
        # Write the info accordingly:

        self.output['viscosity'] = pd.DataFrame(data=mat_info, \
                                                  columns= ['eta'])
    
        # Rescale
        self.output['viscosity'] = viscosity_rescale(
                                                   self.output['viscosity'], \
                                                   self.scf)
    def get_material(self):
         # Set the file path:
        filename = self.model_dir + 'MaterialIndexField.' + \
                                    self.current_step + '.h5'
    
        # Read the h5 file:
        data = h5.File(filename, 'r')
        
        # Get the information from the file:
        mat_info = data['data'][()]
        
        # Write the info accordingly:

        self.output['material'] = pd.DataFrame(data=mat_info, \
                                                  columns= ['mat'])
        
   
        
    # Get the strain information 
    def get_strain(self):
        # Set the file path:
        filename = self.model_dir + 'recoveredStrainRateField.' + \
                                    self.current_step + '.h5'
    
        # Read the h5 file:
        data = h5.File(filename, 'r')
        
        # Get the information from the file:
        strain_info = data['data'][()]
        
        # Write the info accordingly:
        if self.dim == 2:
            self.output['strain'] = pd.DataFrame(data=strain_info, \
                                                  columns= ['xx', 'yy', 'xy'])
        else:
            # in 3D:
            self.output['strain'] = pd.DataFrame(data=strain_info, \
                                                  columns= ['xx', 'yy', 'zz',\
                                                            'xy', 'xz', 'yz'])
    
        
    ##################################################
    #              ADDITIONAL FUNCTIONS              #
    ##################################################  
    
    def extract_by_material(self, mat_index):
        
        if type(mat_index) == int or type(mat_index) == float:
            # Extract only one material index:
            mat_index = float(mat_index)
            
            # Limit the output:
            mesh_sorted = self.output['material'].\
                            loc[self.output['material']['mat'] == mat_index]
    
            # If empty:
            if mesh_sorted.shape[0] == 0: 
                raise Exception('Invalid material submitted, check material DB to see if it exists.')
           
            # Recreate the output files, resetting the index:
            for key in self.output:
                self.output[key] = self.output[key].iloc[mesh_sorted.index].\
                                                    reset_index(drop=True)
        elif type(mat_index) == list or type(mat_index) == np.ndarray:
            # Extract by subset
            temp_bool = [self.output['material']['mat'].values == float(x) for x in mat_index]
            
            # Find correct locations:
            temp_bool = sum(temp_bool) # Any area with zero is not important 
            
            # Get the index array
            index_bool = temp_bool > 0
            
            # Recreate the output dictionary:
            for key in self.output:
                self.output[key] = self.output[key].iloc[index_bool].\
                                                    reset_index(drop=True)
#            