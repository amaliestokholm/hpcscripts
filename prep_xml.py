import argparse
import os
import subprocess
import h5py
import warnings
from basta.xml_create import generate_xml
from astropy.table import Table, join, vstack, unique, setdiff, Column
from astropy.utils.exceptions import AstropyWarning

warnings.filterwarnings("ignore", category=AstropyWarning)


parser = argparse.ArgumentParser()
parser.add_argument("--restart", type=int, required=True)
parser.add_argument("idstr", nargs="+", choices=[
     "equinox_mh",
     "equinox_feh",
     "equinox_fehalphacorr",
     "equinox_mh_floor",
     "equinox_feh_floor",
     "equinox_fehalphacorr_floor",
])
args = parser.parse_args()
restart = args.restart
assert restart == 2
idstrs = args.idstr

##############################################################################
# Make xmls
##############################################################################
###########################################################
# Control of input
# idstrs = [
#     #"equinox_mh",
#     #"equinox_feh",
#     #"equinox_fehalphacorr",
#     #"equinox_mh_floor",
#     "equinox_feh_floor",
#     #"equinox_fehalphacorr_floor",
# ]

# restart = 2

for idstr in idstrs:
    if idstr == "equinox_mh":
        # Here you can vary different things based on your idstr
        date = "20230312"
        # Name of input ascii file
        # Values of the following parameters:
        # Overshooting, Diffusion, mass-loss (Eta), Alpha-enhancement
        odea = (0.0, 0.0, 0.0, 0.0)
    elif idstr == "equinox_feh":
        # Here you can vary different things based on your idstr
        date = "20230312"
        # Name of input ascii file
        odea = (0.0, 0.0, 0.0, 0.0)
    elif idstr == "equinox_fehalphacorr":
        # Here you can vary different things based on your idstr
        date = "20230312"
        # Name of input ascii file
        odea = (0.0, 0.0, 0.0, 0.0)
    elif idstr == "equinox_mh_floor":
        # Here you can vary different things based on your idstr
        date = "20230312"
        # Name of input ascii file
        # Values of the following parameters:
        # Overshooting, Diffusion, mass-loss (Eta), Alpha-enhancement
        odea = (0.0, 0.0, 0.0, 0.0)
    elif idstr == "equinox_feh_floor":
        # Here you can vary different things based on your idstr
        date = "20230312"
        # Name of input ascii file
        odea = (0.0, 0.0, 0.0, 0.0)
    elif idstr == "equinox_fehalphacorr_floor":
        # Here you can vary different things based on your idstr
        date = "20230312"
        # Name of input ascii file
        odea = (0.0, 0.0, 0.0, 0.0)
    else:
        print("wrong")
        raise SystemExit

    # Name of grid input file
    # gridfile = "/home/amalie/BASTA/grids/BaSTI_iso2018.hdf5"
    gridfile = "/scratch/extra/andrea.miglio/amalie.stokholm/grids/BaSTI_iso2018.hdf5"

    # Name of solar model contained in grid
    solarmodel = True

    frame = "icrs"

    missingval = -9999

    ###########################################################
    # Control of output
    # Path of output directory, from current location
    # If it is not there, it will be generated
    # Name of outputfile
    outputfile = "stars_result.ascii"

    cornerplots = ("Teff", "dnufit", "radTot", "age", "massfin")
    kielplots = False
    noplots = True

    ###########################################################
    # Control of fit
    # Use SYD values for APOKASC and APOK2
    priors = {
        "IMF": "salpeter1955",
        "Teff": {"abstol": "300"},
    }
    solarnumax = 3090
    solardnu = 135.1

    prefix = [
        idstr + "_BASTA",
    ]

    CASES = (
        "01",
        "02",
    )

    xmllocation = f"./xmlinput/{idstr}/"
    if restart:
        for case in CASES:
            donefile = f"./results/{idstr}/done_case{case}_before_{restart}.txt"
            if os.path.exists(donefile):
                raise Exception("Already exists: %s" % (donefile,))
            if restart == 2:
                # restart 2: rerun those with nans.
                # in other words, "good" means "not nan"
                subprocess.check_call(
                    f"grep -hv -e starid -e nan results/combined_{idstr}_case_{case}.ascii | cut -d' ' -f1 > results/{idstr}/done_case{case}_before_{restart}.txt",
                    shell=True,
                )
            else:
                # restart 1: rerun those that didn't have an output.
                # in other words, "good" means "in the file".
                subprocess.check_call(
                    f"grep -hv starid case_{case}/*/results.ascii | cut -d' ' -f1 > done_case{case}_before_{restart}.txt",
                    shell=True,
                    cwd=f"./results/{idstr}",
                )
            sz = os.stat(donefile).st_size
            if sz == 0:
                raise Exception("Done file is empty? %s" % (donefile,))
        subprocess.check_call("wc done_*", shell=True, cwd=f"./results/{idstr}")

        restartlocation = os.path.join(
            os.path.join(xmllocation, f"done_before_{restart}/")
        )
        # Move current xml-files to back-up location
        if not os.path.exists(restartlocation):
            os.mkdir(restartlocation)
        for f in os.listdir(xmllocation):
            if f.endswith(".xml"):
                os.rename(
                    os.path.join(xmllocation, f),
                    os.path.join(restartlocation, f),
                )

    for case in CASES:
        print(case)
        bayweights = True

        outparams = (
            "massfin",
            "radPhot",
            "rho",
            "logg",
            "age",
            "LPhot",
            "Teff",
            "FeH",
            "MeH",
            "dnuSer",
            "numax",
        )

        plotparams = [
            "age",
            "radPhot",
            "massini",
            "Teff",
            "FeH",
            "MeH",
            "LPhot",
            "dnuSer",
            "numax",
            "logg",
        ]
        """
        inputparams = (
                'ticid',
                'starid',
                'ra', 'dec',
                'parallax', 'parallax_err',
                'G_GAIA', 'G_GAIA_err',
                'numax', 'numax_err',
                'Teff', 'Teff_err',
                'FeH', 'FeH_err',
                )
        """
        if case == "01":
            # 1: teff/feh/numax
            # Parameters as ordered in the input ascii file
            fitparams = tuple(["Teff", "FeH", "numax"])
            filters = ()
            inputparams = (
                "starid",
                "sourceid",
                "RA",
                "RA_err",
                "DEC",
                "DEC_err",
                "parallax",
                "parallax_err",
                "G_GAIA",
                "G_GAIA_err",
                "numax",
                "numax_err",
                "Teff",
                "Teff_err",
                "FeH",
                "FeH_err",
            )
        elif case == "02":
            # 2: teff/feh/numax/gmag
            # Parameters as ordered in the input ascii file
            fitparams = tuple(
                [
                    "Teff",
                    "FeH",
                    "numax",
                    "parallax",
                ]
            )
            plotparams.append("distance")
            filters = "G_GAIA"
            inputparams = (
                "starid",
                "sourceid",
                "RA",
                "RA_err",
                "DEC",
                "DEC_err",
                "parallax",
                "parallax_err",
                "G_GAIA",
                "G_GAIA_err",
                "numax",
                "numax_err",
                "Teff",
                "Teff_err",
                "FeH",
                "FeH_err",
            )
        plotparams = tuple(plotparams)
        optionaloutputs = False
        datadir = f"./data/{idstr}"
        outpath = "/home/work/astro/amalie.stokholm/equinox/results/"

        for i, asciifile in enumerate(os.listdir(datadir)):
            if asciifile.endswith(".dat"):
                asciifile = os.path.join(datadir, asciifile)
                outputfile = "results.ascii"
                outputpath = os.path.join(outpath, f"{idstr}/case_{case}/{i}/")

                if restart:
                    donefile = f"./results/{idstr}/done_case{case}_before_{restart}.txt"
                    outputfile = f"results_before_{restart}.ascii"
                    assert os.path.isfile(donefile)
                else:
                    donefile = None

                if not os.path.exists(outputpath):
                    print(f"Makes {outputpath}")
                    os.mkdir(outputpath)

                if noplots:
                    xml = generate_xml(
                        gridfile=gridfile,
                        asciifile=asciifile,
                        outputpath=outputpath,
                        odea=odea,
                        params=inputparams,
                        fitparams=fitparams,
                        outparams=outparams,
                        missingval=missingval,
                        priors=priors,
                        bayweights=bayweights,
                        optionaloutputs=optionaloutputs,
                        outputfile=outputfile,
                        dustframe=frame,
                        filters=filters,
                        solarmodel=True,
                        sunnumax=solarnumax,
                        sundnu=solardnu,
                        delimiter=",",
                        donefile=donefile,
                    )
                else:
                    xml = generate_xml(
                        gridfile=gridfile,
                        asciifile=asciifile,
                        outputpath=outputpath,
                        odea=odea,
                        params=inputparams,
                        fitparams=fitparams,
                        outparams=outparams,
                        missingval=missingval,
                        priors=priors,
                        bayweights=bayweights,
                        optionaloutputs=optionaloutputs,
                        outputfile=outputfile,
                        kielplots=kielplots,
                        cornerplots=plotparams,
                        dustframe=frame,
                        filters=filters,
                        solarmodel=True,
                        sunnumax=solarnumax,
                        sundnu=solardnu,
                        delimiter=",",
                        donefile=donefile,
                    )

                xmlfile = os.path.join(
                    xmllocation, f"{prefix[0]}_{date}_case{str(case)}{i}.xml"
                )
                with open(xmlfile, "w") as inpfile:
                    print(xml, file=inpfile)
