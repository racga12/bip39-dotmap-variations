# bip39-dotmap-encryptor-visualizer

A secure, educational utility to convert cryptocurrency BIP39 mnemonic seed phrases (12 or 24 words) into abstract, binary dot map representations (○/●) for ultra-durable physical backups.

> Originally based on the OneKeyHQ repository: https://github.com/OneKeyHQ/bip39-dotmap

#### Work In Progress/TO-DO:
* [x] Make user friendly version and guide to execute the app in a offline Linux Live session.
* [ ] Multi Language support
      
---
## Table of Contents
1. [Core Methodology](#-core-methodology)
2. [Quick Start & Installation](#-quick-start--installation)
    - [Option A: Standalone Binary (Recommended for Tails/Debian Live OS)](#option-a-standalone-binary-recommended-for-tailsdebian-live-os)
    - [Option B: Local Development (Python 3.12+)](#option-b-local-development-python-312)
3. [Trust-Minimized Build (Self-Compilation)](#%EF%B8%8F-trust-minimized-build-self-compilation)
4. [Documentation & Technical Wiki](#-documentation--technical-wiki)

---

## 🧠 Core Methodology
Instead of storing recovery words in vulnerable plain text, this project maps data layers physically:

1. **Word to Index**: Translates words to their 1-based BIP39 indices (1 to 2048).

2. **Obfuscation & Encryption**: Optionally applies layers like XOR Masking, Bit Permutations, or Decoy Dots to alter rows/columns before printing.

3. **Dot Matrix Generation**: Converts sequences into a clean 12-column monospace grid (○ for 0, ● for 1) perfect for metal plates engraving.

---

## 🚀 Quick Start & Installation

To maintain absolute maximum security, you should run this application exclusively in a completely offline, air-gapped environment.

### Option A: Standalone Binary (Recommended for Tails/Debian Live OS)
No Python or dependencies required.
1. Download the compiled [released binary](https://github.com/racga12/bip39-dotmap-encryptor-visualizer/releases).
2. Grant execution permissions and execute:
   ```bash
   chmod +x bip39-dotmap-visualizer
   ./bip39-dotmap-visualizer
3. Access via browser at `http://127.0.0.1:5000`. Kill the process anytime using *Ctrl + C** if you opened from console or `pkill -f bip39-dotmap-visualizer` if you used the file explorer.

### Option B: Local Development (Python 3.12+)
1. Clone the repo and install Flask:

   ```bash
   git clone [https://github.com/racga12/bip39-dotmap-encryptor-visualizer.git](https://github.com/racga12/bip39-dotmap-encryptor-visualizer.git)
   cd bip39-dotmap-encryptor-visualizer
   pip install Flask
   ```
2. Run the application:

   ```bash
   python app.py

---

## 🛠️ Trust-Minimized Build (Self-Compilation)
To audit the application code and generate the frozen Linux binary yourself:
```bash
pip install Flask pyinstaller
pyinstaller --onefile --add-data "templates:templates" --add-data "wordslists:wordslists" --name "bip39-dotmap-visualizer" app.py
```
---

## 📚 Documentation & Technical Wiki

For comprehensive operational guides, cryptographic definitions, and instructions for complete offline disaster recovery by hand, please visit our official documentation pages:

* 📕 [Normal/Original Method Explanation](https://github.com/racga12/bip39-dotmap-encryptor-visualizer/wiki/Normal-Method)
* 🔎 [Detailed application documentation](https://github.com/racga12/bip39-dotmap-variations/wiki/BIP39-Mnemonic-Dotmap-Visualizer-Documentation)
* 🔒 [Air-Gapped Physical Workflow Guide](https://github.com/racga12/bip39-dotmap-encryptor-visualizer/wiki/BIP39-Mnemonic-Dotmap-Visualizer-Documentation#3-recommended-air-gapped-physical-workflow)
* 🪟 [Overview of Additional Encryption Methods
](https://github.com/racga12/bip39-dotmap-encryptor-visualizer/wiki/Overview-of-Additional-Encryption-Methods)
  * 🧮 [Detailed info: XOR Masking (Vernam Cipher) Recovery](https://github.com/racga12/bip39-dotmap-variations/wiki/XOR-Masking-(Vernam-Cipher))
  * 🧩 [Detailed info: Bit Permutation (P-Boxes) Recovery](https://github.com/racga12/bip39-dotmap-variations/wiki/Bit-Permutation-(P%E2%80%90Boxes))
  * 👁️ [Detailed info: Decoy Dots (Grid Steganography) Theory](https://github.com/racga12/bip39-dotmap-variations/wiki/Decoy-Dots-(Grid-Steganography))


### 📋 *Link to original wordlists to the bitcoin repo*

[bip-0039 wordlists](https://github.com/bitcoin/bips/tree/master/bip-0039)
