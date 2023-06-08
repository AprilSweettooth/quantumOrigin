from pyqpanda import *

if __name__ == "__main__":
    init(QMachineType.CPU)
    qubits = qAlloc_many(4)
    cbits = cAlloc_many(4)

    # 构建量子程序
    prog = QProg()
    prog << H(qubits[0])\
        << CNOT(qubits[0], qubits[1])\
        << CNOT(qubits[1], qubits[2])\
        << CNOT(qubits[2], qubits[3])\
        << Measure(qubits[0], cbits[0])

    print(prog)
    result = directly_run(prog)

    # 打印测量结果
    print(result)
    finalize()