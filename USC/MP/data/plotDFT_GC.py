import pickle
import pylab as plt
import scipy.stats
from scipy import fftpack
import numpy as np
import DFT
from import_spikedata import *

#######################################################
# Plotting space on the x-axis and time on the y-axis #
#######################################################
tres = 15.0
sres = 0.01

num_t = int(round((tstop - tstart) / tres))
num_s = int(round(DG_length / sres))

GC_spacevtime = [[0 for ii in range(num_s)] for ii in range(num_t)]

for ii in range(len(GC_pos)):
    if GC_pos_t[ii] >= tstart:
        time = int((GC_pos_t[ii] - tstart) / tres)
        location = int(GC_pos[ii] / sres)
        GC_spacevtime[time][location] += 1

#######################################################
# Plotting time on the x-axis and space on the y-axis #
#######################################################
tresr = 4.0
sresr = 0.1
num_tr = int(round((tstop - tstart) / tresr))
num_sr = int(round(DG_length / sresr))

GC_timevspace = [[0 for ii in range(num_tr)] for ii in range(num_sr)]

for ii in range(len(GC_pos)):
    if GC_pos_t[ii] >= tstart:
        time = int((GC_pos_t[ii] - tstart) / tresr)
        location = int(GC_pos[ii] / sresr)
        GC_timevspace[location][time] += 1

#######################################
# 2-D DFT of the space vs time matrix #
#######################################
tres2D = tresr
sres2D = sres * 2
num_t2D = int(round((tstop - tstart) / tres2D))
num_s2D = int(round(DG_length / sres2D))

GC_rast = [[0 for ii in range(num_t2D)] for ii in range(num_s2D)]

for ii in range(len(GC_pos)):
    if GC_pos_t[ii] >= tstart:
        time = int((GC_pos_t[ii] - tstart) / tres2D)
        location = int(GC_pos[ii] / sres2D)
        GC_rast[location][time] += 1

psd2Dr, log10r = DFT.twoD(GC_rast)

#######################################
# 1-D DFT of the space vs time matrix #
#######################################

log10, power, Y = DFT.average_oneD(GC_spacevtime)
mean_space = np.mean(log10, 0)
stdev_space = np.std(log10, 0)

#######################################
# 1-D DFT of the time vs space matrix #
#######################################

log10tvs, powertvs, Ytvs = DFT.average_oneD(GC_timevspace)
mean_time = np.mean(log10tvs, 0)
stdev_time = np.std(log10tvs, 0)

############################################
# Creating the frequency axes for the DFTs #
############################################

# 1-D DFT #
speriod = 1 / (num_s * sres)
max_sfreq = (1 / sres) * 0.5
sfrequency = [-max_sfreq + ii * speriod for ii in range(num_s)]

tperiod = 1 / (num_tr * tresr) * 1000
max_tfreq = (1 / tresr) * 0.5 * 1000
tfrequency = [-max_tfreq + ii * tperiod for ii in range(num_tr)]

# 2-D DFT #
speriod2D = 1 / (num_s2D * sres2D)
max_sfreq2D = (1 / sres2D) * 0.5
sfrequency2D = [-max_sfreq2D + ii * speriod2D for ii in range(num_s2D)]

tperiod2D = 1 / (num_t2D * tres2D) * 1000
max_tfreq2D = (1 / tres2D) * 0.5 * 1000
tfrequency2D = [-max_tfreq2D + ii * tperiod2D for ii in range(num_t2D)]

########################
# Plotting the figures #
########################
log10tvs.reverse()
delta_time = abs(tfrequency[0] * 2) / 5.0
xtick_lbls = np.arange(tfrequency[0], -tfrequency[0] + delta_time, delta_time)
xtick_lbls = np.round(xtick_lbls, 1)
xtick_locs = [(ii / 5.0) * num_tr for ii in range(len(xtick_lbls))]

ytick_lbls = np.arange(10, -2, -2)
ytick_locs = [(ii / 5.0) * num_sr for ii in range(len(ytick_lbls))]

plt.figure(1)
plt.imshow(log10tvs, vmin=0, vmax=100, interpolation='nearest')
plt.xticks(xtick_locs, xtick_lbls)
plt.yticks(ytick_locs, ytick_lbls)
plt.xlim(int(0.5 * len(log10tvs[0])), len(log10tvs[0]))
plt.colorbar()
plt.xlabel('Temporal Frequency (Hz)')

plt.figure(2)
plt.plot(tfrequency, np.mean(log10tvs, 0))
#plt.errorbar(tfrequency, np.mean(log10tvs, 0), yerr=np.std(log10tvs, 0))
plt.xlim(0, -tfrequency[0])
plt.ylim(30, np.max(np.mean(log10tvs, 0)))
plt.xlabel('Temporal Frequency (Hz)')

log10.reverse()
delta_space = abs(sfrequency[0] * 2) / 20.0
ytick_lbls = np.arange(tstart, tstop + 280, 280)
xtick_lbls = np.arange(sfrequency[0], sfrequency[-1] + delta_space, delta_space)
ytick_locs = [(ii / 5.0) * num_t for ii in range(len(ytick_lbls))]
xtick_locs = [(ii / 20.0) * num_s for ii in range(len(xtick_lbls))]

plt.figure(3)
plt.imshow(log10, vmin=0, vmax=110, interpolation='nearest')
plt.xticks(xtick_locs, xtick_lbls)
plt.yticks(ytick_locs, ytick_lbls)
plt.xlim(int(0.5 * len(log10[0])), len(log10[0]))
plt.colorbar()
plt.xlabel('Spatial Frequency (1/mm)')

plt.figure(4)
plt.plot(sfrequency, np.mean(log10, 0))
#plt.errorbar(sfrequency, np.mean(log10, 0), yerr=np.std(log10, 0))
plt.xlim(0, -sfrequency[0])
plt.ylim(30, np.max(np.mean(log10, 0)))
plt.xlabel('Spatial Frequency (1/mm)')

plt.show()

