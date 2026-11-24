"""Versioned MPS extension; initialization and analysis remain on CPU."""
import os

# Training backend is explicit in each configuration; never infer CUDA use.
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['DEVICE'] = 'cpu'
for _name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
              'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_name] = os.environ.get('REVISION_THREADS', '2')
os.environ['MPLBACKEND'] = 'Agg'
