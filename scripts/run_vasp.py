#!/usr/bin/env python

"""
TODO: Change the module doc.
"""

from __future__ import division

__author__ = "shyuepingong"
__version__ = "0.1"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyuep@gmail.com"
__status__ = "Beta"
__date__ = "2/4/13"

import logging

from custodian.custodian import Custodian
from custodian.vasp.handlers import VaspErrorHandler, \
    UnconvergedErrorHandler, PoscarErrorHandler
from custodian.vasp.jobs import VaspJob


def do_run(args):
    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.INFO, filename="run.log")
    handlers = [VaspErrorHandler(), UnconvergedErrorHandler(),
                PoscarErrorHandler()]
    vasp_command = args.command.split()
    jobs = []
    njobs = len(args.jobs)
    for i, job_type in enumerate(args.jobs):
        final = False if i != njobs - 1 else True
        suffix = ".{}{}".format(job_type, i + 1)
        settings = None
        if i > 0:
            settings = [
                {"dict": "INCAR",
                 "action": {"_set": {"ISTART": 1}}},
                {"filename": "CONTCAR",
                 "action": {"_file_copy": {"dest": "POSCAR"}}}]
        gzip = True if args.gzip and i == njobs - 1 else False

        jobs.append(
            VaspJob(vasp_command, final=final, suffix=suffix,
                    settings_override=settings,
                    gzipped=gzip))

    c = Custodian(handlers, jobs, max_errors=10)
    c.run()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="""
    run_vasp.py is a master script to perform various kinds of VASP runs.
    """,
    epilog="""
    Author: Shyue Ping Ong
    Version: {}
    Last updated: {}""".format(__version__, __date__))

    parser.add_argument(
        "-c", "--command", dest="command", nargs="?",
        default="pvasp", type=str,
        help="VASP command. Defaults to pvasp. If you are using mpirun, "
             "set this to something like \"mpirun pvasp\".")

    parser.add_argument(
        "-z", "--gzip", dest="gzip", action="store_true",
        help="Add this option to gzip the final output. Do not gzip if you "
             "are going to perform an additional static run."
    )

    parser.add_argument("jobs", metavar="jobs", type=str, nargs='+',
                         default=["relax", "relax"],
                         help="Jobs to execute. Only sequences of relax "
                              "and static are supported at the moment. For "
                              "example, \"relax relax static\" will run a "
                              "double relaxation followed by a static run.")

    args = parser.parse_args()
    do_run(args)