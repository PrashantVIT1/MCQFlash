import os
import time
import requests
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional


from paddleocr import PaddleOCR

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------
# LIGHTWEIGHT OCR FOR SCREENSHOTS
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

DET_MODEL = BASE_DIR / "models" / "PP-OCRv6_tiny_det"
REC_MODEL = BASE_DIR / "models" / "PP-OCRv6_tiny_rec"

ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv6_tiny_det",
    text_detection_model_dir=str(DET_MODEL),

    text_recognition_model_name="PP-OCRv6_tiny_rec",
    text_recognition_model_dir=str(REC_MODEL),

    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)
# ---------------------------------------------------------
# Clef configration
# ---------------------------------------------------------

ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

# ---------------------------------------------------------
# FIND THE ANSWER
# ---------------------------------------------------------
def get_answer(texts):

    url = (f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/cloudflare/clef-flash")

    criteria_dict={index:text for index,text in (enumerate(texts))}

    payload = {
        "model": "clef-flash",
        "state": "Identify the correct MCQ question from the following options and find the correct answer.",
        "questions": {
            "answer": {
                "type": "choice",
                "instructions": "Which option is the correct solution?",
                "criteria": criteria_dict
            }
        }
    }


    try:

        # Start latency measurement for this request
        start_time = time.perf_counter()

        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {API_TOKEN}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )

        # End latency measurement
        end_time = time.perf_counter()

        latency_ms = (end_time - start_time) * 1000

        data = response.json()


        # --------------------------------------------------
        # Check response
        # --------------------------------------------------

        if not response.ok or not data.get("success"):

            print("\nCloudflare Error:")
            print(data.get("errors", data))

        # --------------------------------------------------
        # Extract answer
        # --------------------------------------------------

        answer = data["result"]["answers"]["answer"]



        return criteria_dict[int(answer['choice'])], answer['confidence'], latency_ms


    except requests.exceptions.Timeout:

        print("\nERROR: Request timed out after 30 seconds.")

    except requests.exceptions.RequestException as e:

        print(f"\nERROR: Network request failed: {e}")

    except Exception as e:

        print(f"\nERROR: {e}")





# ---------------------------------------------------------
# EXTRACT TEXT
# ---------------------------------------------------------

def extract_text(image_path: str):

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    start = time.perf_counter()

    result = ocr.predict(str(image_path))

    elapsed = time.perf_counter() - start

    texts = []
    scores = []
    boxes = []

    for res in result:

        # PaddleOCR result object
        data = res.json

        if callable(data):
            data = data()

        if isinstance(data, dict):
            data = data.get("res", data)

        texts.extend(data.get("rec_texts", []))
        scores.extend(data.get("rec_scores", []))
        boxes.extend(data.get("rec_boxes", []))

    return texts, scores, boxes, elapsed

# ---------------------------------------------------------
# WEB SIDE
# ---------------------------------------------------------
app = FastAPI()

# ---------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Prediction function
# ---------------------------------------------------------
def predict_answer():
    IMAGE_PATH = "Mcq.jpeg"

    try:

        texts, scores, boxes, elapsed = extract_text(
            IMAGE_PATH
        )

        Ans, confidence, decision_latency = get_answer(texts)

        print("\n" + "=" * 60)
        total_latency= elapsed * 1000+ decision_latency

        print(
            f"OCR TIME: {elapsed * 1000:.2f} ms", f"TOTAL TIME TAKEN:{total_latency:.2f}ms"
        )
        print("=" * 60)

        print("Answer of your question: ", Ans)

        return Ans, confidence, decision_latency, total_latency

    except Exception as e:

        print("\nOCR ERROR:")
        print(e)
        return e, None, None


# ---------------------------------------------------------
# IMAGE-BASED PREDICTION
# ---------------------------------------------------------
def predict_answer_from_image(image_path: str):
    try:
        texts, scores, boxes, elapsed = extract_text(image_path)
        Ans, confidence, decision_latency = get_answer(texts)

        print("\n" + "=" * 60)
        total_latency = elapsed * 1000 + decision_latency

        print(
            f"OCR TIME: {elapsed * 1000:.2f} ms", f"TOTAL TIME TAKEN:{total_latency:.2f}ms"
        )
        print("=" * 60)

        print("Answer of your question: ", Ans)

        return Ans, confidence, decision_latency, total_latency

    except Exception as e:
        print("\nOCR ERROR:")
        print(e)
        raise e


@app.post("/solve")
async def solve_mcq(image: UploadFile = File(...)):
    """
    Accept an uploaded MCQ image, process it through OCR + Clef-flash,
    and return the answer with confidence and latency metrics.
    """
    # Validate file type
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Validate file size (max 10MB)
    MAX_SIZE = 10 * 1024 * 1024  # 10MB
    contents = await image.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

    # Save temporary file
    temp_dir = BASE_DIR / "temp"
    temp_dir.mkdir(exist_ok=True)
    temp_path = temp_dir / f"upload_{int(time.time())}_{image.filename}"

    try:
        # Write uploaded file to disk
        with open(temp_path, "wb") as f:
            f.write(contents)

        # Process the image
        Ans, confidence, decision_latency, total_latency = predict_answer_from_image(str(temp_path))

        # Format response
        confidence_str = f"{confidence * 100:.2f}%"
        decision_latency_str = f"{decision_latency:.2f} ms"
        total_latency_str = f"{total_latency:.2f} ms"

        return {
            "message": Ans,
            "confidence": confidence_str,
            "decision_latency": decision_latency_str,
            "total_latency": total_latency_str
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    finally:
        # Clean up temporary file
        if temp_path.exists():
            temp_path.unlink()


@app.get("/")
def mcq_solution():
    Ans, confidence, decision_latency, total_latency = predict_answer()
    confidence = f"{confidence * 100:.2f}%"
    decision_latency=f"{decision_latency:.2f} ms"
    total_latency= f"{total_latency:.2f} ms"

    return {
        "message": Ans,
        "confidence": confidence,
        "decision_latency": decision_latency,
        "total_latency": total_latency
    }
