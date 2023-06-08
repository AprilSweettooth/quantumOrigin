from unittest import result
from pyqpanda import *
import numpy as np
def adder(a: int, b: int) -> int:
    a += 8
    b += 8
    a = bin(a)[2:].zfill(4)
    b = bin(b)[2:].zfill(4)
    return int(add(a, b))



def multiplier(a: int, b: int) -> int:
    pass


def add(a, b):
    machine = init_quantum_machine(QMachineType.CPU)
    x = machine.qAlloc_many(4)
    y = machine.qAlloc_many(4) 
    Prog = QProg()
    for index in range(4):
        if a[index]=='1':
            Prog << X(x[3-index])
    for index in range(4):
        if b[index]=='1':
            Prog << X(y[3-index]) 
    Prog << QFT(y)
    for i in range(4):
        for j in range(4-i):
            Prog << U1(y[i],np.pi/(2**j)).control(x[3-(j+i)])
    
    Prog << QFT(y).dagger()
    
    directly_run(Prog)
    result = quick_measure(y, 1)
    r = list(result.keys())[0]
    destroy_quantum_machine(machine)
    return r

def mul(a, b):
    machine = init_quantum_machine(QMachineType.CPU)
    multiplicand = machine.qAlloc_many(4)
    multiplier = machine.qAlloc_many(4) 
    accumulator = machine.qAlloc_many(8)
    cb = machine.cAlloc_many(8)
    qb = machine.qAlloc_many(1)   
    t = machine.cAlloc_many(4)  
    Prog = QProg()
    Prog << X(qb)
    for index in range(4):
        if a[index]=='1':
            Prog << X(multiplicand[3-index])
    for index in range(4):
        if b[index]=='1':
            Prog << X(multiplier[3-index])
    loop = True
    while(loop):
        n = 7
        for i in range(0, n+1):
            Prog << H(accumulator[n-i])
            for k in range(0, n-i):
                Prog << U1(accumulator[n-i], np.pi/(2**(k+1))).control(accumulator[n-i-k-1])
        for i in range(0, n+1):
            for j in range(0, n+4-i):
                if n-i-j > 3:
                    pass
                else:
                    Prog << U1(accumulator[n-i], np.pi/(2**j)).control(multiplicand[n-i-j])
        for i in range(0, n+1):
            for j in range(0, i):
                Prog << U1(accumulator[i], -1*np.pi/(2**(i-j))).control(accumulator[j])
            Prog << H(accumulator[i])

        n = 3
        for i in range(0, n+1):
            Prog << H(multiplier[n-i])
            for k in range(0, n-i):
                Prog << U1(multiplier[n-i], np.pi/(2**(k+1))).control(multiplier[n-i-k-1])
        for i in range(0, n+1):
            for j in range(0, n+1-i):
                if n-i-j > 0:
                    pass
                else:
                    Prog << U1(multiplier[n-i], -1*np.pi/(2**j)).control(qb[n-i-j])
        for i in range(0, n+1):
            for j in range(0, i):
                Prog << U1(multiplier[i], -1*np.pi/(2**(i-j))).control(multiplier[j])
            Prog << H(multiplier[i])

        for i in range(4):
            Prog << Measure(multiplier[i], t[i])
        r = directly_run(Prog)
        pro = quick_measure(accumulator, 1)
        loop = bool(list(r.values())[0])
    print(pro)

# adder("1011", "0011")
print(adder(-6, 6))