import t_ccl_par
import IOUtils
import dynamic_simulation
import disturbances   
import control
import copy

def exportToLatex(buses,control_coefs,builder,tolerance=.01,table_file="table_latex.txt",res_file="temp.txt"):
    """
       Calculates the t_ccl for given BusFaults and control coefficients, then xports them to tex table format
    """
    builders = [copy.deepcopy(builder).withDisturbance(disturbances.BusFault(1,.1,each)) for each in buses]
    builders = t_ccl_par.getAllBuildersWithControl(builders,[control.SimpleLocalControl(each) for each in control_coefs])
    with open(res_file,"w"):
        pass
    t_ccl_par.calculatetccl(builders,tolerance,res_file,False,True,12)
    convertResultsToTex(table_file,res_file)
    
def convertResultsToTex(table_file="table_latex.txt",res_file="temp.txt"):

    #first load the results from the res_file
    dict = {}
    hs = set()
    with open(res_file,"r") as pin:
        for line in pin:
            sline = line.split()
            bus = int(sline[0])
            h = float(sline[1])
            tccl = float(sline[2])
            if not bus in dict:
                dict[bus] = {}
            dict[bus][h] = tccl
            hs.add(h)
            
    #then format them and output to table_file
    with open(table_file,"w") as pout:
        pout.write("\\begin{tabular}{ | c || ")
        for h in hs:
            pout.write(" c | ")
        
        pout.write("} \n \\hline \n")
        
        pout.write("Bus")
        for h in sorted(hs):
            pout.write(" & "+str(h))
        pout.write("  \\\\ \\hline \n")
            
        for each in sorted(dict):
            pout.write(str(each))
            for h in sorted(hs):
                pout.write(" & "+str(round(dict[each][h],2)))
            pout.write("  \\\\ \\hline \n")
        pout.write("\\end{tabular}\n")

def main():
    """
       Calculates the t_ccl for given BusFaults and control coefficients
    """
    control_coefs = [.3*x for x in range(0,20)]
    
    buses = range(1,40)
    
    builder = dynamic_simulation.DynamicSimulationBuilder().withRawFile("normal_case39.raw").withDyrFile("normal_case39.dyr").\
              withEndTime(20).withNumIterations(2000)
        
    exportToLatex(buses,control_coefs,builder,.003,table_file="table_latex.txt",res_file="temp.txt")
    #convertResultsToTex()
            
            
if __name__ == '__main__':
    main()
     