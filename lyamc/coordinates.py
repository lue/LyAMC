import numpy as np

# Pauli matrices
id_m = np.identity(2).reshape(1, 2, 2)
S_x = np.array(((0, 1), (1, 0))).reshape(1, 2, 2)
S_y = np.array(((0, -1j), (1j, 0))).reshape(1, 2, 2)
S_z = np.array(((1, 0), (0, -1))).reshape(1, 2, 2)


# In what follows, everything is written to track n rays at once
# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------
def vs_to_quat(vs):
    """Converts array of velocities to boost quaternions (boost into frame
    with v)
    Parameters:
        vs: nx3 array of velocities (in units of c), where n is ray index
    Outputs:
        nx2x2 matrix representing the boost quaternions
    """
    # compute prefactor involving lorentz gamma
    prefac = (1.0 / (1.0 + np.sqrt(1.0 - np.sum(vs * vs, axis=-1)))).\
        reshape(-1, 1, 1)
    vq = -1j * (vs[:, 0].reshape(-1, 1, 1) * S_z +
                vs[:, 1].reshape(-1, 1, 1) * S_y +
                vs[:, 2].reshape(-1, 1, 1) * S_x)
    outq = prefac * vq
    return outq


def ns_to_quat(ns):
    """Converts array of input direction cosines to null-ray quaternions
    Parameters:
        ns: nx3 array of direction cosines, where n is ray index
    Outputs:
        nx2x2 matrix representing the null-ray quaternions
    """
    outq = 1j * (ns[:, 0].reshape(-1, 1, 1) * S_z +
                 ns[:, 1].reshape(-1, 1, 1) * S_y +
                 ns[:, 2].reshape(-1, 1, 1) * S_x)
    return outq


def quat_to_ns(quats):
    """Converts array of null-ray quaternions to direction cosines
    Parameters:
        quats: nx2x2 matrix representing the null-ray quaternions, where n is
               ray index
    Outputs:
        nx3 array of direction cosines
    """
    # Project out components
    nx = np.real(
        -0.5 * 1j * np.trace(np.matmul(S_z, quats), axis1=-2, axis2=-1))
    ny = np.real(
        -0.5 * 1j * np.trace(np.matmul(S_y, quats), axis1=-2, axis2=-1))
    nz = np.real(
        -0.5 * 1j * np.trace(np.matmul(S_x, quats), axis1=-2, axis2=-1))
    ns = np.c_[nx, ny, nz]
    # Normalize to make sure
    norms = np.linalg.norm(ns, axis=-1).reshape(-1, 1)
    ns = ns / norms
    return ns


def ns_to_rot(ns):
    """Converts array of input direction cosines to rotation quaternions
    Parameters:
        ns: nx3 array of direction cosines, where n is ray index
    Outputs:
        nx2x2 matrix representing the rotation quaternions
    """
    # Normalize to be safe
    norms = np.linalg.norm(ns, axis=-1)
    mus = (ns[:, 2] / norms).reshape(-1, 1, 1)
    phib2 = 0.5 * np.arctan(ns[:, 1] / ns[:, 0])
    # Fix correct branch
    phib2[ns[:, 0] < 0] += 0.5 * np.pi
    phib2 = phib2.reshape(-1, 1, 1)
    # First Euler rotation by phi
    phiq = np.cos(phib2) * id_m - 1j * np.sin(phib2) * S_x
    # Second Euler rotation by theta
    thetaq = (np.sqrt(0.5 * (1.0 + mus)) * id_m -
              1j * np.sqrt(0.5 * (1.0 - mus)) * S_y)
    outq = np.matmul(thetaq, phiq)
    return outq


def quat_to_rot(qs):
    """Converts array of input null-ray quaternions to rotation quaternions
    Parameters:
        qs: nx2x2 matrix with input null-ray quaternions
    Outputs:
        nx2x2 matrix representing the rotation quaternions
    """
    ns = quat_to_ns(qs)
    qrot = ns_to_rot(ns)
    return qrot


