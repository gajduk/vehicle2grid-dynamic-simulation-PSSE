import sys
import psspy_import
import dyntools
import IOUtils

def chanToMatlab(chan_file,mat_file):
    """ Converts a chan file to matlab to make use of the sofiticated plotting functionality matlab ofers.
    A newer version can be found in ChannelUtils export to matlab function.
    """
    id = chan_file[:-4]

    chan = dyntools.CHNF(chan_file)
    short_title, chanid_dict, chandata_dict = chan.get_data()
    with open(mat_file,"w") as f:
        for each in chanid_dict:
            f.write("c_"+str(chanid_dict[each]).replace(" ","_").replace("(","_").replace(")","_")+" = ")
            f.write(str(chandata_dict[each])+";\n")
    
if __name__ == "__main__":
    chanToMatlab(sys.argv[1],sys.argv[2])
    