import math
from bitarray import bitarray
import tkinter as tk
from tkinter import filedialog

class LZ77Compressor:
    MAX_WINDOW_SIZE = 400

    def __init__(self, window_size=20):
        self.window_size = min(window_size, self.MAX_WINDOW_SIZE) 
        self.lookahead_buffer_size = 15  # length of match is at most 4 bits

    def compress(self, input_file_path, verbose=False):
        data = None
        i = 0
        output_buffer = bitarray(endian='big')

        # read the input file 
        try:
            with open(input_file_path, 'rb') as input_file:
                data = input_file.read()
        except IOError:
            print('Could not open input file ...')
            raise

        while i < len(data):
            match = self.findLongestMatch(data, i)

            if match: 
                (bestMatchDistance, bestMatchLength) = match

                output_buffer.append(True)
                output_buffer.frombytes(bytes([bestMatchDistance >> 4]))
                output_buffer.frombytes(bytes([((bestMatchDistance & 0xf) << 4) | bestMatchLength]))

                if verbose:
                    print("<1, %i, %i>" % (bestMatchDistance, bestMatchLength), end='')

                i += bestMatchLength
            else:
                output_buffer.append(False)
                output_buffer.frombytes(bytes([data[i]]))
                
                if verbose:
                    print("<0, %s>" % data[i], end='')

                i += 1

        output_buffer.fill()
        return output_buffer

    def decompress(self, input_file_path):
        data = bitarray(endian='big')
        output_buffer = []

        # Read the input file
        try:
            with open(input_file_path, 'rb') as input_file:
                data.fromfile(input_file)
        except IOError:
            print('Could not open input file ...')
            raise

        while len(data) >= 9:
            flag = data.pop(0)

            if not flag:
                byte = data[0:8].tobytes()

                output_buffer.append(byte)
                del data[0:8]
            else:
                byte1 = ord(data[0:8].tobytes())
                byte2 = ord(data[8:16].tobytes())

                del data[0:16]
                distance = (byte1 << 4) | (byte2 >> 4)
                length = (byte2 & 0xf)

                for i in range(length):
                    output_buffer.append(output_buffer[-distance])
        out_data = b''.join(output_buffer)

        output_file_path = input_file_path[:-4] + '_decompress.txt'
        try:
            with open(output_file_path, 'wb') as output_file:
                output_file.write(out_data)
                print('File was decompressed successfully and saved to output path: as your filename_decompress', output_file_path)
        except IOError:
            print('Could not write to output file path. Please check if the path is correct ...')

    def findLongestMatch(self, data, current_position):
        end_of_buffer = min(current_position + self.lookahead_buffer_size, len(data) + 1)

        best_match_distance = -1
        best_match_length = -1

        for j in range(current_position + 2, end_of_buffer):
            start_index = max(0, current_position - self.window_size)
            substring = data[current_position:j]

            for i in range(start_index, current_position):
                repetitions = len(substring) // (current_position - i)
                last = len(substring) % (current_position - i)
                matched_string = data[i:current_position] * repetitions + data[i:i+last]

                if matched_string == substring and len(substring) > best_match_length:
                    best_match_distance = current_position - i 
                    best_match_length = len(substring)

        if best_match_distance > 0 and best_match_length > 0:
            return (best_match_distance, best_match_length)
        return None


if __name__ == '__main__':
    # Create a Tkinter window
    window = tk.Tk()
    window.withdraw()  # Hide the root window

    # Open file dialog to select a file for compression
    input_file_path = filedialog.askopenfilename(title="Select File for Compression")

    # Create an instance of the LZ77Compressor
    compressor = LZ77Compressor()

    # Compress the input file
    compressed_data = compressor.compress(input_file_path, verbose=True)

    # Specify the desired name for the compressed file
    compressed_file_path = filedialog.asksaveasfilename(defaultextension='.bin',
                                                        filetypes=(('Binary Files', '*.bin'), ('All Files', '*.*')),
                                                        title='Save Compressed File As')

    # Write the compressed data to the file
    try:
        with open(compressed_file_path, 'wb') as compressed_file:
            compressed_file.write(compressed_data.tobytes())
            print('File was compressed successfully and saved to output path:', compressed_file_path)
    except IOError:
        print('Could not write to output file path. Please check if the path is correct ...')

    # Open file dialog to select a file for decompression
    decompress_file = filedialog.askopenfilename(title="Select File for Decompression")

    # Decompress the selected file
    compressor.decompress(decompress_file)

    # Close the Tkinter window
    window.destroy()
