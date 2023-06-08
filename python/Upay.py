from pyqpanda import *
import numpy as np

if __name__ == "__main__":
   init(QMachineType.CPU)
   qubits = qAlloc_many(3)
   control_qubits = [[qubits[0], qubits[1]], [qubits[1], qubits[2]]]
   prog = create_empty_qprog()

   # 构建量子程序
   prog  << H(qubits[0]) \
         << RX(qubits[1], np.pi/4) \
         << CNOT(qubits[0], qubits[1]) \
         << CNOT(qubits[1], qubits[2]) \
         << RZ(qubits[2], np.pi/4) \
         << CNOT(qubits[1], qubits[2]) \
         << CNOT(qubits[0], qubits[1]) \
         << H(qubits[0]) \
         << RX(qubits[1], np.pi/4)

   # 对量子程序进行概率测量
   result = prob_run_dict(prog, qubits, -1)

   # 打印测量结果
   print(result)
   finalize()