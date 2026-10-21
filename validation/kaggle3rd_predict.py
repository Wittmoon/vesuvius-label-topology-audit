"""Run one 3rd-place Kaggle 3d_fullres nnU-Net checkpoint on Kaggle crops (MPS).

usage: predict.py (--ckpt X.pth | --model-dir DIR [--fold 0]) --crops a b c --out DIR [--tile 192] [--step 0.85] [--mirror]
Builds a stock nnU-Net results folder (plans/dataset json from the jirkaborovec preprocessed dataset,
checkpoint as fold_all/checkpoint_final.pth), then predicts with nnUNetPredictor on the given
sample_XXXXX crops. Writes <out>/<crop>.tif (argmax) and <crop>.npz (probabilities).
"""
import argparse, json, os, shutil, sys, time
from pathlib import Path
import torch

HERE = Path(__file__).resolve().parent
IMAGES = HERE.parent / "kaggle_full" / "images"


def build_model_dir(ckpt: Path, trainer: str) -> Path:
    d = HERE / "models" / f"{ckpt.stem}" / f"{trainer}__nnUNetResEncUNetMPlans__3d_fullres"
    (d / "fold_all").mkdir(parents=True, exist_ok=True)
    shutil.copy(HERE / "meta" / "dataset.json", d / "dataset.json")
    shutil.copy(HERE / "meta" / "nnUNetResEncUNetMPlans.json", d / "plans.json")
    tgt = d / "fold_all" / "checkpoint_final.pth"
    if tgt.is_symlink() or tgt.exists():
        tgt.unlink()
    tgt.symlink_to(ckpt.resolve())
    return d


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt", type=Path)
    p.add_argument("--model-dir", type=Path, help="stock nnU-Net results folder (plans/dataset json + fold_N/checkpoint_best.pth), e.g. the HF m7 download")
    p.add_argument("--fold", default="0")
    p.add_argument("--crops", nargs="+", required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--tile", type=int, default=192)
    p.add_argument("--step", type=float, default=0.85)
    p.add_argument("--mirror", action="store_true")
    p.add_argument("--trainer", default="nnUNetTrainer")
    a = p.parse_args()
    import nnunetv2.inference.predict_from_raw_data as pr
    from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer
    pr.recursive_find_python_class = lambda *x, **k: nnUNetTrainer  # custom trainer class is not shipped; base builds the same net
    nnUNetPredictor = pr.nnUNetPredictor
    if a.model_dir:
        md, folds, ckname = a.model_dir, (int(a.fold),), "checkpoint_best.pth"
        ckpath = md / f"fold_{a.fold}" / ckname
    else:
        md, folds, ckname = build_model_dir(a.ckpt, a.trainer), ("all",), "checkpoint_final.pth"
        ckpath = a.ckpt
    ck = torch.load(ckpath, map_location="cpu", weights_only=False)
    print("checkpoint keys:", sorted(ck.keys()), "| trainer:", ck.get("trainer_name"), "| epoch:", ck.get("current_epoch"),
          "| mirror axes:", ck.get("inference_allowed_mirroring_axes"), "| init_args:", list(ck.get("init_args", {}).keys()))
    dev = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    pred = nnUNetPredictor(tile_step_size=a.step, use_gaussian=True, use_mirroring=a.mirror,
                           perform_everything_on_device=False, device=dev, verbose=False, allow_tqdm=False)
    pred.initialize_from_trained_model_folder(str(md), use_folds=folds, checkpoint_name=ckname)
    pred.configuration_manager.configuration["patch_size"] = [a.tile] * 3
    print("patch", pred.configuration_manager.patch_size, "norm", pred.configuration_manager.normalization_schemes, "device", dev)
    a.out.mkdir(parents=True, exist_ok=True)
    inp = a.out / "_in"; inp.mkdir(exist_ok=True)
    files = []
    for c in a.crops:
        src = IMAGES / f"{c}.tif"; dst = inp / f"{c}_0000.tif"
        if not dst.is_symlink(): dst.symlink_to(src)
        files.append([str(dst)])
    t0 = time.time()
    pred.predict_from_files_sequential(files, [str(a.out / c) for c in a.crops], save_probabilities=True,
                                       overwrite=False, folder_with_segs_from_prev_stage=None)
    print(f"{len(a.crops)} crops in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    sys.exit(main())
