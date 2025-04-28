import streamlit as st
import matplotlib.pyplot as plt
import pdfkit
import tempfile
import os
import base64
import re

# Path to wkhtmltopdf executable
path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'  # Update if needed
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

# Save matplotlib figure as base64 image
def fig_to_base64(fig):
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpfile:
        fig.savefig(tmpfile.name, bbox_inches='tight')
        tmpfile_path = tmpfile.name

    with open(tmpfile_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()

    os.unlink(tmpfile_path)  # Safer file delete
    plt.close(fig)  # Important to close figure

    return f"data:image/png;base64,{encoded}"

# Helper function to clean emojis
def clean_emojis(html):
    replacements = {
        "📊": "",
        "🌱": "",
        "🚶‍♂️": "",
        "🚗": "",
        "🗑": "",
        "⚡": "",
        "🛒": "",
        "📋": "",
        "✈️": "",
        "♻️": "",
    }
    for emoji, text in replacements.items():
        html = html.replace(emoji, text)

    # Remove any leftover emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "]+",
        flags=re.UNICODE
    )
    html = emoji_pattern.sub("", html)
    return html

def generate_html_report(input_data, prediction, travel_values, waste_values, feedback_list, travel_chart, waste_chart):
    travel_img_base64 = fig_to_base64(travel_chart)
    waste_img_base64 = fig_to_base64(waste_chart)

    html = f"""
    <html>
    <head>
        <title>Carbon Footprint Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #4CAF50; }}
            h2 {{ color: #2196F3; }}
            p, li {{ font-size: 16px; }}
            ul {{ padding-left: 20px; }}
            img {{ max-width: 600px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <h1>📊 Your Personalized Carbon Dashboard Report</h1>
        <h2>🌱 Estimated Carbon Footprint</h2>
        <p><strong>{prediction:.2f} units</strong></p>

        <h2>🚶‍♂️ Personal Profile</h2>
        <p><strong>Sex:</strong> {input_data.get('gender', 'Unknown')}</p>
        <p><strong>Body Type:</strong> {input_data.get('body_type', 'Unknown')}</p>
        <p><strong>Social Activity:</strong> {input_data.get('social_activity', 'Unknown')}</p>
        <p><strong>Diet:</strong> {input_data.get('diet', 'Unknown')}</p>
        <p><strong>Shower Frequency:</strong> {input_data.get('shower_frequency', 'Unknown')}</p>

        <h2>🚗 Transport Overview</h2>
        <p><strong>Vehicle Monthly Distance:</strong> {travel_values[0]} km</p>
        <p><strong>Air Travel Score:</strong> {travel_values[1]}</p>
        <img src="{travel_img_base64}" alt="Transport Chart"/>

        <h2>🗑 Waste Management</h2>
        <p><strong>Waste Bags per Week:</strong> {waste_values[0]}</p>
        <p><strong>Recycling Materials:</strong> {waste_values[1]}</p>
        <img src="{waste_img_base64}" alt="Waste Chart"/>

        <h2>⚡ Energy Usage</h2>
        <p><strong>Heating Energy Source:</strong> {input_data.get('heating_energy_source', 'Unknown')}</p>
        <p><strong>Energy Efficiency Devices:</strong> {input_data.get('energy_efficiency', 'Unknown')}</p>
        <p><strong>Daily PC/TV Hours:</strong> {input_data.get('tv_pc_daily_hours', 0)} hours</p>
        <p><strong>Daily Internet Hours:</strong> {input_data.get('internet_daily_hours', 0)} hours</p>

        <h2>🛒 Consumption</h2>
        <p><strong>Monthly Grocery Bill:</strong> ${input_data.get('monthly_grocery_bill', 0)}</p>
        <p><strong>New Clothes Bought Monthly:</strong> {input_data.get('new_clothes_monthly', 0)} items</p>

        <h2>📋 Insights and Suggestions</h2>
        <ul>
    """
    for feedback in feedback_list:
        html += f"<li>{feedback}</li>"

    html += """
        </ul>
    </body>
    </html>
    """
    return html

