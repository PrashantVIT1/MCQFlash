import os
import time
import uuid
import requests
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from paddleocr import PaddleOCR
from dotenv import load_dotenv

load_dotenv()

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

ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_answer(texts):

    url = (
        f"https://api.cloudflare.com/client/v4/accounts/"
        f"{ACCOUNT_ID}/ai/run/@cf/cloudflare/clef-flash"
    )

    criteria_dict = {
        index: text
        for index, text in enumerate(texts)
    }

    payload = {
        "model": "clef-flash",
        "state": (
            "Identify the MCQ question and determine the correct "
            "answer from the provided OCR text."
        ),
        "questions": {
            "answer": {
                "type": "choice",
                "instructions": "Which option is the correct answer?",
                "criteria": criteria_dict
            }
        }
    }

    start_time = time.perf_counter()

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {API_TOKEN}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )

        latency_ms = (time.perf_counter() - start_time) * 1000

        data = response.json()

        if not response.ok or not data.get("success"):
            raise RuntimeError(
                f"Cloudflare error: {data.get('errors', data)}"
            )

        answer = data["result"]["answers"]["answer"]

        choice = int(answer["choice"])

        return (
            criteria_dict[choice],
            answer["confidence"],
            latency_ms,
        )

    except requests.exceptions.Timeout:
        raise RuntimeError("Cloudflare request timed out after 30 seconds")

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Cloudflare network error: {e}")

# ---------------------------------------------------------
# EXTRACT TEXT
# ---------------------------------------------------------
def extract_text(image_path: str):
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    # Start OCR timer
    start = time.perf_counter()

    # Run PaddleOCR
    result = ocr.predict(str(image_path))

    # End OCR timer
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

        texts.extend(
            data.get("rec_texts", [])
        )

        scores.extend(
            data.get("rec_scores", [])
        )

        boxes.extend(
            data.get("rec_boxes", [])
        )

    return texts, scores, boxes, elapsed

def predict_answer_from_image(image_path: str):

    texts, scores, boxes, elapsed = extract_text(image_path)

    Ans, confidence, decision_latency = get_answer(texts)

    total_latency = elapsed * 1000 + decision_latency

    print("\n" + "=" * 60)
    print(f"OCR TIME: {elapsed * 1000:.2f} ms")
    print(f"DECISION TIME: {decision_latency:.2f} ms")
    print(f"TOTAL TIME TAKEN: {total_latency:.2f} ms")
    print("=" * 60)

    print("Answer of your question:", Ans)

    return (
        Ans,
        confidence,
        decision_latency,
        total_latency,
    )

@app.post("/solve")
async def solve_mcq(image: UploadFile = File(...)):

    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )

    MAX_SIZE = 10 * 1024 * 1024

    contents = await image.read()

    if len(contents) > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 10MB limit"
        )

    temp_dir = BASE_DIR / "temp"
    temp_dir.mkdir(exist_ok=True)

    temp_path = temp_dir / f"upload_{uuid.uuid4().hex}.jpg"

    try:

        with open(temp_path, "wb") as f:
            f.write(contents)

        (
            Ans,
            confidence,
            decision_latency,
            total_latency,
        ) = predict_answer_from_image(str(temp_path))

        return {
            "message": Ans,
            "confidence": f"{confidence * 100:.2f}%",
            "decision_latency": f"{decision_latency:.2f} ms",
            "total_latency": f"{total_latency:.2f} ms",
        }

    except Exception as e:

        print(f"Processing failed: {e}")

        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )

    finally:

        if temp_path.exists():
            temp_path.unlink()

@app.get("/")
def root():
    return {"message": "MCQFlash API is running"}