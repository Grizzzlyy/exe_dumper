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

    chunk_size = int(os.getenv('CHUNK_SIZE'))
    f_size = os.path.getsize(filename)

    if chunk_number * (chunk_size) > f_size:
        return None
    
    elif (chunk_number+1) * chunk_size > f_size:
        chunk_size = f_size - (chunk_number) * chunk_size 

    try:
        with open(filename,'r+b') as f:
            f.seek(chunk_size*chunk_number,0)
            chunk = str()

            with mmap.mmap(fileno=f.fileno(),length=chunk_size,access=mmap.ACCESS_READ) as mm:
                chunk = mm.read(chunk_size).hex()

            f.close()
            return chunk
    except Exception as e:
        logging.info(e)

def write_changes_to_file(offset,str_,str_len,filename):
    with open(filename,'wb') as of:
        of.seek(offset)
        with mmap.mmap(of.fileno(),length=str_len,access=mmap.ACCESS_WRITE) as mm:
            mm[:str_len] = str_
            mm.flush()
            