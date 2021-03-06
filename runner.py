"""

Main script for running the MC simulation.

"""

import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('nsim', metavar='nsim', type=int, nargs=1,
                    help='geometry name')
parser.add_argument('randtype', metavar='randtype', type=str, nargs=1,
                    help='')
parser.add_argument('geometry', metavar='geom', type=str, nargs=1,
                    help='geometry name')
parser.add_argument('params', metavar='params', type=float, nargs='+',
                    help='geometry name')

from scipy import interpolate

args = parser.parse_args()

nsim = args.nsim[0]
print(args.geometry)

from lyamc.redistribution import *
from lyamc.trajectory import *
from lyamc.coordinates import *
from lyamc.cons import *

m_hz = 2.2687318181383202e+23

if args.geometry[0] == 'Neufeld_test':
    geom = Neufeld_test(tau=args.params[0],
                        T=args.params[1])
elif args.geometry[0] == 'plane_gradient':
    geom = plane_gradient(n=args.params[0],
                          T=args.params[1],
                          gradV=args.params[2])
elif args.geometry[0] == 'Zheng_sphere':
    geom = Zheng_sphere(nbar=args.params[0],
                        T=args.params[1],
                        R=args.params[2],
                        A=args.params[3],
                        V=args.params[4],
                        DeltaV=args.params[5],
                        IC='center')
else:
    print('define a proper geometry')
### Photon parameters:

print('N_HI = ', geom.nbar * cm_in_pc * geom.R)

p_last = []
k_last = []
x_last = []
i_last = []

z_map_list = np.linspace(-geom.R * 10, geom.R * 10, 1000)
z_map = np.zeros([len(z_map_list) - 1, 3])

