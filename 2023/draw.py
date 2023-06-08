import pyqpanda.pyQPanda as pq
from pyqpanda.Visualization.circuit_draw import *
import math
class InitQMachine:
    def __init__(self, quBitCnt, cBitCnt, machineType = pq.QMachineType.CPU):
        self.m_machine = pq.init_quantum_machine(machineType)
        self.m_qlist = self.m_machine.qAlloc_many(quBitCnt)
        self.m_clist = self.m_machine.cAlloc_many(cBitCnt)

    def __del__(self):
        pq.destroy_quantum_machine(self.m_machine)

def test_print_qcircuit(q, c):
    # 构建量子程序
    prog = pq.QCircuit()
    prog << pq.CU(1, 2, 3, 4, q[0], q[5]) << pq.H(q[0]) << pq.S(q[2]) << pq.CNOT(q[0], q[1]) << pq.CZ(q[1], q[2]) << pq.CR(q[2], q[1], math.pi/2)
    prog.set_dagger(True)

    print('draw_qprog:')
    print(prog)
    draw_qprog(prog, 'text', console_encode_type='gbk')
    # draw_qprog接口还可以将量子线路保存成图片，调用方式如下。参数“filename”用于指定保存的文件名。
    draw_qprog(prog, 'pic', filename='/Users/peteryang/Downloads/quantumOrigin/2023/draw.png')

if __name__=="__main__":
    init_machine = InitQMachine(16, 16)
    qlist = init_machine.m_qlist
    clist = init_machine.m_clist
    machine = init_machine.m_machine

    test_print_qcircuit(qlist, clist)