import weaviate
import json
from utils import convert_to_base64, vectorize_img, base64_to_img, vectorize_img_raw
import re
import os


path = '../archive/cars_test/cars_test'
batch_size=100
'''

'''


def setup_batch(client):
    client.batch.configure(
        batch_size=batch_size,
        dynamic=True,
        timeout_retries=3,
        callback=None
    )

def upload_img(client, name, img):
    b64str = convert_to_base64(img)

    

    data_properties = {
        "description": name,
        "image": b64str,
        
    }


def import_data(client, path):
    client.batch.configure(batch_size=batch_size)
    with client.batch as batch:
        i = 0
        for file_path in os.listdir(path):
            
            fp = path+'/'+file_path
            
            vector = vectorize_img(fp)
            

            base64_encoding = convert_to_base64(fp)

            image_file = file_path.replace(".jpg", "")

            name = re.sub(".(jpg|jpeg|png)", "", image_file).replace("-", " ")

            # The properties from our schema
            data_properties = {
                "description": name,
                "image": base64_encoding,
                "filepath": file_path,
            }

            batch.add_data_object(data_properties, "Image", vector=vector)

def clear_data(client):
    with client.batch as batch:
        batch.delete_objects(
            class_name="Image",
            where={
                'operator': 'NotEqual',
                'path': ['description'],
                'valueString': 'x'
            },
            output='verbose'
        )

def image_search(img_str, client):
    img = base64_to_img(img_str)

    vector = { 'vector': vectorize_img_raw(img).detach() }

    result = client.query.get(
        'Image', ['description', 'image', 'filepath']
    ).with_near_vector(
        vector
    ).with_limit(10).with_additional(['certainty']).do()

    return result['data']['Get']['Image']


def init_client():

    client = weaviate.Client(
        embedded_options=weaviate.embedded.EmbeddedOptions(
            persistence_data_path='./img_vecs',
        ),
    )

    schema = {
        'class': 'Image',
        'description': 'Random pictures',
        'vectorIndexType': 'hnsw',
        'vectorizer': 'none',
        'properties': [
            {
                    "name": "description",
                    "dataType": ["string"],
                    "description": "Description of picture",
                },
                {
                    "name": "image",
                    "dataType": ["blob"],
                    "description": "image",
                },
                {
                    "name": "filepath",
                    "dataType":["string"],
                    "description": "filepath of the images",
                }
        ]
    }

    if not client.schema.contains(schema=schema):
        client.schema.create_class((schema))

    return client

#Import dataset to db

#setup_batch()
#clear_data()
#import_data(path)
