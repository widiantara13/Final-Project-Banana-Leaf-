import os
from PIL import Image
from datetime import datetime
import random


def image_saver(file, folder_name:str = ''):
    try:
        time = datetime.now().strftime("%Y%m%d%H%M%S")
        rundom_number = random.randint(1, 10000)

        image_name = f"{time}_{rundom_number}.jpg"

        path = os.path.join("app/static", folder_name)
        if not os.path.exists(path):
            os.mkdir(path)
        image_path = os.path.join(path, image_name)

        img = Image.open(file.file)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img =img.resize((224, 224), Image.Resampling.LANCZOS)
        img.save(image_path, "JPEG", quality=90)
        img.close
        return f"app/static/{folder_name}/{image_name}"
    except Exception as e:
        print(f"Detail error: {repr(e)} disini ya")



def image_delete(img_path: str):
    try:
          
        if os.path.exists(img_path):
            os.remove(img_path)
    except Exception as e:
        print(f"Detail error: {repr(e)}")
        

