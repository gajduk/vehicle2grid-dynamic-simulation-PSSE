import os,sys
#adds the PSS/E folder to the current path
PSSE_LOCATION = r"C:\Program Files (x86)\PTI\PSSEXplore33\PSSBIN"
if not os.path.exists(PSSE_LOCATION):
    PSSE_LOCATION = r"C:\Program Files\PTI\PSSEXplore33\PSSBIN"
sys.path.append(PSSE_LOCATION)

os.environ['PATH'] = os.environ['PATH'] + ';' + PSSE_LOCATION

import psspy
