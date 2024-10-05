import logging
import mmap 
import os


# file_content: byte string, offset:int, length:int, hex_str: string
def binary_substitute(file_content, offset,length, hex_str):
    logging.basicConfig(
            filename='logs/file_changing.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s')
    file_list=list(file_content)
    sub_list=list(bytes.fromhex(hex_str))
    file_list[offset:offset+length]=sub_list
    logging.info("[SUCCES] file:{fiel}")
    return bytes(f"file changed")

def file_to_hex(file_content):
    """
    Reads a file and returns its contents in hexadecimal format.

    :param file_path: Path to the file to be read.
    :return: Hexadecimal representation of the file contents as a string.
    """
    try:
        hex_output = file_content.hex()
        return hex_output
    except Exception as e:
        logging.info(f"[ERROR] {e}")

def get_chunk(chunk_number,filename):
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE'))
    with open(filename,'r+b') as inputfile:
        file_desc = inputfile.fileno()
        mmapped_file = mmap.mmap(file_desc,0)

        chunk = mmapped_file[chunk_number*CHUNK_SIZE:(chunk_number+1)*CHUNK_SIZE]

        hex_view = file_to_hex(chunk)
        inputfile.close()
        return hex_view