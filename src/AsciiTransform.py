import bitstring
import collections
import huffman
import msgpack

from pathlib import Path

class Encoder:
    def __init__(self, data):
        self.data = data
        self.binary_arr = []
        self.huffman_coding = None

    def encode(self):
        ''' Encodes the ASCII bitmap data of the Encoder instance and
            returns the result
        '''
        def _integer_to_binary(num, padding):
            ''' Converts an integer to a binary string with
                a set number of zeroes as padding
            '''
            if isinstance(num, int):
                # unreachable code because the previous <= 2 check
                if num < 0:
                    raise ValueError('Number must be positive.') 
                return str(format(num, 'b')).zfill(padding)
            raise ValueError('Number must be an integer.') 
            
        def _create_huffman_coding(data):
            ''' Creates a huffman coding dictionary from 
                ASCII bitmap data of the Encoder instance
            '''
            frequency_dict = collections.Counter(data).items()
            return huffman.codebook(frequency_dict)

        def _pack_binary_data(arr):
            ''' Converts the array of binary strings representing 
                the ASCII bitmap data to binary
            '''
            data = ''.join(arr)
            return bitstring.BitArray(bin=data).tobytes()

        def _append_entry(entry, occurrences):
            ''' Appends a new entry to binary_arr. The new entry is the huffman
                coding representation of the ASCII character and binary string 
                representing how many times that character occurred.

                If the ASCII character to append occurred less than 2 times, the
                ASCII character will be appended with a 1 directly after, signaling 
                that it was a character instance. This saves bytes in the encoded 
                data.
            '''
            if tracking_char_counter <= 2:
                self.binary_arr.append((self.huffman_coding[chr(tracking_char)] + "1") * tracking_char_counter)
            else:
                self.binary_arr.append(self.huffman_coding[chr(tracking_char)])
                self.binary_arr.append(_integer_to_binary(tracking_char_counter, 8))

        if self.data is None:
            raise ValueError("Input parameter (data) cannot be Null")

        # set the tracked char to the 1st char of the data
        tracking_char = ord(self.data[0])
        tracking_char_counter = 0

        self.huffman_coding = _create_huffman_coding(self.data)
        for char in self.data:
            current_char = ord(char)

            if current_char > 255:
                raise ValueError("Non-ASCII character found: {0}".format(chr(current_char)))

            if current_char == tracking_char:
                tracking_char_counter += 1
            else:
                _append_entry(tracking_char, tracking_char_counter)

                # update the tracking char and reset tracking_char_counter value to 1
                tracking_char = current_char
                tracking_char_counter = 1
        
        # after the loop finishes, add the final tracked char and count
        _append_entry(tracking_char, tracking_char_counter)

        # create binary representation of huffman coding
        packed_huffman_coding = msgpack.packb(self.huffman_coding)
        huffman_coding_size = len(packed_huffman_coding)

        num_bytes = 1
        # if huffman_coding_size < 16:
        #     if huffman_coding_size > 4:
        #         num_bytes = 2
        # else:
        #     if huffman_coding_size < 256:
        #         num_bytes = 3
        #     else:
        #         num_bytes = 4

        num_bytes_as_binary = num_bytes.to_bytes(1, byteorder='big', signed=False) 
        packed_huffman_coding_size = huffman_coding_size.to_bytes(num_bytes, byteorder='big', signed=False)
        binary_input_data = _pack_binary_data(self.binary_arr)

        return num_bytes_as_binary + packed_huffman_coding_size + packed_huffman_coding + binary_input_data


class Decoder:
    def __init__(self, data):
        self.data = data
        self.huffman_coding = None

    def decode(self):
        ''' Decodes the data of the Decoder instance and
            returns the result. The result will be the original data.

            The data contains the number of bytes for the size of the 
            huffman coding, the size of the huffman coding, the huffman
            coding, and the original ASCII bitmap data.
        '''
        def _unpack_binary_bitmap():
            ''' Convert the remaining binary file data to the 
                original ASCII bitmap data
            '''
            lower_bound, upper_bound = 0, 1
            decompressed_data = []

            # swap the keys and values in the huffman coding dict
            self.huffman_coding = { y:x for x,y in self.huffman_coding.items() }
            
            length = len(self.data)
            while upper_bound < length:
                current = self.data[lower_bound:upper_bound]

                if current.bin in self.huffman_coding:            
                    if self.data[upper_bound:upper_bound+1].bin == '1':
                        decompressed_data.append(self.huffman_coding[current.bin])

                        lower_bound = upper_bound + 1
                        upper_bound = lower_bound + 1

                        continue
                    else:
                        # increase window size to 8 to get the byte after for the number of chars
                        lower_bound = upper_bound
                        upper_bound += 8

                        num_chars = self.data[lower_bound:upper_bound]
                        decompressed_data.append(self.huffman_coding[current.bin] * int(num_chars.bin, 2))

                        # move the window to the next character
                        lower_bound = upper_bound
                        upper_bound += 1
                else:
                    # increase window of bits by 1 for huffman coding
                    upper_bound += 1

            return "".join(decompressed_data)

        if self.data is None:
            raise ValueError("Input parameter (data) cannot be Null")

        # if isinstance(self.data, str):
        #     raise ValueError("Data must be binary, not string")

        size_of_binary_data = len(self.data)
        data_stream = bitstring.ConstBitStream(self.data)

        huffman_coding_num_bytes = int.from_bytes(data_stream.read('bytes:1'), byteorder='big')
        size_of_binary_data -= huffman_coding_num_bytes
        huffman_coding_size = int.from_bytes(data_stream.read("bytes:{}".format(huffman_coding_num_bytes)), byteorder='big')
        size_of_binary_data -= huffman_coding_size
        huffman_bin_data = data_stream.read("bytes:{}".format(huffman_coding_size))

        # unpack the huffman coding from the binary
        self.huffman_coding = msgpack.unpackb(huffman_bin_data, raw=False)
        self.data = bitstring.BitArray(bytes=data_stream.read("bytes:{}".format(size_of_binary_data-1)))
        
        return _unpack_binary_bitmap()


def serialize_data(filename, data, is_binary):
    ''' Write data to file. Data can be text
        or binary, denoted by the is_binary flag
    '''
    fmt = "w"
    if is_binary:
        fmt += "b"

    output_file = open(filename, fmt)
    output_file.write(data)
    output_file.close()


def get_file_data(filename, is_binary):
    ''' Opens a file and reads the data. Data 
        can be text or binary, denoted by the is_binary 
        flag
    '''
    f = Path(filename)
    if not f.is_file():
        raise FileNotFoundError("Filename specified ({}) does not exist.".format(filename))

    fmt = "r"
    if is_binary:
        fmt += "b"

    file_data = ""
    with open(filename, fmt) as current_file:
        file_data = current_file.read()
    return file_data