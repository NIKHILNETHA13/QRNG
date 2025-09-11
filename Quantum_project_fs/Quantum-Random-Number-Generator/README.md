# QRNG
This repo is about Quantum Random Number Generator.
Welcome to my QRNG project, crafted with love and a bit of quantum magic for the Amaravati Quantum Valley Hackathon 2025! 🌌🚀 This repository houses a Quantum Random Number Generator built using Qiskit, designed to produce truly random bits for cryptographic purposes. Let’s dive into the adventure!
What I Built
I’ve created a Quantum Random Number Generator (QRNG) using the Qiskit library, a powerful tool for quantum computing. The heart of this project is an 8-qubit quantum circuit where I applied Hadamard gates to throw each qubit into superposition—a state of pure quantum uncertainty. When measured, these qubits collapse into either 0 or 1 with equal probability, generating around 255 unique 8-bit strings. I saved these random treasures in a random_bits.txt file, ready to spark some cryptographic creativity! The process was a thrilling mix of coding, debugging, and marveling at quantum weirdness.
How It Works
The magic happens in the quantum realm! Here’s the gist:

I set up an 8-qubit circuit and used Hadamard gates to create superposition, making each qubit a blend of 0 and 1 until measured.
Running this on Qiskit’s AerSimulator with 100 to 1000 shots, I collected the resulting bitstrings, with the final 1000-shot run yielding my random dataset.
The randomness comes from quantum mechanics’ inherent unpredictability—unlike classical pseudo-random number generators, this is true randomness straight from the quantum world!

I also whipped up some cool visualizations using Matplotlib:

A circuit diagram to show the setup.
A histogram of bitstring frequencies.
A Cumulative Distribution Function (CDF) of those frequencies.
A plot tracking how entropy grows with more shots.

The Role of Entropy
Entropy is the star of the show here—it measures the randomness and unpredictability of my bitstrings, which is crucial for cryptography. I calculated two types:

Shannon Entropy: This tells us the average information content. For my 1000-shot run, it hovered around 7.9 bits (out of a max 8 bits), showing the bits are pretty darn random!
Min-Entropy: This focuses on the worst-case predictability, coming in at about 6.9 bits. It reflects the highest probability of any single outcome, and a higher value means better randomness.

These entropy metrics prove my QRNG produces high-quality random numbers, making it a solid foundation for secure applications. The more shots I used, the better the entropy got—proof that quantum scaling pays off!
Cryptographic Applications
These random bits aren’t just for show—they’re a goldmine for cryptography! I took the 255 bitstrings, combined the first 32 into a 256-bit sequence, and hashed it with SHA-256 to create a superkey. Using this key, I encrypted a sample text (e.g., "Hello") by converting it to binary, XORing it with a key stream derived from the superkey, and decrypted it back—successfully! This unpredictability makes quantum random numbers ideal for:

Generating secure encryption keys that hackers can’t predict.
Enhancing data protection in fields like finance, defense, and healthcare.
Building future quantum-safe cryptographic systems as quantum computers grow.

It’s a small step, but it’s opened my eyes to the power of quantum randomness in security!
These are the outputs:
<img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/844f2e1d-dbee-41c4-99fe-13ebc1fd0613" />
<img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/16a17bcd-ca5a-48e1-9907-340fa3137f27" />
<img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/fcdbff0b-ee14-4823-81a7-f29e34ee9f53" />
<img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/d13a3c8c-287a-4a27-825a-e70daaf83223" />


