"""
Format data for frontend
"""

import os

from back.BD_interface import BD_int


def get_report_info(file_id):
    bd = BD_int()
    report = bd.get_report(file_id)

    # Format output
    for k in ["header_first", "header_second"]:
        for elem in report[k]:
            new_elem = report[k][elem]

            # Get offset and position
            mask = 2 ** (4 * 9) - 16
            new_elem["g_offset"] = f"{new_elem['offset'] & mask :09X}"

            report[k][elem] = new_elem

    for k in ["import_table", "export_table"]:
        for dll in report[k]:
            for idx, func in enumerate(report[k][dll]):
                new_func = func

                # Get offset and position
                mask = 2 ** (4 * 9) - 16
                new_func["g_name_offset"] = f"{new_func['name_offset'] & mask :09X}"
                new_func['g_rva_offset_offset'] = f"{new_func['rva_offset_offset'] & mask :09X}"

                report[k][dll][idx] = new_func
    return report


def format_hex(chunk_idx, hex_str):
    offsets = []
    hex_lines = []
    decoded_text = []
    bytes_per_line = 16
    chunk_len = int(os.getenv("CHUNK_SIZE"))

    for i in range(0, len(hex_str), bytes_per_line * 2):
        offset = f"{i // 2 + chunk_len * chunk_idx:09X}"
        hex_bytes = [hex_str[j:j + 2] for j in range(i, min(i + bytes_per_line * 2, len(hex_str)), 2)]
        hex_section = ' '.join(hex_bytes)
        ascii_section = ''.join([chr(int(b, 16)) if 32 <= int(b, 16) <= 126 else '.' for b in hex_bytes])

        offsets.append(offset)
        hex_lines.append(hex_section)
        decoded_text.append(ascii_section)

    result = {
        "offsets": offsets,
        "hex_lines": hex_lines,
        "decoded_text": decoded_text
    }
    return result
