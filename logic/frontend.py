"""
Format data for frontend
"""

from back.BD_interface import BD_int


def get_report_info(file_id):
    bd = BD_int()
    report = bd.get_report(file_id)

    # Format output in headers
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