# def simulation(geom, verbal=True):
#     # np.random.seed(4)
#     # p = [0, 0, 0]  # position in pc
#     p = geom.get_IC()
#
#     local_temperature = geom.temperature(p)
#
#     k, temp = random_n([], mode='uniform')  # normal vector
#
#     x = np.random.normal(0, 1)  # * get_vth(local_temperature) / c
#     x = 0
#
#     N = 2000000
#
#     p_history = np.zeros([N, 3]) * np.nan
#     p_history[0, :] = p
#
#     k_history = np.zeros([N, 3])
#     k_history[0, :] = k
#
#     x_history = np.zeros(N)
#     x_history[0] = x
#
#     d_absorbed = 0
#     d = np.concatenate([[0], np.logspace(-10, 0, 10000)])
#
#     proper_redistribution = True
#
#     i = -1
#
#     # Loading parallel velocity intepolation table
#     a = ALYA / 4 / np.pi / (NULYA * get_vth(local_temperature) / c)
#     a_data = np.load('a_%0.10f.npz' % a)
#     a_x_list = a_data['x_list']
#     a_s_list = a_data['s_list']
#     a_p_list = a_data['p_list']
#     a_ltab = a_data['ltab']
#     f_ltab = interpolate.interp2d(a_s_list, a_x_list, a_ltab, kind='linear')
#
#     while (d_absorbed < d.max()) & (i < N - 2):
#         d = np.concatenate([[0], np.logspace(-10, 0, 10000)])
#         # d = np.linspace()
#         i += 1
#         if verbal:
#             print(i, d_absorbed, x, np.sqrt(p[0] ** 2 + p[1] ** 2 + p[2] ** 2))
#         # define initial parameters
#         p = p_history[i, :].copy()  # position
#         k = k_history[i, :].copy()  # direction
#         x = x_history[i].copy()  # dimensionless frequency
#         nu = get_nu(x=x, T=local_temperature)  # frequency
#         # Find the position of new scattering
#         l, d = get_trajectory(p, k, d)  # searching for a trajectory
#         sf = get_survival_function(nu, l, d, k, geom)  # getting surfvival function
#         q = np.random.rand()
#         d_absorbed = interp_d(d, sf, q)  # randomly selecting absorption point
#         while (d_absorbed == d.max()) & (d.max() < geom.R * 2):
#             # print('Expanding!')
#             d *= 2
#             l, d = get_trajectory(p, k, d)  # searching for a trajectory
#             sf = get_survival_function(nu, l, d, k, geom)  # getting surfvival function
#             d_absorbed = interp_d(d, sf, q)
#         while d_absorbed < d[2000]:
#             # print('Refining!')
#             d /= 2
#             l, d = get_trajectory(p, k, d)  # searching for a trajectory
#             sf = get_survival_function(nu, l, d, k, geom)  # getting surfvival function
#             d_absorbed = interp_d(d, sf, q)
#         p_new = get_shift(p, k, d_absorbed)  # extracting new position
#         if np.sum(p_new ** 2) < geom.R ** 2:
#             # The environment of new scattering
#             local_velocity_new = geom.velocity(p_new.reshape(1, -1))  # new local velocity
#             local_temperature_new = geom.temperature(p_new.reshape(1, -1))  # new local temperature
#             # selecting a random atom
#             v_atom = local_velocity_new + \
#                      get_par_velocity_of_atom(nu, local_temperature_new, local_velocity_new, k, f_ltab,
#                                               mode=args.randtype[0]) + \
#                      get_perp_velocity_of_atom(nu, local_temperature_new, local_velocity_new, k)
#             # generating new direction and new frequency
#             if proper_redistribution:
#                 nu_i = np.array([nu / m_hz])
#                 ns = k.reshape(1, -1)
#                 vs = v_atom.reshape(1, -1) / c
#                 res = scattering_lab_frame(nu_i, ns, vs)
#                 x_new = get_x(res[0] * m_hz, local_temperature_new)
#                 k_new = res[1]
#                 vth = get_vth(local_temperature_new)
#                 # print(x_new - x - np.sum(vs * (res[1] - ns), axis=-1)/vth*c)
#             else:
#                 k_new, mu = random_n(k)  # , mode='uniform')  # new direction
#                 # print(k, k_new)
#                 x_new_in = get_x(nu, local_temperature_new)
#                 x_new = get_xout(xin=x_new_in,
#                                  v=v_atom,
#                                  kin=k,
#                                  kout=k_new,
#                                  mu=mu,
#                                  T=local_temperature)
#             # recording data into arrays
#             p_history[i + 1, :] = p_new
#             k_history[i + 1, :] = k_new
#             x_history[i + 1] = x_new
#         else:
#             i = i - 1
#     print(i)
#     return i, p_history, k_history, x_history



p = geom.get_IC()

local_temperature = geom.temperature(p)

a = ALYA / 4 / np.pi / (NULYA * get_vth(local_temperature) / c)
a_data = np.load('a_%0.10f.npz' % a)
a_x_list = a_data['x_list']
a_s_list = a_data['s_list']
a_p_list = a_data['p_list']
a_ltab = a_data['ltab']
f_ltab = interpolate.interp2d(a_p_list, a_x_list, a_ltab, kind='linear', bounds_error=True)

# np.random.seed(10)

