from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd

app = FastAPI()


model = joblib.load("../models/kmeans_model.pkl")  #استنى وريف ترسله

# أوصاف الكلسترات
cluster_descriptions = {
    0: "😌 ذا الواحد اللي عايش حياته على مود رايق. كل شيء عنده \"عادي\"، يقهوي نفسه الساعة ٥ العصر ويحوس بالبلانر يوم ويختفي سنة. لو أحد ناداه بالشارع يسوي نفسه ما سمع، بس لو شاف قطة قال لها \"هلا والله\". منظم؟ حسب المزاج. يجرب شي جديد؟ إيه بس بشرط ما يتطلب يلبس جزمة رياضة ولا يرد على اتصال.",

    1: "🎭 ذا اللي قلبه ألين من خبز التنور. يبكي من إعلان زين ويكتب خواطر عن ذكرى منديل. كل شوية يرسل وردات وقلوب و\"أنا آسف لو زعجتك بكلامي\". يخبز إذا تضايق، يرسل سبوتيفاي إذا اشتاق، وإذا شاف طير فوق سيارته قال \"سبحان من خلقه\" وكتب قصيدة.",

    2: "📚 ذا اللي لو قلت له \"خل نروح الطايف\" قالك: \"طيب أرسل لي على الإيميل الخطة\". حياته كلها ملفات Excel و\"شرايح باوربوينت للوناسة\". ما يتنفس إلا إذا عنده جدول. لو ضاع قلمه المفضل، يكتب تعزية في ستوري. ويصححك لو قلت \"data\" وانت تقصد \"information\".",

    3: "🔕 ذا اللي تحسبه طالع من مسلسل كوري، بس هو ساكن في حي الربيع، بس ما أحد قد شافه. يدخل القروب وما يشارك، يسحب سنتين، وإذا كتب شي يكون \"هلا\". روتينه ما تغير من أيام نوكيا N73، مشاعره ثابته لدرجة لو شفت له ردة فعل تنصدم. كأنه الحجر، بس لابس تيشيرت.",

    4: "🎢 هذا بركان عواطف. يغير اهتماماته أسرع من عروض نون، وكل شوي يدخل هواية جديدة: رسم، خط، خبز كيك، فجأة يبيع شاورما بيته. يكتب رواية من ٢٠١٩ ولسى ما خلص الفصل الأول. يشتري أدوات تنظيم، بس يستخدمها لتنظيم كيف يقلق. تفكيره كأنه ٧٢ تبويب مفتوحة، وحده منهم فيها ذكريات عيد الفطر ٢٠١٥."
}



class PersonalityRaw(BaseModel):
    EXT2: int
    EXT3: int
    EXT4: int
    EXT5: int
    EXT7: int
    EXT9: int
    EXT10: int
    EST6: int
    EST8: int
    AGR7: int
    OPN9: int
    CSN4: int

@app.post("/analyze")
def analyze(data: PersonalityRaw):
    raw = data.dict()

  
    extroversion = sum([raw[q] for q in ['EXT2', 'EXT3', 'EXT4', 'EXT5', 'EXT7', 'EXT9', 'EXT10']]) / 7
    neurotic = sum([raw[q] for q in ['EST6', 'EST8']]) / 2
    agreeable = raw['AGR7'] / 1
    conscientious = raw['CSN4'] / 1
    openness = raw['OPN9'] / 1

    input_df = pd.DataFrame([{
        'extroversion': extroversion,
        'neurotic': neurotic,
        'agreeable': agreeable,
        'conscientious': conscientious,
        'open': openness
    }])


    cluster = int(model.predict(input_df)[0])
    description = cluster_descriptions.get(cluster, "🧩 ما عرفنا شخصيتك، بس أكيد فريدة من نوعها!")

    return {
        "cluster": cluster,
        "description": description,
        "scores": {
            "extroversion": round(extroversion, 2),
            "neurotic": round(neurotic, 2),
            "agreeable": round(agreeable, 2),
            "conscientious": round(conscientious, 2),
            "open": round(openness, 2)
        }
    }
