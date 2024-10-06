elements = {
    "000000000": "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00",
    "000000020": "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00",
    "000000030": "00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00",
    "000000040": "ba 10 00 0e 1f b4 09 cd 21 b8 01 4c cd 21 90 90"
}


def create_to_color(offset, total_length):
    init_pos = offset % 16
    init_offset = f"{offset - init_pos :09X}"
    if total_length <= 16 - init_pos:
        init_len = total_length
    else:
        init_len = 16 - init_pos
    total_length -= init_len
    idx = 1

    to_color = [
        {"offset": init_offset,
         "pos": init_pos,
         "len": init_len}
    ]

    while total_length > 0:
        pos = 0
        offset = f"{int(to_color[idx - 1]['offset'], 16) + 16  :09X}"
        len = 16 if total_length >= 16 else total_length

        total_length -= len
        idx += 1

        to_color.append({"offset": offset,
                         "pos": pos,
                         "len": len})

    return to_color


def color_element(to_color_dict, element):
    bytes_ = element.split(" ")
    before_colored = ' '.join(bytes_[:row_dict["pos"]])
    after_colored = ' '.join(bytes_[row_dict["pos"] + row_dict["len"]:])
    colored = f"""<span style="background-color: yellow;">{" ".join(bytes_[row_dict["pos"]:row_dict["pos"] + row_dict["len"]])}</span>"""
    res = colored
    if before_colored != '':
        res = before_colored + ' '+ res
    if after_colored != '':
        res = res + ' ' + after_colored

    return res


if __name__ == "__main__":
    # Test data
    offset = 0x2
    total_length = 2

    to_color = create_to_color(offset, total_length)

    for row_dict in to_color:
        element = elements[row_dict["offset"]]
        colored_element = color_element(row_dict, element)
        print(colored_element)

    pass
