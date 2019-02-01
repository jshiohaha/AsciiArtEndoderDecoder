# ASCII Art Encoder/Decoder

The goal of this exercise was to design a transport format for transferring ASCII art images, and implement `Encode` and `Decode` functions for the format. The ASCII art images can be expected to be

- Bitmap size of 100x100.
- ASCII characters (i.e. character code point range of 0 to 255).

## Environment Setup
This implementation was written in `3.6.5`, but it should run with any version of Python 3. You will also need the **pip** package manager to install three packages. The required environment setup steps are outlined below.

If you do not want to install the **pip** packages globally, then you can follow the steps to setup a virtual environment. If you don't mind installing the packages globally, you can skip down to the **Install the required pip packages** section. 

#### Setup pip package manager

Check to see if your Python installation has pip by running `pip -h`. If you see the help text for pip then you have pip installed, otherwise [download and install pip](https://pip.pypa.io/en/latest/installing/).

#### Install and Create the virtual environment

Use pip to install the `virtualenv` package required to create virtual environments. A virtual environment will ensure any python commands will work with your virtual environment. Additionally, installed packages will not be installed globally. You can install the virtualenv package with pip by running `pip install virtualenv`.

Now, create a virtual environment. The parameter after the `virtualenv` command denotes the local directory where the virtual environment will be created. For example, `virtualenv venv` will create a virtual environment named venv in your current directory. 

#### Activate the virtual environment

You can activate the python environment you created by running the following command:

**Mac OS / Linux**

`source venv/bin/activate`

**Windows**

`venv\Scripts\activate`

You should now see the name of your virtual environment in brackets on your terminal line, e.g. (venv).

#### Deactivate the virtual environment

To decativate the virtual environment and use your original Python environment, just type `deactivate`.

## Install the required pip packages
You should be able to include all of the files in the gist into the same directory as your virtual environment. Once that is done, ensure your virtual environment is activated (if you made one) and run `pip install -r requirements.txt`.

Now that the pip packages are installed, your environment should be ready to run the program.

## Running the program
There file `driver.py` contains the code to execute the encoding and decoding functions. The comments explain what each section does in `driver.py`. To run the `driver.py` file, type `python driver.py`. If `Python3` is not the default version of Python on your system, you will have to explicitly type `python3 driver.py`.

To use the encoding function, you need to create an instance of `Encoder` with the ASCII data (there is also a function to read in file data). Once the `Encoder` instance is created, you just have to call the `encode()` function. An example is below.

```
ascii_data = get_file_data(filename, False)
encoder = Encoder(ascii_data)
encoded_data = encoder.encode()
```

To use the decoding function, the process is very similar. You need to create an instance of `Decoder` with the encoded ASCII data. Once the `Decoder ` instance is created, you just have to call the `decode()` function. An example is below.

```
decoder = Decoder(encoded_ascii_data)
encoded_data = decoder.decode()
```

To run the **tests**, simply run `python tests_AsciiTransform.py`. Again, if `Python3` is not the default version of Python on your system, you will have to explicitly type `python3 driver.py`.

**Note:** If you have a problem with imports, you might need to add the path of the directory to your PYTHONPATH.

## Encoding Approach
The lossless compression approach used combines huffman coding and run-length encoding. The benefit of huffman coding is that the most common characters can be represented with fewer bits. Run-length encoding is a simple way to keep track of how many times characters appear.

## Data Format
The data format was designed so that the decoder did not have to know anything about the encoder. The benefit to this is that data can be decoded independently of the encoding. The downside to this approach is that additional data had to be included so that the decoder would know how to decode the data, e.g. the huffman coding had to be serialized along with the ASCII bitmap data.

The data format is made up of the following. 
 - A single byte representing how many bytes (we'll call it `num_bytes`) are needed to represent the size of the serialized huffman coding. This is included because it is possible that a huffman coding would be larger than 255, which is the maximum number for a single byte.
 - `num_bytes` denoting the size of the serialized huffman coding
 - The serialized huffman coding
 - The serialized ASCII file data (described more below)

Each character in the ASCII file data is represented by a binary string from the huffman coding. The benefit of this is that the most common occurring characters can be represented with fewer bits. We also need to know how many of those  characters occurred consecutively, so that is represented with a single byte. However, using an entire byte to represent the number of occurrences when a character only occurs 1 or 2 times is really inefficient. So, if a character only occurs consecutively 1 or 2 times, its huffman coding value is used along with a trailing `1` to signify that the following byte does not represent how many times that character occurred. This approach works because of the `100x100` size of the ASCII bitmap. The number 100 only uses 7 bits, so the 8th bit is always `0`. Therefore, we know that a `1` directly after a character means that we should look for another character. To further explain this, examples are included below.

Let's say there is a `@` character that occurs 30 times. Let's also assume that it is the most common occuring character, so its huffman coding value is `0`. It would then be represented as `000100000`. The first `0` bit represents the `@` value in the huffman coding. The following byte tells us that the character occurred 32 consecutive times.

Alternatively, let's say that the `@` character only occurs 1 time at a certain point in the ASCII bitmap. It would be represented as `01`. The first `0` bit represents the value in the huffman coding. The following `1` bit tells us that the character only occurred once, and there is another character directly after. As you can see, that representation is far more efficient than using the approach described above, which would be `000000001`. Using this approach in this instance saves 7 bits.

## Future Improvements
Depending on the contents of the original ASCII bitmap data, it is possible that the encoded data would be larger than the original file because of the huffman coding. Therefore, instead of always encoding the ASCII bitmap data with the huffman coding, we could check if the encoded data is larger than the original data. If so, we could simply convert the original data to binary to limit the maximum encoded data size.