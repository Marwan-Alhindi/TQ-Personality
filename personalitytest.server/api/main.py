from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib
import os
from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client, Client
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import joblib

app = FastAPI()

# تحميل النموذج المدرب
model_small = joblib.load("models/kmeans_small_model.pkl")


# تحميل نموذج KMeans المدرب على الـ 50 سؤال
model_large = joblib.load("models/kmeans_model.pkl")

# وصف كل كلستر
cluster_descriptions = {
    0: "😌 ذا الواحد اللي عايش حياته على مود رايق. كل شيء عنده \"عادي\"، يقهوي نفسه الساعة ٥ العصر ويحوس بالبلانر يوم ويختفي سنة...",
    1: "🎭 ذا اللي قلبه ألين من خبز التنور. يبكي من إعلان زين ويكتب خواطر عن ذكرى منديل...",
    2: "📚 ذا اللي لو قلت له \"خل نروح الطايف\" قالك: \"طيب أرسل لي على الإيميل الخطة\"...",
    3: "🔕 ذا اللي تحسبه طالع من مسلسل كوري، بس هو ساكن في حي الربيع، بس ما أحد قد شافه...",
    4: "🎢 هذا بركان عواطف. يغير اهتماماته أسرع من عروض نون، وكل شوي يدخل هواية جديدة..."
}

# نموذج البيانات الواردة
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

class PersonalityFullInput(BaseModel):
    EXT1: int; EXT2: int; EXT3: int; EXT4: int; EXT5: int
    EXT6: int; EXT7: int; EXT8: int; EXT9: int; EXT10: int
    EST1: int; EST2: int; EST3: int; EST4: int; EST5: int
    EST6: int; EST7: int; EST8: int; EST9: int; EST10: int
    AGR1: int; AGR2: int; AGR3: int; AGR4: int; AGR5: int
    AGR6: int; AGR7: int; AGR8: int; AGR9: int; AGR10: int
    CSN1: int; CSN2: int; CSN3: int; CSN4: int; CSN5: int
    CSN6: int; CSN7: int; CSN8: int; CSN9: int; CSN10: int
    OPN1: int; OPN2: int; OPN3: int; OPN4: int; OPN5: int
    OPN6: int; OPN7: int; OPN8: int; OPN9: int; OPN10: int

@app.post("/analyze")
def analyze(data: PersonalityRaw):
    raw = data.dict()
    input_df = pd.DataFrame([raw])

    # إنشاء MinMaxScaler بقيم min=0 و max=5
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(pd.DataFrame([[0]*12, [5]*12], columns=input_df.columns))  # نمرر القيم المتوقعة

    scaled_input = scaler.transform(input_df)

    # توقع الكلستر
    cluster = int(model_small.predict(scaled_input)[0])

    # وصف الكلستر
    description = cluster_descriptions.get(cluster, "🧩 ما عرفنا شخصيتك، بس أكيد فريدة من نوعها!")

    # حساب الأبعاد الخمسة من القيم الأصلية (لعرضها فقط)
    ext = ['EXT2', 'EXT3', 'EXT4', 'EXT5', 'EXT7', 'EXT9', 'EXT10']
    est = ['EST6', 'EST8']
    agr = ['AGR7']
    opn = ['OPN9']
    csn = ['CSN4']

    trait_scores = {
        'extroversion': round(input_df[ext].sum(axis=1).iloc[0] / len(ext), 2),
        'neurotic': round(input_df[est].sum(axis=1).iloc[0] / len(est), 2),
        'agreeable': round(input_df[agr].sum(axis=1).iloc[0] / len(agr), 2),
        'conscientious': round(input_df[csn].sum(axis=1).iloc[0] / len(csn), 2),
        'open': round(input_df[opn].sum(axis=1).iloc[0] / len(opn), 2)
    }

    return {
        "cluster": cluster,
        "description": description,
        "scores": trait_scores
    }

