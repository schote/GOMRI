# GOMRI

**G**raphical user interface for **O**pen-source **M**agnetic **R**esonance **I**maging.

This user interface is communicating via a TCP/IP connection with a RedPitaya, that functions
as a console for real-time acquisition. This project includes a server, that is executable on the console
and a graphical user interface (GUI) to control it. This project is close connected to the
OCRA project (Open-source Console for Real-time Acquisition), that can be found under the
following link:
https://openmri.github.io/ocra/ 

# Features of GOMRI

Here is an overview of the implemented functionalities, the GOMRI application comes with.
The interface was build with PyQt5 and holds sub applications for different acquisitions.

## (1) Spectrometry

The spectrometer sub application is capable of acquiring the spectrum of a sample with 
free induction decay (FID), spin echo (SE), inversion recovery (IR) or saturation inversion recovery (SIR) sequences.
It is also possible to upload a custom sequence and acquire a spectrum with it.
Through the control center, the frequency and attenuation can be set.
Tools were implemented to automatically find the center frequency of the system, perform a 
transmit power adjust or to set shim currents, in case shim coils are connected to the system.
An output section gives feedback about critical output parameters, like real center frequency,
signal to noise ratio (SNR) and full width half maximum (FWHM) in [Hz] to get the system accuracy in [ppm].

## (2) T1 Relaxometry

The sub application for T1 measurements is used to calculate T1 from a fitted exponential function. 
Therefor, either the IR or the SIR sequence can be used and a parameter space for the time of inversion needs 
to be set by the user. The acquisition of the sequence is repeated for every parameter in the calculated space and
the exponential function is fitted. From this, T1 can be calculated.

## (3) T2 Relaxometry

This sub application works exactly the T1 relaxometer sub application. Instead of IR/SIR sequences the 
SE sequence is used here and the parameter space is calculated for TE. 

## (4) Protocol

The protocol sub application gives the ability to automatically perform the T1/T2 measurements sequentially.
It further holds operations to change the temperature in the system, change the sample, pause or calibrate the center 
frequency. Therethrough it is possible to automate standard measurement routines.

## (5) 2D Imaging

The sub application for 2D imaging can be used to acquire images of samples with a spin echo sequence.
The resolution can be chosen by the user. As a result, all k-space information is presented.
It is possible to test the gradient setup by measuring 1D projections. The echo time (TE) for the spin echo
sequence can be set in the control center. Also shim currents can be controlled if necessary. 