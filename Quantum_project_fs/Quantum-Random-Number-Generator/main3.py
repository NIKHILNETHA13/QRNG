from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt
import math
import numpy as np
import hashlib

# Parameters
num_qubits = 8  # Generate 8-bit strings
shot_values = [100, 200, 500, 1000]  # Different shot counts to test

# Create quantum circuit
qc = QuantumCircuit(num_qubits, num_qubits)
qc.h(range(num_qubits))  # Apply Hadamard gates for superposition
qc.measure(range(num_qubits), range(num_qubits))  # Measure all qubits

# Plot 1: Circuit Diagram
plt.figure("Quantum Circuit")
try:
    qc.draw("mpl")
    plt.show(block=False)  # Non-blocking display
except Exception:
    print(qc.draw("text"))

# Initialize lists to store entropy values
shannon_entropies = []
min_entropies = []

# Run simulator for different shot values
backend = AerSimulator()
compiled_circuit = transpile(qc, backend)
for shots in shot_values:
    try:
        job = backend.run(compiled_circuit, shots=shots)
        result = job.result()
        counts = result.get_counts()

        # Extract random bitstrings for the last run (1000 shots)
        if shots == 1000:
            random_bits = list(counts.keys())
            frequencies = [counts[bit] for bit in random_bits]

        # Calculate Shannon and Min-Entropy
        def shannon_entropy(counts_dict):
            total = sum(counts_dict.values())
            entropy = 0
            for count in counts_dict.values():
                p = count / total
                entropy -= p * math.log2(p) if p > 0 else 0
            return entropy

        def min_entropy(counts_dict):
            total = sum(counts_dict.values())
            max_prob = max(counts_dict.values()) / total
            return -math.log2(max_prob)

        shannon_entropies.append(shannon_entropy(counts))
        min_entropies.append(min_entropy(counts))

    except Exception as e:
        print(f"An error occurred for {shots} shots: {e}")

# Print results for the last run (1000 shots)
print(f"Generated {len(random_bits)} random {num_qubits}-bit strings:")
for i, bitstring in enumerate(random_bits[:10]):  # Show first 10 for brevity
    print(f"Bitstring {i+1}: {bitstring}")
with open("random_bits.txt", "w") as f:
    for bitstring in random_bits:
        f.write(bitstring + "\n")
print("Random bits saved to 'random_bits.txt'")
print(f"Estimated Shannon Entropy (1000 shots): {shannon_entropies[-1]:.4f} bits (max possible = {num_qubits:.2f} bits)")
print(f"Estimated Min-Entropy (1000 shots): {min_entropies[-1]:.4f} bits")

# Plot 2: Improved Histogram (for 1000 shots)
plt.figure("QRNG Histogram")
plt.bar(range(len(random_bits)), frequencies, width=0.8, color='skyblue', edgecolor='black')
plt.xlabel("Bitstring Index")
plt.ylabel("Count")
plt.title(f"Distribution of 8-bit Strings (Shannon Entropy = {shannon_entropies[-1]:.4f} bits | Min-Entropy = {min_entropies[-1]:.4f} bits)")
plt.xticks([])  # Hide x-axis labels to reduce clutter
plt.grid(True, which="both", ls="--", alpha=0.7)
plt.tight_layout()
plt.show(block=False)

# Plot 3: CDF of Bitstring Frequencies (for 1000 shots)
plt.figure("CDF of Bitstring Frequencies")
sorted_freqs = sorted(counts.values())
cumulative_probs = np.cumsum(sorted_freqs) / 1000
plt.plot(sorted_freqs, cumulative_probs, marker='.', linestyle='-', color='green')
plt.xlabel("Frequency")
plt.ylabel("Cumulative Probability")
plt.title(f"CDF of Bitstring Frequencies (Shannon Entropy = {shannon_entropies[-1]:.4f} bits | Min-Entropy = {min_entropies[-1]:.4f} bits)")
plt.grid(True, ls="--", alpha=0.7)
plt.show(block=False)

# Plot 4: Entropy vs. Shots
plt.figure("Entropy vs. Shots")
plt.plot(shot_values, shannon_entropies, label="Shannon Entropy", marker='o', color='blue')
plt.plot(shot_values, min_entropies, label="Min-Entropy", marker='o', color='red')
plt.xlabel("Number of Shots")
plt.ylabel("Entropy (bits)")
plt.title("How Randomness Improves with More Shots")
plt.legend()
plt.grid(True, ls="--", alpha=0.7)
plt.show(block=False)

# Advancement: Encrypt and Decrypt using bits from 'random_bits.txt'
print("\n--- Encryption and Decryption Demo ---")

# Step 1: Get sample text from user
sample_text = input("Enter a sample text to encrypt (e.g., 'Hello'): ")
print(f"Original text: {sample_text}")

# Step 2: Convert text to binary (bits)
def text_to_binary(text):
    return ''.join(format(ord(char), '08b') for char in text)  # 8 bits per character

binary_text = text_to_binary(sample_text)
print(f"Binary text: {binary_text}")

# Step 3: Generate superkey from random bits
with open("random_bits.txt", "r") as f:
    bitstrings = f.read().splitlines()[:32]  # Take first 32 bitstrings for 256 bits
    combined_bits = "".join(bitstrings)  # Combine into 256 bits
superkey = hashlib.sha256(combined_bits.encode()).hexdigest()  # Hash to 256-bit hex
print(f"Superkey (hashed 256-bit hex): {superkey}")

# Step 4: Generate key stream (repeat superkey bits to match text length)
key_stream = ''
for i in range(0, len(binary_text), 256):  # Repeat superkey in 256-bit chunks
    key_stream += superkey[:64]  # Use first 64 hex chars (256 bits in hex)
key_stream = key_stream[:len(binary_text)]  # Trim to match text length
key_stream_binary = bin(int(key_stream, 16))[2:].zfill(len(binary_text))  # Convert to binary
print(f"Key stream (binary): {key_stream_binary[:50]}... (truncated)")

# Step 5: Encrypt (XOR binary text with key stream)
encrypted_binary = ''.join('1' if a != b else '0' for a, b in zip(binary_text, key_stream_binary))
print(f"Encrypted binary: {encrypted_binary[:50]}... (truncated)")

# Step 6: Convert encrypted binary back to text
def binary_to_text(binary):
    return ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))

encrypted_text = binary_to_text(encrypted_binary)
print(f"Encrypted text: {encrypted_text}")

# Step 7: Decrypt (XOR again with the same key stream)
decrypted_binary = ''.join('1' if a != b else '0' for a, b in zip(encrypted_binary, key_stream_binary))
decrypted_text = binary_to_text(decrypted_binary)
print(f"Decrypted text: {decrypted_text}")

# Keep plots open until user closes them
plt.show()