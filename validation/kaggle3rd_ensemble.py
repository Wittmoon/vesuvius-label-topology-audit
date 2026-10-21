"""Weighted ensemble of two nnU-Net probability outputs -> argmax tif (the 3rd-place kernel's 0.65/0.35 step).
usage: ensemble.py DIR_A W_A DIR_B W_B OUT   (reads <dir>/<crop>.npz 'probabilities', writes OUT/<crop>.tif uint8)
"""
import sys, os, glob, numpy as np, tifffile
a, wa, b, wb, out = sys.argv[1], float(sys.argv[2]), sys.argv[3], float(sys.argv[4]), sys.argv[5]
os.makedirs(out, exist_ok=True)
n = 0
for pa in sorted(glob.glob(os.path.join(a, '*.npz'))):
    crop = os.path.basename(pa)[:-4]
    pb = os.path.join(b, crop + '.npz')
    if not os.path.exists(pb):
        continue
    p = wa * np.load(pa)['probabilities'] + wb * np.load(pb)['probabilities']
    tifffile.imwrite(os.path.join(out, crop + '.tif'), np.argmax(p, axis=0).astype(np.uint8))
    np.savez_compressed(os.path.join(out, crop + '.npz'), probabilities=p.astype(np.float16))
    n += 1
print('ensembled', n)
