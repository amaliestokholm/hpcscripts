import numpy as np
from astropy.table import Table
from skycats import funkycat
from cattoys import laser

tablefiles = ["nebulacat_v0.42.txt"]
formats = ["ascii.ipac"]

step = 2000

def ready_table(tablefiles, formats=["ascii"], alphacorr=True, cols=None): 

    for tf, f in zip(tablefiles, formats):
        a = Table.read(tf, format=f)

        if alphacorr:
            feh = "FEH"
            alpha = "SI_FE"
            colname = "MH_ACORR"
            assert feh in a.columns
            assert alpha in a.columns
            meh_alpha_corr = laser.alphacorr_meh(a[feh], a[alpha])
            if colname in a.columns:
                a.remove_column(colname)
            a.add_column(meh_alpha_corr, name=colname)


        if cols is not None:
            a = a[cols]

        j = 0
        for i in range(step, len(a) + step, step):
            print(j, i)
            print(len(a[j:i]))
            a[j:i].write(
                tf.split(".")[0] + "_" + str(i // step) + ".dat",
                format="ascii.commented_header",
                delimiter=",",
                overwrite=True,
            )
            j += step

cols = [
        'SOURCE_ID_GAIA',
        'FEH',
        'SI_FE',
        'TEFF',
        'RA_GAIA',
        'DEC_GAIA',
        'PARALLAX_GAIA',
        'UNCORRECTED_PARALLAX_GAIA',
        'ERROR_PARALLAX_GAIA',
        'PHOT_BP_MEAN_MAG_GAIA',
        'ERROR_PHOT_BP_MEAN_MAG_GAIA',
        'PHOT_G_MEAN_MAG_GAIA',
        'ERROR_PHOT_G_MEAN_MAG_GAIA',
        'PHOT_RP_MEAN_MAG_GAIA',
        'ERROR_PHOT_RP_MEAN_MAG_GAIA',
        'WARNINGS_PARALLAXOFFSET_GAIA',
        'MH_ACORR',
        ]
ready_table(tablefiles, formats, cols=cols)
