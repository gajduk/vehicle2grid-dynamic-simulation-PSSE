import psspy_import
import psspy

def convertLoads(load_representation = [0.0,100.0,0.0,100.0]):
    #group all the buses into a common subsystem, when they don't belong to the same area
    #owner number 2 is reserved for AEV loads
    psspy.bsys(0,0,[ 345., 345.],3,[1,2,3],0,[],1,[1],0,[])
    #then convert the subsystem of buses
    #init conversion = 1
    psspy.conl(0,0,1,[0,0],load_representation)
    #do conversion = 2
    psspy.conl(0,0,2,[0,0],load_representation)
    #clean up = 3
    psspy.conl(0,0,3,[0,0],load_representation)

def convertPEVs(aev_representation = [0.0,0.0,0.0,0.0]):
    psspy.bsys(1,0,[ 345., 345.],3,[1,2,3],0,[],1,[2],0,[])
    psspy.conl(1,0,1,[0,0],[0.0,0.0,0.0,0.0])
    psspy.conl(1,0,2,[0,0],[0.0,0.0,0.0,0.0])
    psspy.conl(1,0,3,[0,0],[0.0,0.0,0.0,0.0])
    