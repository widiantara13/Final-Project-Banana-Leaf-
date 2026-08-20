import os
from fastapi import HTTPException
from dotenv import load_dotenv, find_dotenv
from starlette import status
from PIL import Image
import tensorflow as tf
import numpy as np
import gc


load_dotenv(find_dotenv())

model_url = os.getenv("MODEL_URL")

async def upload_model(file):
    try:
        ext_allowed = [".h5", ".keras"]
        file_name = file.filename
        ext = os.path.splitext(file_name)[1].lower()
        if ext not in ext_allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail = "Mohon inputkan file dengan ekstensi .h5 atau .keras")

        file_path = os.path.join(model_url, file_name)

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        return [file_name, file_path]
    except Exception as e:
        print(f"Detail error: {repr(e)}")


model_filter = None
model_diseases = None
filter_url = None
diseases_url = None
async def load_model_filter(model_url: str):
    global model_filter, filter_url
    filter_url = model_url
    model_filter = tf.keras.models.load_model(model_url)
    return model_filter

async def load_model_diseases(model_url: str):
    global model_diseases, diseases_url
    diseases_url = model_url
    model_diseases = tf.keras.models.load_model(model_url)
    return model_diseases
    
async def set_active_all(model_f: str, model_d : str):
    await load_model_filter(model_f)
    await load_model_diseases(model_d)
    return True
    
async def set_inactive():
    global model_filter, model_diseases
    tf.keras.backend.clear_session()
    gc.collect()
    model_diseases = None
    model_filter = None

    return False

async def update_set_model(url: str, url2: str):
    await set_inactive()
    return await set_active_all(url, url2)

async def start_up():
    if filter_url is None and diseases_url is None:
        print("model tidak aktif")
    load_model_filter(filter_url)
    load_model_diseases(diseases_url)
    return "model aktif"


banana_or_random = ["random", "banana"]
diseases =["Cordana", "Healthy", "Panama", "Yellow & Black Sigota"]

async def preprocessing_filter(img: Image.Image):
    img_arr = tf.keras.utils.img_to_array(img.resize((150,150)))
    img_arr = np.expand_dims(img_arr, axis=0) / 255.0
    predict = model_filter.predict(img_arr)
    return int(np.argmax(predict)), float(np.max(predict))

async def preprocessing_diseases(img: Image.Image):
    img_arr = tf.keras.utils.img_to_array(img.resize((224,224)))
    img_arr = np.expand_dims(img_arr, axis=0) / 255.0
    predict = model_diseases.predict(img_arr)
    
    return int(np.argmax(predict)), float(np.max(predict))

async def predict(file):
    try:
        img = Image.open(file.file)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        predict_class, confidence = await preprocessing_filter(img)
        if predict_class == 0:  # random
            return {"class": banana_or_random[predict_class], "confidence": round(confidence*100, 2)}

        
        predict_class, confidence = await preprocessing_diseases(img)
        return {"index":predict_class, "class": diseases[predict_class], "confidence": round(confidence*100, 2)}

        

        
    except Exception as e:
        print(f"Detail error: {repr(e)}")   
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail = "terjadi kesalahan internal")
        





    
    


        

        