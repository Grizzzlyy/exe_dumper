"""
Format data for frontend
"""

from back.BD_interface import BD_int


def get_report(file_id):
    bd = BD_int()
    report = bd.get_report(file_id)
    return report
