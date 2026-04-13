# Basic Text Editor with Huffman Compression

A clean multi-file Python project for a CSE 323 style final project.

## Folder Structure

```text
project/
│
├── main.py
├── editor.py
├── huffman.py
├── file_handler.py
├── utils.py
├── README.md
├── sample_files/
│   ├── input1.txt
│   ├── input2.txt
│
└── compressed/
    ├── example.huff
    └── restored.txt
```

## Features

- Tkinter-based text editor GUI
- New, Open, Save, Save As
- Huffman compression to `.huff`
- Huffman decompression back to `.txt`
- Clean multi-file structure for submission
- Uses only Python standard library

## Requirements

- Python 3.x
- Tkinter available in Python installation

## Run

```bash
python3 main.py
```

## How to Use

1. Run the app.
2. Create or open a text file.
3. Save the file.
4. Use **Compression > Compress Saved File** to create a `.huff` file.
5. Use **Compression > Decompress .huff File** to restore it to a text file.

## Important Notes

- Compression is for text files encoded in UTF-8.
- Very small files may not compress well because metadata adds overhead.
- Empty files are intentionally blocked from compression.
