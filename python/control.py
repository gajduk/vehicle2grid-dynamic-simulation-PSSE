import dyntools
import psspy
import IOUtils

class AbstractControl(object):
    """An abstract control class that defines the contract for Control classes"""
    
    def exhibitControl(self,time):
        """A stub implementation that does no control"""
        pass
        
    def setSimulation(self,simulation):
        self._simulation = simulation
        
    def _setPEVTotalOutputPower(self,power):
        """Set the pevs total output power. The individual PEV power is proportional to the P at that bus"""
        #PEVs needs to be defined with owner number 2
        total_power = sum(pev._P for pev in self._simulation._power_system_object._pevs)
        for pev in self._simulation._power_system_object._pevs:
            p_to_set = pev._P/total_power*power
            psspy.bsys(0,0,[ 345., 345.],3,[1,2,3],1,[pev._bus],1,[2],0,[])
            psspy.scal_2(0,0,0,[psspy._i,1,0,0,0],[p_to_set,0.0,0.0,-.0,0.0,-.0, 1.0])
            psspy.scal_2(0,0,1,[psspy._i,1,0,0,0],[p_to_set,0.0,0.0,-.0,0.0,-.0, 1.0])
            psspy.scal_2(0,0,2,[psspy._i,1,0,0,0],[p_to_set,0.0,0.0,-.0,0.0,-.0, 1.0])
            
    def _setPEVOutputPower(self,power,bus):
        """Sets the PEV power for a specified bus"""
        psspy.bsys(0,0,[ 345., 345.],3,[1,2,3],1,[bus],1,[2],0,[])
        psspy.scal_2(0,0,0,[psspy._i,1,0,0,0],[power,0.0,0.0,-.0,0.0,-.0, 1.0])
        psspy.scal_2(0,0,1,[psspy._i,1,0,0,0],[power,0.0,0.0,-.0,0.0,-.0, 1.0])
        psspy.scal_2(0,0,2,[psspy._i,1,0,0,0],[power,0.0,0.0,-.0,0.0,-.0, 1.0])
        
    def _getSumP(self,buses):
        sum_P = 0.0
        for pev in self._simulation._power_system_object._pevs:
            if len(buses) == 0:
                sum_P += pev._P
            else:
                if pev._bus in buses:
                    sum_P += pev._P
        return sum_P
        
    def _getFrequencyDeviation(self):
        frequency_deviations = self._simulation._channels.getFrequencyDeviationsForPEVS()
        i = 0
        for pev in self._simulation._power_system_object._pevs:
            frequency_deviation = frequency_deviations[i]
            if frequency_deviation > .1:
                frequency_deviation = .1
            if frequency_deviation < -.1:
                frequency_deviation = -.1
            frequency_deviations[i] = frequency_deviation
            i += 1
        return frequency_deviations
            
            
class NoControl(AbstractControl):
    """A control strategy that doesnt change the PEVs output power. Usefull as benchmark"""
        
    def __str__(self):
        return "NoControl"
                
class SimpleControl(AbstractControl):
    """Simple linear control that uses the average frequency deviation. Bounded at +- 100 mHz and the PEV output power is distributed proportionally to the power consumption at the respective bus.
    """
        
    def __init__(self,control_constant=0):
        self._control_constant = control_constant

    def exhibitControl(self,time):
        #if self._simulation._disturbance._fault_start+self._simulation._disturbance._fault_duration > time-0.1:
        #    return
        if not self._control_constant == 0:
            average_frequency_deviation = self._simulation._channels.getAverageFrequencyDeviation(time)
            if average_frequency_deviation > .1:
                average_frequency_deviation = .1
            if average_frequency_deviation < -.1:
                average_frequency_deviation = -.1
            power_to_set = average_frequency_deviation*self._control_constant
            self._setPEVTotalOutputPower(power_to_set) 
        
    def __str__(self):
        return "SimpleControl h="+str(round(self._control_constant))
        
class SimpleLocalControl(AbstractControl):
    """Simple linear control that uses the local frequency deviation. Bounded at +- 100 mHz and the PEV output power is distributed proportionally to the power consumption at the respective bus.
    """
    
    def __init__(self,control_constant=0,buses=[]):
        self._control_constant = control_constant
        self._buses = buses
        
    def __str__(self):
        return "SimpleLocalControl h="+str("{0}".format(self._control_constant))+" buses="+(" ".join(str(e) for e in self._buses))
        
    def exhibitControl(self,time):
        #if self._simulation._disturbance._fault_start+self._simulation._disturbance._fault_duration > time-0.1:
        #    return
        if not self._control_constant == 0:
            total_P = self._getSumP([])
            batery_P = self._getSumP(self._buses)
            frequency_deviations = self._getFrequencyDeviation()
            i = 0
            for pev in self._simulation._power_system_object._pevs:
                frequency_deviation = frequency_deviations[i]
                if len(self._buses) == 0 or pev._bus in self._buses:
                    power_to_set = frequency_deviation*self._control_constant*total_P*(pev._P*1.0/batery_P)
                    #print total_P,batery_P,pev._P,frequency_deviation,pev._bus,power_to_set
                    self._setPEVOutputPower(power_to_set,pev._bus)
                i += 1

class LocalControlUniform(AbstractControl):
    """Simple linear control that uses the local frequency deviation, one bus feed all the power
    """
    
    def __init__(self,control_constant=0,buses=[]):
        self._control_constant = control_constant
        self._buses = buses
        
    def __str__(self):
        return "LocalControlUniform h="+str(round(self._control_constant))+" buses="+str(self._buses)
        
    def getDistribution(self):
        pass
        
    def exhibitControl(self,time):
        if self._simulation._disturbance._fault_start+self._simulation._disturbance._fault_duration > time-0.1:
            return
        if not self._control_constant == 0:
            total_P = self._getSumP([])
            batery_P = self._getSumP(self._buses)
            frequency_deviations = self._getFrequencyDeviation()
            i = 0
            c = len(self._buses)
            if c == 0:
                c = len(self._simulation._power_system_object._pevs)
            for pev in self._simulation._power_system_object._pevs:
                frequency_deviation = frequency_deviations[i]
                if len(self._buses) == 0 or pev._bus in self._buses:
                    power_to_set = frequency_deviation*self._control_constant*total_P/c
                    self._setPEVOutputPower(power_to_set,pev._bus)
                i += 1
              
    
class SimpleDelayedControl(AbstractControl):
    """Simple linear control that uses the average frequency deviation at time t-delay. Bounded at +- 100 mHz and the PEV output power is distributed proportionally to the power consumption at the respective bus.
    """

    def __init__(self,control_constant=0,delay=0):
        self._control_constant = control_constant
        self._delay = delay

    def __str__(self):
        return "SimpleDelayControl h="+str(self._control_constant)+" t="+str(self._delay)
        
    def exhibitControl(self,time):
        #start with control only after the disturbance has passed
        if self._simulation._disturbance._fault_start+self._simulation._disturbance._fault_duration > time-0.1:
            return
        if not self._control_constant ==0:
            average_frequency_deviation = self._simulation._channels.getAverageFrequencyDeviation(time-self._delay)
            if average_frequency_deviation > .1:
                average_frequency_deviation = .1
            if average_frequency_deviation < -.1:
                average_frequency_deviation = -.1
            power_to_set = average_frequency_deviation*self._control_constant
            self._setPEVTotalOutputPower(power_to_set) 
    