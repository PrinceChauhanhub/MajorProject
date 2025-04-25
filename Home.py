import streamlit as st
import base64

# Set page config
st.set_page_config(page_title="About Carbon Footprint", layout="wide")
st.title("Carbon Vision")

# Function to get base64 string of the image
def get_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Background image
img_path = "Images/background_min.jpg"
img_base64 = get_base64(img_path)

# Inject CSS
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/png;base64,{img_base64}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}

.container {{
    background-color: rgba(255, 255, 255, 0.85);
    padding: 3rem;
    border-radius: 20px;
    margin: auto;
    max-width: 900px;
    font-family: 'Arial', sans-serif;
    color: #333;
}}

[data-testid="stSidebar"] {{
    background-color: black;
    color: #333;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# Main content
st.markdown('<div class="container">', unsafe_allow_html=True)

st.markdown("### 🌳 **About Carbon Footprint**")
st.write(
    "🌱 **Carbon Vision** is an intelligent application that predicts your carbon footprint based on your daily lifestyle activities. "
    "From your travel habits to energy consumption, it helps you understand your environmental impact and guides you toward sustainable choices."
)

st.markdown("### 🌳 **Why It Matters**")
st.subheader("🌿 **Climate Impact**")
st.write("Reducing your carbon footprint directly contributes to global efforts against climate change...")

st.subheader("🌿 **Resource Conservation**")
st.write("Cutting carbon often means using fewer natural resources...")

st.subheader("🌿 **Health and Well-being**")
st.write("Lowering emissions supports healthier lifestyle choices...")

st.subheader("🌿 **Sustainable Practices**")
st.write("Lowering emissions supports healthier lifestyle choices...")

st.subheader("🌿 **Responsibility**")
st.write("Lowering emissions supports healthier lifestyle choices...")

st.markdown('</div>', unsafe_allow_html=True)

# Navigation button
if st.button("➡️ Calculate your Carbon Footprint!"):
    st.switch_page("pages/CarbonFootprint.py")
