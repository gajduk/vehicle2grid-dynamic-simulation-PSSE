import psspy_import
import psspy
from math import ceil
import disturbances
import control
import channel_utils
import utils
import os
import power_system
import dyntools
import IOUtils
from random import randrange

trash_dir = "trash"
matlab_dir = "matlab_results"

#create the trash and the matlab dirs if they don't already exist
if not os.path.exists(trash_dir):
    os.mkdir(trash_dir) 

if not os.path.exists(matlab_dir):
    os.mkdir(matlab_dir) 
    
class DynamicSimulation(object):
    """Holds information for a single dynamic simulation (end_time, disturbance, control, power_system data etc). 
    The simulation can be ran using runSimulation.
    Construct objects of this class using the DynamicSimulationBuilder"""
    
    def __init__(self,disturbance,control_object,end_time,num_iterations,channels,plot,power_system_object,suppress_output,export_to_matlab,export_figures):
        self._disturbance = disturbance
        self._control = control_object
        self._end_time = end_time
        self._num_iterations = num_iterations
        self._channels = channels
        self._plot = plot
        self._power_system_object = power_system_object
        self._suppress_output = suppress_output
        self._control.setSimulation(self)
        self._export_to_matlab = export_to_matlab
        self._export_figures = export_figures
    
    def runSimulation(self):
        """Runs the simulation by crating an instance of psspy, loading the raw and dyr data, applying the disturbance and controling PEV output power. Finally plots in native PSS/E or export to matlab."""
        sufix = str(self._disturbance)+"_"+str(self._control)
        conec_file = trash_dir+"\\CC1_"+sufix+".out"
        conet_file = trash_dir+"\\CT1_"+sufix+".out"
        compile_file = trash_dir+"\\compile_"+sufix+".out"
    
        psspy.psseinit(49)
        
        #suppress output if required, else redirect it to python
        if self._suppress_output:
            psspy.report_output(6,"",[0,0])
            psspy.progress_output(6,"",[0,0])
            #psspy.progress_output(2,r"""pot.txt""",[0,0])
        else:
            #redirect psse output to python
            import redirect
            redirect.psse2py()
    
        #----------------------
        #read in case data
        psspy.read(0,self._power_system_object._raw_filename)

        #solve the power flow
        psspy.fdns([0,0,0,1,1,1,99,0])

        #----------------------
        #convert all generators
        psspy.cong(0)

        #----------------------
        #conv_standard_loads
        #change the vector of numbers to get constant current, admittance or power conversion
        utils.convertLoads([0.0,100.0,0.0,100.0])

        #convert the PEVs to constant power loads
        utils.convertPEVs()
        
        #----------------------------------------
        #read in dynamics data

        psspy.dyre_new([1,1,1,1],self._power_system_object._dyr_filename,"","","")

        #solve power flow with dynamics tysl - and fact devices (was in tutorial) - not sure if we need it though
        psspy.fact()
        psspy.tysl(1)
    
        #set up pre designated channels
        self._channels.setUpChannels()
    
    
        #designate channel output_file
        psspy.strt(0,self._channels._channel_file)
        
        self._performDynamicSimulation()
        
        if self._plot:
            self._channels.plot(self._channels._channels_to_include)
            
        if self._export_to_matlab:
            description = sufix.replace(" ","_").replace(".","_").replace("=","__")
            self._channels.exportToMatlab(matlab_dir+"\\"+description+".m",description,True,True,self._export_figures)
            if self._export_figures:
                import win32com.client
                h = win32com.client.Dispatch('matlab.application')
                h.Execute ("cd('"+os.getcwd()+"\\"+matlab_dir+"');")
                h.Execute (description)
            
            
        #clean up
        try:
            os.remove(conec_file)
        except:
            pass
        try:
            os.remove(conet_file)
        except:
            pass
        try:
            os.remove(compile_file)
        except:
            pass
            
        return self._channels
             
    def _simulateANumberofSteps(self,start_time,duration,num_steps,control):
        if num_steps == 0:
            num_steps = 1
        step_duration = duration*1.0/num_steps
        for i in range(0,int(num_steps)):
            step_end_time = step_duration*(i+1)+start_time
            psspy.run(0,step_end_time,1000,1,0)
            control.exhibitControl(step_end_time)
        return start_time+duration
        
    def _performDynamicSimulation(self,):
        """An internal method that performs dynamic simulations with variable step sizes."""
         
        end_time,num_steps,disturbance,control = self._end_time, self._num_iterations, self._disturbance, self._control
        #-------------------------------------------------------------
        #some parameters that control the step sizes and simulation granularity
        
        #min step sizes for differently grained dynamic simulations, if the actual size is smaller then this it is trimmed down to its minimum value
        normal_min_step_size = .001
        fine_grained_min_step_size = .00001
        extra_fine_grained_min_step_size = .0000001
        #max number of steps during each period
        ns_initial_period = ceil(.05*num_steps)
        ns_extra_fine_grained_faulted = ceil(.10*num_steps)
        ns_fine_grained_faulted = ceil(.10*num_steps)
        ns_normal_faulted = ceil(.10*num_steps)
        ns_extra_fine_grained_post_fault = ceil(.20*num_steps)
        ns_fine_grained_post_fault = ceil(.20*num_steps)
        ns_normal_post_fault = ceil(.25*num_steps)
        #max duration of each phase
        d_extra_fine_grained_faulted = .05*end_time
        d_fine_grained_faulted = .15*end_time
        d_extra_fine_grained_post_fault = .05*end_time
        d_fine_grained_post_fault = .15*end_time
        current_time = 0
        
        #-------------------------------------------------------------
        #simulate the initial period
        duration_to_simulate = disturbance.getFaultStart()
        number_of_steps = min(ceil(duration_to_simulate/normal_min_step_size),ns_initial_period)
        current_time = self._simulateANumberofSteps(current_time,duration_to_simulate,number_of_steps,control)
        
        
        #apply the disturbance
        disturbance.applyDisturbance()
        
        #-------------------------------------------------------------
        #simulate the faulted period
        
        
        faulted_duration_left = disturbance.getFaultDuration()
        #simulate extra fine grained faulted period
        #duration to simulate - either max duration or until fault is cleared
        duration_to_simulate = min(faulted_duration_left,d_extra_fine_grained_faulted)
        number_of_steps = min(ns_extra_fine_grained_faulted,duration_to_simulate/extra_fine_grained_min_step_size)
        current_time = self._simulateANumberofSteps(current_time,duration_to_simulate,number_of_steps,control)
        faulted_duration_left -= duration_to_simulate
        
        #simulate fine grained faulted period
        #duration to simulate - either max duration or until fault is cleared
        duration_to_simulate = min(faulted_duration_left,d_fine_grained_faulted)
        number_of_steps = min(ns_fine_grained_faulted,duration_to_simulate/fine_grained_min_step_size)
        current_time = self._simulateANumberofSteps(current_time,duration_to_simulate,number_of_steps,control)
        faulted_duration_left -= duration_to_simulate
        
        #simulate faulted period
        duration_to_simulate = faulted_duration_left
        number_of_steps = min(ns_normal_faulted,duration_to_simulate/normal_min_step_size)
        current_time = self._simulateANumberofSteps(current_time,duration_to_simulate,number_of_steps,control)
        
        #-------------------------------------------------------------
        #clear disturbance
        disturbance.clearDisturbance()
        
        
        #-------------------------------------------------------------
        #simulate the post-fault period
        
        post_fault_duration_left = end_time - current_time
        
        #simulate extra fine grained post-fault period
        #duration to simulate - either max duration or until end time reached
        duration_to_simulate = min(post_fault_duration_left,d_extra_fine_grained_post_fault)
        number_of_steps = min(ns_extra_fine_grained_post_fault,duration_to_simulate/extra_fine_grained_min_step_size)
        current_time = self._simulateANumberofSteps(current_time,duration_to_simulate,number_of_steps,control)
        post_fault_duration_left -= duration_to_simulate
        
        #simulate fine grained post_fault period
        #duration to simulate - either max duration or until fault is cleared
        duration_to_simulate = min(post_fault_duration_left,d_fine_grained_post_fault)
        number_of_steps = min(ns_fine_grained_post_fault,duration_to_simulate/fine_grained_min_step_size)
        current_time = self._simulateANumberofSteps(current_time,duration_to_simulate,number_of_steps,control)
        post_fault_duration_left -= duration_to_simulate
        
        #simulate post-fault period
        duration_to_simulate = post_fault_duration_left
        number_of_steps = min(ns_normal_faulted,duration_to_simulate/normal_min_step_size)
        current_time = self._simulateANumberofSteps(current_time,duration_to_simulate,number_of_steps,control)
       
      
