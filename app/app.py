from flask import Flask, render_template, request
from db import *
from io import BytesIO
from PIL import Image
import base64
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "/temp_images"

client = init_client()

def list_images():
    """
    Checks the static/img folder and returns a list of image paths
    """
    if os.path.exists('./flask-app'):
        img_path = "./flask-app/static/img/"
    elif os.path.exists('./static'):
        img_path = "./static/img/"
    else:
        return []

    images = []
    for file_path in os.listdir(img_path):
        images.append({
            "path": file_path
        })

    return images


if client.is_ready():
    @app.route("/")
    def home(): # home page
        return render_template("index.html", content = list_images())

    @app.route("/process_image", methods = ["POST"]) # save the uploaded image and convert it to base64
    # process the image upload request by converting it to base64 and querying Weaviate
    def process_image():
        uploaded_file = Image.open(request.files['filepath'].stream)
        buffer = BytesIO()
        uploaded_file.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        weaviate_results = image_search(img_str, client=client)
        print(weaviate_results)
        results = []
        for result in weaviate_results:
            results.append({
                "path": result["filepath"],
                "description": result["description"],
                "image":result["image"]
            })
        print(f"\n {results} \n")
        return render_template("index.html", content = results, dog_image = img_str)
    
    @app.route("/upload_image", methods=["POST"])
    #upload and store image in vector db
    def upload_image():
        uploaded_file = Image.open(request.files['filepath'].stream)
        