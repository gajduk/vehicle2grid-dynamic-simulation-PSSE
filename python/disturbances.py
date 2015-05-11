import psspy

class AbstractDisturbance(object):
    """An abstract disturbance class that defines the contract for Disturbance classes"""
     
    def __init__(self,fault_start,fault_duration):
        self._fault_start = fault_start
        self._fault_duration = fault_duration
    
    def applyDisturbance(self):
        pass
        
    def clearDisturbance(self):
        pass
        
    def getFaultStart(self):
        return self._fault_start
        
    def getFaultDuration(self):
        return self._fault_duration
        
    def setFaultDuration(self,fault_duration):
        self._fault_duration = fault_duration
        
    def mkStr(self):
        return ""

class NoDisturbance(AbstractDisturbance):
    """Useful as a benchmark and for testing."""

    def __init__(self,fault_start,fault_duration):
        super(NoDisturbance, self).__init__(fault_start,fault_duration)
        
    def applyDisturbance(self):
        pass
        
    def clearDisturbance(self):
        pass
    
    def __str__(self):
        return "NoDisturbance"
        
class BusFault(AbstractDisturbance):
    """Applies a three phase bus fault at the specified bus"""

    def __init__(self,fault_start,fault_duration,bus_number):
        self._bus = bus_number
        super(BusFault, self).__init__(fault_start,fault_duration)
        
    def applyDisturbance(self):
        psspy.dist_bus_fault(self._bus,1, 345.0,[0.0,-0.2E+10])
        
    def clearDisturbance(self):
        psspy.dist_clear_fault(1)
        
    def __str__(self):
        return "BusFault_at_"+str(self._bus)
                
    def mkStr(self):
        return "DJ "+str(self._bus)
   
class BranchTrip(AbstractDisturbance):

    def __init__(self,fault_start,fault_duration,ibus,jbus,branch_id):
        self._ibus = ibus
        self._jbus = jbus
        self._branch_id = branch_id
        super(BranchTrip, self).__init__(fault_start,fault_duration)
        
    def applyDisturbance(self):
        psspy.dist_branch_trip(self._ibus,self._jbus,self._branch_id)
        
    def clearDisturbance(self):
        psspy.dist_branch_close(self._ibus,self._jbus,self._branch_id)
    
    def __str__(self):
        return str("BranchTrip_at_branch_{}_{}_and_id_{}".format(self._ibus,self._jbus,self._branch_id))
        
    def mkStr(self):
        return "KV "+str(self._ibus)+" "+str(self._jbus)

class BranchFault(AbstractDisturbance):

    def __init__(self,fault_start,fault_duration,ibus,jbus,branch_id,units=1,basekv=0.0,values=[0.0,-0.2E+11]):
        self.__ibus = ibus
        self.__jbus = jbus
        self.__branch_id = branch_id
        self.__units = units
        self.__basekv = basekv
        self.__values = values
        super(BranchFault, self).__init__(fault_start,fault_duration)
        
    def applyDisturbance(self):
        psspy.dist_branch_fault(self.__ibus,self.__jbus,self.__branch_id,self.__units,self.__basekv,self.__values)
        
    def clearDisturbance(self):
        psspy.dist_clear_fault(1)

    def __str__(self):
        return "BranchTrip_at_branch_{}_{}_and_id_{}".format(self.__ibus,self.__jbus,self.__branch_id)
        
        
class LoadChange(AbstractDisturbance):
    """Abrupt load change at specified buses"""

    def __init__(self,fault_start,fault_duration,busses,percent_change):
        self.__busses = busses
        self.__percent_change = percent_change
        super(LoadChange, self).__init__(fault_start,fault_duration)
    
    
    def applyDisturbance(self):
        self._increaseLoadAtBuses(self.__busses,self.__percent_change)
        
        
    def clearDisturbance(self):
        p = self.__percent_change*1.0/100
        if p < 0:
            p = -p
            q = p/(p-1)
            if q < 0:
                q = -q
        else:
            q = p/(1+p)
            if q > 0:
                q = -q
        self._increaseLoadAtBuses(self.__busses,q*100)
        
    def _increaseLoadAtBuses(self,load_buses,percent_change):
        #define the bus subsystem
        psspy.bsys(1,0,[0.0,0.0],0,[],len(load_buses),load_buses,1,[1],0,[])
        #prepare the load increase
        #in first array
        #1st zero = include all buses in the subsystem both interruptible and uninterrupted 
        #5th zero = loads of all types (1,2 and 3) 
        psspy.scal_2(1,0,1,[0,0,0,0,0],[0.0,0.0,0.0,0.0,0.0,0.0,0.0])
        #increase the loads
        #in first array
        #2nd number = percent change
        #3rd number = ignore machine limits
        #4th number = increase the reactive load equally (in percents)
        #in second array 
        #1st number load increase
        _i = psspy.getdefaultint()
        psspy.scal_2(0,0,2,[_i,2,0,3,0],[ percent_change,0.0,0.0,0.0,0.0,0.0,0.0])
    
    def mkStr(self):
        return "PP "+str(self.__busses[0])+" "+str(self.__percent_change)+"\\%"
    
    def __str__(self):
        return "LoadChange_at_buses_{}_percent_change_{}".format(self.__busses,self.__percent_change)
        