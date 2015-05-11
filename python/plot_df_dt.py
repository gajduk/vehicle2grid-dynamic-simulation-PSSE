import numpy
import pylab
import dynamic_simulation
import control
import disturbances
import channel_utils

def main():
    ds = dynamic_simulation.DynamicSimulationBuilder().withControl(control.NoControl()).withEndTime(15).withNumIterations(500).\
        withRawFile("1rts96_reduced_gens.raw").withDyrFile("1rts96.dyr").withChannel(channel_utils.CHANNELS.P_LOAD).withExportFigures().\
        withDisturbance(disturbances.LoadChange(2,.1,range(1,24),1)).build()
    ds.runSimulation()
    res,times = ds._channels.getFrequencysForPEVS()
    
    for f in res:
        s = []
        t = []
        for i in range(len(times)-1):
            if times[i+1] == times[i]:
                continue
            s.append((f[i+1]-f[i])/(times[i+1]-times[i]))
            t.append(times[i+1])
        pylab.plot(t,s)
    pylab.show()    
    
if __name__ == "__main__":
    main()