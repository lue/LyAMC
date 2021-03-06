import glob
import os

import numpy as np
from numba import jit

import lyamc.cons as cons

NU0 = cons.NULYA / (cons.MHK * cons.K2HZ)

### Consts
km_in_pc = 3.086e+13
cm_in_pc = 3.086e+18
nua = cons.NULYA  # Hz
c = 2.99792e5  # km/s
DeltanuL = 99471839.  # natural line width in Hz
sigmat = 6.65e-25  # cm^2

# https://www.wolframalpha.com/input/?i=(proton+mass+%2F+2)+%2F+(Bolzmann+constant)+in+s%5E2*K%2Fkm%5E2
mp_over_2kB = 60.57  # s^2 K / km^2


@jit(nopython=True)
def sigmaa0(T):
    '''
    Ly-alpha absorption cross-section at line center
    :param T: temperature in K
    :return: cross-section at line center in cm^2
    '''
    return 5.9e-14 * (T / 1e4) ** -0.5


@jit(nopython=True)
def H_fit(a, x):
    '''
    Analytical fir to Voight profile from Tasitsiomi (2006), copied from Lauren, Razoumov & Sommer-Larsen (2009)
    :param a:
    :param x:
    :return:
    '''
    zeta = (x ** 2 - 0.855) / (x ** 2 + 3.42)
    P = 5.674 * zeta ** 4 - 9.207 * zeta ** 3 + 4.421 * zeta ** 2 + 0.1117 * zeta
    q = (zeta > 0) * (1. + 21 / (x ** 2 + 1e-10)) * a / np.pi / (x ** 2 + 1) * P
    return q * np.sqrt(np.pi) + np.exp(-x ** 2)


@jit(nopython=True)
def sigmaax(T, x):
    '''
    Ly-alpha absorption cross-section for given x
    :param T: temperature in K
    :param x: temperature in K
    :return: cross-section at line center in cm^2
    '''
    # return 0.4162 * np.sqrt(np.pi) * (4.8e-10)**2 / 9.1e-28 / 2.9979e10 / get_vth(T)
    anu = 4.7e-4 * (T / 1e4) ** -0.5
    return 5.9e-14 * (T / 1e4) ** -0.5 * H_fit(anu, x)


def read_last(geom, params, mode):
    s = glob.glob('output/' + decodename(geom, params, sep='_') + '*%s_last*npz'%mode)
    temp = np.load(s[0])
    k = temp['k'].copy()
    x = temp['x'].copy()
    p = temp['p'].copy()
    i = temp['i'].copy()
    for si in s[1:]:
        temp = np.load(si)
        k = np.concatenate([k, temp['k']])
        x = np.concatenate([x, temp['x']])
        p = np.concatenate([p, temp['p']])
        i = np.concatenate([i, temp['i']])
    # x = np.array(x).reshape(-1,1)
    # k = np.array(k).reshape(-
    filename = str(np.random.rand())[2:]
    np.savez('output/' + decodename(geom, params) + '_%s_%s_last.npz' % (filename, mode),
             p=p,
             k=k,
             x=x,
             i=i)
    for si in s:
        os.system('rm -f ' + si)
    direction = npsumdot(k, [0, 0, 1])
    print(len(x))
    return x, k, direction, i

def decodename(geom, params, sep='_'):
    if len(params) == 6:
        s = '%s %0.2f %.1e %0.2f %0.2f %0.2f %0.2f' % (
        geom, params[0], params[1], params[2], params[3], params[4], params[5])
    elif len(params) == 3:
        s = '%s %0.2f %.1e %0.2f' % (geom, params[0], params[1], params[2])
    elif len(params) == 2:
        s = '%s %0.2e %.2e' % (geom, params[0], params[1])
    s = s.replace(' ', sep)
    return s


def npsumdot(x, y):
    '''Dot product for two arrays'''
    if len(x.shape) > 1:
        t = np.sum(x * y, axis=1)
    else:
        t = np.dot(x, y)
    return t


def npsumdot2(x, y):
    '''Dot product for two arrays'''
    if len(x.shape) > 1:
        t = np.sum(x, axis=1)
    else:
        t = np.dot(x, y)
    return t


@jit(nopython=True)
def get_x(nu, T):
    '''returns dimensionless frequency for nu in Hz and T in K'''
    vth = get_vth(T)
    Deltanua = nua * vth / c
    return (nu - nua) / Deltanua


@jit(nopython=True)
def get_nu(x, T):
    '''returns nu in Hz given dimensionless frequency and T in K'''
    vth = get_vth(T)
    Deltanua = nua * vth / c
    return x * Deltanua + nua


@jit(nopython=True)
def get_vth(T):
    '''return vth in km/s for T in K
    IT IS VELOCITY DISPERSION TIMES SQRT(2)
    '''
    return 0.1285 * np.sqrt(T)  # in km/s


@jit(nopython=True)
def get_a(T):
    '''
    :param T: temperature in K
    :return: \Delta nu_c / (2 * \Delta nu_D)
    '''
    DeltanuD = nua * np.sqrt(T / c ** 2 / mp_over_2kB)
    return DeltanuL / 2. / DeltanuD
