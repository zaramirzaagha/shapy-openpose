import json
import os
import subprocess

SHAPY_DIR = "/shapy"
REGRESSOR_DIR = f"{SHAPY_DIR}/regressor"
REGRESSOR_SCRIPT = f"{REGRESSOR_DIR}/demo.py"
REGRESSOR_CONFIGS_DIR = f"{REGRESSOR_DIR}/configs"
DATA_DIR = f"{SHAPY_DIR}/data"
SHAPY_OUTPUT_DIR = "/tmp/shapy-output"

# Create output directory
os.makedirs(SHAPY_OUTPUT_DIR, exist_ok=True)

def run_shapy(images_dir: str, keypoints_dir: str, attributes_dir: str):
    command = [
        "python3", REGRESSOR_SCRIPT,
        "--datasets", "openpose",
        "--output-folder", attributes_dir,
        "--exp-cfg", f"{REGRESSOR_CONFIGS_DIR}/b2a_expose_hrnet_demo.yaml",
        "--exp-opts", f"output_folder={DATA_DIR}/trained_models/shapy/SHAPY_A",
        "part_key=pose",
        f"datasets.pose.openpose.img_folder={images_dir}",
        f"datasets.pose.openpose.keyp_folder={keypoints_dir}",
        "datasets.batch_size=1",
        "datasets.pose_shape_ratio=1.0"
    ]

    result = subprocess.run(command, cwd=REGRESSOR_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        raise RuntimeError(f"SHAPY failed: {result.stderr.decode()}")

    # Example: look for a result.json or similar
    json_path = os.path.join(attributes_dir, "result.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"SHAPY result file not found at {json_path}")

    with open(json_path) as f:
        result_data = json.load(f)

    return result_data