def show_dashboard():
    st.title("📊 Your Personalized Carbon Dashboard")

    if "input_data" not in st.session_state:
        st.error("No data available. Please calculate your carbon footprint first.")
        st.stop()

    input_data = st.session_state.input_data
    prediction = st.session_state.prediction

    feedback_list = []

    # Carbon Footprint
    st.metric(label="🌱 Estimated Carbon Footprint", value=f"{prediction:.2f} units")

    # --- Personal Section ---
    st.header("🚶‍♂️ Personal Profile")
    st.write(f"**Sex**: {input_data.get('gender', 'Unknown')}")
    st.write(f"**Body Type**: {input_data.get('body_type', 'Unknown')}")
    st.write(f"**Social Activity**: {input_data.get('social_activity', 'Unknown')}")
    st.write(f"**Diet**: {input_data.get('diet', 'Unknown')}")
    st.write(f"**Shower Frequency**: {input_data.get('shower_frequency', 'Unknown')}")

    # --- Transport Section ---
    st.header("🚗 Transport Overview")
    vehicle_distance = input_data.get('vehicle_monthly_distance_km', 0)
    air_travel = input_data.get('air_travel_frequency', 'never')
    transport_mode = input_data.get('transport', 'Unknown')

    travel_modes = ["Vehicle (km)", "Air Travel (score)"]
    travel_values = [
        vehicle_distance,
        {"never": 0, "rarely": 1, "frequently": 4, "very frequently": 8}.get(air_travel, 0)
    ]

    fig1, ax1 = plt.subplots()
    ax1.bar(travel_modes, travel_values, color=['green', 'skyblue'])
    ax1.set_ylabel("Usage")
    ax1.set_title(f"Transport Mode: {transport_mode}")
    st.pyplot(fig1)

    if vehicle_distance > 720:
        msg = "🚗 High vehicle usage detected! Try to reduce your monthly driving distance."
        st.warning(msg)
        feedback_list.append(msg)
    if air_travel in ["frequently", "very frequently"]:
        msg = "✈️ You travel by air very often. Reducing air travel can greatly cut your carbon footprint."
        st.warning(msg)
        feedback_list.append(msg)

    # --- Waste Management ---
    st.header("🗑 Waste Management")
    waste_bag_count = input_data.get('waste_bag_weekly_count', 0)
    recycling_raw = input_data.get('recycling', [])
    if isinstance(recycling_raw, str):
        import ast
        try:
            recycling = ast.literal_eval(recycling_raw)
        except:
            recycling = []
    else:
        recycling = recycling_raw

    waste_labels = ['Waste Bags per Week', 'Recycling Materials']
    waste_values = [waste_bag_count, len(recycling)]

    fig2, ax2 = plt.subplots()
    ax2.bar(waste_labels, waste_values, color=['orange', 'lightgreen'])
    ax2.set_ylabel("Count")
    ax2.set_title("Waste and Recycling Overview")
    st.pyplot(fig2)

    if waste_bag_count > 5:
        msg = "🗑 You are generating a lot of waste every week! Try to reduce waste or recycle more."
        st.warning(msg)
        feedback_list.append(msg)
    if not recycling:
        msg = "♻️ You are not recycling any materials. Start recycling to lower your footprint."
        st.warning(msg)
        feedback_list.append(msg)

    # --- Energy Usage ---
    st.header("⚡ Energy Usage")
    st.write(f"**Heating Energy Source**: {input_data.get('heating_energy_source', 'Unknown')}")
    st.write(f"**Energy Efficiency Devices**: {input_data.get('energy_efficiency', 'Unknown')}")
    st.write(f"**Daily PC/TV Hours**: {input_data.get('tv_pc_daily_hours', 0)} hours")
    st.write(f"**Daily Internet Hours**: {input_data.get('internet_daily_hours', 0)} hours")

    # --- Consumption Section ---
    st.header("🛒 Consumption")
    st.write(f"**Monthly Grocery Bill**: ${input_data.get('monthly_grocery_bill', 0)}")
    st.write(f"**New Clothes Bought Monthly**: {input_data.get('new_clothes_monthly', 0)} items")

    # --- Generate PDF Button ---
    st.subheader("📄 Download Your Full Report")
    if st.button("Generate & Download PDF"):
        html_report = generate_html_report(
            input_data, prediction, travel_values, waste_values, feedback_list, fig1, fig2
        )

        # Clean the html (remove emojis)
        cleaned_html_report = clean_emojis(html_report)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp_html:
            tmp_html.write(cleaned_html_report.encode('utf-8'))
            tmp_html_path = tmp_html.name

        pdf_path = tmp_html_path.replace('.html', '.pdf')
        pdfkit.from_file(tmp_html_path, pdf_path, configuration=config)

        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="📥 Download Report as PDF",
                data=pdf_file,
                file_name="carbon_dashboard_report.pdf",
                mime="application/pdf"
            )

        os.unlink(tmp_html_path)
        os.unlink(pdf_path)

if __name__ == "__main__":
    show_dashboard()
