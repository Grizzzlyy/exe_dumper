import logging

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

def file_to_hex(file_path):
    """
    Reads a file and returns its contents in hexadecimal format.

    :param file_path: Path to the file to be read.
    :return: Hexadecimal representation of the file contents as a string.
    """
    try:
        with open(file_path, 'rb') as file:
            file_content = file.read()
            hex_output = file_content.hex()
            return hex_output
    except Exception as e:
        logging.info("file readed")

