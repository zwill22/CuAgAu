import os

import rundir


def main(*args):
    orca = ("B2PLYP-D3BJ", "TPSSh-D3BJ", "TPSS-D3BJ", "DSD-BLYP-D3BJ",
            "M06-D3", "wB97X-V", "wB97M-V")
    psi = ("GAM", "M11-D3BJ", "MN15-D3BJ", "SCAN-D3BJ")
    qcore = ('B3LYP-D3BJ', 'BLYP-D3BJ', 'B-LYP-osUW12-D3BJ', 'CAM-B3LYP-D3BJ',
             'PBE0-D3BJ', 'PBE-D3BJ', 'wB97X-D3', 'WM21-D3BJ',
             'XCH-BLYP-UW12-D3BJ')

    for xc in os.listdir():
        if not os.path.isdir(xc):
            continue

        if xc in ("__pycache__", ".git", ".idea"):
            continue

        print(xc)
        if xc in orca:
            program = "orca"
        elif xc in psi:
            program = "psi"
        elif xc in qcore:
            program = "qcore"
        else:
            raise ValueError("XC {} not in list".format(xc))

        rundir.main(program, xc, *args)


if __name__ == '__main__':
    import sys
    argv = sys.argv[1:]

    main(*argv)
