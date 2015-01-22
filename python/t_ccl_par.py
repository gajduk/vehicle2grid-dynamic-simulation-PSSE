import os,sys
import psspy_import
import control
import disturbances        
import t_ccl
import dyntools
import concurrent.futures
import dynamic_simulation
import IOUtils
import time
import copy
    
current_milli_time = lambda: int(round(time.time() * 1000))
    
def getAllBusFaultsBuilders(builder):
    """
    Returns an array of DynamicSimulationBuilders that are a copy of the builder object supplied as argument
    and the disturbances are bus faults at all the buses in the system
    """
    power_system = builder.build()._power_system_object
    res = []
    for each in range(1,power_system._nbus):
        res.append(copy.deepcopy(builder).withDisturbance(disturbances.BusFault(2,1,each)))
        
    return res
    
def getAllBuildersWithControl(builders,control_objects):
    """
    Returns an array of DynamicSimulationBuilders (with len(builder)*len(control) elements) that have all the properties as the ones supplied in the builders array, but with control_bojects specified in the control array
    """
    res = []
    for control_object in control_objects:
        for each in builders:
            res.append(copy.deepcopy(each).withControl(control_object))
    
    return res
    
def calculatetccl(builders,tolerance=0.01,res_file="",pretty_print=True,progress=True,max_threads=9):
    """
    Concurrently calculates the ccl for an array of DynamicSimulationBuilders
    The results are outputted to IOUtils.res_file, and the progress to IOUtils.log_file
    """
    
    dynamic_simulations = [each.build() for each in builders]
    if progress:
        IOUtils.log("IT HAS BEGAN \n")
    if pretty_print:
        header = "Disturbance".ljust(40)+"Control".ljust(35)+"T_ccl".ljust(10)+"\n"
        if res_file == "":
            IOUtils.res(header)
        else:
            IOUtils.logToFile(header,res_file)
            
    start = current_milli_time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_threads) as executor:
        for each in dynamic_simulations:
            executor.submit(t_ccl.determineT_ccl,each,tolerance,res_file,pretty_print,progress)
            
    end = current_milli_time()
    if progress:
        IOUtils.log("Total time: "+str((end-start)/60000/60)+" h "+str((end-start)/60000%60)+" m "+str((end-start)/1000%60)+" s\n")
    
    

def main():
    """
        Calculating the t_ccl for all bus faults on the case39 and a range of control_coefficients
    """
    control_coefficients = [0.1*x for x in range(0,30)]
    control_objects = [control.SimpleLocalControl(each) for each in control_coefficients]
    
    builder = dynamic_simulation.DynamicSimulationBuilder().withRawFile("normal_case39.raw").withDyrFile("normal_case39.dyr").\
              withEndTime(30).withNumIterations(1000)
        
    all_builders = getAllBuildersWithControl(getAllBusFaultsBuilders(builder),control_objects)
    
    calculatetccl(all_builders)
            
            
if __name__ == '__main__':
    main()
     