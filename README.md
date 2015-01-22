vehicle2grid-dynamic-simulation-PSSE
========================

A Python framework that facilitates running dynamic simulations in PSS/E. 
Developed in order to study the effects of vehicle-to-grid on the overall stability of the power system.

------------------------

We have used this framework to produce the results for the paper ["Improving power grid transient stability by plug-in electric vehicles"](http://iopscience.iop.org/1367-2630/16/11/115011/article) published in the [New Journal of Physics](http://iopscience.iop.org/1367-2630).
Some of the findings from this paper were also covered by [Phys.org](http://phys.org/) a popular science and technology web-magazine that did a [short story on our work](http://phys.org/news/2014-11-electric-vehicles-stabilize-large-disturbances.html). Currently our focus is on developing even better control strategies for the power grid of the future.

-------------------------
Instalation
-------------------------

You must have PSS/E installed and added to the system path. 
You can download a free copy from the [Siemens website](http://w3.usa.siemens.com/smartgrid/us/en/transmission-grid/products/grid-analysis-tools/transmission-system-planning/Pages/University-Order.aspx). 
The framework was developed on top of PSS/E version 33, I am not sure how it will behave with other versions.
The PSS/E installations comes with a python 2.7 installer and is automatically configures during instalation.
I had a lot of problems when there were more then one python versions installed on Windows.
Therefore, I strongly suggest that you delete any previous version of Python you might have and software like Anaconda, Canopy, Wing IDE and IPython.

Using the framework
===================

Running a dynamic simulation and plotting the results
---------------------------------------------------
Create a new file e.g. "my_dynamic_simulation.py" and use the builder syntax to build a Dynamic Simulation object with the desired properties. For example to simulate a bus fault at bus 5 that starts at 1 seconds, lasts for 0.1 seconds on case39 (New England) and monitor the generator speeds and all bus voltages you would write

```python
import psspy_import
import disturbances
import channel_utils
import dynamic_simulation

builder = dynamic_simulation.DynamicSimulationBuilder()

#set the power system source files
builder.withRawFile("normal_case39.raw").withDyrFile("normal_case39.dyr")

#set the disturbance
builder.withDisturbance(disturbances.BusFault(1,.1,5))

#set generator speed and bus voltage as channels in PSS/E
builder.withChannel(channel_utils.CHANNELS.SPEED).withChannel(channel_utils.CHANNELS.V)

#plot the results in PSS/E
builder.withPlot()

#finally build and run the simulation
builder.build().runSimulation()
```
---------------------

Comparing the system stability with and without vehicle-to-grid
---------------------
You can reuse most of the code from the previous example to see how the system behaves when vehicle-to-grid is implemented.
Lets create a new file "stability_comparison.py" and see how the system reacts to a branch trip between buses 5 and 6 that starts at 2 seconds and lasts for half a second.

```python
import psspy_import
import disturbances
import channel_utils
import dynamic_simulation
import control

builder = dynamic_simulation.DynamicSimulationBuilder().\
        withRawFile("normal_case39.raw").withDyrFile("normal_case39.dyr").\
        withDisturbance(disturbances.BranchTrip(2,.5,5,6,'1 ')).withPlot()
        
#run a standard simulation without vehicle-to-grid
builder.build().runSimulation()

#build and run a simulation with vehicle-to-grid where the vehicles output power is governed by the SimpleLocalControl strategy
builder.withControl(control.SimpleLocalControl(5)).build().runSimulation()
```
----------------------

Calculating the critical clearing time (t_ccl)
----------------------
The framework comes with a utility that uses binary search to find the t_ccl. All you need to do is define the type of disturbance and control and invoke the `determineT_ccl` function like so

```python
import psspy_import
import disturbances
import dynamic_simulation
import t_ccl

simulation = dynamic_simulation.DynamicSimulationBuilder().\
        withRawFile("normal_case39.raw").withDyrFile("normal_case39.dyr").\
        withDisturbance(disturbances.BusFault(1,.5,5)).build()
result = t_ccl.determineT_ccl(simulation)
```

Since you will usually want to calculate t_ccl for many different disturbances and different types of control we developed a utility that calculates t_ccl in parallel for a list of dynamic_simulations. For example you can find t_ccl for all bus faults and a range of control coefficients using the following code

```python
import psspy_import
import disturbances
import dynamic_simulation
import t_ccl_par
import control

#define control objects
control_coefficients = [0.1*x for x in range(0,30)]
control_objects = [control.SimpleLocalControl(each) for each in control_coefficients]

#make the initial builder
builder = dynamic_simulation.DynamicSimulationBuilder().withRawFile("normal_case39.raw").withDyrFile("normal_case39.dyr")

#create a list of builders with bus faults at each bus
builders = t_ccl_par.getAllBusFaultsBuilders(builder)

#for each bus fault create a list of builders that have different control objects
all_builders = t_ccl_par.getAllBuildersWithControl(builders,control_objects)

#finally calculate the t_ccl for all these different scenarios concurrently
t_ccl_par.calculatetccl(all_builders,1,"results_t_ccl.txt")
#the results will be written to the file "results_t_ccl.txt"
```

---------------------------

Some nice plots that I've done with this framework. Just a reminder about the export_to_matlab option which enables you to use Matlab's rich plotting functionality 

![alt tag](https://raw.githubusercontent.com/gajduk/vehicle2grid-dynamic-simulation-PSSE/master/speed_no_control_red_fluc.jpg)

![alt tag](https://raw.githubusercontent.com/gajduk/vehicle2grid-dynamic-simulation-PSSE/master/speed_control_red_fluc.jpg)


