"""Document the modeled illuminant axis and the limits of the Dress claim."""
import argparse
from pathlib import Path
import numpy as np
from .spectral import CONES,planck_illuminant
from .analysis import TRANSFORM
from .common import atomic_json


def run(output):
    temperatures=np.linspace(3000,25000,221)
    spectra=np.stack([planck_illuminant(t) for t in temperatures])
    # Fixed 6500-K reference retains illumination changes; normalizing each
    # illuminant by its own white would erase the signal being analyzed.
    reference=planck_illuminant(6500) @ CONES.T
    coordinates=np.log(np.maximum(spectra @ CONES.T/reference,1e-12)) @ TRANSFORM.T
    chromatic=coordinates[:,1:]
    covariance=np.cov(chromatic,rowvar=False)
    values,vectors=np.linalg.eigh(covariance)
    record=dict(temperatures_kelvin=temperatures,spectra=spectra,log_lms_opponent_coordinates=coordinates,
        fixed_reference_lms=reference,chromatic_covariance=covariance,eigenvalues=values,eigenvectors=vectors,
        dominant_axis_degrees=float(np.rad2deg(np.arctan2(vectors[1,-1],vectors[0,-1]))%180),
        illuminants='Analytic unit-maximum Planck spectra, NOT measured daylight',
        dress_status='Not reproduced: original calibrated image, observer/readout definition, and original result artifacts unavailable.',
        interpretation='A model illuminant axis is descriptive. It does not establish why the model fails on the Dress or prove a missing illuminant prior.')
    root=Path(output)/'analysis';atomic_json(root/'E5g_daylight_limits.json',record)
    (root/'E5g_Findings.md').write_text('# Daylight-axis and Dress limits\n\nThe modeled Planck illuminant axis has been computed with a fixed 6500 K reference. These spectra are generated, not measured daylight.\n\nThe empirical Dress claim remains unverified because its calibrated stimulus, evaluation definition, and original numerical artifacts were not available. No cause is assigned to that unverified failure. Model-filter axes in E1 are separately converted to log-LMS coordinates; comparisons require the recorded reference scaling.\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();run(a.output)
