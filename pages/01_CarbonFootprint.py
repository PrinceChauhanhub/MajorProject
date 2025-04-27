import streamlit as st
import pickle
import pandas as pd
import numpy as np
import ast
import base64

# --- Load models ---
try:
    with open('models/ensemble_model.pkl', 'rb') as ensemble:
        model = pickle.load(ensemble)

    with open('models/dummy_info.pkl', 'rb') as dummy:
        dummy_info = pickle.load(dummy)

    with open('models/preprocessor.pkl', 'rb') as process:
        preprocessor = pickle.load(process)

    with open('models/feature_order.pkl', 'rb') as order:
        feature_order = pickle.load(order)

except FileNotFoundError as e:
    st.error(f"Error loading model files: {str(e)}")
    st.stop()
except Exception as e:
    st.error(f"An unexpected error occurred: {str(e)}")
    st.stop()

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

# --- App title ---
st.title("🌍 Carbon Footprint Calculator")

# --- Tabs ---
tabs = ["👤 Personal", "🚗 Travel", "🗑 Waste", "⚡ Energy", "💊 Consumption"]
tab = st.radio("Navigator", tabs, horizontal=True)

# --- Initialize Session State ---
fields = [
    "height", "weight", "sex", "social_activity", "diet",
    "transport", "vehicle_monthly_distance_km", "air_travel_frequency",
    "waste_bag_size", "waste_bag_weekly_count", "recycling",
    "heating_energy_source", "cooking_with", "energy_efficiency",
    "tv_pc_daily_hours", "internet_daily_hours",
    "shower_frequency", "monthly_grocery_bill", "new_clothes_monthly"
]

for key in fields:
    st.session_state.setdefault(key, None)

# --- Inputs ---
if tab == "👤 Personal":
    st.session_state.height = st.number_input(
        "Height (cm)", 100, 250,
        value=st.session_state.height if st.session_state.height is not None else 170
    )
    st.session_state.weight = st.number_input(
        "Weight (kg)", 20, 300,
        value=st.session_state.weight if st.session_state.weight is not None else 70
    )
    st.session_state.sex = st.selectbox(
        "Sex", ["Please select", "Male", "Female"],
        index=["Please select", "Male", "Female"].index(st.session_state.sex) if st.session_state.sex else 0
    )
    st.session_state.social_activity = st.selectbox(
        "Social Activity", ["Please select", "never", "sometimes", "often"],
        index=["Please select", "never", "sometimes", "often"].index(st.session_state.social_activity) if st.session_state.social_activity else 0
    )
    st.session_state.diet = st.selectbox(
        "Diet", ["Please select", "omnivore", "vegetarian", "pescatarian", "vegan"],
        index=["Please select", "omnivore", "vegetarian", "pescatarian", "vegan"].index(st.session_state.diet) if st.session_state.diet else 0
    )

elif tab == "🚗 Travel":
    st.session_state.transport = st.selectbox(
        "Transportation", ["Please select", "private", "public", "walk/bicycle"],
        index=["Please select", "private", "public", "walk/bicycle"].index(st.session_state.transport) if st.session_state.transport else 0
    )
    st.session_state.vehicle_monthly_distance_km = st.slider(
        "Monthly vehicle distance (Km)", 0, 5000,
        value=st.session_state.vehicle_monthly_distance_km if st.session_state.vehicle_monthly_distance_km is not None else 0
    )
    st.session_state.air_travel_frequency = st.selectbox(
        "Air travel frequency", ["Please select", "never", "rarely", "frequently", "very frequently"],
        index=["Please select", "never", "rarely", "frequently", "very frequently"].index(st.session_state.air_travel_frequency) if st.session_state.air_travel_frequency else 0
    )

elif tab == "🗑 Waste":
    # Ensure the session state is initialized properly for multi-select
    if 'recycling' not in st.session_state:
        st.session_state.recycling = []

    st.session_state.recycling = st.multiselect(
        "Recycling materials",
        ['Metal', 'Paper', 'Plastic', 'Glass', 'Electronics'],
        default=st.session_state.recycling
    )

    st.session_state.waste_bag_size = st.selectbox(
        "Waste bag size", ["Please select", "small", "medium", "large", "extra large"],
        index=["Please select", "small", "medium", "large", "extra large"].index(st.session_state.waste_bag_size) if st.session_state.waste_bag_size else 0
    )
    st.session_state.waste_bag_weekly_count = st.number_input(
        "Weekly waste bag count", 1, 7,
        value=st.session_state.waste_bag_weekly_count if st.session_state.waste_bag_weekly_count is not None else 1
    )

elif tab == "⚡ Energy":
    st.session_state.heating_energy_source = st.selectbox(
        "Heating power source", ["Please select", "coal", "natural gas", "electricity", "wood"],
        index=["Please select", "coal", "natural gas", "electricity", "wood"].index(st.session_state.heating_energy_source) if st.session_state.heating_energy_source else 0
    )
    st.session_state.cooking_with = st.multiselect(
        "Cooking methods",
        ['Grill', 'Airfryer', 'Stove', 'Oven', 'Microwave'],
        default=st.session_state.cooking_with if st.session_state.cooking_with else []
    )
    st.session_state.energy_efficiency = st.selectbox(
        "Energy-efficient devices?", ["Please select", "Yes", "No"],
        index=["Please select", "Yes", "No"].index(st.session_state.energy_efficiency) if st.session_state.energy_efficiency else 0
    )
    st.session_state.tv_pc_daily_hours = st.slider(
        "Daily PC/TV usage (hours)", 0, 16,
        value=st.session_state.tv_pc_daily_hours if st.session_state.tv_pc_daily_hours is not None else 0
    )
    st.session_state.internet_daily_hours = st.slider(
        "Daily internet usage (hours)", 0, 16,
        value=st.session_state.internet_daily_hours if st.session_state.internet_daily_hours is not None else 0
    )