# ---------------------------------------------------------------------
# Transformations
# ---------------------------------------------------------------------
def rot_q(qin, qrot):
    """Rotates input null-ray quaternions
    Parameters:
        qin: nx2x2 array with input null-ray quaternions
        qrot: 1x2x2 array with rotation quaternion
    Outputs:
        nx2x2 array with output null-ray quaternions
    """
    qout = np.matmul(np.matmul(qrot, qin), np.linalg.inv(qrot))
    return qout


def boost_q(ein, qin, vb):
    """Boosts input null-ray quaternions and energies
    Parameters:
        ein: array of length n with input energies
        qin: nx2x2 array with input null-ray quaternions
        vb: nx3 array with velocities in units of c
    Outputs:
        array of length n with output energies
        nx2x2 array with output null-ray quaternions
    """
    # Get directions
    ns = quat_to_ns(qin)
    # Lorentz factor for boost
    gamma = 1.0 / np.sqrt(1.0 - np.sum(vb * vb, axis=-1))
    # Output energies
    eout = gamma * ein * (1.0 - np.sum(vb * ns, axis=-1))

    # Boost quaternion
    qb = vs_to_quat(vb)
    qout = np.matmul(qin + qb, np.linalg.inv(id_m - np.matmul(qb, qin)))

    return eout, qout


# ---------------------------------------------------------------------
# Main functions
# ---------------------------------------------------------------------
def samplephase(n):
    """Function to generate n rays sampling the scattering phase function,
    assumed to be ~ (1 + \mu^2)
    Parameters:
        n: number of rays
    Outputs:
        nx3 array of direction cosines (relative to incoming rays on z)
    """
    rvs = np.random.random((n, 2))
    phis = rvs[:, 1] * 2.0 * np.pi
    sqfact = np.power(- 2.0 + 4.0 * rvs[:, 0] +
                      np.sqrt(5.0 - 16.0 * rvs[:, 0] + 16.0 * rvs[:, 0]**2),
                      1.0/3.0)
    # Invert CDF
    mus = sqfact - 1 / sqfact
    sins = np.sqrt(1.0 - mus**2)
    ns = np.c_[sins * np.cos(phis), sins * np.sin(phis), mus]
    return ns


def scattering_lab_frame(freqs, ns, vs):
    """Function to perform one scattering for n rays off n atoms
    Parameters:
        freqs: array with n frequencies of input rays in units of hydrogen mass
        ns:    nx3 array with lab-frame direction cosines of input rays
        vs:    nx3 array with velocities of atoms (in units of c)
    Outputs:
        array with n frequencies of output rays in units of hydrogen mass
        nx3 array with lab-frame direction cosines of output rays
    """
    # Define initial null-ray quaternion
    qs_in = ns_to_quat(ns)

    # Boost into atom rest frame
    freqs_in_arf, qs_in_arf = boost_q(freqs, qs_in, vs)

    # Velocity to boost by to go to the center of mass frame
    ns_in_arf = quat_to_ns(qs_in_arf)
    vzs_com = (freqs_in_arf / (1.0 + freqs_in_arf)).reshape(-1, 1)
    vs_to_com = vzs_com * ns_in_arf

    # Boost into com frame
    freqs_in_com, qs_in_com = boost_q(freqs_in_arf, qs_in_arf, vs_to_com)

    # Rotation quaternion to make the incoming photon travel along the z-axis
    qs_rot_euler = quat_to_rot(qs_in_com)

    # Sample outgoing rays in rotated center of mass frame
    ns_out_rot_com = samplephase(len(freqs))
    # Define output null-ray quaternions
    qs_out_rot_com = ns_to_quat(ns_out_rot_com)

    # Undo rotation
    qs_out_com = rot_q(qs_out_rot_com, np.linalg.inv(qs_rot_euler))

    # Boost back into incoming atom rest frame
    freqs_out_arf, qs_out_arf = boost_q(freqs_in_com, qs_out_com, -vs_to_com)

    # Boost back into lab frame
    freqs_out_lab, qs_out_lab = boost_q(freqs_out_arf, qs_out_arf, -vs)
    # Compute directions
    ns_out_lab = quat_to_ns(qs_out_lab)

    return freqs_out_lab, ns_out_lab


pass
