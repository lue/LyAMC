import matplotlib.pyplot as plt

import lyamc.coordinates as coord
from lyamc.general import *

# Eq. (65) can be written as \Delta \nu/\nu_0 = (v/c).(k_out - k_in) + (h \nu_0/m_p c^2)(\mu - 1)
# The following code checks this

# Number of scatterings
N = 100000

# Nu_Lyman alpha in units of Hydrogen mass
NU0 = cons.NULYA / (cons.MHK * cons.K2HZ)
T = 1.0e+4  # Temperature in K
sigma = np.sqrt(T / cons.MHK)   # Standard deviation of a single velocity component in units of c
                                # Numerically, for our parameters, sigma = 3E-6

# Inject photons at line center
freqs_in = np.ones(N) * NU0
# All photons move along x
ns_in = np.c_[np.ones(N), np.zeros((N, 2))]
# Pick random velocities of atoms
vs = np.random.randn(N, 3) * sigma

# Perform scattering
freqs_out, ns_out = coord.scattering_lab_frame(freqs_in, ns_in, vs)

m_hz = 2.2687318181383202e+23

x_in = get_x(freqs_in * m_hz, T)
x_out = get_x(freqs_out * m_hz, T)
# Fractional change in energy
delta = (freqs_out - freqs_in) / freqs_in

# Recoil contribution (i.e., subtracting the first two terms of Eq. (65))
recoil = delta - np.sum(vs * (ns_out - ns_in), axis=-1)

# Recoil contribution minus that of Eq. (65)
drecoil = recoil - NU0 * (np.sum(ns_out * ns_in, axis=-1) - 1)

plt.hist(recoil, bins=100)
# plt.hist(drecoil, bins=100)

plt.show()
# The residuals are consistent with being O(v_th^2/c^2 = sigma^2)

from lyamc.redistribution import *

# k_new, mu = random_n(k)

plt.hist([get_xout(x_in, vs * 0, [1, 0, 0], [0, 1, 0], 1, T), x_out], 100)
plt.show()