@app.post("/analyze_50")
def analyze_50(data: PersonalityFullInput):
    raw = data.dict()
    input_df = pd.DataFrame([raw])

    # ترتيب الأعمدة حسب الترتيب
    ordered_cols = sorted(input_df.columns, key=lambda x: (x[:3], int(x[3:])))
    input_df = input_df[ordered_cols]

    # مقياس MinMax من 0 إلى 5
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(pd.DataFrame([[0]*50, [5]*50], columns=ordered_cols))
    scaled = scaler.transform(input_df)

    # توقع الكلستر
    cluster = int(model_large.predict(scaled)[0])
    description = cluster_descriptions.get(cluster, "🧩 ما عرفنا شخصيتك، بس أكيد فريدة!")

    # حساب السمات
    trait_scores = {
        'extroversion': round(input_df[[f'EXT{i}' for i in range(1, 11)]].mean(axis=1).iloc[0], 2),
        'neurotic': round(input_df[[f'EST{i}' for i in range(1, 11)]].mean(axis=1).iloc[0], 2),
        'agreeable': round(input_df[[f'AGR{i}' for i in range(1, 11)]].mean(axis=1).iloc[0], 2),
        'conscientious': round(input_df[[f'CSN{i}' for i in range(1, 11)]].mean(axis=1).iloc[0], 2),
        'open': round(input_df[[f'OPN{i}' for i in range(1, 11)]].mean(axis=1).iloc[0], 2),
    }

    return {
        "cluster": cluster,
        "description": description,
        "scores": trait_scores
    }

# ---------------

# Supabase credentials
SUPABASE_URL = "https://fbilhtmxiidtazaxcwhm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZiaWxodG14aWlkdGF6YXhjd2htIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDUzMjI5MDUsImV4cCI6MjA2MDg5ODkwNX0.1Ozd9wzUZb-S7f0zD8WwhDhR-NhFTq2K8JFsrBMm4Uc"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Input schema
class PeerReviewInput(BaseModel):
    target_person: str
    rater: str
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

@app.post("/analyze-peer")
def analyze_peer(data: PeerReviewInput):
    raw = data.dict()

    # Save to Supabase
    supabase.table("peer_reviews").insert(raw).execute()
    print('✅ Peer review inserted into Supabase.')

    return {"message": "Review submitted successfully"}

@app.get("/reviews/{person_name}")
def get_reviews(person_name: str):
    query = supabase.table("peer_reviews").select("*").eq("target_person", person_name).execute()
    data = query.data

    if not data:
        return {"error": "No reviews found"}

    df = pd.DataFrame(data)
    trait_keys = ['EXT2','EXT3','EXT4','EXT5','EXT7','EXT9','EXT10','EST6','EST8','AGR7','OPN9','CSN4']
    avg_scores = df[trait_keys].mean().to_dict()

    # Prepare input
    input_df = pd.DataFrame([{k: int(round(v)) for k, v in avg_scores.items()}])

    scaler = MinMaxScaler((0, 1))
    scaler.fit(pd.DataFrame([[0]*12, [5]*12], columns=input_df.columns))
    scaled = scaler.transform(input_df)

    cluster = int(model_small.predict(scaled)[0])
    description = cluster_descriptions.get(cluster, "🧩 ما عرفنا شخصيتك، بس أكيد فريدة!")

    ext = ['EXT2','EXT3','EXT4','EXT5','EXT7','EXT9','EXT10']
    est = ['EST6','EST8']
    agr = ['AGR7']
    opn = ['OPN9']
    csn = ['CSN4']

    trait_scores = {
        'extroversion': round(input_df[ext].mean(axis=1).iloc[0], 2),
        'neurotic': round(input_df[est].mean(axis=1).iloc[0], 2),
        'agreeable': round(input_df[agr].mean(axis=1).iloc[0], 2),
        'conscientious': round(input_df[csn].mean(axis=1).iloc[0], 2),
        'open': round(input_df[opn].mean(axis=1).iloc[0], 2)
    }

    return {
        "cluster": cluster,
        "description": description,
        "scores": trait_scores
    }