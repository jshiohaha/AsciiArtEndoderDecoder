from src import AsciiTransform as AT

def main():
    # read file data
    file_data = AT.get_file_data('./data/data2.txt', False)

    # encode data and serialize compressed data
    encoded_data = AT.Encoder(file_data).encode()
    AT.serialize_data('output/output.bin', encoded_data, True)

    # decode data and serialize original data
    decoded_data = AT.Decoder(encoded_data).decode()
    AT.serialize_data('output/output.txt', decoded_data, False)

if __name__== "__main__":
    main() 