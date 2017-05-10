from pytriqs.archive import HDFArchive
from pytriqs.gf import *
from pytriqs.operators import Operator, c, c_dag, n
from pytriqs.operators.util.op_struct import set_operator_structure, get_mkind
from pytriqs.operators.util.hamiltonians import h_int_kanamori
from pytriqs.utility import mpi
from pytriqs.applications.impurity_solvers.pomerol2triqs import PomerolED
import numpy as np
from itertools import product

# Input parameters
beta = 10.0
num_orb = 2
mu = 1.5
U = 2.0
J = 0.2

spin_names = ("up", "dn")
orb_names = range(num_orb)

n_iw = 1024
n_tau = 10001

energy_window = (-5, 5)
n_w = 1000

g2_n_iw = 5
g2_n_inu = 10
g2_n_l = 10
g2_blocks = set([("up", "up"), ("up", "dn"), ("dn", "up")])

gf_struct = set_operator_structure(spin_names, orb_names, True)

# Conversion from TRIQS to Pomerol notation for operator indices
index_converter = {(sn, o) : ("loc", o, "down" if sn == "dn" else "up")
                   for sn, o in product(spin_names, orb_names)}

ed = PomerolED(index_converter, verbose = True)

# Number of particles on the impurity
N = sum(n(sn, o) for sn, o in product(spin_names, orb_names))

# Hamiltonian
H = h_int_kanamori(spin_names, orb_names,
                   np.array([[0, U-3*J], [U-3*J, 0]]),
                   np.array([[U, U-2*J], [U-2*J, U]]),
                   J, True)
H -= mu*N

# Diagonalize H
ed.diagonalize(H)

# Compute G(i\omega)
G_iw = ed.G_iw(gf_struct, beta, n_iw)

# Compute G(\tau)
G_tau = ed.G_tau(gf_struct, beta, n_tau)

# Compute G(\omega)
G_w = ed.G_w(gf_struct, beta, energy_window, n_w, 0.01)

common_g2_params = {'gf_struct' : gf_struct,
                    'beta' : beta,
                    'blocks' : g2_blocks,
                    'n_iw' : g2_n_iw }

###############################
# G^{(2)}(i\omega;i\nu,i\nu') #
###############################

# Compute G^{(2),ph}(i\omega;i\nu,i\nu'), AABB block order
G2_iw_inu_inup_ph_AABB = ed.G2_iw_inu_inup(channel = "PH",
                                           block_order = "AABB",
                                           n_inu = g2_n_inu,
                                           **common_g2_params)

# Compute G^{(2),ph}(i\omega;i\nu,i\nu'), ABBA block order
G2_iw_inu_inup_ph_ABBA = ed.G2_iw_inu_inup(channel = "PH",
                                           block_order = "ABBA",
                                           n_inu = g2_n_inu,
                                           **common_g2_params)

# Compute G^{(2),pp}(i\omega;i\nu,i\nu'), AABB block order
G2_iw_inu_inup_pp_AABB = ed.G2_iw_inu_inup(channel = "PP",
                                           block_order = "AABB",
                                           n_inu = g2_n_inu,
                                           **common_g2_params)

# Compute G^{(2),pp}(i\omega;i\nu,i\nu'), ABBA block order
G2_iw_inu_inup_pp_ABBA = ed.G2_iw_inu_inup(channel = "PP",
                                           block_order = "ABBA",
                                           n_inu = g2_n_inu,
                                           **common_g2_params)

#########################
# G^{(2)}(i\omega;l,l') #
#########################

# Compute G^{(2),ph}(i\omega;l,l'), AABB block order
G2_iw_l_lp_ph_AABB = ed.G2_iw_l_lp(channel = "PH",
                                   block_order = "AABB",
                                   n_l = g2_n_l,
                                   **common_g2_params)

# Compute G^{(2),ph}(i\omega;l,l'), ABBA block order
G2_iw_l_lp_ph_ABBA = ed.G2_iw_l_lp(channel = "PH",
                                   block_order = "ABBA",
                                   n_l = g2_n_l,
                                   **common_g2_params)

# Compute G^{(2),pp}(i\omega;l,l'), AABB block order
G2_iw_l_lp_pp_AABB = ed.G2_iw_l_lp(channel = "PP",
                                   block_order = "AABB",
                                   n_l = g2_n_l,
                                   **common_g2_params)

# Compute G^{(2),pp}(i\omega;l,l'), ABBA block order
G2_iw_l_lp_pp_ABBA = ed.G2_iw_l_lp(channel = "PP",
                                   block_order = "ABBA",
                                   n_l = g2_n_l,
                                   **common_g2_params)

if mpi.is_master_node():
    with HDFArchive('2band.atom.h5', 'w') as ar:
        ar['G_iw'] = G_iw
        ar['G_tau'] = G_tau
        ar['G_w'] = G_w
        ar['G2_iw_inu_inup_ph_AABB'] = G2_iw_inu_inup_ph_AABB
        ar['G2_iw_inu_inup_ph_ABBA'] = G2_iw_inu_inup_ph_ABBA
        ar['G2_iw_inu_inup_pp_AABB'] = G2_iw_inu_inup_pp_AABB
        ar['G2_iw_inu_inup_pp_ABBA'] = G2_iw_inu_inup_pp_ABBA
        ar['G2_iw_l_lp_ph_AABB'] = G2_iw_l_lp_ph_AABB
        ar['G2_iw_l_lp_ph_ABBA'] = G2_iw_l_lp_ph_ABBA
        ar['G2_iw_l_lp_pp_AABB'] = G2_iw_l_lp_pp_AABB
        ar['G2_iw_l_lp_pp_ABBA'] = G2_iw_l_lp_pp_ABBA