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

async def unload_model_filter():
    global model_filter, filter_url
    model_filter = None
    filter_url = None
    gc.collect()

async def unload_model_diseases():
    global model_diseases, diseases_url
    model_diseases = None
    diseases_url = None
    gc.collect()

FILTER_TYPES = ["0", "False", "false", "Filter", "filter"]
DISEASE_TYPES = ["1", "True", "true", "Prediksi", "diseases", "dieases"]

def is_filter_type(model_type) -> bool:
    return str(model_type).strip().lower() in ["0", "false", "filter"]

def is_disease_type(model_type) -> bool:
    return str(model_type).strip().lower() in ["1", "true", "prediksi", "diseases", "dieases"]

async def update_set_model(url: str, url2: str):
    await set_inactive()
    return await set_active_all(url, url2)

def resolve_model_path(path: str) -> str:
    """Mencari path file model, baik path langsung maupun relatif terhadap folder MODEL_URL"""
    if os.path.exists(path):
        return path
    base_folder = model_url or "app/ai"
    fallback_path = os.path.join(base_folder, os.path.basename(path))
    if os.path.exists(fallback_path):
        return fallback_path
    return path

async def start_up():
    """
    Dipanggil saat aplikasi FastAPI startup (lifespan).
    Mengecek database untuk mencari model filter & diseases yang aktif (is_active = True),
    lalu memuatnya ke memori TensorFlow.
    """
    print("[INFO] Memeriksa model aktif di database...")
    try:
        from app.database.database import async_session
        from app.models.models_model import Models
        from sqlalchemy.future import select

        async with async_session() as db:
            get_filter = await db.execute(
                select(Models).where(
                    (Models.is_active == True)
                    & (Models.model_type.in_(["0", "False", "false", "Filter", "filter"]))
                )
            )
            get_diseases = await db.execute(
                select(Models).where(
                    (Models.is_active == True)
                    & (Models.model_type.in_(["1", "True", "true", "Prediksi", "diseases", "dieases"]))
                )
            )
            active_filter = get_filter.scalars().first()
            active_diseases = get_diseases.scalars().first()

            if active_filter:
                f_path = resolve_model_path(active_filter.url)
                if os.path.exists(f_path):
                    try:
                        await load_model_filter(f_path)
                        print(f"[SUCCESS] Filter Model berhasil dimuat: {active_filter.models_name} ({f_path})")
                    except Exception as err:
                        print(f"[ERROR] Gagal memuat Filter Model ({f_path}): {repr(err)}")
                else:
                    print(f"[WARNING] File Filter Model tidak ditemukan di: {active_filter.url}")
            else:
                print("[INFO] Tidak ada Filter Model dengan status aktif di database.")

            if active_diseases:
                d_path = resolve_model_path(active_diseases.url)
                if os.path.exists(d_path):
                    try:
                        await load_model_diseases(d_path)
                        print(f"[SUCCESS] Diseases Model berhasil dimuat: {active_diseases.models_name} ({d_path})")
                    except Exception as err:
                        print(f"[ERROR] Gagal memuat Diseases Model ({d_path}): {repr(err)}")
                else:
                    print(f"[WARNING] File Diseases Model tidak ditemukan di: {active_diseases.url}")
            else:
                print("[INFO] Tidak ada Diseases Model dengan status aktif di database.")

    except Exception as e:
        print(f"[WARNING] Gagal memeriksa model aktif saat startup: {repr(e)}")


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
        if model_filter is None or model_diseases is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model deteksi belum aktif, mohon tunggu beberapa saat lagi atau hubungi administrator."
            )
        img = Image.open(file.file)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        predict_class, confidence = await preprocessing_filter(img)
        if predict_class == 0:  # random
            return {"class": banana_or_random[predict_class], "confidence": round(confidence*100, 2)}

        
        predict_class, confidence = await preprocessing_diseases(img)
        return {"index":predict_class, "class": diseases[predict_class], "confidence": round(confidence*100, 2)}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Detail error: {repr(e)}")   
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail = "terjadi kesalahan internal")
        





    
    


        

        