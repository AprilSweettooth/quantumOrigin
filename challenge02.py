from pyqpanda import *
import numpy as np
import matplotlib.pyplot as plt
from fractions import Fraction
import contfrac
import collections
import math as m
from typing import List

def solution() -> List[int]:
    return shor(21)
# utils functions

def plotBar(result, filename):
    xdata = []
    ydata = []

    for i in result:
        xdata.append(i)
        ydata.append(result[i])

    fig, ax = plt.subplots()
    fig.set_size_inches(6,6)
    fig.set_dpi(100)
    
    rects =  ax.bar(xdata, ydata, color='b')

    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width() / 2, height, str(height), ha="center", va="bottom")
    
    plt.rcParams['font.sans-serif']=['Arial']
    plt.title("Origin Q", loc='right', alpha = 0.5)
    plt.ylabel('Times')
    plt.xlabel('States')
    plt.savefig(filename)
    plt.show() 


def qft(qlist):
    circ = QCircuit()
    
    qnum = len(qlist)
    for i in range(0, qnum):
        circ.insert(H(qlist[qnum-1-i]))
        for j in range(i + 1, qnum):
            circ.insert(CR(qlist[qnum-1-j], qlist[qnum-1-i], np.pi/(1 << (j-i))))

    for i in range(0, qnum//2):
        circ.insert(CNOT(qlist[i], qlist[qnum-1-i]))
        circ.insert(CNOT(qlist[qnum-1-i], qlist[i]))
        circ.insert(CNOT(qlist[i], qlist[qnum-1-i]))

    return circ


# shor's algorithm
def shor(N):
    # Factoring base: 2,4,5,8,10,11,13,16,17,19
    factor = []
    # a = Fraction(0.675).limit_denominator(21)
    # when a = 4 or 16
    a_1 = 4
    a_2 = 8
    #If the GCD is not 1, x is a nontrivial factor of N, so we're done
    if (m.gcd(a_1, N) != 1):
        print("\nFactors found classically, re-attempt...")
    if (m.gcd(a_2, N) != 1):
        print("\nFactors found classically, re-attempt...") 
    
    # Otherwise it means that x and N are coprime, so we can use Shor's algorithm to find r which is the period for a
    
    # period 4
    result_1 = find_period_4()
    # filtre out the noise values in period as well as all 0's which is invalid
    noise_filtre_1 = dict(filter(lambda elem: elem[1] > 100 and int(elem[0]) > 0, result_1.items()))

    #period 8
    result_2 = dict(find_period_8())
    # filtre out all 0's which is invalid
    noise_filtre_2 = dict(filter(lambda elem: int(elem[0]) > 0, result_2.items()))

    # use the result of noise_filtre_2 we can get the r value, 2. 
    # Put the value in formula below we can get the guessed factors gcd(8^(2/2) + 1, 21) = 3 and gcd(8^(2/2) - 1, 21) = 7
    # But here we only demonstrate the first method

    # find phase and use continued fraction to find r
    r = []
    for i in range(len([*noise_filtre_1])):
        phase = int([*noise_filtre_1][i],2)/(2**3)
        coefficients = list(contfrac.continued_fraction(phase))
        r.append(coefficients)
    print(r)
    r = list(set([val for sublist in r for val in sublist]))
    # because in this method we have reduce 2 bits as 1 bit so even if r is odd it might work
    for i in range(len(r)):
        # compute 4^(r/2) +/- 1, to simplify the expression, 2^r +/- 1
        p = m.gcd(2**r[i] + 1, N)
        q = m.gcd(2**r[i] - 1, N)

        # compute factors if only one is found
        # if ((not p * q == N) and p * q > 1 and int(N/ (p * q)) * p * q == N):
        #     p, q = p * q, int(N / (p * q))

        if p * q == N and p > 1 and q > 1:
            factor.append(q)
            factor.append(p)
    factor.sort()
    return factor

# minimum qubits implementation approach with observation |1> -> |4> -> |16> -> |1>
def find_period_4():
    # initiate quantum program with 3 bits for control register 
    # and two reduced quantum bits for work register
    machine = init_quantum_machine(QMachineType.CPU)
    qb = machine.qAlloc_many(5)
    measure_bit = [qb[2], qb[1], qb[0]]
    Prog = QProg()
    Prog << H(qb[0])
    Prog << H(qb[1])
    Prog << H(qb[2])

    # U^1
    Prog << CNOT(qb[2], qb[4])

    # U^2
    Prog << CNOT(qb[1], qb[4])\
         << CNOT(qb[4], qb[3])\
         << Toffoli(qb[1], qb[3], qb[4])\
         << CNOT(qb[4], qb[3])
    
    # U^4
    Prog << X(qb[4])\
         << Toffoli(qb[0], qb[4], qb[3])\
         << X(qb[4])\
         << CNOT(qb[4], qb[3])\
         << Toffoli(qb[0], qb[3], qb[4])\
         << CNOT(qb[4], qb[3])

    # QFT*
    Prog << qft(measure_bit).dagger()
    
    # run the program and visualize data
    directly_run(Prog)
    result = quick_measure(qb[0:3], 1000)
    plotBar(result, "period_4")
    destroy_quantum_machine(machine)

    return result

# Another implemention with a = 8 with observation that 8 has a small r(period),
#  which gives us a fast way to compute factors. Also the logic is base on Kitaev's
# algorithm which reduce the previously required 3n qubits to n+1 working qubits
def find_period_8():
    # n+1 working qubits
    q = int(np.ceil(np.log2(21))) + 1
    # classic bits to store measured value
    c = q

    # initiation
    machine = init_quantum_machine(QMachineType.CPU)
    qb = machine.qAlloc_many(q)
    cb = machine.cAlloc_many(c)
    data = []
    for i in range(100):
        Prog = QProg()

        Prog << X(qb[0])
        Prog << H(qb[q-1])

        # first bit x
        Prog << H(qb[q-1])
        Prog << Measure(qb[q-1], cb[0])
        result_x = directly_run(Prog)
        x = int(result_x['c0'])
        Reset(qb[q-1])
        Prog << H(qb[q-1])
        if x == 1:
            Prog << U1(qb[q-1], np.pi/2)  

        #second bit y
        Prog << H(qb[q-1])
        Prog << Measure(qb[q-1], cb[1])
        result_y = directly_run(Prog)
        y = int(result_y['c1'])
        Reset(qb[q-1]) 
        Prog << H(qb[q-1])
        if y == 1:
            Prog << U1(qb[q-1], np.pi/2) 
        if x == 1:
            Prog << U1(qb[q-1], np.pi/4) 

        # third bit z
        Prog << H(qb[q-1])
        Prog << Measure(qb[q-1], cb[2])
        result_z = directly_run(Prog)
        z = int(result_z['c2']) 
        Reset(qb[q-1])
        Prog << H(qb[q-1])
        if z == 1:
            Prog << U1(qb[q-1], np.pi/2)
        if y == 1:
            Prog << U1(qb[q-1], np.pi/4) 
        if x == 1:
            Prog << U1(qb[q-1], np.pi/8) 

        # fourth bit w
        Prog << H(qb[q-1])
        Prog << Measure(qb[q-1], cb[3])
        result_w = directly_run(Prog)
        w = int(result_w['c3']) 
        Reset(qb[q-1])
        Prog << H(qb[q-1])

        # U gate, which is the modular operation gate
        # implement cswap gate, e.g. Cswap(5, 0, 3)
        Prog << CNOT(qb[3], qb[5])
        Prog << Toffoli(qb[5], qb[0], qb[3])
        Prog << CNOT(qb[3], qb[0])
        

        if w == 1:
            Prog << U1(qb[q-1], np.pi/2) 
        if z == 1:
            Prog << U1(qb[q-1], np.pi/4) 
        if y == 1:
            Prog << U1(qb[q-1], np.pi/8) 
        if x == 1:
            Prog << U1(qb[q-1], np.pi/16) 
        Prog << H(qb[q-1])
        Prog << Measure(qb[q-1], cb[4])
        result_t = directly_run(Prog)
        t = int(result_t['c4']) 
        
        data.append(str(x)+str(y)+str(z)+str(w)+str(t))
    
    # collect data and visualize
    print(Prog)
    data_count = collections.Counter(data)
    plotBar(data_count, "period_8")
    destroy_quantum_machine(machine)
    return data_count

print(solution())