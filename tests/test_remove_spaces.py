from os import remove

from get_metars.__main__ import remove_white_spaces


def test_version():
    """Test remove white spaces, tabs and end of line from the report."""
    bad_reports = [
        "MRLB \n\n\n151922Z   17006KT 0500\tRA\t SCT005 BKN015 24/23 A2983\n",
        "MRLB               151916Z 24006KT           3000 0500NE RA SCT012 BKN025 \n\n\n24/23\nA2982",
        "MRLB 151900Z        28010KT\t\t\t\t\t9999 RA SCT020 BKN080 26/24 A2982",
        "MRLB 151800Z 21006KT 9999 -RA SCT025 BKN080 26/24 A2983\n\n\n\n           ",
        "MRLB 151700Z 13005KT 100V190 9999\t \t \t \t \tVCSH SCT020 BKN060 28/24 A2985",
        "MRLB 151600Z\n\t\t\t\t\n\n\n\t\n\t15005KT 090V200 9999 BKN020 27/24 A2986",
        "MRLB 151500Z 14006KT 100V170 9999           \t          SCT015 SCT080 26/24 A2985",
        "MRLB 151400Z 12006KT 090V160\t\n\t\n\t\n\t9999 FEW010 SCT080 25/24 A2983",
        "             MRLB 151300Z 10005KT 9999 FEW005 BKN040 23/23 A2983             ",
        "\n\n\n\nMRLB 151200Z 11004KT 9999 SCT005 BKN030 22/22 A2982\n\n\n\n\n",
        "\t\t\t\tMRLB 150600Z 0903KT 9999 SCT010 BKN100 23/23 A2985\t\t\t\t\t\t",
    ]

    good_reports = [
        "MRLB 151922Z 17006KT 0500 RA SCT005 BKN015 24/23 A2983",
        "MRLB 151916Z 24006KT 3000 0500NE RA SCT012 BKN025 24/23 A2982",
        "MRLB 151900Z 28010KT 9999 RA SCT020 BKN080 26/24 A2982",
        "MRLB 151800Z 21006KT 9999 -RA SCT025 BKN080 26/24 A2983",
        "MRLB 151700Z 13005KT 100V190 9999 VCSH SCT020 BKN060 28/24 A2985",
        "MRLB 151600Z 15005KT 090V200 9999 BKN020 27/24 A2986",
        "MRLB 151500Z 14006KT 100V170 9999 SCT015 SCT080 26/24 A2985",
        "MRLB 151400Z 12006KT 090V160 9999 FEW010 SCT080 25/24 A2983",
        "MRLB 151300Z 10005KT 9999 FEW005 BKN040 23/23 A2983",
        "MRLB 151200Z 11004KT 9999 SCT005 BKN030 22/22 A2982",
        "MRLB 150600Z 0903KT 9999 SCT010 BKN100 23/23 A2985",
    ]

    sanitized_reports = remove_white_spaces(bad_reports)
    assert sanitized_reports == good_reports
