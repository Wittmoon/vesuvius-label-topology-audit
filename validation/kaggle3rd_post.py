import os
import numpy as np
from skimage.morphology import (
    ball,
    disk,
    binary_closing,
    remove_small_objects,
    remove_small_holes,
)
import pandas as pd
import tifffile
from pathlib import Path
from typing import Optional, Union, Literal, List
import matplotlib.pyplot as plt
from tqdm import tqdm

import numpy as np
from skimage.morphology import (
    remove_small_objects,
    remove_small_holes,
    binary_closing,
    disk,
)

import numpy as np
from skimage.morphology import (
    remove_small_objects,
    remove_small_holes,
    binary_closing,
    disk,
)

def prune_isolated_z(pred_bin: np.ndarray) -> np.ndarray:
    Z = pred_bin.shape[0]
    keep = np.zeros_like(pred_bin, dtype=bool)

    for z in range(1, Z - 1):
        keep[z] = pred_bin[z] & (pred_bin[z - 1] | pred_bin[z + 1])

    return keep


def topo_postprocess_volume(
    pred_volume: np.ndarray,
    min_component_size: int = 2000,
    closing_radius_xy: int = 1,
    hole_area_threshold_2d: int = 64,
    hole_area_threshold_3d: int = 64,
) -> np.ndarray:

    # --- 0. binarize ---
    pred_bin = pred_volume > 0

    # --- 1. remove tiny 3D blobs ---
    pred_bin = remove_small_objects(pred_bin, min_size=min_component_size)

    # --- 2. strong 2D morphology per slice ---
    se2d = disk(closing_radius_xy)
    for z in range(pred_bin.shape[0]):
        pred_bin[z] = binary_closing(pred_bin[z], se2d)
        # pred_bin[z] = remove_small_holes(
        #     pred_bin[z], area_threshold=hole_area_threshold_2d
        # )

    # --- 3. Z-consistency pruning (CRITICAL) ---
    pred_bin = prune_isolated_z(pred_bin)

    # --- 4. anisotropic 3D closing (XY only) ---
    se3d = np.zeros((1, 3, 3), dtype=bool)
    se3d[0, :, :] = True
    pred_bin = binary_closing(pred_bin, se3d)

    # --- 5. conservative 3D hole filling ---
    # pred_bin = remove_small_holes(
    #     pred_bin, area_threshold=hole_area_threshold_3d
    # )

    return pred_bin.astype(np.uint8)

    

    
from typing import Mapping, Tuple

import numpy as np

DEFAULT_TARGET_DTYPE = np.float32
EPS = 1e-8

__all__ = [
    "normalize_minmax",
    "normalize_zscore",
    "normalize_ct",
    "normalize_robust",
    "DEFAULT_TARGET_DTYPE",
    "NORMALIZATION_FUNCTIONS",
]


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _prepare_image(image: np.ndarray, target_dtype: np.dtype | type = DEFAULT_TARGET_DTYPE) -> np.ndarray:
    arr = np.asarray(image)
    if target_dtype is not None:
        arr = arr.astype(target_dtype, copy=False)
    return arr


def _prepare_mask(mask: np.ndarray, image_shape: Tuple[int, ...]) -> np.ndarray:
    """
    Broadcast the provided mask to match the image shape, ensuring boolean dtype.
    Raises ValueError when broadcasting is impossible.
    """
    mask_arr = np.asarray(mask)
    if mask_arr.ndim > len(image_shape):
        raise ValueError(
            f"Mask with shape {mask_arr.shape} has higher dimensionality than image shape {image_shape}"
        )

    if mask_arr.ndim < len(image_shape):
        expand_dims = (1,) * (len(image_shape) - mask_arr.ndim)
        mask_arr = mask_arr.reshape(expand_dims + mask_arr.shape)

    try:
        broadcast = np.broadcast_to(mask_arr, image_shape, subok=True)
    except ValueError as exc:
        raise ValueError(
            f"Mask with shape {mask_arr.shape} cannot broadcast to image shape {image_shape}"
        ) from exc

    return broadcast.astype(bool, copy=False)


def _select_valid_region(
    image: np.ndarray,
    mask: np.ndarray | None,
    use_mask: bool,
) -> Tuple[np.ndarray, np.ndarray | None]:
    """
    Return the flattened view of valid pixels and the boolean mask used.

    When no valid mask pixels exist, the full image is returned and mask_bool is None.
    """
    if use_mask and mask is not None:
        mask_bool = _prepare_mask(mask, image.shape)
        if np.any(mask_bool):
            return image[mask_bool], mask_bool
    return image.reshape(-1), None


# --------------------------------------------------------------------------- #
# Normalisation functions
# --------------------------------------------------------------------------- #

