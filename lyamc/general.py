import numpy as np

### Consts
km_in_pc = 3.086e+13
cm_in_pc = 3.086e+18
nua = 2.47e15  # Hz
c = 2.99792e5  # km/s
DeltanuL = 99471839.  # natural line width in Hz
sigmat = 6.65e-25  # cm^2


def get_x(nu, T):
    '''returns dimensionless frequency for nu in Hz and T in K'''
    vth = get_vth(T)
    Deltanua = nua * vth / c
    return (nu - nua) / Deltanua


def get_nu(x, T):
    '''returns nu in Hz given dimensionless frequency and T in K'''
    vth = get_vth(T)
    Deltanua = nua * vth / c
    return x * Deltanua + nua


def get_g(T):
    '''returns g for T in K'''
    return 2.6e-4 * (T / 1e4) ** -0.5


def get_vth(T):
    '''return vth in km/s for T in K'''
    return 0.1285 * np.sqrt(T)  # in km/s


def get_xout(xin, v, kin, kout, mu, T):
    '''Equation 65'''
    g = get_g(T)
    vth = get_vth(T)
    return xin - np.dot(v, kin) / vth + np.dot(v, kout) / vth + g * (mu - 1)