class DynamicSimulationBuilder(object):
    """Used to build a dynamic simulation by specifying only the parameters that matter to you using the withParameter(value) methods.
    You can chain multiple withParameter method together.
    Also takes care of loading the PowerSystem and constructing the Channels object."""

    def __init__(self):
        self._disturbance = disturbances.NoDisturbance(2,0.5)
        self._control_object = control.NoControl()
        self._end_time = 20
        self._num_iterations = 1000
        self._channels_to_include = [channel_utils.CHANNELS.SPEED,channel_utils.CHANNELS.PEV_SPEED]
        self._channel_file = ""
        self._plot = False
        self._raw_file = r"""case39_multipleAEV.raw"""
        self._dyr_file = r"""case39_nogov.dyr"""
        self._suppress_output = True
        self._export_to_matlab = False
        self._export_figures = False
    
    
    def withDyrFile(self,dyr_file):
        self._dyr_file = dyr_file
        return self
        
    def withDisturbance(self,dist):
        self._disturbance = dist
        return self
        
    def withControl(self,control_object):
        self._control_object = control_object
        return self
        
    def withEndTime(self,end_time):
        self._end_time = end_time
        return self
        
    def withNumIterations(self,num_iterations):
        self._num_iterations = num_iterations
        return self
        
    def withChannel(self,channel):
        self._channels_to_include.append(channel);
        self._channels_to_include = list(set(self._channels_to_include))
        return self
    
    def withPlot(self):
        self._plot = True
        return self

    def withOutput(self):
        self._suppress_output = False
        return self
        
    def withChannelFile(self,channel_file):
        self._channel_file = channel_file
        return self
        
    def withRawFile(self,raw_file):
        self._raw_file = raw_file
        return self
        
    def withExportToMatlab(self):
        self._export_to_matlab = True
        return self
        
    def withExportFigures(self):
        self._export_to_matlab = True
        self._export_figures = True
        return self
        
    def build(self):
        self._power_system_object = power_system.PowerSystem(self._raw_file,self._dyr_file)
        if self._channel_file == "":
            self._channel_file = "channels\\"+str(hex(randrange(1000000000)))+".out"
        self._channels = channel_utils.Channels(self._channel_file,self._channels_to_include,self._power_system_object)
        return DynamicSimulation(self._disturbance,self._control_object,
            self._end_time,self._num_iterations,self._channels,
            self._plot,self._power_system_object,self._suppress_output,self._export_to_matlab,self._export_figures)
            
 
def main():
    ds = DynamicSimulationBuilder().withControl(control.SimpleLocalControl()).withEndTime(30).withNumIterations(5000).\
        withRawFile("case39_pevs_everywhere.raw").withDyrFile("normal_case39.dyr").withExportFigures().\
        withDisturbance(disturbances.BusFault(2,.05,10)).withChannel(channel_utils.CHANNELS.PEV_SPEED).build()
        
    ds.runSimulation()
    
    print ds._channels.getTimeOfStabilization(ds._disturbance.getFaultStart()+ds._disturbance.getFaultDuration())
    
if __name__ == "__main__":
    main()