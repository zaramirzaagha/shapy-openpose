import io
import os
import shutil
import uuid

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image

from app.openpose import run_openpose
from app.shapy import run_shapy

IMAGES_DIR = "/tmp/images"
os.makedirs(IMAGES_DIR, exist_ok=True)

KEYPOINTS_DIR = "/tmp/keypoints"
os.makedirs(KEYPOINTS_DIR, exist_ok=True)

ATTRIBUTES_DIR = "/tmp/attributes"
os.makedirs(ATTRIBUTES_DIR, exist_ok=True)

app = FastAPI()

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    contents = await file.read()
    
    # Validate the image
    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid image file"})

    # Save image to disk
    request_id = str(uuid.uuid4())
    
    request_images_dir = f"{IMAGES_DIR}/{request_id}"
    os.makedirs(request_images_dir, exist_ok=True)

    reqeust_keypoints_dir = f"{KEYPOINTS_DIR}/{request_id}"
    os.makedirs(reqeust_keypoints_dir, exist_ok=True)

    request_attributes_dir = f"{ATTRIBUTES_DIR}/{request_id}"
    os.makedirs(request_attributes_dir, exist_ok=True)
    
    image_id = str(uuid.uuid4())
    save_path = f"{request_images_dir}/{image_id}.jpg"
    with open(save_path, "wb") as f:
        f.write(contents)
    
    try:
        keypoints = run_openpose(save_path, reqeust_keypoints_dir)
        attributes = run_shapy(request_images_dir, reqeust_keypoints_dir, request_attributes_dir)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        # Remove the directory after processing
        shutil.rmtree(request_images_dir)
        shutil.rmtree(reqeust_keypoints_dir)

    return {
            "keypoints": keypoints,
            "shapy_result": attributes
    }
