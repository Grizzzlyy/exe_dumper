import sys
import binascii
import json
import lief
ELF_HEADER_FIELDS_64 = [
    {"name": "EI_MAG", "size": 4, "description": "Magic number"},
    {"name": "EI_CLASS", "size": 1, "description": "File class"},
    {"name": "EI_DATA", "size": 1, "description": "Data encoding"},
    {"name": "EI_VERSION", "size": 1, "description": "File version"},
    {"name": "EI_OSABI", "size": 1, "description": "OS/ABI identification"},
    {"name": "EI_ABIVERSION", "size": 1, "description": "ABI version"},
    {"name": "EI_PAD", "size": 7, "description": "Padding bytes"},
    {"name": "e_type", "size": 2, "description": "Object file type"},
    {"name": "e_machine", "size": 2, "description": "Architecture"},
    {"name": "e_version", "size": 4, "description": "Object file version"},
    {"name": "e_entry", "size": 8, "description": "Entry point address"},
    {"name": "e_phoff", "size": 8, "description": "Program header table file offset"},
    {"name": "e_shoff", "size": 8, "description": "Section header table file offset"},
    {"name": "e_flags", "size": 4, "description": "Processor-specific flags"},
    {"name": "e_ehsize", "size": 2, "description": "ELF header size in bytes"},
    {"name": "e_phentsize", "size": 2, "description": "Program header table entry size"},
    {"name": "e_phnum", "size": 2, "description": "Program header table entry count"},
    {"name": "e_shentsize", "size": 2, "description": "Section header table entry size"},
    {"name": "e_shnum", "size": 2, "description": "Section header table entry count"},
    {"name": "e_shstrndx", "size": 2, "description": "Section header string table index"},
]

ELF_HEADER_FIELDS_32 = [
    {"name": "EI_MAG", "size": 4, "description": "Magic number"},
    {"name": "EI_CLASS", "size": 1, "description": "File class"},
    {"name": "EI_DATA", "size": 1, "description": "Data encoding"},
    {"name": "EI_VERSION", "size": 1, "description": "File version"},
    {"name": "EI_OSABI", "size": 1, "description": "OS/ABI identification"},
    {"name": "EI_ABIVERSION", "size": 1, "description": "ABI version"},
    {"name": "EI_PAD", "size": 7, "description": "Padding bytes"},
    {"name": "e_type", "size": 2, "description": "Object file type"},
    {"name": "e_machine", "size": 2, "description": "Architecture"},
    {"name": "e_version", "size": 4, "description": "Object file version"},
    {"name": "e_entry", "size": 4, "description": "Entry point address"},
    {"name": "e_phoff", "size": 4, "description": "Program header table file offset"},
    {"name": "e_shoff", "size": 4, "description": "Section header table file offset"},
    {"name": "e_flags", "size": 4, "description": "Processor-specific flags"},
    {"name": "e_ehsize", "size": 2, "description": "ELF header size in bytes"},
    {"name": "e_phentsize", "size": 2, "description": "Program header table entry size"},
    {"name": "e_phnum", "size": 2, "description": "Program header table entry count"},
    {"name": "e_shentsize", "size": 2, "description": "Section header table entry size"},
    {"name": "e_shnum", "size": 2, "description": "Section header table entry count"},
    {"name": "e_shstrndx", "size": 2, "description": "Section header string table index"},
]

def parse_elf_header(file_path):
    binary  = lief.parse(file_path)
    exe_data = {}
    segments={}
    sections={}
    symbols={}

    offsets_list = []
    for i in range(len(binary.segments)):
        segments["Segment"+str(i)] = {
                    'vaddr': binary.segments[i].virtual_address,
                    'offset': binary.segments[i].file_offset,
                    'virtual_size': binary.segments[i].virtual_size,
                    'physical_size': binary.segments[i].physical_size
                }
    for i in range(len(binary.sections)):
        sections[binary.sections[i].name] = {
                    'type': str(binary.sections[i].type).split(".")[-1],
                    'vaddr': binary.sections[i].virtual_address,
                    'offset': binary.sections[i].file_offset,
                    'size': binary.sections[i].size

                }
    for i in range(len(binary.symbols)):
        symbols[binary.symbols[i].name] = {
                    'type': str(binary.symbols[i].type).split(".")[-1],
                    'vaddr': binary.symbols[i].value,
                    'size': binary.symbols[i].size,
                    'exported': binary.symbols[i].exported,
                    'imported': binary.symbols[i].imported

                }
    try:
        with open(file_path, 'rb') as f:

            f.seek(0)
            raw_header = f.read(64)
            is_64bit = raw_header[4]==2
            
            endian = 'little' if raw_header[5] == 1 else 'big'
            
            if is_64bit:
                header_fields = ELF_HEADER_FIELDS_64
            else:
                header_fields = ELF_HEADER_FIELDS_32
            
            
            
            current_offset = 0
            for field in header_fields:
                field_name = field['name']
                field_size = field['size']
                
                field_bytes = raw_header[current_offset:current_offset + field_size]
                
                if field_name.startswith("EI_MAG") or field_name.startswith("EI_PAD"):
                    field_value = field_bytes.hex(" ")
                else:
                    field_value = int.from_bytes(field_bytes, byteorder=endian)
                
                exe_data[field_name] = {
                    'value': field_value,
                    'offset': current_offset,
                    'length': field_size
                }
                
                offsets_list.append(current_offset)
                current_offset += field_size
            
            for idx, field in enumerate(header_fields):
                field_name = field['name']
                if idx < len(header_fields) - 1:
                    field_length = header_fields[idx + 1]['size']
                else:
                    field_length = header_fields[idx]['size']
                exe_data[field_name]['length'] = field['size']
            
        return exe_data,segments,sections,symbols
    
    except ELFError as e:
        print(f"Error parsing ELF file: {e}")
        return None
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
def binary_substitute(file_content, offset,length,hex_str):
    file_list=list(file_content)
    sub_list=list(bytes.fromhex(hex_str))
    file_list[offset:offset+length]=sub_list
    return bytes(file_list)

def parse_elf_as_hex(file_path):
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
        hex_data = binascii.hexlify(file_content).decode('utf-8')
        return hex_data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error reading file as hex: {e}")
        return None
