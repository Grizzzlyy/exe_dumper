def format_hex(hex_str):
    hex_lines = []
    bytes_per_line = 16

    for i in range(0, len(hex_str), bytes_per_line * 2):
        offset = f"{i // 2:08X}"
        hex_bytes = [hex_str[j:j+2] for j in range(i, min(i + bytes_per_line * 2, len(hex_str)), 2)]
        hex_section = ' '.join(hex_bytes)
        ascii_section = ''.join([chr(int(b, 16)) if 32 <= int(b, 16) <= 126 else '.' for b in hex_bytes])
        hex_lines.append(f"{offset}  {hex_section:<47}  {ascii_section}")

    return hex_lines

with open("file_content.txt", "r") as fp:
    hex_ = fp.read()
formatted_hex = format_hex(hex_)

pass