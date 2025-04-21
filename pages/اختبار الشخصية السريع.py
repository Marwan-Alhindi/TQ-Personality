import streamlit as st
import requests

st.markdown("""
<style>
    /* Base RTL settings */
    .rtl, .stMarkdown, .stTitle, p, h1, h2, h3, h4, h5, h6, .stButton {
        direction: rtl;
        text-align: right;
    }
    html, body, [class*="st-"] {
        background-color: #f5f7fa;
    }
            
    /* Ensure slider label text stays RTL */
    .stSlider label {
        text-align: right;
        width: 100%;
        display: block;
    }

</style>
""", unsafe_allow_html=True)


# عنوان الموقع
st.title("تحليل شخصيتك بطريقتنا الخاصة")

st.markdown("""
### هل عمرك حسّيت إنك كائن غريب؟
لا تشيل هم، احنا هنا نحلل شخصيتك ونطقطق عليها شوي (بحب طبعًا).

في هالموقع، ما راح نقول لك إنك "طموح ومبدع" وبس، لا لا...
راح نكشف لك الحقيقة كاملة: إنك مزاجي، تحب المفطّح، وتخاف من المشاعر 😌

جاوب على الأسئلة وخلّنا نبدأ حفلة التحليل ✨
""")

st.markdown("**اختر من 0 (لا أوافق أبدًا) إلى 5 (أوافق تمامًا)**")

# الأسئلة حسب السمات
questions = {
    'EXT2': 'أنا ما أتكلم كثير',
    'EXT3': 'أشعر بالراحة حول الناس',
    'EXT4': 'أفضل أكون بالخلفية وما أكون مركز الانتباه',
    'EXT5': 'أبدأ المحادثات من نفسي',
    'EXT7': 'أتكلم مع ناس كثير في الحفلات',
    'EXT9': 'ما عندي مشكلة أكون مركز الانتباه',
    'EXT10': 'أكون ساكت لما أتعامل مع ناس ما أعرفهم',
    'EST6': 'أنزعج بسهولة',
    'EST8': 'مزاجي يتقلب كثير',
    'AGR7': 'ما أهتم كثير بالناس الآخرين',
    'OPN9': 'أقضي وقت أفكر في أشياء كثيرة',
    'CSN4': 'أخبص الأمور وما أرتبها'
}

responses = {}
for key, question in questions.items():
    responses[key] = st.slider(question, min_value=0, max_value=5, value=3, key=key)

# زر الإرسال
if st.button("احللني!"):
    try:
        res = requests.post("http://127.0.0.1:8000/analyze", json=responses)

        if res.status_code == 200:
            result = res.json()
            st.success("✨ تم التحليل! وهذه النتيجة 👇")
            st.markdown(f"### Cluster رقم: `{result['cluster']}`")
            st.markdown(f"**{result['description']}**")
            
            st.markdown("#### درجاتك في الأبعاد الخمسة:")
            for trait, score in result['scores'].items():
                st.markdown(f"- **{trait.capitalize()}**: {score}")

        else:
            st.error("💥 صار خطأ في الاتصال بالـ API. تأكد أنه شغال.")
    except Exception as e:
        st.error(f"❌ فشل الاتصال بالسيرفر: {e}")