for iii in range(nsim):
    verbal = True
    p = geom.get_IC()

    local_temperature = geom.temperature(p)

    k, temp = random_n([], mode='uniform')  # normal vector

    x = np.random.normal(0, 1)  # * get_vth(local_temperature) / c
    x = 0

    N = 10000

    p_history = np.zeros([N, 3]) * np.nan
    p_history[0, :] = p

    k_history = np.zeros([N, 3])
    k_history[0, :] = k

    x_history = np.zeros(N)
    x_history[0] = x

    d_absorbed = 0
    d = np.concatenate([[0], np.logspace(-10, 0, 100)])

    proper_redistribution = True

    i = -1
    # Loading parallel velocity intepolation table
    while (d_absorbed < d.max()) & (i < N - 2):
        d = np.concatenate([[0], np.logspace(-7, 0, 100)])
        # d = np.linspace()
        i += 1
        if verbal:
            if i % 1000 == 0:
                print(i, d_absorbed, x, np.sqrt(p[0] ** 2 + p[1] ** 2 + p[2] ** 2))
        # define initial parameters
        p = p_history[i, :].copy()  # position
        k = k_history[i, :].copy()  # direction
        x = x_history[i].copy()  # dimensionless frequency
        nu = get_nu(x=x, T=local_temperature)  # frequency
        # Find the position of new scattering
        l, d = get_trajectory(p, k, d)  # searching for a trajectory
        sf = get_survival_function(nu, l, d, k, geom)  # getting surfvival function
        q = np.random.rand()
        d_absorbed = interp_d(d, sf, q)  # randomly selecting absorption point
        while (d_absorbed == d.max()) & (d.max() < geom.R * 2):
            # print('Expanding!')
            d *= 2
            l, d = get_trajectory(p, k, d)  # searching for a trajectory
            sf = get_survival_function(nu, l, d, k, geom)  # getting surfvival function
            d_absorbed = interp_d(d, sf, q)
        while d_absorbed < d[10]:
            # print('Refining!')
            d /= 2
            l, d = get_trajectory(p, k, d)  # searching for a trajectory
            sf = get_survival_function(nu, l, d, k, geom)  # getting surfvival function
            d_absorbed = interp_d(d, sf, q)
        p_new = get_shift(p, k, d_absorbed)  # extracting new position
        if np.sum(p_new ** 2) < geom.R ** 2:
            # The environment of new scattering
            local_velocity_new = geom.velocity(p_new.reshape(1, -1))  # new local velocity
            local_temperature_new = geom.temperature(p_new.reshape(1, -1))  # new local temperature
            # selecting a random atom
            v_atom = local_velocity_new + \
                     get_par_velocity_of_atom(nu, local_temperature_new, local_velocity_new, k, f_ltab,
                                              mode=args.randtype[0]) + \
                     get_perp_velocity_of_atom(nu, local_temperature_new, local_velocity_new, k)
            # generating new direction and new frequency
            if proper_redistribution:
                nu_i = np.array([nu / m_hz])
                ns = k.reshape(1, -1)
                vs = v_atom.reshape(1, -1) / c
                res = scattering_lab_frame(nu_i, ns, vs)
                x_new = get_x(res[0] * m_hz, local_temperature_new)
                k_new = res[1]
                vth = get_vth(local_temperature_new)
                # print(x_new - x - np.sum(vs * (res[1] - ns), axis=-1)/vth*c)
            else:
                k_new, mu = random_n(k)  # , mode='uniform')  # new direction
                # print(k, k_new)
                x_new_in = get_x(nu, local_temperature_new)
                x_new = get_xout(xin=x_new_in,
                                 v=v_atom,
                                 kin=k,
                                 kout=k_new,
                                 mu=mu,
                                 T=local_temperature)
            # recording data into arrays
            p_history[i + 1, :] = p_new
            k_history[i + 1, :] = k_new
            x_history[i + 1] = x_new
        else:
            i = i - 1
    print(i)
    # filename = str(np.random.rand())[2:]
    # np.savez('output/' + decodename(args.geometry[0], args.params) + '_%s.npz' % filename, p=p_history[:i + 2],
    #          k=k_history[:i + 2], x=x_history[:i + 2])
    # i, p_history, k_history, x_history = simulation(geom)
    p_last.append(p_history[i + 1, :])
    k_last.append(k_history[i + 1, :])
    x_last.append(x_history[i + 1])
    i_last.append(i + 1)

filename = str(np.random.rand())[2:]
np.savez('output/' + decodename(args.geometry[0], args.params) + '_%s_%s_last.npz' % (filename, args.randtype[0]),
         p=p_last,
         k=k_last,
         x=x_last,
         i=i_last)
