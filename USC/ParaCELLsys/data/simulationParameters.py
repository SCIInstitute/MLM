# This file contains all relevant parameters for the EC-to-DG simulation code, and can be copied into the data directory for each simulation that's run.


###############################
## Main simulation variables ##
###############################
numCells = (6600,4600) 	# (# MEA cells, # LEA cells)
N_GC = 100000		# Number of Granule Cells
numBasketCells = 1000 	# Number of Basket Cells (1:150 to 1:180 of GCs, depending on septo-temporal location)
tstop = 1500.0 		# How much biological time to simulate

# Output directory for results - Needs to be changed each simulation!
outputDir_prefix = "/auto/rcf-proj/tb/phendric/ECtoDG_Model/{" + str(numCells[0]) + "." + str(numCells[1]) + "." + str(N_GC) + "." + str(numBasketCells) + "}-t" + str(int(tstop))
outputDir_suffix = ".recurInh_02.03.13-d"
outputDir = outputDir_prefix + outputDir_suffix



#########################
##Synapse Variables
#########################

# Cells that project to the granule cell layer generally make there synapses in the inner, middle, or outer third of the dendritic tree
# Define Number of synapses per third
nsyn_inner_min = 115  
nsyn_inner_max = 135
nsyn_mid_min = 105
nsyn_mid_max = 120
nsyn_outer_min = 110
nsyn_outer_max = 130

# Define Synaptic Weights & transmission delays  
w_MEA_GC_av = 0.5e-4		#average peak conductance
w_MEA_GC_range = 0.5e-4		#range of peak conductance (minimum possible range is [average], max is [average+range])
w_LEA_GC_av = 0.5e-4
w_LEA_GC_range = 0.5e-4

w_MEA_BC_av = 2.5e-4
w_MEA_BC_range = 2.5e-4
w_LEA_BC_av = 2.5e-4
w_LEA_BC_range = 2.5e-4

w_GC_BC_av = 1.0e-4
w_GC_BC_range = 1.0e-4
w_BC_GC_av = 5.0e-4
w_BC_GC_range = 5.0e-4

baseSynDelay_MEA_GC = 0.7
baseSynDelay_LEA_GC = 0.7
baseSynDelay_MEA_BC = 0.7
baseSynDelay_LEA_BC = 0.7
baseSynDelay_GC_BC = 0.05
baseSynDelay_BC_GC = 0.05


# Define Synaptic Variables
synvars={}

# Choose a Synapse type to use by uncommenting one type
synvars['type'] = "E2"  		#Simple double exponential
#synvars['type'] = "STDPE2"      	#STDP, Double Exponential 
#synvars['type'] = "STDPE2_Prob"   	#STDP, Double Exponential, with probabilistic Release
#synvars['type'] = "STDPE2_Clo"  	#STDP, Clopath Dynamics, double exponential <<NOT VALIDATED YET>>
#synvars['type'] = "E2_Prob"  		#double exponential& probabilistic release 
#synvars['type'] = "E2_STP_Prob"  	#for double exponential with STP, probabilistic release
#synvars['type'] = "STDPE2_STP"		#For double exponential with STP and STDP, probabilistic release

# For all double exponential synapses
synvars['t1_av']= 1.05         #t1 and t2 refer to tau1 and tau2 for the conductance double exponential
synvars['t1_range'] = 1.5
synvars['t2_av'] = 5.75
synvars['t2_range'] = .9
synvars['rev_av'] = 0
synvars['rev_range'] = 10

# For STDP Rules (Clopath + Standard)
synvars['wmax'] = w_MEA_GC_av*2
synvars['wmin'] = w_MEA_GC_av*.25
synvars['thresh'] = -20

# For probabilistic double exponential
synvars['P']=.24 

# For STP Rule
synvars['F1']=.24

# Define physical dimensions of DG
L = 10.0 	# Total longitudinal length of the dentate gyrus (mm)
res = 0.05 	# Size of each bin; the resolution (mm)
