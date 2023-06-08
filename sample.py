open Microsoft.Quantum.Intrinsic;
open Microsoft.Quantum.Math;
open Microsoft.Quantum.Measurement;

//
// Implement : |x⟩ |y⟩ -> |x⟩ |x + y mod 2^n⟩ where n = Length(x) = Length(y)
// with Drapper algorithm (See https://arxiv.org/pdf/1411.5949.pdf)
//
operation QuantumAdd (x : Qubit[], y : Qubit[]) : Unit is Adj + Ctl {
  let n = Length(x);
  QFTImpl(y);
  for (i in 0 .. n - 1) {
    for (j in 0 .. (n - 1) - i) {
      Controlled R1Frac([x[i + j]], (2, j + 1, (y)[(n - 1) - i]));
    }
  }
  Adjoint QFTImpl(y);
}

operation TestQuantumAdd (a : Int, b : Int, n : Int) : Int {
  mutable resultArray = new Result[n];

  using((x, y) = (Qubit[n], Qubit[n])) {
    // create qubit's array from integer a (ex: 3 -> |011⟩)
    mutable array1 = new Bool[n];
    mutable tempInt1 = a;
    for (idxBit in 0 .. n - 1) {
      set array1 w/= ((n - 1) - idxBit) <- tempInt1 % 2 == 0 ? false | true;
      set tempInt1 = tempInt1 / 2;
    }
    for (idx in 0 .. n - 1) {
      if(array1[idx]) {
        X(x[idx]);
      }
    }

    // create qubit's array from integer b (ex: 3 -> |011⟩)
    mutable array2 = new Bool[n];
    mutable tempInt2 = b;
    for (idxBit in 0 .. n - 1) {
      set array2 w/= ((n - 1) - idxBit) <- tempInt2 % 2 == 0 ? false | true;
      set tempInt2 = tempInt2 / 2;
    }
    for (idx in 0 .. n - 1) {
      if(array2[idx]) {
        X(y[idx]);
      }
    }

    // apply Drapper adder
    QuantumAdd(x, y);

    // measure and reset
    for (idx in 0 .. n - 1) {
      set resultArray w/= idx <- MResetZ(y[idx]);
    }
    for (idx in 0 .. n - 1) {
      Reset(x[idx]);
    }
  }

  // get integer's result from measured array (ex : |011⟩ -> 3)
  let resultBool = Microsoft.Quantum.Convert.ResultArrayAsBoolArray(resultArray);
  mutable resultInt = 0;
  for (idx in 0 .. n - 1) {
    if(resultBool[idx]) {
      set resultInt = resultInt + (2 ^ ((n - 1) - idx));
    }
  }
  return resultInt;
}

//
// Implement : |y⟩ -> |a y mod 2^n⟩ for some integer a
//
// Important Note :
// Integer "a" and modulus 2^n must be co-prime number.
// (For making this operator must be controlled. Otherwise InverseModI() raises an error.)
//
operation QuantumMultiply (a : Int, y : Qubit[]) : Unit is Adj + Ctl {
  let n = Length(y);
  let a_mod = a % (2^n);
  using (s = Qubit[n]) {
    // start |y⟩ |0⟩

    // apply adder by repeating "a" (integer) times
    for(r in 0 .. a_mod - 1) {
      QuantumAdd(y, s);
    }
    // now |y⟩ |a y mod N⟩

    // swap first register and second one by tuple
    Microsoft.Quantum.Canon.ApplyToEachCA(SWAP, Microsoft.Quantum.Arrays.Zip(y, s));
    // now |a y mod N⟩ |y⟩

    // reset all s qubits !
    // but it's tricky because we cannot use "Reset()". (See my above description.)
    let a_inv = InverseModI(a_mod, 2^n);
    for(r in 0 .. a_inv - 1) {
      Adjoint QuantumAdd(y, s);
    }
  }
}

operation TestQuantumMultiply (a : Int, b : Int, n : Int) : Int {
  mutable resultArray = new Result[n];

  using(y = Qubit[n]) {
    // create qubit's array from integer b (ex: 3 -> |011⟩)
    mutable array2 = new Bool[n];
    mutable tempInt2 = b;
    for (idxBit in 0 .. n - 1) {
      set array2 w/= ((n - 1) - idxBit) <- tempInt2 % 2 == 0 ? false | true;
      set tempInt2 = tempInt2 / 2;
    }
    for (idx in 0 .. n - 1) {
      if(array2[idx]) {
        X(y[idx]);
      }
    }

    // apply multiplier
    QuantumMultiply(a, y);

    // measure and reset
    for (idx in 0 .. n - 1) {
      set resultArray w/= idx <- MResetZ(y[idx]);
    }
  }

  // get integer's result from measured array (ex : |011⟩ -> 3)
  let resultBool = Microsoft.Quantum.Convert.ResultArrayAsBoolArray(resultArray);
  mutable resultInt = 0;
  for (idx in 0 .. n - 1) {
    if(resultBool[idx]) {
      set resultInt = resultInt + (2 ^ ((n - 1) - idx));
    }
  }
  return resultInt;
}







multiplicand_in = input("Enter the multiplicand.")
l1 = len(multiplicand_in)
multiplier_in = input("Enter the multiplier.")
l2 = len(multiplier_in)
# Make sure multiplicand_in holds the larger number
if l2 > l1:
    multiplier_in, multiplicand_in = multiplicand_in, multiplier_in
    l2, l1 = l1, l2

multiplicand = QuantumRegister(l1)
multiplier = QuantumRegister(l2)
accumulator = QuantumRegister(l1 + l2)
cl = ClassicalRegister(l1 + l2)
d = QuantumRegister(1)

circ = QuantumCircuit(accumulator, multiplier, multiplicand,
    d, cl, name="qc")

circ.x(d)
# Store bit strings in quantum registers
for i in range(l1):
    if multiplicand_in[i] == '1':
        circ.x(multiplicand[l1 - i - 1])

for i in range(l2):
    if multiplier_in[i] == '1':
        circ.x(multiplier[l1 - i - 1])

multiplier_str = '1'
# Perform repeated addition until the multiplier
# is zero
while(int(multiplier_str) != 0):
    add(accumulator, multiplicand, circ, 1)
    add(multiplier, d, circ, -1)
    for i in range(len(multiplier)):
        circ.measure(multiplier[i], cl[i])
    result = execute(circ, backend=Aer.get_backend('qasm_simulator'),
                    shots=2).result().get_counts(circ.name)
    multiplier_str = list(result.keys())[0]

circ.measure(accumulator, cl)
result = execute(circ, backend=Aer.get_backend('qasm_simulator'),
            shots=2).result().get_counts(circ.name)

print(result)