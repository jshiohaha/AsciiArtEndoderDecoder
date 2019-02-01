import builtins
import collections
import pathlib
import unittest
from unittest.mock import patch, mock_open

import bitstring
import huffman
import mock
import msgpack

from src import AsciiTransform as AT
from test_constants import *


class AsciiTransformTests(unittest.TestCase):
    def test_get_file_data_raises_exception(self):
        with self.assertRaises(FileNotFoundError) as context:
            AT.get_file_data("file", False)

        self.assertTrue('Filename specified (file) does not exist.' in str(context.exception))

    def test_get_file_data_not_binary(self):
        result = None
        with patch.object(pathlib.Path, 'is_file') as mock_exists:
            mock_exists.return_value = True

            with patch('builtins.open', unittest.mock.mock_open(read_data=file_data)) as open_file:
                result = AT.get_file_data("file", False)

        self.assertEqual(result, file_data)


    def test_get_file_data_binary(self):
        result = None

        with patch.object(pathlib.Path, 'is_file') as mock_exists:
            mock_exists.return_value = True

            with patch('builtins.open', unittest.mock.mock_open(read_data=binary_file_data)) as open_file:
                result = AT.get_file_data("file", True)

        self.assertEqual(result, binary_file_data)


class EncoderTests(unittest.TestCase):
    # encode function
    def test_encode_with_null_data(self):
        with self.assertRaises(ValueError) as context:
            AT.Encoder(None).encode()

        self.assertTrue('Input parameter (data) cannot be Null' in str(context.exception))


    def test_encode_with_non_ascii_character(self):
        with self.assertRaises(ValueError) as context:
            AT.Encoder(non_ascii_file_data).encode()

        self.assertTrue('Non-ASCII character found' in str(context.exception))


    def test_encode_success(self):
        original_huffman_coding = huffman.codebook(collections.Counter(file_data).items())
        encoded_data = AT.Encoder(file_data).encode()

        self.assertEqual(encoded_data, encoded_file_data)
        
        data_stream = bitstring.ConstBitStream(encoded_data)

        huffman_coding_num_bytes = int.from_bytes(data_stream.read('bytes:1'), byteorder='big')
        self.assertEqual(huffman_coding_num_bytes, 1)

        huffman_coding_size = int.from_bytes(data_stream.read("bytes:{}".format(huffman_coding_num_bytes)), byteorder='big')
        huffman_bin_data = data_stream.read("bytes:{}".format(huffman_coding_size))
        unpacked_huffman_coding = msgpack.unpackb(huffman_bin_data, raw=False)

        self.assertEqual(original_huffman_coding, unpacked_huffman_coding)
        self.assertEqual(len(original_huffman_coding), len(unpacked_huffman_coding))
    

    def test_encode_success_small_file_data(self):
        original_huffman_coding = huffman.codebook(collections.Counter(file_data_big).items())
        encoded_data = AT.Encoder(file_data_big).encode()

        data_stream = bitstring.ConstBitStream(encoded_data)

        huffman_coding_num_bytes = int.from_bytes(data_stream.read('bytes:1'), byteorder='big')
        self.assertEqual(huffman_coding_num_bytes, 1)

        huffman_coding_size = int.from_bytes(data_stream.read("bytes:{}".format(huffman_coding_num_bytes)), byteorder='big')
        huffman_bin_data = data_stream.read("bytes:{}".format(huffman_coding_size))
        unpacked_huffman_coding = msgpack.unpackb(huffman_bin_data, raw=False)

        self.assertEqual(original_huffman_coding, unpacked_huffman_coding)
        self.assertEqual(len(original_huffman_coding), len(unpacked_huffman_coding))


class DecoderTests(unittest.TestCase):
    def test_decode_with_null_data(self):
        with self.assertRaises(ValueError) as context:
            AT.Decoder(None).decode()


    def test_decode_with_string_data(self):
        with self.assertRaises(ValueError) as context:
            AT.Decoder("hello world").decode()


    def test_decode_success(self):
        original_data = AT.Decoder(encoded_file_data).decode()
        self.assertEqual(original_data, file_data)


class UtilityTests(unittest.TestCase):
    def test_serialize_data_non_binary_data(self):
        fake_file_path = "fake/file/path"
        with patch('builtins.open', mock_open()) as mocked_file:
            AT.serialize_data(fake_file_path, file_data, is_binary=False)
            mocked_file.assert_called_once_with(fake_file_path, 'w')
            mocked_file().write.assert_called_once_with(file_data)

    def test_serialize_data_binary_data(self):
        fake_file_path = "fake/file/path"
        with patch('builtins.open', mock_open()) as mocked_file:
            AT.serialize_data(fake_file_path, binary_file_data, is_binary=True)
            mocked_file.assert_called_once_with(fake_file_path, 'wb')
            mocked_file().write.assert_called_once_with(binary_file_data)


if __name__ == '__main__':
    unittest.main()
