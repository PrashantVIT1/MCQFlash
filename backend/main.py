import os
import time
import uuid
import base64
from pathlib import Path

import requests
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from paddleocr import PaddleOCR
from dotenv import load_dotenv


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")


# =========================================================
# OCR MODEL
# =========================================================

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


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="MCQFlash API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# CLOUDFLARE / CLEF
# =========================================================

CLOUDFLARE_URL = (
    f"https://api.cloudflare.com/client/v4/accounts/"
    f"{ACCOUNT_ID}/ai/run/@cf/cloudflare/clef-flash"
)


def get_answer(
        texts=None,
        image_data_uri=None,
):
    """
    Send either OCR text OR the original image to Clef.

    OCR mode:
        image -> PaddleOCR -> text -> Clef

    Direct-image mode:
        image -> Clef
    """

    if not ACCOUNT_ID or not API_TOKEN:
        raise RuntimeError(
            "Cloudflare credentials are not configured. "
            "Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN."
        )

    # -----------------------------------------------------
    # OCR TEXT MODE
    # -----------------------------------------------------

    if texts:

        # NOTE:
        # This is still your current OCR representation.
        # Each OCR result is sent as a criterion.
        criteria_dict = {
            index: text
            for index, text in enumerate(texts)
        }

        payload = {
            "model": "clef-flash",
            "state": f"""Identify the correct MCQ question from the following options and find the correct answer. If not sure choose I don't know. here is the OCR extraction for
            {texts}""",
            "questions": {
                "answer": {
                    "type": "choice",
                    "instructions": f"""Before you make a decision here is the 
            text extracted by an OCR model it can contain question in multiple index as a chunk and also contain some text not a part of question. 
            You have to predict the correct answer option only. Don't predict the part of question or anything other then answer. If not sure choose I don't know
            {texts}""",
                    "criteria": criteria_dict
                }
            }
        }

    # -----------------------------------------------------
    # DIRECT IMAGE MODE
    # -----------------------------------------------------

    elif image_data_uri:

        payload = {
            "model": "clef-flash",

            "images": [
                image_data_uri
            ],

            "state": (
                "This image contains a multiple-choice question. "
                "Read the question and answer choices from the image "
                "and determine the correct answer."
            ),

            "questions": {
                "answer": {
                    "type": "choice",

                    "instructions": (
                        "Return the letter of the correct answer."
                    ),

                    "criteria": {
                        "A": "Option A",
                        "B": "Option B",
                        "C": "Option C",
                        "D": "Option D",
                    }
                }
            }
        }

    else:
        raise ValueError(
            "Either OCR text or image data must be provided."
        )

    # -----------------------------------------------------
    # REQUEST
    # -----------------------------------------------------

    start_time = time.perf_counter()

    try:

        response = requests.post(
            CLOUDFLARE_URL,

            headers={
                "Authorization": f"Bearer {API_TOKEN}",
                "Content-Type": "application/json",
            },

            json=payload,

            timeout=30,
        )

        latency_ms = (
                             time.perf_counter() - start_time
                     ) * 1000

        # Handle invalid JSON responses safely
        try:
            data = response.json()
        except ValueError:
            raise RuntimeError(
                f"Cloudflare returned invalid JSON. "
                f"HTTP {response.status_code}: "
                f"{response.text[:500]}"
            )

        # -------------------------------------------------
        # CLOUDFLARE ERROR
        # -------------------------------------------------

        if not response.ok or not data.get("success"):

            raise RuntimeError(
                f"Cloudflare error: "
                f"{data.get('errors', data)}"
            )

        # -------------------------------------------------
        # EXTRACT ANSWER
        # -------------------------------------------------

        answer = (
            data
            .get("result", {})
            .get("answers", {})
            .get("answer")
        )

        if not answer:
            raise RuntimeError(
                f"Unexpected Cloudflare response: {data}"
            )

        choice = answer.get("choice")
        confidence = answer.get("confidence", 0.0)

        if choice is None:
            raise RuntimeError(
                f"Cloudflare did not return a choice: {answer}"
            )

        # -------------------------------------------------
        # OCR MODE RESULT
        # -------------------------------------------------

        if texts:

            try:
                choice_index = int(choice)
            except (TypeError, ValueError):
                raise RuntimeError(
                    f"Unexpected OCR-mode choice: {choice}"
                )

            answer_text = criteria_dict.get(
                choice_index,
                str(choice)
            )

        # -------------------------------------------------
        # DIRECT IMAGE RESULT
        # -------------------------------------------------

        else:

            answer_text = str(choice).upper()

        return (
            answer_text,
            float(confidence),
            latency_ms,
        )

    except requests.exceptions.Timeout:

        raise RuntimeError(
            "Cloudflare request timed out after 30 seconds."
        )

    except requests.exceptions.RequestException as e:

        raise RuntimeError(
            f"Cloudflare network error: {e}"
        )


