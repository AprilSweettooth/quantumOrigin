from pyqpanda import *
import numpy as np
from numpy import linalg as LA
from numpy.linalg import inv

qvm = CPUQVM()
qvm.init_qvm()
q = qvm.qAlloc_many(4)
c = qvm.cAlloc_many(4)
p = QProg()

A=np.array([[1,1],[1/np.sqrt(2),-1/np.sqrt(2)]])
b=np.array([0.5,-1/np.sqrt(2)])

w, v = LA.eig(A)
w = list(np.array([[w[0], 0], [0, w[1]]]).flatten())

b = list(np.matmul(inv(v), b).flatten())
n_b = np.sqrt(np.sum([i**2 for i in b]))
b = b/n_b

# theta = np.arctan(b[1]/b[0])
# p << RY(q[3], theta) # initalize b
# QPE
# p << H(q[1]) << H(q[2]) << RY(q[3], np.pi/4).control(q[1]) << RY(q[3], np.pi/8).control(q[2])
# p << SWAP(q[1], q[2]) << H(q[2]) << S(q[1]).dagger().control(q[2]) << H(q[1]) << SWAP(q[1], q[2])
# p << RY(q[0], np.pi/4).control(q[1]) << RY(q[0], np.pi/2).control(q[2])
# p << SWAP(q[1], q[2]) << H(q[1]) << S(q[2]).control(q[1]) << H(q[2]) << SWAP(q[1], q[2])
# p << RY(q[3], -np.pi/8).control(q[2]) << RY(q[3], -np.pi/4).control(q[1]) << H(q[1]) << H(q[2])
# p << measure_all(q, c)
# r = qvm.run_with_configuration(p, c, 1000)
# print(r)
# qvec = q[1:4]
# p << RY(q[0], -2.808754) << H(qvec) << Unitary(q[0], np.pi).set_control(q[4])

# print(p)

r = HHL_solve_linear_equations(w,b,0)
# c = build_HHL_circuit(w, b, qvm, 0)

# print(c)
print(list((np.matmul(v, r)*n_b).flatten()))