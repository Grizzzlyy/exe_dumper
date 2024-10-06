"""
Format data for frontend
"""

from back.BD_interface import BD_int


def get_report_info(file_id):
    bd = BD_int()
    report = bd.get_report(file_id)

    # if report["filetype"] == "exe":
    #     json_fields = ['MS_DOS_header', 'PE_header', 'Import_table', 'Export_table']
    # else:
    #     json_fields = ['ELF_header', 'Segments', 'Sections', 'Symbols']
    # for
    return report
