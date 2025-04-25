import streamlit as st
import pickle
import pandas as pd
import numpy as np

# Load model & encoders
with open('models/ensemble_model.pkl', 'rb') as ensemble:
    model = pickle.load(ensemble)

with open('models/dummy_info.pkl', 'rb') as dummy:
    dummy_info = pickle.load(dummy)

with open('models/preprocessor.pkl', 'rb') as process:
    preprocess = pickle.load(process)

with open('models/selected_features.pkl', 'rb') as features:
    selected_features = pickle.load(features)

st.title("🌍 Carbon Footprint Calculator")

# Tabs
tabs = ["👤 Personal", "🚗 Travel", "🗑 Waste", "⚡ Energy", "💊 Consumption"]
tab = st.radio("Navigator", tabs, horizontal=True)

# Ensure safe default initialization
for key in ["height", "weight", "sex", "social_activity", "diet",
            "transport", "vehicle_monthly_distance_km", "air_travel_frequency",
            "waste_bag_size", "waste_bag_weekly_count", "recycling",
            "heating_energy_source", "cooking_with", "energy_efficiency",
            "tv_pc_daily_hours", "internet_daily_hours",
            "shower_frequency", "monthly_grocery_bill", "new_clothes_monthly"]:
    if key not in st.session_state:
        st.session_state[key] = None

# TABS
if tab == "👤 Personal":
    st.session_state.height = st.number_input("Height (cm)", 100, 250)
    st.session_state.weight = st.number_input("Weight (kg)", 20, 300)
    st.session_state.sex = st.selectbox("Sex", ["Please select", "Male", "Female"])
    st.session_state.social_activity = st.selectbox("Social Activity", ["Please select", "never", "sometimes", "often"])
    st.session_state.diet = st.selectbox("Diet", ["Please select", "omnivore", "vegetarian", "pescatarian", "vegan"])

elif tab == "🚗 Travel":
    st.session_state.transport = st.selectbox("Transportation", ["Please select", "private", "public", "walk/bicycle"])
    st.session_state.vehicle_monthly_distance_km = st.slider("Monthly vehicle distance (Km)", 0, 5000, 0)
    st.session_state.air_travel_frequency = st.selectbox("Air travel frequency", ["Please select", "never", "rarely", "frequently", "very frequently"])

elif tab == "🗑 Waste":
    st.session_state.waste_bag_size = st.selectbox("Waste bag size", ["Please select", "small", "medium", "large", "extra large"])
    st.session_state.waste_bag_weekly_count = st.number_input("Weekly waste bag count", 1, 7, 1)
    st.session_state.recycling = st.multiselect("Recycling materials", ['Metal', 'Paper', 'Plastic', 'Glass', 'Electronics'])

elif tab == "⚡ Energy":
    st.session_state.heating_energy_source = st.selectbox("Heating power source", ["Please select", "coal", "natural gas", "electricity", "wood"])
    st.session_state.cooking_with = st.multiselect("Cooking methods", ['Grill', 'Airfryer', 'Stove', 'Oven', 'Microwave'])
    st.session_state.energy_efficiency = st.selectbox("Energy-efficient devices?", ["Please select", "Yes", "No"])
    st.session_state.tv_pc_daily_hours = st.slider("Daily PC/TV usage (hours)", 0, 16, 0)
    st.session_state.internet_daily_hours = st.slider("Daily internet usage (hours)", 0, 16, 0)

elif tab == "💊 Consumption":
    st.session_state.shower_frequency = st.selectbox("Shower frequency", ["Please select", "daily", "twice a day", "less frequently", "more frequently"])
    st.session_state.monthly_grocery_bill = st.slider("Monthly grocery bill ($)", 50, 299, 50)
    st.session_state.new_clothes_monthly = st.slider("New clothes bought monthly", 0, 25, 0)

    if st.button("Calculate Carbon Footprint"):
        height = st.session_state.height
        weight = st.session_state.weight

        if not height or not weight:
            st.warning("Please enter both height and weight.")
        elif "Please select" in [st.session_state.sex, st.session_state.social_activity, st.session_state.diet,
                                 st.session_state.transport, st.session_state.air_travel_frequency,
                                 st.session_state.waste_bag_size, st.session_state.heating_energy_source,
                                 st.session_state.energy_efficiency, st.session_state.shower_frequency]:
            st.warning("Please fill all required dropdowns.")
        else:
            # BMI & Body Type
            bmi = weight / ((height / 100) ** 2)
            body_type = "underweight" if bmi < 18.5 else "normal" if bmi <= 24.9 else "overweight" if bmi <= 29.9 else "obese"

        try:
            # Input Data
            df = pd.DataFrame([{
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
                "recycling": [st.session_state.recycling],
                "energy_efficiency": st.session_state.energy_efficiency,
                "cooking_with": [st.session_state.cooking_with]
            }])

            # Store and remove multi-label fields before preprocessing
            multi_label_cols = {"recycling": df["recycling"][0], "cooking_with": df["cooking_with"][0]}
            df = df.drop(columns=["recycling", "cooking_with"])

            # Step 1: Preprocess base columns
            df_transformed = preprocess.transform(df)
            df_final = pd.DataFrame(df_transformed, columns=preprocess.get_feature_names_out())

            # Step 2: Add multi-label dummy features with all expected columns
            for col, categories in dummy_info.items():
                for cat in categories:
                    df_final[cat] = 1 if cat in multi_label_cols.get(col, []) else 0

            # Step 3: Ensure all expected columns exist
            for col in selected_features:
                if col not in df_final.columns:
                    df_final[col] = 0  # Add any missing feature as 0

            # Step 4: Reorder columns to match training
            df_final = df_final[selected_features]

            # Step 5: Predict
            prediction = model.predict(df_final)[0]
            st.success(f"Your estimated carbon footprint is: **{round(prediction, 2)} kg CO2e/month**")

        except Exception as e:
            st.error(f"Something went wrong during prediction: {e}")
