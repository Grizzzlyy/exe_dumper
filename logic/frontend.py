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

    k = "import_table"
    for elem in report[k]:
        new_elem = report[k][elem]

        # Get offset and position
        mask = 2 ** (4 * 9) - 16
        new_elem["g_offset"] = f"{new_elem['offset'] & mask :09X}"

        report[k][elem] = new_elem




    return report
