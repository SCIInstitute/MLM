# Perform a shifted DFT #
from scipy import fftpack
import numpy as np


def average_oneD(signal):
    # DFT and shift so the 0 Hz is centered
    # Reduce 0 Hz band by subtracting mean
    F = [fftpack.fftshift(fftpack.fft(signal[ii] - np.mean(signal[ii]))) for ii in range(len(signal))]

    # Square the absolute value
    psd2D = [np.abs(F[ii]) ** 2 for ii in range(len(F))]

    # Make sure the DC component is non-zero (but still small)
    # so that there is no trouble with computing the logarithm: log10(0) = inf
    DC = []
    zero_ind = int(len(psd2D[0]) * 0.5)

    for ii in range(len(psd2D)):
        DC.append(psd2D[ii][zero_ind])

    DC_zero = np.mean(DC)

    for ii in range(len(psd2D)):
        if psd2D[ii][zero_ind] == 0:
            psd2D[ii][zero_ind] = DC_zero

    # Convert magnitude into decibels
    #log10 = [ 10*np.log10(psd2D[ii]/max(psd2D[ii])) for ii in range(len(psd2D)) ]
    log10 = [10 * np.log10(psd2D[ii]) for ii in range(len(psd2D))]
    return log10, psd2D, F


def twoD(signal):
    F = fftpack.fftshift(fftpack.fft2(signal - np.mean(signal)))
    psd2D = np.abs(F)
    log10 = 20 * np.log10(psd2D)

    return psd2D, log10


def TF(y, x):
    Y = [fftpack.fftshift(fftpack.fft(y[ii] - np.mean(y[ii]))) for ii in range(len(y))]
    X = [fftpack.fftshift(fftpack.fft(x[ii] - np.mean(x[ii]))) for ii in range(len(x))]
    tf = [[0 for ii in range(len(y[0]))] for ii in range(len(y))]
    for ii in range(len(y)):
        for jj in range(len(y[0])):
            tf[ii][jj] = Y[ii][jj] / X[ii][jj]

    psd2D = [np.abs(tf[ii]) ** 2 for ii in range(len(tf))]
    #log10 = [ 10*np.log10(psd2D[ii]/max(psd2D[ii])) for ii in range(len(psd2D)) ]
    log10 = [10 * np.log10(psd2D[ii]) for ii in range(len(psd2D))]
    return log10, psd2D, tf


def moving_average(signal, window):
    output = []
    limit = int(round(window * 0.5))
    for ii in range(len(signal) - window):
        average = np.mean(signal[ii + limit:ii + window])
        output.append(average)

    return output