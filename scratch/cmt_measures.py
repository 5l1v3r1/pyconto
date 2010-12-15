#!/usr/bin/env python

# For Pipeline Validation, Francesca Pizzorni <francesca.pizzorni@gmail.com>
# Coded by Stephan Gerhard <connectome@unidesign.ch>

# User NetworkX for some graph measures
import networkx as nx

# Use Scipy for Matlab IO
import scipy.io as spio

# Use NumPy for matrix operations
import numpy as np

# Use csv library for output writing
import csv

# For benchmarking
import time

def create_datastructure(fname):
    """ Creates a NetworkX graph for all matrices, stores the
    value in the edge values. """
    
    data = spio.matlab.loadmat(fname, matlab_compatible = True)
    
    # load data fields as specified for the Lausanne pipeline
    
    mstruct = data['matrix'][0][0]
    
    density = mstruct.density
    length = mstruct.length
    
    adcmax = mstruct.adc[0][0].max
    adcmean = mstruct.adc[0][0].mean
    adcstd = mstruct.adc[0][0].std

    famax = mstruct.fa[0][0].max
    famean = mstruct.fa[0][0].mean
    fastd = mstruct.fa[0][0].std

    t1max = mstruct.t1[0][0].max
    t1mean = mstruct.t1[0][0].mean
    t1std = mstruct.t1[0][0].std
    
    data_matrices = {'density':density, 'length':length, 'adcmax':adcmax,\
                     'adcmean':adcmean, 'adcstd':adcstd, 'famax':famax,\
                     'famean':famean, 'fastd':fastd, 't1max':t1max,\
                     't1mean':t1mean, 't1std':t1std}
    
    # create networkx graphs
    bigG = {}
    for na, mat in data_matrices.items():
        bigG[na] = nx.from_numpy_matrix(mat)
        
    return bigG 
    

def compute_measures(bigDict):
    """ Computes the measures for each network
    
    Measures to compute:
    
    nr_of_nodes
    nr_of_edges
    
    max_edge_value
    min_edge_value
    
    is_connected
    number_connected_components
    
    average_unweighted_node_degree
    average_weighted_node_degree
    
    average_clustering_coefficient
    average_weighted_shortest_path_length
    average_unweighted_shortest_path_length
    
    To be added:
     single node values, e.g. node degree of brainstem etc.
    
    Non-scalar return values: (not used yet)
     degree_distribution
     edge_weight_distribution
    
    """
    
    returnMeasures = {}

    for key, netw in bigDict.items():

        outm = {}
        
        outm['nr_of_nodes'] = netw.number_of_nodes()
        outm['nr_of_edges'] = netw.number_of_edges()
        
        outm['max_edge_value'] = np.max([d['weight']for f,t,d in netw.edges(data=True)])
        outm['min_edge_value'] = np.min([d['weight']for f,t,d in netw.edges(data=True)])
        
        outm['is_connected'] = nx.is_connected(netw)
        outm['number_connected_components'] = nx.number_connected_components(netw)
        outm['average_unweighted_node_degree'] =  np.mean(nx.degree(netw, weighted = False).values())
        outm['average_weighted_node_degree'] = np.mean(nx.degree(netw, weighted = True).values())
        outm['average_clustering_coefficient'] = nx.average_clustering(netw)
        outm['average_weighted_shortest_path_length'] = nx.average_shortest_path_length(netw, weighted = True)
        outm['average_unweighted_shortest_path_length'] = nx.average_shortest_path_length(netw, weighted = False)
        
        returnMeasures[key] = outm
        
    return returnMeasures
        
           
def write_measures(measurements, fieldnames, out_fname):
    """ Writes the computed measurements out in a csv file
    
    Each row representing a different edge attribute, each
    column representing a different measure. """

    file = open(out_fname, 'w')

    fieldnames.append('name')
    
    dw = csv.DictWriter(file, fieldnames , restval = -99)
    
    # to be compatible to Python 2.6
    dw.writerow(dict(zip(fieldnames, fieldnames)))
    
    for key, meas in measurements.items():
        
        meas['name'] = key
        dw.writerow(meas)

    file.close()


if __name__ == '__main__':
    import sys
    import os, os.path
    
    if len(sys.argv) < 2:
        print "Please enter a matlab matrix file (from the pipeline output) as input parameter!"
        sys.exit()
    else:
        if os.path.isfile(sys.argv[1]):
            fname = os.path.abspath(sys.argv[1])
            
    start = time.time()
        
    bigG = create_datastructure(fname)
    
    measurements = compute_measures(bigG)
    
    out_fname = fname.split('.')[0] + '_measures.csv'
    
    write_measures(measurements, measurements['length'].keys(), out_fname)
        
    end = time.time()
    
    print 'Measures successfully computed and stored: ' + out_fname
    print 'It took %s seconds' % str(end-start)
    