elif tab == "💊 Consumption":
    st.session_state.shower_frequency = st.selectbox(
        "Shower frequency", ["Please select", "daily", "twice a day", "less frequently", "more frequently"],
        index=["Please select", "daily", "twice a day", "less frequently", "more frequently"].index(st.session_state.shower_frequency) if st.session_state.shower_frequency else 0
    )
    st.session_state.monthly_grocery_bill = st.slider(
        "Monthly grocery bill ($)", 50, 299,
        value=st.session_state.monthly_grocery_bill if st.session_state.monthly_grocery_bill is not None else 50
    )
    st.session_state.new_clothes_monthly = st.slider(
        "New clothes bought monthly", 0, 25,
        value=st.session_state.new_clothes_monthly if st.session_state.new_clothes_monthly is not None else 0
    )

    if st.button("Track Your Carbon Footprint"):
        try:
            height = st.session_state.height
            weight = st.session_state.weight
            dropdowns = [
                st.session_state.sex, st.session_state.social_activity, st.session_state.diet,
                st.session_state.transport, st.session_state.air_travel_frequency,
                st.session_state.waste_bag_size, st.session_state.heating_energy_source,
                st.session_state.energy_efficiency, st.session_state.shower_frequency
            ]

            if not height or not weight:
                st.warning("Please enter both height and weight.")
            elif "Please select" in dropdowns:
                st.warning("Please fill all required dropdowns.")
            else:
                # --- Calculate Body Type ---
                bmi = weight / ((height / 100) ** 2)
                body_type = "underweight" if bmi < 18.5 else "normal" if bmi <= 24.9 else "overweight" if bmi <= 29.9 else "obese"

                # --- Prepare Data ---
                input_data = {
                    "body_type": body_type,
                    "gender": st.session_state.sex,
                    "diet": st.session_state.diet,
                    "shower_frequency": st.session_state.shower_frequency,
                    "heating_energy_source": st.session_state.heating_energy_source,
                    "transport": st.session_state.transport,
                    "social_activity": st.session_state.social_activity,
                    "monthly_grocery_bill": st.session_state.monthly_grocery_bill,
                    "air_travel_frequency": st.session_state.air_travel_frequency,
                    "vehicle_monthly_distance_km": st.session_state.vehicle_monthly_distance_km,
                    "waste_bag_size": st.session_state.waste_bag_size,
                    "waste_bag_weekly_count": st.session_state.waste_bag_weekly_count,
                    "tv_pc_daily_hours": st.session_state.tv_pc_daily_hours,
                    "new_clothes_monthly": st.session_state.new_clothes_monthly,
                    "internet_daily_hours": st.session_state.internet_daily_hours,
                    "recycling": str(st.session_state.recycling),
                    "energy_efficiency": st.session_state.energy_efficiency,
                    "cooking_with": str(st.session_state.cooking_with)
                }

                df = pd.DataFrame([input_data])

                def transform_multilabel(df, column_name, categories):
                    df = df.copy()
                    def parse(x):
                        if isinstance(x, list) or isinstance(x, np.ndarray):
                            return x
                        if isinstance(x, str):
                            return ast.literal_eval(x)
                        if pd.isnull(x):
                            return []
                        return []
                    for value in categories:
                        df[value] = df[column_name].apply(lambda x: int(value in parse(x)))
                    df.drop(columns=column_name, inplace=True)
                    return df

                df = transform_multilabel(df, 'recycling', dummy_info['recycling'])
                df = transform_multilabel(df, 'cooking_with', dummy_info['cooking_with'])

                ordinal_cols = ['body_type', 'shower_frequency', 'social_activity', 'air_travel_frequency', 'waste_bag_size', 'energy_efficiency']
                onehot_cols = ['gender', 'diet', 'heating_energy_source', 'transport']

                def transform_input(df_raw):
                    df = df_raw.copy()
                    X_transformed = preprocessor.transform(df)
                    ohe_feature_names = preprocessor.named_transformers_['onehot'].get_feature_names_out(onehot_cols)
                    all_feature_names = ordinal_cols + list(ohe_feature_names) + [col for col in df.columns if col not in ordinal_cols + onehot_cols]
                    X_df = pd.DataFrame(X_transformed, columns=all_feature_names)
                    X_df.reset_index(drop=True, inplace=True)
                    return X_df

                transformed_input = transform_input(df)
                transformed_input = transformed_input.reindex(columns=feature_order, fill_value=0)

                prediction = model.predict(transformed_input)
                st.success(f"🌱 Your estimated carbon footprint is: **{prediction[0]:.2f} units**")

                # Save prediction
                st.session_state.prediction = prediction[0]
                st.session_state.input_data = input_data
                # st.session_state.show_dashboard_button = True

                # Reset inputs
                for key in fields:
                    st.session_state[key] = None

        except Exception as e:
            st.error(f"An error occurred during Tracking: {str(e)}")
            import traceback
            st.error(traceback.format_exc())