def normalize_minmax(
    image: np.ndarray,
    *,
    target_dtype: np.dtype | type = DEFAULT_TARGET_DTYPE,
) -> np.ndarray:
    """
    Min-max normalisation that rescales intensities into the [0, 1] range.
    """
    arr = _prepare_image(image, target_dtype)
    min_val = float(arr.min())
    max_val = float(arr.max())

    if max_val > min_val:
        arr -= min_val
        arr /= max(max_val - min_val, EPS)
    else:
        arr.fill(0.0)

    return arr


def normalize_zscore(
    image: np.ndarray,
    *,
    mask: np.ndarray | None = None,
    use_mask: bool = False,
    target_dtype: np.dtype | type = DEFAULT_TARGET_DTYPE,
) -> np.ndarray:
    """
    Standard score normalisation (z-score).

    Parameters
    ----------
    image : np.ndarray
        Input image.
    mask : np.ndarray, optional
        Optional mask restricting the statistics to masked pixels.
    use_mask : bool
        When true and mask is provided, restrict mean/std computation to masked region.
    """
    arr = _prepare_image(image, target_dtype)
    valid, mask_bool = _select_valid_region(arr, mask, use_mask)

    mean = float(valid.mean()) if valid.size else 0.0
    std = float(valid.std()) if valid.size else 0.0
    std = max(std, EPS)

    if mask_bool is not None:
        arr_masked = arr[mask_bool]
        arr_masked -= mean
        arr_masked /= std
        arr[mask_bool] = arr_masked
    else:
        arr -= mean
        arr /= std

    return arr


def normalize_ct(
    image: np.ndarray,
    *,
    intensity_properties: Mapping[str, float] | None,
    target_dtype: np.dtype | type = DEFAULT_TARGET_DTYPE,
) -> np.ndarray:
    """
    CT-style normalisation using global percentiles, mean, and standard deviation.
    """
    if intensity_properties is None:
        raise ValueError("normalize_ct requires intensity_properties")

    required_keys = ("mean", "std", "percentile_00_5", "percentile_99_5")
    missing = [key for key in required_keys if key not in intensity_properties]
    if missing:
        raise ValueError(
            f"normalize_ct missing intensity properties: {missing}. "
            f"Provided keys: {list(intensity_properties.keys())}"
        )

    arr = _prepare_image(image, target_dtype)
    mean_intensity = float(intensity_properties["mean"])
    std_intensity = max(float(intensity_properties["std"]), EPS)
    lower_bound = float(intensity_properties["percentile_00_5"])
    upper_bound = float(intensity_properties["percentile_99_5"])

    np.clip(arr, lower_bound, upper_bound, out=arr)
    arr -= mean_intensity
    arr /= std_intensity

    return arr


