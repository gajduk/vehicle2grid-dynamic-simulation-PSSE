import dynamic_simulation
import control
import disturbances
import channel_utils
import copy
import concurrent.futures
from random import randrange

def asd(dsim,d,c):
    channel_dir = "channels"
    channel_file = channel_dir+"\\"+str(hex(randrange(1000000000)))+".out"
    dsim._channels.setChannelFile(channel_file)
    dsim._control.setSimulation(dsim)
           
    dsim.runSimulation()
    with open("times4.txt","a") as f:
        f.write(str(d)+" "+str(c)+" "+str(dsim._channels.getTimeOfStabilization(dsim._disturbance.getFaultStart()+dsim._disturbance.getFaultDuration()))+"\n")

def main():

    builder = dynamic_simulation.DynamicSimulationBuilder().withEndTime(30).withNumIterations(3000).\
        withRawFile("1rts96_reduced_gens.raw").withDyrFile("1rts96.dyr").withChannel(channel_utils.CHANNELS.PEV_POWER)

    #hs = [i*0.05 for i in range(1,10)]
    h = 0.5
    
    buses = [1,3,4,8,10,11,14,16,18,21]
    
    bus_arrays = [[1,3,10,14,16,18,21],[1,3,4,8,11,16,21],[3,4,8,10,11,16,21],[1,3,8,10,11,14,16],[9],[11],[6],[5],[20],[7],[22],[14],[10],[1],[21],[18],[1,2,5],[16,18,21],[10,11,14],\
                 [1,8,21],[4,8,11],[1,3,10],[4,8,11],[1,3,8],[3,4,10],[1,3,10,14,18],[4,8,11,16,21],[3,4,10,11,21],[8,10,11,14,18]]
    
    controls = []
    
    for bus_array in bus_arrays:
        controls.append(control.LocalControlUniform(h,bus_array))
        controls.append(control.SimpleLocalControl(h,bus_array))
       
    
    #controls = [control.SimpleLocalControl(h,[1,3,10,14,16,18,21]),control.SimpleLocalControl(h,[1,3,4,8,11,16,21]),control.SimpleLocalControl(h,[3,4,8,10,11,16,21]),\
    #           control.SimpleLocalControl(h,[1,3,8,10,11,14,16])]
    #controls = [control.LocalControlUniform(h,[9]),control.LocalControlUniform(h,[12]),control.LocalControlUniform(h,[11]),\
    #          control.LocalControlUniform(h,[5]),control.LocalControlUniform(h,[6]),\
    #          control.LocalControlUniform(h,[20]),control.LocalControlUniform(h,[7]),control.LocalControlUniform(h,[22])]
    #controls = [control.NoControl(),control.SimpleLocalControl(h),control.LocalControlUniform(h),control.LocalControlAtOneBus(h,1),control.LocalControlAtOneBus(h,21),\
    #            control.LocalControlAtOneBus(h,14),control.LocalControlAtOneBus(h,10),control.LocalControlAtOneBus(h,4),control.LocalControlAtOneBus(h,18)]
    ds = [disturbances.BusFault(2,.03,19), disturbances.BranchTrip(2,2,9,3,"1"),disturbances.BranchTrip(2,.1,15,24,"1"),disturbances.BranchTrip(2,.03,14,16,"1"),disturbances.BranchTrip(2,.2,11,13,"1"),\
          disturbances.BusFault(2,.06,5), disturbances.BusFault(2,.01,16), disturbances.BusFault(2,.01,21),disturbances.BusFault(2,.06,3)]
          
    with open("times4.txt","w") as f:
        pass
        
    with concurrent.futures.ProcessPoolExecutor(max_workers=7) as executor:
        for d in ds:
            for c in controls:
                dsim = copy.deepcopy(builder).withControl(c).withDisturbance(d).build()
                #executor.submit(asd,dsim,d,c)
                asd(dsim,d,c)
        
    
if __name__ == "__main__":
    main()