import datetime


def get_report(username, repord_id):
    # Check user access to report. If no access, return None
    # Return report
    return {
        "filename": "binary1.exe",
        "type": "PE32+ executable(console) x86-64",
        "size": "420 kB",
        "md5": "xyz5",
        "sha1": "xyz1",
        "sha256": "xyz256",
        "sha512": "xyz512",
        "crc32": "xyz32",
        "ssdeep": "ssdeep string",
        "upload_time": datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"),
        "yara_matches": ["rule1", "rule3"],
        "children": ["157", "123"],
        "parents": ["90009"]
    }
