import base64
import torchvision.models as models
import torchvision.transforms as transforms

from PIL import Image

from io import BytesIO


IMG_DIMENSIONS = (224, 224)
model = models.resnet18(pretrained=True)
model.eval()

#Transformations necessary for image to work with pretrained resenet
scaler = transforms.Resize((224,224))
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])

to_tensor = transforms.ToTensor()

def convert_to_base64(img):
    
    buff = BytesIO()
    img.save(buff, format="JPEG")
    b64_str = base64.b64encode(buff.getvalue()).decode('utf-8')

    return b64_str

def base64_to_img(data):
    buff = BytesIO(base64.b64decode(data))
    return Image.open(buff)


def vectorize_img(path):
    img = Image.open(path)
    img = img.convert('RGB')
    img = scaler(img)
    img = to_tensor(img)
    img = normalize(img)
    img = img.unsqueeze(0)
    #img = normalize(to_tensor(scaler(img))).unsqueeze(0)
    features = model(img)
    flat_feat =  features.flatten()

    return flat_feat

def vectorize_img_raw(img):
    img = img.convert('RGB')
    img = scaler(img)
    img = to_tensor(img)
    img = normalize(img)
    img = img.unsqueeze(0)
    #img = normalize(to_tensor(scaler(img))).unsqueeze(0)
    features = model(img)
    flat_feat =  features.flatten()
    return flat_feat