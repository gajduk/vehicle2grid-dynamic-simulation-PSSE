import psspy_import
import power_system
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import gridspec
import dyntools
import numpy
import random
from scipy import misc

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
    node_labels = {i:str(i) for i in range(1,40)}
    
    time,frequencies,res = getFrequencyDeviation(channel_file)
    
    gens = [gen._bus for gen in power_system_object._generators]
    loads = [load._bus for load in power_system_object._loads]
    stubs = list(set(range(1,power_system_object._nbus+1)) - (set(gens+loads)))
    nodelists = [gens,loads,stubs]
    bus_colors = {}
    node_colors = []
    
    qss = nx.shortest_path_length(G,10)
    qsna =  {key:(12-qss[key])*1.0/10 for key in qss}
    qsa = {key:(14-qss[key])*1.0/9 for key in qss}
    qsna[10] = 2.4
    qsna[32] = 1.9
    qsna[13] = 1.3
    qsna[12] = 1.1
    qsna[11] = 1.15
    #qs = {10:0.99,32:0.93,13:0.94,12:0.923,11:0.947,14:0.912,15:0.901,6:0.873,31:}
    
    
    for nodelist in nodelists:
        #node_colors.append([float(res[key]) for key in res if key in nodelist])
        temp = []
        for i in range(len(nodelist)):
            if a:
                if nodelist[i] in qsa:
                    q = qsa[nodelist[i]]*random.gauss(.7,.08)
                else:
                    q = 0#random.gauss(.25,.25)
            else:
                if nodelist[i] in qsna:
                    q = qsna[nodelist[i]]*random.gauss(.35,.08)
                else:
                    q = 0#random.gauss(.25,.25)
                
            if q < 0:
                q = 0.0
            if q > 1:
                q = 1.0
            bus_colors[nodelist[i]] = q
            temp.append(q)
        node_colors.append(temp)
        
    shapes = ['s','o','o']
    node_sizes = [90,90,90]
    img = misc.imread('asd.PNG')    
    img[:,:,3] = 190#set alpha
    
    plt.subplot(subplots[0])
    plt.imshow(img,zorder=0,extent=[0.0, 1.0, 0.0, 1.0])
    for i in range(3):
        im = nx.draw_networkx_nodes(G,pos,
                   nodelist=nodelists[i],
                   node_color=node_colors[i],
                   node_shape=shapes[i],
                   node_size=node_sizes[i],
                   cmap=plt.cm.get_cmap('RdYlBu_r'),
                   vmin=0.0, vmax=1.0)
                   
    #nx.draw_networkx_labels(G,pos,labels=node_labels,font_size=15)
                   
    plt.axis('off')
    
    nx.draw_networkx_edges(G,pos)
    
    
    cmap = plt.cm.get_cmap('RdYlBu_r')
    plt.subplot(subplots[1])
    #bus_colors[bus]
    for bus in sorted(bus_colors):
        #colorVal = plt.cm.get_cmap('RdYlBu_r').to_rgba(res[bus])
        plt.plot(time,frequencies[bus],color=cmap(bus_colors[bus]),alpha=0.7)
        plt.xlim([0.0,30.0])
        plt.ylim([59.62,60.38])
        plt.xlabel('Time [s]')
        if a:
            plt.ylabel('Frequency [Hz]')
        plt.xticks([0,10,20,30])
        plt.yticks([59.7,60,60.3])
    return im
    

def visualize(power_system_object,no_control,with_control):
    
    G = nx.Graph()
    weights = []
    for branch in power_system_object._branches:
        weight = .02/((branch._X+0.001)**2)
        weights.append(weight)
        G.add_edge(branch._ibus,branch._jbus,length=weight)
    
    pos = nx.spring_layout(G,weight="length")
    #print pos
    gs = gridspec.GridSpec(2, 2, width_ratios=[1, 1],height_ratios=[4, 2]) 
    fig, axes = plt.subplots(nrows=2, ncols=2)
    positions = {1:[0.58,0.25], 2:[0.55,0.28],30:[0.52,0.26],25:[0.50,0.36],3:[0.45,.30],18:[0.44,.34],17:[0.435,.38],37:[0.48,0.37],\
                27:[0.48,0.41],26:[0.53,0.46],28:[0.56,0.6],29:[0.67,0.7],38:[0.7,0.75],39:[0.51,0.2],9:[0.46,0.22],8:[0.38,0.21],\
                 7:[0.34,0.15], 6:[0.26,0.135],31:[0.29,0.17],5:[0.25,0.21],4:[0.31,0.27],14:[0.24,0.3],12:[0.11,0.09],11:[0.2,0.13],\
                10:[0.18,0.19],32:[0.15,0.19],13:[0.13,0.24],15:[0.28,0.34],16:[0.28,0.43],24:[0.18,0.53],22:[0.17,0.78],35:[0.19,0.82],\
                23:[0.165,0.65],36:[0.2,0.635],21:[0.26,0.57],19:[0.37,0.46],33:[0.35,0.495],20:[0.445,0.59],34:[0.465,0.61]}
    
    for key in range(1,40):
        if key in positions:
            pos[key] = numpy.array(positions[key])
        else:
            pos[key] = numpy.array([0.0,0.0])
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