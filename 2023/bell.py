import pyqpanda.pyQPanda as pq
from numpy import pi
from pyqpanda.Visualization.circuit_draw import *

class InitQMachine:
    def __init__(self, quBitCnt, cBitCnt):
        self.qvm = pq.CPUQVM()
        self.qvm.init_qvm()
        # self.m_machine = pq.init_quantum_machine(machineType)
        self.q = self.qvm.qAlloc_many(quBitCnt)
        self.c = self.qvm.cAlloc_many(cBitCnt)
        self.prog = pq.QProg()

    def __del__(self):
        pq.destroy_quantum_machine(self.qvm)

    def bell_state(self, state:str):
        if state=='00':
            self.prog << pq.H(self.q[0]) << pq.CNOT(self.q[0], self.q[1])
        elif state=='01':
            self.prog  << pq.X(self.q[0]) << pq.H(self.q[0]) << pq.CNOT(self.q[0], self.q[1])
        elif state=='10':
            self.prog << pq.X(self.q[1]) << pq.H(self.q[0]) << pq.CNOT(self.q[0], self.q[1]) 
        elif state=='11':
            self.prog << pq.H(self.q[0]) << pq.X(self.q[1]) << pq.Z(self.q[0]) << pq.Z(self.q[1]) << pq.CNOT(self.q[0], self.q[1]) 
        r = self.qvm.prob_run_tuple_list(self.prog, self.q, -1)
        #return pq.get_qstate(self.qvm)
        return r

    def teleportation(self):
        self.prog << pq.RY(self.q[2], pi/4)
        self.bell_state('00')
        self.prog << pq.CNOT(self.q[2], self.q[0]) << pq.H(self.q[2]) << pq.Measure(self.q[2], self.c[0]) << pq.Measure(self.q[0], self.c[1])
        # branch_x = pq.QProg()
        # branch_z = pq.QProg()
        # branch_x << pq.X(self.q[1])
        # branch_z << pq.Z(self.q[1])

        # qif_x = pq.QIfProg(self.c[1]==1, branch_x)
        #qif_z = pq.QIfProg(self.c[0]==1, branch_z)

        #self.prog << qif_x << qif_z
        print(self.prog)
        result = self.qvm.prob_run_tuple_list(self.prog, self.q[1], -1)
        print(result)

print(InitQMachine(3,2).bell_state('00'))