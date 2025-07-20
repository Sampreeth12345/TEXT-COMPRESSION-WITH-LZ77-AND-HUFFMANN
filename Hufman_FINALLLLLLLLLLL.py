from heapq import heappush, heappop, heapify
from collections import defaultdict
from bitarray import bitarray
import time
import tkinter as tk
from tkinter import filedialog

print("File Compression Using Huffman Coding".center(148))

def display_message(message, duration):
    print(message) 
    time.sleep(duration)

# Create a Tkinter window
window = tk.Tk()
window.withdraw()  # Hide the root window

# Open file dialog to select a file for compression
compress_file = filedialog.askopenfilename(title="Select File for Compression")

display_message('Compressing File...', 1)

freq_lib = defaultdict(int)
with open(compress_file, 'r') as file:
    for line in file:
        for ch in line.strip():
            freq_lib[ch] += 1

heap = [[fq, [sym, ""]] for sym, fq in freq_lib.items()]
heapify(heap)

while len(heap) > 1:
    right = heappop(heap)
    left = heappop(heap)
    for pair in right[1:]:
        pair[1] = '0' + pair[1]
    for pair in left[1:]:
        pair[1] = '1' + pair[1]
    heappush(heap, [right[0] + left[0]] + right[1:] + left[1:])

huffman_list = right[1:] + left[1:]
huffman_dict = {a[0]: bitarray(str(a[1])) for a in huffman_list}

encoded_text = bitarray()
with open(compress_file, 'r') as file:
    for line in file:
        encoded_text.encode(huffman_dict, line.strip())

padding = 8 - (len(encoded_text) % 8)
compressed_file = compress_file + '.compressed'
with open(compressed_file, 'wb') as w:
    encoded_text.tofile(w)

display_message('File Successfully Compressed! in the name your_input_file_name.txt.compressed', 0.5)

freq_lib = dict(sorted(freq_lib.items(), key=lambda x: x[1], reverse=True))

dictionary_file = 'dictionary.txt'
with open(dictionary_file, 'w') as dict1:
    for x, y in freq_lib.items():
        z = str(x)+"\n"
        dict1.write(z)

display_message('Compression dictionary saved!', 0.5)

# Open file dialog to select a file for decompression
decompress_file = filedialog.askopenfilename(title="Select File for Decompression")

display_message('Decompressing File...', 1)

decoded_text = bitarray()

with open(decompress_file, 'rb') as r:
    decoded_text.fromfile(r)

decoded_text = decoded_text[:-padding]
decoded_text = decoded_text.decode(huffman_dict)
decoded_text = ''.join(decoded_text)

display_message('File Successfully Decompressed!', 0.5)
print(f'Decompressed text is: {decoded_text}')

# Specify the desired name for the decompressed file
decompressed_file = filedialog.asksaveasfilename(defaultextension='.txt',
                                                 filetypes=(('Text Files', '*.txt'), ('All Files', '*.*')),
                                                 title='Save Decompressed File As')

with open(decompressed_file, 'w') as w:
    w.write(decoded_text)

display_message('Decompressed file saved!', 0.5)
