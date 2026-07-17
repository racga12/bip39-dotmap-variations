# BIP39 Mnemonic Dotmap Visualizer Documentation

Welcome to the **BIP39 Mnemonic Dotmap Visualizer** documentation. This wiki page provides a comprehensive guide on the internal mechanics, security measures, and cryptographic flows of the application. It is designed to help you understand how raw mnemonic seed phrases are converted into visual binary representations (dot maps) and safe bytearray outputs.

---

## Table of Contents
1. [Core Purpose & Background](#1-core-purpose--background)
2. [High-Level Application Architecture](#2-high-level-application-architecture)
3. [The Normal Translation Method (Step-by-Step)](#3-the-normal-translation-method-step-by-step)
4. [Advanced Encryption Layers](#4-advanced-encryption-layers)
    - [XOR Masking (Vernam Cipher / One-Time Pad)](#xor-masking-vernam-cipher--one-time-pad)
    - [Bit Permutation (P-Boxes)](#bit-permutation-p-boxes)
5. [Bytearray Transformation Outputs](#5-bytearray-transformation-outputs)
6. [Security Engineering & Offline Workflow](#6-security-engineering--offline-workflow)

---

## 1. Core Purpose & Background

Storing recovery seed phrases in plain text (e.g., written on paper cards) is highly vulnerable to physical theft, unauthorized camera/lens captures, or casual shoulder-surfing.

This visualizer translates standard 12-to-24-word BIP39 cryptocurrency mnemonic phrases into a physical-medium friendly, visual **12-bit binary representation (a dot map)**.
- A **filled dot (●)** represents a binary `1`.
- An **empty dot (○)** represents a binary `0`.

Because the grid represents mathematical indices in binary rather than letters, it is highly unrecognizable to a casual observer, yet extremely easy to restore manually or engrave onto durable, fireproof, and waterproof metal plates (e.g., steel or titanium).

---

## 2. High-Level Application Architecture

The application is built using a lightweight Python-based **Flask** backend and a responsive **Bootstrap 5** frontend template.

```
┌────────────────────────────────────────────────────────┐
│                      FRONTEND                          │
│  - Form input (Mnemonic Words, Language, Encryption)    │
│  - Interactive visual Modals (Security Checks)         │
│  - Result grids rendering Dot Maps (●/○)               │
└──────────────────────────┬─────────────────────────────┘
                           │ POST Request (Cleaned Input)
                           ▼
┌────────────────────────────────────────────────────────┐
│                      BACKEND                           │
│  - Sanitizes input (length-limit, null-byte stripping) │
│  - Maps each word to a 1-2048 index from wordlists     │
│  - Generates 12-bit binary representations             │
│  - Optionally applies XOR / Bit-Permutation            │
│  - Packs outputs to Big-Endian Decimal/Hex Bytearrays  │
└────────────────────────────────────────────────────────┘
```

### File Structure:
- `app.py`: The entry point for the Flask web application. It handles route routing, input validation and sanitization, dictionary loading for multi-language BIP39 wordlists, index translation, bitwise calculations, encryption/permutation, and hexadecimal/decimal bytearray serialization.
- `templates/index.html`: The UI layer styled with Bootstrap. Contains standard inputs, visual dot maps (using monospace characters for aligned grids), interactive decryption keys, and security instructions modal popups.
- `wordslists/` (or `wordlists/`): Holds localized dictionary text files (English, Spanish, French, Japanese, etc.), each containing exactly 2048 words (one word per line).

---

## 3. The Normal Translation Method (Step-by-Step)

The normal translation process works without active encryption keys, utilizing only the standard BIP39 localized dictionary to map words to indices.

```
Mnemonic Word ──► Localized Wordlist Index (1 to 2048) ──► 12-Bit Binary Sequence ──► 12-Column Dot Grid (○/●)
```

### Detailed Steps:

1. **Word-to-Index Translation:**
   Each input recovery word is cleaned and matched to its corresponding index in the selected standard BIP39 language wordlist. Since computer array indices are typically `0-based` (0 to 2047), the standard BIP39 specification lists word indices as `1-based` (1 to 2048).
   - *Example:* The word `"abandon"` is the 1st word in the English list $\rightarrow$ Index: `1`.
   - *Example:* The word `"about"` is the 4th word in the English list $\rightarrow$ Index: `4`.
   - *Example:* The word `"zoo"` is the 2048th word in the English list $\rightarrow$ Index: `2048`.

2. **Index-to-Binary Conversion:**
   The index number is converted into a **12-bit binary sequence**. A 12-bit limit is used because $2^{11} = 2048$, meaning any index from `1` to `2048` can be represented in exactly 12 bits (representing columns valued: $2048, 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1$).
   - *Index 1* becomes: `0000 0000 0001`
   - *Index 4* becomes: `0000 0000 0100`
   - *Index 977* (for `"key"`) becomes: `0011 1101 0001` (512 + 256 + 128 + 64 + 16 + 1)

3. **Binary-to-Dot Grid Mapping:**
   The binary sequence is split into three blocks of 4 bits to facilitate visual scanning and engraving on grids. Every `1` is plotted as a filled dot (**●**), and every `0` is plotted as an empty dot (**○**).

   | Index | Word | Column 1 (2048-256) | Column 2 (128-16) | Column 3 (8-1) | Raw Binary |
   |:---:|:---:|:---:|:---:|:---:|:---:|
   | **1** | abandon | ○ ○ ○ ○ | ○ ○ ○ ○ | ○ ○ ○ ● | `000000000001` |
   | **4** | about | ○ ○ ○ ○ | ○ ○ ○ ○ | ○ ● ○ ○ | `000000000100` |
   | **977** | key | ○ ○ ● ● | ● ● ○ ● | ○ ○ ○ ● | `001111010001` |

---

## 4. Advanced Encryption Layers

To prevent physical adversaries from visually decoding the dot map grid, the app implements two cryptographically secure encryption layers.

### XOR Masking (Vernam Cipher / One-Time Pad)

When XOR Masking is selected, the application generates a cryptographically secure, random 12-bit key for **each word** in the recovery phrase.

$$\text{Encrypted Dot Map} = \text{Original Dot Map} \oplus \text{Random XOR Key}$$

#### Manual Recovery Process (Pen and Paper):
You can easily decrypt this visual representation by hand using basic logical XOR rules without needing a computer:
- Compare the **Encrypted Dot Map** column-by-column against your printed/engraved **Decryption Key**:
  - If the dots are the same (**○○** or **●●**), draw an **empty dot (○)** ($0 \oplus 0 = 0$, $1 \oplus 1 = 0$).
  - If the dots are different (**○●** or **●○**), draw a **filled dot (●)** ($0 \oplus 1 = 1$, $1 \oplus 0 = 1$).

---

### Bit Permutation (P-Boxes)

Bit Permutation shuffles the order of the 12 columns in your binary dot map using a random mapping scheme. This eliminates visual pattern recognition, scattering adjacent bits across the grid.

```
Original Bit Positions:   [1] [2] [3] [4] [5] [6] [7] [8] [9] [10] [11] [12]
                                \   /   \   /   /   /   \   \    /    /
Permuted Column Order:    [5] [1] [12] [3] [8] [2] [11] [6] [4] [9] [7] [10]
```

#### Manual Recovery Process:
A physical lookup/reference grid (Column Re-Ordering Reference Card) is generated:
- For example, if the card states: *"Original Position 1 $\rightarrow$ Read from Encrypted Col 5"*, you look at column 5 of your permuted map, and copy its status back into position 1.

---

## 5. Bytearray Transformation Outputs

The visualizer provides binary serialization details as safe hexadecimal strings and decimal lists. It exposes three primary bytearray transformations:

1. **Raw Words Input Bytearray (UTF-8 Encoded):**
   Converts the input words (joined by a single space) into raw UTF-8 bytes. Helpful for programmatic string validations.
2. **Original Word Indices Bytearray:**
   Converts the matched BIP39 indices (1-2048) into raw big-endian 2-byte values.
   - *Example:* Word Index `1` is written as `\x00\x01` (`[0, 1]` in decimal), Index `2048` is written as `\x08\x00` (`[8, 0]` in decimal).
3. **Encrypted Word Indices Bytearray:**
   Presents the encrypted equivalent (computed under XOR or Permutation models) mapped to big-endian 2-byte lists.

---

## 6. Security Engineering & Offline Workflow

Because mnemonic recovery phrases control direct access to blockchain addresses, the Visualizer has been built with strict **zero-trust design principles** to ensure your keys are never leaked:

### Built-in Code Protections:
- **Strict Input Length Limits:** The form limits user entries to a maximum of 10,000 characters to block buffer overflow exploits or server memory exhaustion vectors.
- **Null-Byte Stripping:** The Flask server strips null characters (`\x00`) from user-supplied strings before internal bytearray conversion to prevent low-level language structure termination exploits.

### Recommended Air-Gapped Physical Workflow:
For maximum safety, perform the visual generation entirely **offline**:

1. **Download Code:** Clone or download the repository to an external USB flash drive.
2. **Offline OS Boot:** Disconnect your computer from the internet. Better yet, boot your system using a clean offline OS (e.g., a *Tails* live USB).
3. **Run Local Server:** Plug in the USB flash drive, boot the Flask app (`python app.py`), and access `http://127.0.0.1:5000`.
4. **Incognito Mode:** Load the page in an Incognito/Private window with all browser extensions/add-ons completely disabled to prevent background keyloggers or scraper plugins.
5. **Session Cleanup:** After you have recorded or engraved your visual dot map:
   - Clear your clipboard history by copying random dummy strings (e.g., `"abc"`).
   - Close all browser tabs.
   - Kill the Flask server process (`Ctrl+C` in the terminal).
   - **Reboot the computer** to completely wipe volatile RAM.

---
*This guide is maintained by the repository developers. If you have questions about the core binary logic or cryptographic formulas, please open an issue in the main repository.*
