from numba import jit
from scipy.special import wofz

from lyamc.general import *


### Voight profile functions:

@jit(nopython=False)
def G(x, alpha):
    """ Return Gaussian line shape at x with HWHM alpha """
    return np.sqrt(np.log(2) / np.pi) / alpha \
           * np.exp(-(x / alpha) ** 2 * np.log(2))


@jit(nopython=False)
def L(x, gamma):
    """ Return Lorentzian line shape at x with HWHM gamma """
    return gamma / np.pi / (x ** 2 + gamma ** 2)


@jit(nopython=False)
def V(x, alpha, gamma):
    """
    Return the Voigt line shape at x with Lorentzian component HWHM gamma
    and Gaussian component HWHM alpha.

    """
    sigma = alpha / np.sqrt(2)
    return np.real(wofz((x + 1j * gamma) / sigma / np.sqrt(2))) / sigma / np.sqrt(2 * np.pi)


@jit(nopython=False)
def sigma(nu, T, u, k):
    '''
    Crossection sigma in 1/cm^2
    :param nu: frequency of the photon
    :param T: temperature of gas
    :param u: bulk velocity of gas in km/s
    :param k: direction of the photon
    :return: sigma in 1/cm^2
    '''
    nu_new = (1. - npsumdot(u, k) / c) * nu
    x_new = get_x(nu_new, T)
    # vth = get_vth(T)
    # Deltanua = nua * vth / c
    # a = DeltanuL / 2.0 / Deltanua
    a = 4.7e-4 * (T / 1e4) ** -0.5  # Eq 53 from D's motes
    return 1.045e-13 * (T / 1e4) ** -0.5 * V(x_new, alpha=1., gamma=a)
    # return sigmaax(T, x_new)


@jit(nopython=False)
def DtauDl(k, nu, v, T, ndens):
    '''
    d\tau / dl for l in pc
    :param k: direction of the photon
    :param nu: frequency of the photon
    :param v: bulk velocity of gas in km/s -- array [N,3]
    :param T: temperature in K
    :param ndens: number density of hydrogen in 1/cm^3 -- array [N]
    :return: array [N]
    '''
    kvec = v.copy()
    kvec[:, 0] = k[0]
    kvec[:, 1] = k[1]
    kvec[:, 2] = k[2]
    s = sigma(nu, T, v, kvec)
    return s * ndens * cm_in_pc
