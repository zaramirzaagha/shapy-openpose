import json
import os
import subprocess

OPENPOSE_DIR = "/openpose"
OPENPOSE_BIN = f"{OPENPOSE_DIR}/build/examples/openpose/openpose.bin"
OPENPOSE_MODEL_DIR = f"{OPENPOSE_DIR}/models"

def run_openpose(image_path: str, keypoints_dir: str):
    image_dir = os.path.dirname(image_path)
    command = [
        OPENPOSE_BIN,
        "--model_folder", OPENPOSE_MODEL_DIR,
        "--image_dir", image_dir,
        "--write_json", keypoints_dir,
        "--display", "0",
        "--render_pose", "0"
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        raise RuntimeError(f"OpenPose failed: {result.stderr.decode()}")

    # Get the generated JSON file
    basename = os.path.basename(image_path)
    json_path = os.path.join(keypoints_dir, os.path.splitext(basename)[0] + "_keypoints.json")
    
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"OpenPose output not found at {json_path}")

    with open(json_path) as f:
        keypoints_data = json.load(f)

    return keypoints_data