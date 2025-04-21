import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="تحليل الشخصية", layout="wide")

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

# جمع الإجابات
responses = {}
with st.form("form_arabic"):
    for key, question in questions.items():
        responses[key] = st.slider(question, min_value=0, max_value=5, value=3, key=key)
    submitted = st.form_submit_button("احللني!")

# إرسال وتحليل
if submitted:
    try:
        res = requests.post("http://127.0.0.1:8000/analyze", json=responses)

        if res.status_code == 200:
            result = res.json()

            st.success("✨ تم التحليل! وهذه النتيجة 👇")
            st.markdown(f"### الكلستر الخاص بك: `{result['cluster']}`")
            st.markdown(f"**{result['description']}**")

            st.markdown("### ملخص الأبعاد الخمسة:")
            trait_scores = result["scores"]
            summary_df = pd.DataFrame([trait_scores])
            st.dataframe(summary_df.style.format(precision=1), use_container_width=True)

            # رسم بياني بـ Plotly
            st.markdown("### تمثيل مرئي لأبعادك")
            traits = list(trait_scores.keys())
            values = [trait_scores[t] * 10 for t in traits]

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=traits,
                y=values,
                name='قيمك',
                marker_color='lightgreen',
                opacity=0.6
            ))

            fig.add_trace(go.Scatter(
                x=traits,
                y=values,
                mode='lines+markers',
                name='خط التحليل',
                line=dict(color='red'),
                marker=dict(size=10)
            ))

            fig.update_layout(
                title=f"الكلستر رقم {result['cluster']}",
                yaxis=dict(range=[0, 50]),
                xaxis_title="البُعد",
                yaxis_title="الدرجة (مضروبة ×10)",
                template="plotly_white"
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.error("💥 صار خطأ في الاتصال بالـ API. تأكد أنه شغال.")
    except Exception as e:
        st.error(f"❌ فشل الاتصال بالسيرفر: {e}")