import os
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import numpy as np

IMG_DIR = "images"
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

def quantum_teleportation():
    #create quantum and classical registers
    qr = QuantumRegister(3, name="q")
    crz = ClassicalRegister(1, name="crz")
    crx = ClassicalRegister(1, name="crx")
    qc = QuantumCircuit(qr, crz, crx)

    #step 1 : prepare the message qubit (q0) in a superposition state
    #we set the qubit 0 to an unknown complex state (eg. random rotation)
    #we choose pi/3
    secret_angle = np.pi / 3
    qc.ry(secret_angle, 0)  # Rotate qubit 0 to create the secret state
    qc.barrier()

    #step 2 : create entanglement between qubit 1 and qubit 2
    #create a Bell pair
    qc.h(1)  # Apply Hadamard gate to qubit 1
    qc.cx(1, 2)  # Apply CNOT gate with qubit
    qc.barrier()

    #step 3 : Bell measurement on qubit 0 and qubit 1
    qc.cx(0, 1)  # Apply CNOT gate with qubit
    qc.h(0)  # Apply Hadamard gate to qubit 0
    qc.barrier()

    qc.measure(0, crz)  # Measure qubit 0
    qc.measure(1, crx)  # Measure qubit 1
    qc.barrier()

    #step 4 : apply conditional operations on qubit 2 based on measurement results
    #if crx == 1, apply X gate
    with qc.if_test((crx, 1)):
        qc.x(2)
    #if crz == 1, apply Z gate
    with qc.if_test((crz, 1)):
        qc.z(2)


    #verify the teleportation by measuring qubit 2
    #we expect qubit 2 to be in the same state as the original qubit 0
    #we do the inverse of the initial rotation to bring it back to |0> if teleportation was successful
    qc.ry(-secret_angle, 2)  # Inverse rotation
    cr_result = ClassicalRegister(1, name="cr_result")
    qc.add_register(cr_result)
    qc.measure(2, cr_result)  # Measure qubit 2

    #draw the circuit 
    path_circuit = os.path.join(IMG_DIR, "quantum_teleportation_circuit.png")
    qc.draw('mpl', filename=path_circuit)
    print(f"Quantum Teleportation Circuit saved as '{path_circuit}'")

    simulateur = AerSimulator()
    job = simulateur.run(qc, shots=1000)
    results = job.result().get_counts()

    path_hist = os.path.join(IMG_DIR, "teleportation_results_histogram.png")
    fig = plot_histogram(results, title="Quantum Teleportation Results (1000 shots)")
    fig.savefig(path_hist)
    print(f"Results histogram saved as '{path_hist}'")
    

    successes = 0
    total = 0
    for key, count in results.items():
        bits = key.replace(" ", "")
        bit_bob = bits[0]  # Measurement result of qubit 2
        if bit_bob == '0' :
            successes += count
        total += count

    print(f"Teleportation success rate: {successes}/{total} = {successes/total*100:.2f}%")
    if successes/total > 0.95:
        print("Teleportation successful!")
    else :
        print("Teleportation failed.")

if __name__ == "__main__":
    quantum_teleportation()