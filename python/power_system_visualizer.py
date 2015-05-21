import psspy_import
import power_system
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import gridspec

def visualize(power_system_object):
    G = nx.Graph()
    for branch in power_system_object._branches:
        G.add_edge(branch._ibus,branch._jbus)
        
    pos=nx.spring_layout(G)
    
    
    gens = [gen._bus for gen in power_system_object._generators]
    loads = [load._bus for load in power_system_object._loads]
    stubs = list(set(range(1,power_system_object._nbus+1)) - (set(gens+loads)))

    nodelists = [gens,loads,stubs]
    shapes = ['s','o','d']
    
    gs = gridspec.GridSpec(2, 2, width_ratios=[1, 1],height_ratios=[4, 2]) 
    
    node_size1 = 80
    
    fig, axes = plt.subplots(nrows=2, ncols=2)
    plt.subplot(gs[0])
    for i in range(3):
        nx.draw_networkx_nodes(G,pos,
                   nodelist=nodelists[i],
                   node_color=range(len(nodelists[i])),
                   node_shape=shapes[i],
                   node_size=node_size1,
                   cmap=plt.cm.get_cmap('RdYlBu'))
                   
    plt.axis('off')
    nx.draw_networkx_edges(G,pos)
    
    plt.subplot(gs[1])
    for i in range(3):
        im = nx.draw_networkx_nodes(G,pos,
                   nodelist=nodelists[i],
                   node_color=range(len(nodelists[i])),
                   node_shape=shapes[i],
                   node_size=node_size1,
                   cmap=plt.cm.get_cmap('RdYlBu'))
                   
    plt.subplot(gs[1])
    
                   
    plt.axis('off')                       
    nx.draw_networkx_edges(G,pos)
    position=fig.add_axes([0.91,0.18,0.02,0.64])
    fig.colorbar(im, cax=position,ax=axes.ravel().tolist())
    
    
    plt.show()
    
    
    
def main():
    power_system_object = power_system.PowerSystem("case39_pevs_everywhere.raw","normal_case39.dyr")
    print [pev._bus for pev in power_system_object._pevs]
    visualize(power_system_object)
    
if __name__ == "__main__":
    main()