#!/usr/bin/env python3
import argparse
import datetime
import os
import subprocess


CASES = "feh feh_floor fehalphacorr fehalphacorr_floor mh mh_floor".split()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=CASES)
    args = parser.parse_args()
    fitparams = "_" + args.case

    job_id = os.environ["SLURM_JOB_ID"]
    print(
        f"========= Job started at {datetime.datetime.now()} on {os.uname().nodename} =========="
    )
    print()
    print(f"Job id       : {job_id}")
    print()

    # Settings
    project_name = "equinox"
    scratch_home = "/scratch/extra/andrea.miglio/amalie.stokholm"
    personal_home = "/home/PERSONALE/amalie.stokholm"
    work_home = "/home/work/astro/amalie.stokholm"
    project_home = f"{work_home}/{project_name}"
    xml_dir = f"{project_home}/xmlinput/{project_name}{fitparams}"
    venv_name = "venv"
    options = []

    # Do the things
    activate_script = f"{os.environ['BASTADIR']}/{venv_name}/bin/activate"
    jobtitle = project_name + fitparams
    print("Job title:", jobtitle)
    subprocess.check_call(("scontrol", "update", "job", job_id, "JobName=" + jobtitle))
    parallel = os.environ.get("SLURM_CPUS_PER_TASK", 1)
    subprocess.check_call(
        [
            "bash",
            "-c",
            f'source {activate_script} && BASTAmultirun "$@"',
            "--",
            *options,
            "--parallel",
            parallel,
            xml_dir + "/",
        ],
        cwd=project_home,
    )
    print(f"========= Job finished at {datetime.datetime.now()} ==========")


if __name__ == "__main__":
    main()
