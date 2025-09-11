from flask import Flask, render_template, request, url_for
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import math
import numpy as np
import hashlib
import os

app = Flask(__name__)

# Parameters for the quantum circuit
num_qubits = 8
shot_values = [100, 200, 500, 1000]

# --- Statistical Test Functions ---
def monobit_test(bitstring_list):
    full_string = "".join(bitstring_list)
    num_ones = full_string.count('1')
    total_bits = len(full_string)
    expected_ones = total_bits / 2
    score = abs(num_ones - expected_ones) / math.sqrt(total_bits)
    return score

def runs_test(bitstring_list):
    full_string = "".join(bitstring_list)
    runs = 1
    for i in range(len(full_string) - 1):
        if full_string[i] != full_string[i+1]:
            runs += 1
    total_bits = len(full_string)
    expected_runs = total_bits / 2
    score = abs(runs - expected_runs) / math.sqrt(total_bits)
    return score

def chi_squared_test(counts_dict, num_qubits, shots):
    possible_outcomes = 2**num_qubits
    expected_count = shots / possible_outcomes
    chi_squared_statistic = 0
    
    observed_keys = set(counts_dict.keys())
    all_possible_keys = {format(i, '08b') for i in range(possible_outcomes)}
    
    # Calculate for observed outcomes
    for count in counts_dict.values():
        chi_squared_statistic += (count - expected_count)**2 / expected_count
    
    # Add contribution for outcomes that were not observed (count is 0)
    unobserved_keys = all_possible_keys - observed_keys
    for _ in unobserved_keys:
        chi_squared_statistic += (0 - expected_count)**2 / expected_count
            
    return chi_squared_statistic
    
# Helper function with added print statements
def run_qrng_and_encryption(sample_text):
    print("\n--- Starting Quantum QRNG Process ---")
    
    # Create quantum circuit
    qc = QuantumCircuit(num_qubits, num_qubits)
    qc.h(range(num_qubits))
    qc.measure(range(num_qubits), range(num_qubits))

    shannon_entropies = []
    min_entropies = []
    
    backend = AerSimulator()
    compiled_circuit = transpile(qc, backend)
    
    for shots in shot_values:
        job = backend.run(compiled_circuit, shots=shots)
        result = job.result()
        counts = result.get_counts()
        
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
        print(f"Entropy for {shots} shots: Shannon={shannon_entropies[-1]:.4f}, Min={min_entropies[-1]:.4f}")

    last_counts = counts
    random_bits = list(last_counts.keys())
    
    print(f"\nGenerated {len(random_bits)} random {num_qubits}-bit strings (from 1000 shots).")
    print("First 10 bitstrings:", random_bits[:10])
    
    # --- Plotting ---
    static_folder = os.path.join(app.root_path, 'static', 'images')
    if not os.path.exists(static_folder):
        os.makedirs(static_folder)
        
    frequencies = [last_counts[bit] for bit in random_bits]
    
    plt.figure("QRNG Histogram")
    plt.bar(range(len(random_bits)), frequencies, width=0.8, color='skyblue', edgecolor='black')
    plt.xlabel("Bitstring Index")
    plt.ylabel("Count")
    plt.title(f"Distribution of 8-bit Strings")
    plt.xticks([])
    plt.grid(True, which="both", ls="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(static_folder, 'qrng_histogram.png'))
    plt.close()

    plt.figure("CDF of Bitstring Frequencies")
    sorted_freqs = sorted(last_counts.values())
    cumulative_probs = np.cumsum(sorted_freqs) / sum(sorted_freqs)
    plt.plot(sorted_freqs, cumulative_probs, marker='.', linestyle='-', color='green')
    plt.xlabel("Frequency")
    plt.ylabel("Cumulative Probability")
    plt.title("CDF of Bitstring Frequencies")
    plt.grid(True, ls="--", alpha=0.7)
    plt.savefig(os.path.join(static_folder, 'cdf_plot.png'))
    plt.close()

    plt.figure("Entropy vs. Shots")
    plt.plot(shot_values, shannon_entropies, label="Shannon Entropy", marker='o', color='blue')
    plt.plot(shot_values, min_entropies, label="Min-Entropy", marker='o', color='red')
    plt.xlabel("Number of Shots")
    plt.ylabel("Entropy (bits)")
    plt.title("How Randomness Improves with More Shots")
    plt.legend()
    plt.grid(True, ls="--", alpha=0.7)
    plt.savefig(os.path.join(static_folder, 'entropy_vs_shots.png'))
    plt.close()

    # --- Encryption and Decryption ---
    print("\n--- Starting Encryption and Decryption Demo ---")
    
    def text_to_binary(text):
        return ''.join(format(ord(char), '08b') for char in text)

    def binary_to_text(binary):
        return ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))
    
    def binary_to_bytes(binary_string):
        return int(binary_string, 2).to_bytes((len(binary_string) + 7) // 8, 'big')

    binary_text = text_to_binary(sample_text)
    
    combined_bits = "".join(random_bits)
    superkey = hashlib.sha256(combined_bits.encode()).hexdigest()
    
    key_stream_binary = bin(int(superkey, 16))[2:].zfill(256)
    
    full_key_stream_binary = ''
    while len(full_key_stream_binary) < len(binary_text):
        full_key_stream_binary += key_stream_binary
    full_key_stream_binary = full_key_stream_binary[:len(binary_text)]
    
    encrypted_binary = ''.join('1' if a != b else '0' for a, b in zip(binary_text, full_key_stream_binary))
    decrypted_binary = ''.join('1' if a != b else '0' for a, b in zip(encrypted_binary, full_key_stream_binary))
    
    encrypted_text = binary_to_text(encrypted_binary)
    decrypted_text = binary_to_text(decrypted_binary)
    
    encrypted_hex = binary_to_bytes(encrypted_binary).hex()

    print(f"\nOriginal Text: {sample_text}")
    print(f"Encrypted Text (Hex): {encrypted_hex}")
    print(f"Decrypted Text: {decrypted_text}")
    print("\n--- Process Completed ---")
    
    # --- Run Statistical Tests ---
    monobit_score = monobit_test(random_bits)
    runs_score = runs_test(random_bits)
    chi_squared_stat = chi_squared_test(last_counts, num_qubits, 1000)

    return {
        "shannon_entropy": shannon_entropies[-1],
        "min_entropy": min_entropies[-1],
        "original_text": sample_text,
        "encrypted_text": encrypted_text,
        "decrypted_text": decrypted_text,
        "monobit_score": monobit_score,
        "runs_score": runs_score,
        "chi_squared_stat": chi_squared_stat
    }

# --- Flask Routes ---
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        sample_text = request.form['sample_text']
        results = run_qrng_and_encryption(sample_text)
        return render_template('results.html', **results)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
    # Save the generated bitstrings to a text file in the static folder
    file_path = os.path.join(app.root_path, 'static', 'random_bits.txt')
    with open(file_path, 'w') as f:
        for bitstring in random_bits:
            f.write(bitstring + '\n')
    print(f"\nSaved {len(random_bits)} random bitstrings to {file_path}")