# =========================================================
# IMAGE -> DATA URI
# =========================================================

def image_to_data_uri(
        image_path: str,
        mime_type: str = "image/jpeg",
):
    """
    Convert an image file to a base64 data URI.

    Required for Clef direct-image inference.
    """

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    image_base64 = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    return (
        f"data:{mime_type};base64,{image_base64}"
    )


# =========================================================
# OCR
# =========================================================

def extract_text(image_path: str):

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    # -----------------------------------------------------
    # OCR START
    # -----------------------------------------------------

    start = time.perf_counter()

    result = ocr.predict(
        str(image_path)
    )

    elapsed = (
            time.perf_counter() - start
    )

    # -----------------------------------------------------
    # EXTRACT RESULTS
    # -----------------------------------------------------

    texts = []
    scores = []
    boxes = []

    for res in result:

        data = res.json

        if callable(data):
            data = data()

        if isinstance(data, dict):
            data = data.get(
                "res",
                data
            )

        texts.extend(
            data.get(
                "rec_texts",
                []
            )
        )

        scores.extend(
            data.get(
                "rec_scores",
                []
            )
        )

        boxes.extend(
            data.get(
                "rec_boxes",
                []
            )
        )

    return (
        texts,
        scores,
        boxes,
        elapsed,
    )


# =========================================================
# PREDICTION
# =========================================================

def predict_answer_from_image(
        image_path: str,
        option: int,
        mime_type: str = "image/jpeg",
):
    """
    option 1:
        Image -> PaddleOCR -> Clef

    option 2:
        Image -> Clef directly
    """

    # =====================================================
    # OPTION 1: OCR + CLEF
    # =====================================================

    if option == 1:

        (
            texts,
            scores,
            boxes,
            elapsed,
        ) = extract_text(
            image_path
        )

        if not texts:
            raise RuntimeError(
                "OCR did not detect any text."
            )

        (
            answer,
            confidence,
            decision_latency,
        ) = get_answer(
            texts=texts
        )

        ocr_time_ms = (
                elapsed * 1000
        )

        total_latency = (
                ocr_time_ms
                + decision_latency
        )

    # =====================================================
    # OPTION 2: DIRECT IMAGE
    # =====================================================

    elif option == 2:

        image_data_uri = image_to_data_uri(
            image_path,
            mime_type
        )

        (
            answer,
            confidence,
            decision_latency,
        ) = get_answer(
            image_data_uri=image_data_uri
        )

        # No OCR in direct-image mode
        ocr_time_ms = 0.0

        total_latency = decision_latency

    else:

        raise ValueError(
            "Invalid option. Use 1 for OCR mode "
            "or 2 for direct-image mode."
        )

    # =====================================================
    # LOG
    # =====================================================

    # print("\n" + "=" * 60)

    # print(
    #     f"OCR TIME: "
    #     f"{ocr_time_ms:.2f} ms"
    # )

    # print(
    #     f"DECISION TIME: "
    #     f"{decision_latency:.2f} ms"
    # )

    # print(
    #     f"TOTAL TIME TAKEN: "
    #     f"{total_latency:.2f} ms"
    # )
    #
    # print(
    #     f"ANSWER: {answer}"
    # )
    #
    # print(
    #     f"CONFIDENCE: "
    #     f"{confidence * 100:.2f}%"
    # )
    #
    # print("=" * 60)

    return (
        answer,
        confidence,
        decision_latency,
        total_latency,
        ocr_time_ms,
    )