def normalize_robust(
    image: np.ndarray,
    *,
    mask: np.ndarray | None = None,
    use_mask: bool = False,
    percentile_lower: float = 1.0,
    percentile_upper: float = 99.0,
    clip_values: bool = True,
    target_dtype: np.dtype | type = DEFAULT_TARGET_DTYPE,
) -> np.ndarray:
    """
    Robust normalisation based on the median and MAD (Median Absolute Deviation).
    """
    arr = _prepare_image(image, target_dtype)
    valid, mask_bool = _select_valid_region(arr, mask, use_mask)

    if valid.size == 0:
        return arr

    std_preclip = float(np.std(valid))
    min_preclip = float(np.min(valid))
    max_preclip = float(np.max(valid))

    lower_val = upper_val = None
    if clip_values and valid.size > 0:
        lower_val = float(np.percentile(valid, percentile_lower))
        upper_val = float(np.percentile(valid, percentile_upper))
        np.clip(arr, lower_val, upper_val, out=arr)
        valid, mask_bool = _select_valid_region(arr, mask, use_mask)
        if valid.size == 0:
            return arr

    median = float(np.median(valid))
    mad = float(np.median(np.abs(valid - median)))
    scaled_mad = 1.4826 * mad

    if not np.isfinite(scaled_mad) or scaled_mad < 1e-6:
        percentile_span = None
        if lower_val is not None and upper_val is not None:
            percentile_span = upper_val - lower_val
        else:
            percentile_span = max_preclip - min_preclip

        fallback_values = []
        if np.isfinite(std_preclip):
            fallback_values.append(abs(std_preclip))
        if percentile_span is not None and np.isfinite(percentile_span):
            fallback_values.append(abs(percentile_span) / 2.0)

        scaled_mad = next(
            (candidate for candidate in fallback_values if candidate >= 1e-6),
            None,
        )

        if scaled_mad is None or not np.isfinite(scaled_mad):
            scaled_mad = 1.0

    if mask_bool is not None:
        arr_masked = arr[mask_bool]
        arr_masked -= median
        arr_masked /= scaled_mad
        arr[mask_bool] = arr_masked
    else:
        arr -= median
        arr /= scaled_mad

    np.nan_to_num(arr, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
    return arr


def _normalize_identity(
    image: np.ndarray,
    *,
    target_dtype: np.dtype | type = DEFAULT_TARGET_DTYPE,
    **_: object,
) -> np.ndarray:
    """No-op normalisation helper."""
    arr = _prepare_image(image, target_dtype)
    return arr


NORMALIZATION_FUNCTIONS = {
    "zscore": normalize_zscore,
    "ct": normalize_ct,
    "rescale_to_01": normalize_minmax,
    "minmax": normalize_minmax,
    "robust": normalize_robust,
    "none": _normalize_identity,
}

import numpy as np
from numpy import linalg as LA


def divide_nonzero(array1, array2, eps=1e-10):
    denominator = np.copy(array2)
    denominator[denominator == 0] = eps
    return np.divide(array1, denominator)

import numpy as np
from scipy.ndimage.filters import gaussian_filter

def hessian_curvature_2d(image, gauss_sigma=2, sigma=6):
    image_smoothed = gaussian_filter(image, sigma=gauss_sigma)
    image_smoothed = normalize_minmax(image_smoothed)

    joint_hessian = np.zeros((image.shape[0], image.shape[1], 2, 2), dtype=float)

    Dy = np.gradient(image_smoothed, axis=0, edge_order=2)
    joint_hessian[:, :, 1, 1] = np.gradient(Dy, axis=0, edge_order=2)
    joint_hessian[:, :, 0, 1] = np.gradient(Dy, axis=1, edge_order=2)
    del Dy

    Dx = np.gradient(image_smoothed, axis=1, edge_order=2)
    joint_hessian[:, :, 0, 0] = np.gradient(Dx, axis=1, edge_order=2)
    joint_hessian[:, :, 1, 0] = joint_hessian[:, :, 0, 1]
    del Dx

    joint_hessian = joint_hessian * (sigma ** 2)
    zero_mask = np.trace(joint_hessian, axis1=2, axis2=3) == 0
    return joint_hessian, zero_mask


def hessian_curvature_3d(volume, gauss_sigma=2, sigma=6):
    volume_smoothed = gaussian_filter(volume, sigma=gauss_sigma)
    volume_smoothed = normalize_minmax(volume_smoothed)

    joint_hessian = np.zeros((volume.shape[0], volume.shape[1], volume.shape[2], 3, 3), dtype=float)

    Dz = np.gradient(volume_smoothed, axis=0, edge_order=2)
    joint_hessian[:, :, :, 2, 2] = np.gradient(Dz, axis=0, edge_order=2)
    del Dz

    Dy = np.gradient(volume_smoothed, axis=1, edge_order=2)
    joint_hessian[:, :, :, 1, 1] = np.gradient(Dy, axis=1, edge_order=2)
    joint_hessian[:, :, :, 1, 2] = np.gradient(Dy, axis=0, edge_order=2)
    del Dy

    Dx = np.gradient(volume_smoothed, axis=2, edge_order=2)
    joint_hessian[:, :, :, 0, 0] = np.gradient(Dx, axis=2, edge_order=2)
    joint_hessian[:, :, :, 0, 1] = np.gradient(Dx, axis=1, edge_order=2)
    joint_hessian[:, :, :, 0, 2] = np.gradient(Dx, axis=0, edge_order=2)
    del Dx

    joint_hessian = joint_hessian * (sigma ** 2)
    zero_mask = np.trace(joint_hessian, axis1=3, axis2=4) == 0
    return joint_hessian, zero_mask

def detect_ridges_2d(image, gamma=1.5, beta=0.5, gauss_sigma=2, sigma=6):
    joint_hessian, zero_mask = hessian_curvature_2d(image, gauss_sigma, sigma)
    eigvals = LA.eigvalsh(joint_hessian, 'U')
    idxs = np.argsort(np.abs(eigvals), axis=-1)
    eigvals = np.take_along_axis(eigvals, idxs, axis=-1)
    eigvals[zero_mask, :] = 0

    L1 = np.abs(eigvals[:, :, 0])
    L2 = eigvals[:, :, 1]
    L2abs = np.abs(L2)

    S = np.sqrt(np.square(eigvals).sum(axis=-1))
    background_term = 1 - np.exp(-0.5 * np.square(S / gamma))

    Rb = divide_nonzero(L1, L2abs)
    blob_term = np.exp(-0.5 * np.square(Rb / beta))

    ridges = background_term * blob_term
    ridges[L2 > 0] = 0
    return ridges

def detect_ridges_3d(volume, gamma=1.5, beta1=0.5, beta2=0.5, gauss_sigma=2, sigma=6):
    joint_hessian, zero_mask = hessian_curvature_3d(volume, gauss_sigma, sigma)
    eigvals = LA.eigvalsh(joint_hessian, 'U')
    idxs = np.argsort(np.abs(eigvals), axis=-1)
    eigvals = np.take_along_axis(eigvals, idxs, axis=-1)
    eigvals[zero_mask, :] = 0

    L1 = np.abs(eigvals[:, :, :, 0])
    L2 = np.abs(eigvals[:, :, :, 1])
    L3 = eigvals[:, :, :, 2]
    L3abs = np.abs(L3)

    S = np.sqrt(np.square(eigvals).sum(axis=-1))
    background_term = 1 - np.exp(-0.5 * np.square(S / gamma))

    Ra = divide_nonzero(L2, L3abs)
    planar_term = np.exp(-0.5 * np.square(Ra / beta1))

    Rb = divide_nonzero(L1, np.sqrt(L2 * L3abs))
    blob_term = np.exp(-0.5 * np.square(Rb / beta2))

    ridges = background_term * planar_term * blob_term
    ridges[L3 > 0] = 0
    return ridges

#!/usr/bin/env python
import os
import glob
import argparse
import multiprocessing

import numpy as np
import tifffile
from tqdm import tqdm

from scipy.ndimage import distance_transform_edt
import numpy as np

def dilate_by_inverse_edt(binary_volume, dilation_distance):
    eps = 1e-6
    edt = distance_transform_edt(1 - binary_volume)
    inv_edt = 1.0 / (edt + eps)
    threshold = 1.0 / dilation_distance
    dilated = (inv_edt > threshold).astype(np.uint8)
    return dilated
    



def process_file(file_path, output_folder, dilation_distance=3, ridge_threshold=0.5):
    try:
        volume = tifffile.imread(file_path)
        
        # Check if input is 2D or 3D
        if volume.ndim == 2:
            # 2D processing
            binary_volume = (volume > 0).astype(np.uint8)
            dilated_volume = dilate_by_inverse_edt(binary_volume, dilation_distance)
            dilated_float = dilated_volume.astype(np.float32)
            ridges = detect_ridges_2d(dilated_float)
            binary_ridges = (ridges > ridge_threshold).astype(np.uint8)
        elif volume.ndim == 3:
            # 3D processing
            binary_volume = (volume > 0).astype(np.uint8)
            dilated_volume = dilate_by_inverse_edt(binary_volume, dilation_distance)
            dilated_float = dilated_volume.astype(np.float32)
            ridges = detect_ridges_3d(dilated_float)
            binary_ridges = (ridges > ridge_threshold).astype(np.uint8)
        else:
            raise ValueError(f"Unsupported image dimensions: {volume.ndim}. Only 2D and 3D images are supported.")
        binary_ridges = topo_postprocess_volume(binary_ridges)
        filename = os.path.basename(file_path)
        output_path = os.path.join(output_folder, filename)
        tifffile.imwrite(output_path, binary_ridges, compression='packbits')
        return file_path, True
    except Exception as e:
        return file_path, False, str(e)


# Define a top-level worker function to avoid lambda pickling issues
def worker(args):
    return process_file(*args)


# ---------------------------
# Main Routine Using Multiprocessing and tqdm
# ---------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Process a folder of 2D or 3D TIFF files with inverse EDT dilation and custom ridge detection."
    )
    parser.add_argument("input_folder", help="Folder containing input TIFF files (2D or 3D).")
    parser.add_argument("output_folder", help="Folder where processed TIFF files will be saved.")
    parser.add_argument("--dilation_distance", type=float, default=1, help="Dilation distance (in pixels/voxels).")
    parser.add_argument("--ridge_threshold", type=float, default=0.75,
                        help="Threshold for binarizing the ridge detection.")
    parser.add_argument("--num_workers", type=int, default=multiprocessing.cpu_count(),
                        help="Number of worker processes.")
    args = parser.parse_args()
    
    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)

    file_list = glob.glob(os.path.join(args.input_folder, "*.tif"))
    if not file_list:
        print(f"No .tif files found in {args.input_folder}")
        return

    tasks = [
        (f, args.output_folder, args.dilation_distance, args.ridge_threshold)
        for f in file_list
    ]

    with multiprocessing.Pool(args.num_workers) as pool:
        results = list(
            tqdm(
                pool.imap_unordered(worker, tasks),
                total=len(tasks),
                desc="Processing Files"
            )
        )

    successes = [res for res in results if res[1] is True]
    failures = [res for res in results if res[1] is not True]

    print(f"Processed {len(successes)} files successfully.")
    if failures:
        print(f"{len(failures)} files failed:")
        for fail in failures:
            print(f"File: {fail[0]}, Error: {fail[2]}")


if __name__ == "__main__":
    main()
