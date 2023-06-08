from pyqpanda import *
import numpy as np
from numpy import linalg as LA
from numpy.linalg import inv

def expand_to_hermitian(matrix, vector):
    """ Expand a non-hermitian matrix A to a hermitian matrix by
    [[0, A.H], [A, 0]] and expand vector b to [b.conj, b].

    Args:
        matrix (np.array): the input matrix
        vector (np.array): the input vector

    Returns:
        tuple(np.array, np.array): the expanded matrix, the expanded vector
    """
    d = np.linalg.det(matrix)
    matrix = matrix/d
    half_dim = matrix.shape[0]
    full_dim = 2 * half_dim
    new_matrix = np.zeros([full_dim, full_dim])
    new_matrix = np.array(new_matrix, dtype=complex)
    new_matrix[0:half_dim, half_dim:full_dim] = matrix[:, :]
    new_matrix[half_dim:full_dim, 0:half_dim] = matrix.conj().T[:, :]
    matrix = new_matrix
    n_v = np.sqrt(np.sum([i**2 for i in vector]))
    vector = vector/n_v
    new_vector = np.zeros((1, full_dim))
    new_vector = np.array(new_vector, dtype=complex)
    new_vector[0, :vector.shape[0]] = vector
    new_vector[0, vector.shape[0]:] = 0
    vector = new_vector.reshape(np.shape(new_vector)[1])
    return list(matrix.flatten()), list(vector.flatten()), d, n_v

qvm = CPUQVM()
qvm.init_qvm()
q = qvm.qAlloc_many(4)

x=np.array([[1,1],[1/np.sqrt(2),-1/np.sqrt(2)]])
w, v = LA.eig(x)
w = list(np.array([[w[0], 0], [0, w[1]]]).flatten())
b=np.array([0.5,-1/np.sqrt(2)])
b = list(np.matmul(inv(v), b).flatten())
n_v = np.sqrt(np.sum([i**2 for i in b]))
r = HHL_solve_linear_equations(w,b/n_v,0)
n = np.sqrt(np.sum([i**2 for i in r]))
c = build_HHL_circuit(w, b/n_v, qvm, 0)
print(n)
#print([np.real(r[2]*(n_b/d)), np.real(r[3]*(n_b/d))])
print(np.linalg.det(v))
print(list((np.matmul(v, r)*n_v).flatten()))