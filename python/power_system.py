
class ClassicLoad(object):
    """A classical load with bus,id and P&Q"""

    def __init__(self,bus,id,P,Q):
        self._bus = bus
        self._id = id
        self._P = P
        self._Q = Q
        
    def __str__(self):
        return "ClassicLoad: bus={} id={} P={} Q={}".format(self._bus,self._id,self._P,self._P)
        
    __repr__ = __str__

    
class PEV(object):
    """an aggregated bus of PEVs, P is the total real power at that bus"""
        
    def __init__(self,bus,id,P=0.0):
        self._bus = bus
        self._id = id
        self._P = P
        
    def __str__(self):
        return "PEV: bus={} id={} P={}".format(self._bus,self._id,self._P)
        
    __repr__ = __str__
   
   
class MachineLoad(object):
    """A machine load with bus,id,P,Q,H,D"""

    def __init__(self,bus,id,P,Q,H,D):
        self._bus = bus
        self._id = id
        self._P = P
        self._Q = Q
        self._H = H
        self._D = D
        
    def __str__(self):
        return "MachineLoad: bus={} id={} P={} Q={} H={} D={}".format(self._bus,self._id,self._P,self._Q,self._H,self._D)
            
    __repr__ = __str__
    
    
class Generator(object):
    """A classical turbine generator with bus id,P,Q and dynamic information H,D"""

    def __init__(self,bus,id,P,Q,H,D):
        self._bus = bus
        self._id = id
        self._P = P
        self._Q = Q
        self._H = H
        self._D = D
        
    def __str__(self):
        return "Generator: bus={} id={} P={} Q={} H={} D={}".format(self._bus,self._id,self._P,self._Q,self._H,self._D)
             
    __repr__ = __str__
   

class Branch(object):
    """A branch with ibus-jbus, id and R,X"""

    def __init__(self,ibus,jbus,id,R,X):
        self._ibus = ibus
        self._jbus = jbus
        self._id = id
        self._R = R
        self._X = X
        
    def __str__(self):
        return "Branch: from-to={}-{} id={} R={} X={}".format(self._ibus,self._jbus,self._id,self._R,self._X)
                      
    __repr__ = __str__
  

class PowerSystem(object):
    """The power system description, as given in two files .raw and .dyr
        Contains information about:
            _nbus
            _loads
            _pevs
            _generators
            _machine_loads
            _branches
        Not connected with psspy - in any way, just holds info
        Assumes that both files are found in directory psse"""           
    
    def __init__(self,raw_filename, dyr_filename):
        directory = "psse\\"
        if not "\\" in raw_filename:
            self._raw_filename = directory+raw_filename
        else:
            self._raw_filename = raw_filename
        if not "\\" in dyr_filename:
            self._dyr_filename = directory+dyr_filename
        else:
            self._raw_filename = raw_filename  
        self.load()

    def load(self):
        """Loads the system details from the files"""
        with open(self._raw_filename,"r") as rawf:
            line = ""
            #first three lines are bogus
            for i in range(1,3):
                rawf.readline();
            #bus_data
            self._nbus = -1
            while True:
                line = rawf.readline()
                if "END OF BUS DATA" in line:
                    break
                self._nbus += 1
                
                
            #skip everything until you get to the load data
            while "BEGIN LOAD DATA" not in line:
                line = rawf.readline()
            #load and pevs data
            self._loads = []
            self._pevs = [];
            while True:
                line = rawf.readline()
                if "END OF LOAD DATA" in line:
                    break
                #parse the data
                sline = str.split(line,',')
                bus = int(sline[0])
                id = sline[1].replace('\'','')
                owner = int(sline[11].replace('\'',''))
                P = float(sline[9])+float(sline[7])+float(sline[5])
                Q = float(sline[10])+float(sline[8])+float(sline[6])
                #determine type
                if owner == 2:
                    #its a pev
                    self._pevs.append(PEV(bus,id))
                else:
                    #its a classical load
                    self._loads.append(ClassicLoad(bus,id,P,Q))
                            
                
            #skip everything until you get to the generator data
            while "BEGIN GENERATOR DATA" not in line:
                line = rawf.readline()
            #generator data
            self._generators = []
            self._machine_loads = []
            with open(self._dyr_filename,"r") as dyrf:
                while True:
                    line = rawf.readline()
                    linedyr = dyrf.readline()
                    if "END OF GENERATOR DATA" in line:
                        break
                    #parse raw data
                    sline = str.split(line,',')
                    bus = int(sline[0])
                    id = int(sline[1].replace('\'',''))
                    P = float(sline[2])
                    Q = float(sline[3])
                    #parse dyr data
                    sline = str.split(linedyr)
                    H = float(sline[3])
                    D = float(sline[4])
                    #determine type
                    if P > -0.001:
                        #its a classical generator
                        self._generators.append(Generator(bus,id,P,Q,H,D))
                    else:
                        #its a machine
                        self._machine_loads.append(MachineLoad(bus,id,P,Q,H,D))
                                
            #set the pevs power
            for pev in self._pevs:
                for load in self._loads:
                    if load._bus == pev._bus:
                        pev._P += load._P    
                for machine_load in self._machine_loads:
                    if machine_load._bus == pev._bus:
                        pev._P += machine_load._P    
                        
            #skip everything until you get to the branch data 
            while "BEGIN BRANCH DATA" not in line:
                line = rawf.readline()
            #branch data
            self._branches = []
            while True:
                line = rawf.readline()
                if "END OF BRANCH DATA" in line:
                    break
                #parse raw data
                sline = str.split(line,',')
                ibus = int(sline[0])
                jbus = int(sline[1])
                id = int(sline[2].replace('\'',''))
                R = float(sline[3])
                X = float(sline[4])
                self._branches.append(Branch(ibus,jbus,id,R,X))
                       
            #skip everything until you get to the transformer data 
            while "BEGIN TRANSFORMER DATA" not in line:
                line = rawf.readline()
            #branch data
            while True:
                #4 lines per entry
                line = rawf.readline()
                if "END OF TRANSFORMER DATA" in line:
                    break
                sline = str.split(line,',')
                ibus = int(sline[0])
                jbus = int(sline[1])
                id = int(sline[3].replace('\'',''))
                line = rawf.readline()
                sline = str.split(line,',')
                R = float(sline[0])
                X = float(sline[1])
                line = rawf.readline()
                line = rawf.readline()
                self._branches.append(Branch(ibus,jbus,id,R,X))
            #finished with raw and dyr file
                
    def __str__(self):
        return "Network: "+self._raw_filename
        
    def getGeneratorBuses(self):
        return [m._bus for m in self._generators]

    def getMachineBuses(self):
        return [m._bus for m in self._machine_loads]
        
    def getPEVBuses(self):    
        return [pev._bus for pev in self._pevs]
        
    def getLoadBuses(self):    
        return [load._bus for load in self._loads]


def main():
    """Tests the power system construction, by loading the case 9 the printing information about the loads, Pevs, generators and branches
    """
    power_system = PowerSystem("normal_with_pevs_case9a.raw","normal_with_pevs_case9a.dyr")
    print power_system._nbus
    print "LOADS"
    print len(power_system._loads)
    print "PEVS"
    print len(power_system._pevs)
    print "GENERATORS"
    print len(power_system._generators)
    print "BRANCHES"
    print len(power_system._branches)
    
if __name__ == "__main__":
    main()