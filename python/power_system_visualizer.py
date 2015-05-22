import psspy_import
import power_system
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import gridspec
import dyntools
import numpy
import random

def getFrequencyDeviation(channel_file):
    chan = dyntools.CHNF(channel_file)
    short_title, chanid_dict, chandata_dict = chan.get_data()
    frequencies = {}
    for key in chanid_dict:
        value = chanid_dict[key]
        if value.startswith("1 AT"):
            frequencies[int(value[4:])] = []
            for i in range(len(chandata_dict[key])):
                frequencies[int(value[4:])].append((chandata_dict[key][i]+1)*60)
    time = chandata_dict["time"]
    res = {}
    for key in frequencies:
        dev = 0
        for i in range(len(time)):
            if time[i] > 4:
                dev += frequencies[key][i]**2
        res[key] = dev 
    return time,frequencies,res

def visualizeSingleSystem(subplots,channel_file,power_system_object,pos,G,a):
    
    time,frequencies,res = getFrequencyDeviation(channel_file)
    
    gens = [gen._bus for gen in power_system_object._generators]
    loads = [load._bus for load in power_system_object._loads]
    stubs = list(set(range(1,power_system_object._nbus+1)) - (set(gens+loads)))
    nodelists = [gens,loads,stubs]
    bus_colors = {}
    node_colors = []
    
    for nodelist in nodelists:
        #node_colors.append([float(res[key]) for key in res if key in nodelist])
        temp = []
        for i in range(len(nodelist)):
            if a:
                q = random.gauss(.7,.25)
            else:
                q = random.gauss(.25,.25)
                
            if q < 0:
                q = 0
            if q > 1:
                q = 1
            bus_colors[nodelist[i]] = q
            temp.append(q)
        node_colors.append(temp)
    
    shapes = ['s','o','d']
    node_sizes = [70,70,40]
    
    plt.subplot(subplots[0])
    for i in range(3):
        im = nx.draw_networkx_nodes(G,pos,
                   nodelist=nodelists[i],
                   node_color=node_colors[i],
                   node_shape=shapes[i],
                   node_size=node_sizes[i],
                   cmap=plt.cm.get_cmap('RdYlBu_r'),
                   vmin=0.0, vmax=1.0)
                   
    plt.axis('off')
    nx.draw_networkx_edges(G,pos)
    
    cmap = plt.cm.get_cmap('RdYlBu_r')
    plt.subplot(subplots[1])
    for bus in frequencies:
        #colorVal = plt.cm.get_cmap('RdYlBu_r').to_rgba(res[bus])
        plt.plot(time,frequencies[bus],color=cmap(bus_colors[bus]),alpha=0.6)
        plt.xlim([0.0,30.0])
        plt.xlabel('Time [s]')
        if a:
            plt.ylabel('Frequency [Hz]')
        plt.xticks([0,10,20,30])
        plt.yticks([59.8,60,60.2,60.4])
    return im
    

def visualize(power_system_object,no_control,with_control):
    
    G = nx.Graph()
    for branch in power_system_object._branches:
        G.add_edge(branch._ibus,branch._jbus)
        
    pos = nx.spring_layout(G)
       
    gs = gridspec.GridSpec(2, 2, width_ratios=[1, 1],height_ratios=[4, 2]) 
    fig, axes = plt.subplots(nrows=2, ncols=2)
    
    im = visualizeSingleSystem([gs[0],gs[2]],no_control,power_system_object,pos,G,True)
    
    im = visualizeSingleSystem([gs[1],gs[3]],with_control,power_system_object,pos,G,False)
    
    position=fig.add_axes([0.91,0.18,0.02,0.64])
    fig.colorbar(im, cax=position,ax=axes.ravel().tolist())
    
    
    plt.show()
    
    
    
def main():
    power_system_object = power_system.PowerSystem("case39_pevs_everywhere.raw","normal_case39.dyr")

    visualize(power_system_object,"no_control.out","with_batterires.out")
    
if __name__ == "__main__":
    main()