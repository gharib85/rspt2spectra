#!/usr/bin/env python3

"""

readfile
========

This module contains functions to read files
generated by the RSPt software.

"""

import numpy as np
import sys
import subprocess

from .constants import eV



def hyb(file_re, file_im, norb, spinpol, file_re_off=None, file_im_off=None,
        outfile=None, return_as_full_matrix=False):
    """
    Return hybridization functions and associated energy mesh,
    read from RSPt generated files.

    Can read and return diagonal and off-diagonal hybridization functions.
    When reading off-diagonal functions, an assumption is made.
    Namely that the first occourence of
    'dumpdata: Mask of the printed off-diagonal elements' in the outfile
    refers to the localized orbitals of interest.
    """
    # Number of non-equivalent correlated spin-orbitals
    nc = 2*norb if spinpol else norb
    # Read the diagonal hybridization functions.
    re = np.loadtxt(file_re)
    im = np.loadtxt(file_im)
    # Energy mesh.
    w = eV*re[:, 0]
    # Hybridization functions for each orbital.
    re = eV*np.transpose(re[:,4:4+nc])
    im = eV*np.transpose(im[:,4:4+nc])
    h_diagonal = re + im*1j
    if file_re_off == None and file_im_off == None and outfile == None:
        # Only read diagonal functions.
        if return_as_full_matrix:
            # Allocation of all functions
            h = np.zeros((nc, nc, len(w)), dtype=np.complex)
            for i in range(nc):
                h[i,i,:] = h_diagonal[i,:]
            return w, h
        else:
            return w, h_diagonal
    elif file_re_off != None and file_im_off != None and outfile != None:
        # Read also off-diagonal hybridization functions.
        re = eV*np.loadtxt(file_re_off)[:, 1:]
        im = eV*np.loadtxt(file_im_off)[:, 1:]
        # Loocate which orbitals these hybridization functions belong to.
        search_phrase = 'dumpdata: Mask of the printed off-diagonal elements:'
        # Assume the first Mask refers to the localized orbitals of interest.
        cmd = ('grep -A ' + str(2*norb) + " '" + search_phrase
               + "' " + outfile + ' | head -' + str(2*norb+1)
               +  ' | tail -' + str(2*norb))
        try:
            string = subprocess.check_output(cmd, shell=True)
            mask = np.array(string.split(), dtype=np.int).reshape(2*norb,2*norb)
        except subprocess.CalledProcessError:
            sys.error('Mask in out-file is absent.')
        mask = mask == 1
        if not spinpol:
            mask = mask[:norb,:norb]
        # Allocation of all functions
        h = np.zeros((nc, nc, len(w)), dtype=np.complex)
        # Fill in diagonal functions.
        for i in range(nc):
            h[i, i, :] = h_diagonal[i, :]
        # Fill in off-diagonal functions.
        n = 0
        for j in range(nc):
            for i in range(nc):
                if mask[i,j]:
                    h[i, j, :] += re[:, n] + im[:, n]*1j
                    n += 1

        # Fill in off-diagonal functions, assuming all functions
        # are non-zero, except for spin-off diagonal functions.
        # n = 0
        # for j in range(nc):
        #     if spinpol:
        #         if j < norb:
        #             irange = range(j) + range(j+1, norb)
        #         else:
        #             irange = range(norb, j) + range(j+1, nc)
        #     else:
        #         irange = range(j) + range(j+1, norb)
        #     for i in irange:
        #         h[i, j, :] = re[:, n] + im[:, n]*1j
        #         n += 1
        return w, h
    else:
        sys.exit('Wrong input parameters.')


def self_energy(file_re, file_im, spinpol, file_re_off=None, file_im_off=None):
    """
    Return dynamic self-energy funtions and associated energy mesh,
    read from RSPt generated files.

    Can read and return diagonal and off-diagonal self-energy functions.
    When reading off-diagonal functions, an assumption is made.
    Namely that the first occourence of
    'dumpdata: Mask of the printed off-diagonal elements' in the outfile
    refers to the localized orbitals of interest.
    """
    # Read diagonal part of the self-energy from file
    re = np.loadtxt(file_re)
    im = np.loadtxt(file_im)
    # Energy mesh.
    w = eV*re[:,0]
    # Diagonal
    sig_diagonal = eV*(re[:, 4:] + 1j*im[:, 4:]).T
    # Number of non-equivalent correlated spin-orbitals,
    # and the number of energy mesh points.
    nc, nw = np.shape(sig_diagonal)
    norb = nc//2 if spinpol else nc
    # Read off-diagonal part of the self-energy
    re = eV * np.loadtxt(file_re_off)[:, 1:]
    im = eV * np.loadtxt(file_im_off)[:, 1:]
    # Construct self-energy
    sig = np.zeros((nc, nc, nw), dtype=np.complex)
    # Fill in diagonal functions.
    for i in range(nc):
        sig[i, i, :] = sig_diagonal[i, :]
    # Fill in off-diagonal functions.
    sys.exit('Implementation not complete...')
    # Replace code below with something similar to the code for
    # the hybridization function.
    n = 0
    for j in range(nc):
        if spinpol:
            if j < norb:
                irange = range(j) + range(j+1, norb)
            else:
                irange = range(norb, j) + range(j+1, nc)
        else:
            irange = range(j) + range(j+1, norb)
        for i in irange:
            sig[i, j, :] = re[:, n] + im[:, n]*1j
            n += 1
    return w, sig_diagonal, sig


def pdos(filename, norb, spinpol):
    """
    Return projected density of states and associated energy mesh,
    read from RSPt generated files.

    """
    # Number of non-equivalent correlated spin-orbitals
    nc = 2*norb if spinpol else norb
    tmp = np.loadtxt(filename)
    # Energy mesh.
    w = eV*tmp[:,0]
    p = np.zeros((nc, len(w)))
    k = 7 if spinpol else 2
    for i in range(nc):
        p[i, :] = tmp[:, k + i]/eV
    return w, p