# =========================================================
# SOLVE ENDPOINT
# =========================================================

@app.post("/solve")
async def solve_mcq(
        option: int = Form(...),
        image: UploadFile = File(...),
):
    """
    Solve an MCQ image.

    option=1 -> OCR + Clef
    option=2 -> Direct image + Clef
    """

    # -----------------------------------------------------
    # VALIDATE OPTION
    # -----------------------------------------------------

    if option not in (1, 2):

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid option. "
                "Use 1 for OCR mode or "
                "2 for direct-image mode."
            )
        )

    # -----------------------------------------------------
    # VALIDATE IMAGE
    # -----------------------------------------------------

    if (
            not image.content_type
            or not image.content_type.startswith("image/")
    ):

        raise HTTPException(
            status_code=400,
            detail="File must be an image."
        )

    # -----------------------------------------------------
    # READ IMAGE
    # -----------------------------------------------------

    MAX_SIZE = 10 * 1024 * 1024

    contents = await image.read()

    if len(contents) > MAX_SIZE:

        raise HTTPException(
            status_code=400,
            detail="File size exceeds 10MB limit."
        )

    if len(contents) == 0:

        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty."
        )

    # -----------------------------------------------------
    # MIME TYPE
    # -----------------------------------------------------

    mime_type = image.content_type

    # -----------------------------------------------------
    # FILE EXTENSION
    # -----------------------------------------------------

    extension_map = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }

    extension = extension_map.get(
        mime_type,
        ".jpg"
    )

    # -----------------------------------------------------
    # TEMP DIRECTORY
    # -----------------------------------------------------

    temp_dir = BASE_DIR / "temp"

    temp_dir.mkdir(
        exist_ok=True
    )

    temp_path = (
            temp_dir
            / f"upload_{uuid.uuid4().hex}{extension}"
    )

    try:

        # -------------------------------------------------
        # SAVE IMAGE
        # -------------------------------------------------

        with open(
                temp_path,
                "wb"
        ) as f:

            f.write(contents)

        # -------------------------------------------------
        # PROCESS
        # -------------------------------------------------

        (
            answer,
            confidence,
            decision_latency,
            total_latency,
            ocr_time,
        ) = predict_answer_from_image(
            str(temp_path),
            option,
            mime_type,
        )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return {
            "message": answer,

            "confidence": (
                f"{confidence * 100:.2f}%"
            ),

            "ocr_time": (
                f"{ocr_time:.2f} ms"
            ),

            "decision_latency": (
                f"{decision_latency:.2f} ms"
            ),

            "total_latency": (
                f"{total_latency:.2f} ms"
            ),

            "mode": (
                "ocr"
                if option == 1
                else "direct_image"
            ),
        }

    except HTTPException:
        raise

    except Exception as e:

        print(
            f"Processing failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Processing failed: {str(e)}"
            )
        )

    finally:

        # -------------------------------------------------
        # CLEAN TEMP FILE
        # -------------------------------------------------

        if temp_path.exists():

            try:
                temp_path.unlink()
            except Exception as cleanup_error:
                print(
                    f"Could not delete temporary file: "
                    f"{cleanup_error}"
                )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/")
def root():

    return {
        "message": "MCQFlash API is running"
    }


@app.get("/health")
def health():

    return {
        "status": "ok"
    }