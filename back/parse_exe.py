import pefile
import binascii
import sys

def parse_ms_dos(pe):
    header_data = {}
    offsets_list = []

    for field in pe.DOS_HEADER.__keys__:
        field_value = getattr(pe.DOS_HEADER, field[0])
        offset = pe.DOS_HEADER.__file_offset__ + pe.DOS_HEADER.get_field_absolute_offset(field[0])

        offsets_list.append(offset)        #save offset to list to count field_len

        header_data[field[0]] = {
            'value': str(hex(field_value))[2:] if isinstance(field_value, int) else str(field_value),
            'offset': offset
        }

    offsets_list.append(pe.DOS_HEADER.sizeof()) #add ms dos size 
    idx = 0
    for field in header_data:
        field_length = offsets_list[idx+1] - offsets_list[idx] 
        header_data[field]['length'] = field_length

    return header_data

def parse_pe_header(pe):
    header_data = {}
    offsets_list = []

    header_data['Signature'] = {
            'value': str(hex(pe.NT_HEADERS.Signature))[2:],
            'offset': pe.NT_HEADERS.get_field_absolute_offset('Signature'),
            'length': 4
        }
    tmp_dict = {}
    for field in pe.FILE_HEADER.__keys__:
        field_value = getattr(pe.FILE_HEADER, field[0])
        offset = pe.FILE_HEADER.__file_offset__ + pe.FILE_HEADER.get_field_absolute_offset(field[0])

        offsets_list.append(offset)        #save offset to list to count field_len

        tmp_dict[field[0]] = {
            'value': str(hex(field_value))[2:] if isinstance(field_value, int) else str(field_value),
            'offset': offset
        }

    offsets_list.append(offsets_list[0] + pe.FILE_HEADER.sizeof()) #add header size 

    idx = 0
    for field in tmp_dict:
        field_length = offsets_list[idx+1] - offsets_list[idx] 
        tmp_dict[field]['length'] = field_length
    header_data |= tmp_dict
    return header_data

def parse_imports(pe):
    imports_data = {}
    length = 4
    if pe.FILE_HEADER.Machine == 0x8664:
        length = 8
    # Проверяем, есть ли импортируемые библиотеки
    if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
        for entry in pe.DIRECTORY_ENTRY_IMPORT:
            lib_name = entry.dll.decode('utf-8')  # Имя библиотеки (DLL)
            imports_data[lib_name] = []

            for imp in entry.imports:
                # Если функция имеет имя, вытаскиваем его
                if imp.name is not None:
                    func_name = imp.name.decode('utf-8')
                else:
                    # В случае если функции нет имени, импортируется через Ordinal
                    func_name = f'Ordinal{imp.ordinal}'

                # Получаем виртуальный адрес (RVA) функции
                function_rva = imp.address

                # Получаем смещение (offset) в файле на основе виртуального адреса (RVA)
                function_offset = pe.get_offset_from_rva(function_rva - pe.OPTIONAL_HEADER.ImageBase)

                # Сохраняем информацию о функции в словарь
                imports_data[lib_name].append({
                    'function': func_name,
                    'address': hex(function_rva),        # Виртуальный адрес
                    'offset': hex(function_offset),       # Смещение в файле
                    'length': length
                })
    
    return imports_data

def parse_exports(pe):
    exports_data = {}
    length = 4
    if pe.FILE_HEADER.Machine == 0x8664:
        length = 8
    # Проверяем, есть ли таблица экспортов
    if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
        # Получаем имя библиотеки, которая экспортирует функции
        lib_name = pe.get_string_at_rva(pe.DIRECTORY_ENTRY_EXPORT.struct.Name).decode('utf-8')
        exports_data[lib_name] = []

        # Перебираем все экспортируемые функции
        for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
            # Если функция имеет имя
            if exp.name:
                func_name = exp.name.decode('utf-8')
            else:
                # Если у функции нет имени, используем её порядковый номер (ordinal)
                func_name = f'Ordinal{exp.ordinal}'

            # Получаем виртуальный адрес (RVA) функции
            function_rva = exp.address

            # Получаем смещение (offset) в файле на основе виртуального адреса (RVA)
            function_offset = pe.get_offset_from_rva(function_rva)

            # Сохраняем информацию о функции в словарь
            exports_data[lib_name].append({
                'function': func_name,
                'address': hex(function_rva),        # Виртуальный адрес
                'offset': hex(function_offset),       # Смещение в файле
                'length': length
            })
    
    return exports_data

def parse(file_path):
    # Open PE file
    pe = pefile.PE(file_path)
    exe_data = {}
    parsed_imports = parse_imports(pe)
    parsed_exports = parse_exports(pe)
    parsed_ms_dos= parse_ms_dos(pe)
    parsed_pe_header = parse_pe_header(pe)

    return parsed_ms_dos, parsed_pe_header, parsed_exports, parsed_imports
   

