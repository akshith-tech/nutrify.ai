"""
Nutrify AI – Intelligent Nutrition & Meal Planning Assistant
Single-file Streamlit + FastAPI / Integrated backend application using OpenRouter API.
Run via: streamlit run <filename>.py
"""

import os
import json
import time
from datetime import datetime
import streamlit as st
import pandas as pd
from openai import OpenAI

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="Nutrify AI – Intelligent Nutrition & Meal Planning Assistant",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- OpenRouter Client Setup ---
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY",
)

MODEL_NAME = "openai/gpt-4o"  # Or use another supported OpenRouter model

# --- Session State Initialization ---
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "name": "Alex Smith",
        "age": 28,
        "gender": "Male",
        "height_cm": 178,
        "weight_kg": 75,
        "goal": "Muscle Gain",
        "diet": "Non-Veg",
        "activity": "Moderate (3-5 days/week)",
        "allergies": "None",
        "medical_conditions": "None",
        "calorie_target": 2500,
        "water_target_ml": 3000
    }

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hello! I am your Nutrify AI Nutrition Coach. How can I help you reach your health goals today?"}
    ]

if "water_intake" not in st.session_state:
    st.session_state.water_intake = 1500

if "progress_logs" not in st.session_state:
    st.session_state.progress_logs = [
        {"date": "2026-07-25", "weight": 75.5, "calories": 2400, "water": 2500},
        {"date": "2026-07-26", "weight": 75.4, "calories": 2450, "water": 2800},
        {"date": "2026-07-27", "weight": 75.2, "calories": 2300, "water": 3000},
        {"date": "2026-07-28", "weight": 75.0, "calories": 2500, "water": 3100},
        {"date": "2026-07-29", "weight": 75.0, "calories": 2400, "water": 2900},
        {"date": "2026-07-30", "weight": 74.9, "calories": 2550, "water": 3000},
        {"date": "2026-07-31", "weight": 74.8, "calories": 2480, "water": 3200},
    ]

# --- Helper AI Caller ---
def query_ai(prompt, system_prompt="You are an expert AI nutrition coach, dietitian, and fitness expert."):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error communicating with AI service: {str(e)}"

# --- Sidebar Navigation ---
st.sidebar.title("🥗 Nutrify AI")
st.sidebar.markdown(f"**Welcome, {st.session_state.user_profile['name']}!**")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "AI Chat Assistant",
        "User Profile",
        "Meal Planner",
        "Recipe Generator",
        "Nutrition Analyzer",
        "Hydration Tracker",
        "Progress & Goals",
        "Food Substitution",
        "Settings"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Stats")
st.sidebar.metric("Goal", st.session_state.user_profile["goal"])
st.sidebar.metric("Calorie Target", f"{st.session_state.user_profile['calorie_target']} kcal")
st.sidebar.metric("Water Logged", f"{st.session_state.water_intake} ml")

# ===========================================================
# 1. DASHBOARD MODULE
# ===========================================================
if page == "Dashboard":
    st.title("📊 Nutrify AI Dashboard")
    st.markdown("Your daily overview, nutritional intake, and health metrics.")

    p = st.session_state.user_profile
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Weight", f"{p['weight_kg']} kg", "-0.1 kg this week")
    with col2:
        bmi = round(p['weight_kg'] / ((p['height_cm'] / 100) ** 2), 1)
        st.metric("BMI", bmi, "Normal")
    with col3:
        st.metric("Calories Today", "2,150 kcal", f"Target: {p['calorie_target']}")
    with col4:
        st.metric("Water Intake", f"{st.session_state.water_intake} ml", f"Target: {p['water_target_ml']} ml")

    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🔥 Today's Meal Breakdown")
        st.info("**Breakfast:** Oatmeal with Berries & Whey Protein (450 kcal)\n\n"
                "**Lunch:** Grilled Chicken Breast, Quinoa, and Roasted Veggies (650 kcal)\n\n"
                "**Snack:** Greek Yogurt with Almonds (300 kcal)\n\n"
                "**Dinner:** Baked Salmon with Asparagus and Sweet Potato (750 kcal)")
    
    with col_b:
        st.subheader("📈 Weekly Weight Trend")
        df_progress = pd.DataFrame(st.session_state.progress_logs)
        st.line_chart(df_progress.set_index("date")["weight"])

    st.markdown("### 💡 Daily AI Health Tip")
    tip_prompt = f"Give a short, punchy, actionable nutrition or fitness tip for someone whose goal is {p['goal']}."
    if "daily_tip" not in st.session_state:
        st.session_state.daily_tip = query_ai(tip_prompt)
    st.success(st.session_state.daily_tip)

# ===========================================================
# 2. AI CHAT ASSISTANT MODULE
# ===========================================================
elif page == "AI Chat Assistant":
    st.title("💬 AI Nutrition Coach")
    st.markdown("Ask anything about diet, meal plans, nutrients, or health conditions.")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask your nutrition coach...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                context_profile = json.dumps(st.session_state.user_profile)
                system_msg = f"You are Nutrify AI, an expert nutrition coach. User Profile: {context_profile}. Provide helpful, medically sound, and practical nutrition advice."
                
                # Format recent history for API
                messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history[-6:]]
                messages.insert(0, {"role": "system", "content": system_msg})
                
                try:
                    res = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=messages,
                        max_tokens=1000,
                    )
                    reply = res.choices[0].message.content
                except Exception as e:
                    reply = f"Error: {str(e)}"
                
                st.markdown(reply)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})

# ===========================================================
# 3. USER PROFILE MODULE
# ===========================================================
elif page == "User Profile":
    st.title("👤 User Profile & Health Settings")
    st.markdown("Update your personal and biometric information to recalculate your nutritional goals.")

    p = st.session_state.user_profile
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", p["name"])
            age = st.number_input("Age", 10, 100, p["age"])
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(p["gender"]))
            height = st.number_input("Height (cm)", 100, 250, p["height_cm"])
            weight = st.number_input("Weight (kg)", 30, 200, p["weight_kg"])
        
        with col2:
            goal = st.selectbox("Fitness Goal", ["Weight Loss", "Weight Gain", "Muscle Gain", "Healthy Lifestyle", "Blood Sugar Control"], index=0)
            diet = st.selectbox("Dietary Preference", ["Non-Veg", "Vegetarian", "Vegan", "Eggitarian"], index=0)
            activity = st.selectbox("Daily Activity Level", ["Sedentary", "Light (1-2 days/week)", "Moderate (3-5 days/week)", "Very Active (6-7 days)"], index=2)
            allergies = st.text_input("Allergies", p["allergies"])
            medical = st.text_input("Medical Conditions", p["medical_conditions"])

        submitted = st.form_submit_button("Save & Recalculate Profile")
        if submitted:
            st.session_state.user_profile.update({
                "name": name,
                "age": age,
                "gender": gender,
                "height_cm": height,
                "weight_kg": weight,
                "goal": goal,
                "diet": diet,
                "activity": activity,
                "allergies": allergies,
                "medical_conditions": medical
            })
            # Simple BMR & Calorie estimation logic
            bmr = 10 * weight + 6.25 * height - 5 * age + (5 if gender == "Male" else -161)
            multiplier = 1.2 if "Sedentary" in activity else (1.375 if "Light" in activity else (1.55 if "Moderate" in activity else 1.725))
            tdee = int(bmr * multiplier)
            if goal == "Weight Loss":
                target = tdee - 500
            elif goal in ["Weight Gain", "Muscle Gain"]:
                target = tdee + 400
            else:
                target = tdee
            
            st.session_state.user_profile["calorie_target"] = target
            st.success("Profile updated and daily targets successfully recalculated!")

# ===========================================================
# 4. MEAL PLANNER MODULE
# ===========================================================
elif page == "Meal Planner":
    st.title("🍽️ AI Daily & Weekly Meal Planner")
    st.markdown("Generate custom meals tailored precisely to your macro and dietary requirements.")

    plan_type = st.selectbox("Select Plan Duration", ["Single Day", "7-Day Weekly Plan"])
    
    if st.button("Generate Meal Plan"):
        with st.spinner("Generating personalized meal plan with AI..."):
            p = st.session_state.user_profile
            prompt = f"""Generate a {plan_type} meal plan for a {p['age']} year old {p['gender']}, 
            weight {p['weight_kg']}kg, goal: {p['goal']}, diet: {p['diet']}, 
            calorie target: {p['calorie_target']} kcal, allergies: {p['allergies']}. 
            Include Breakfast, Lunch, Dinner, Snacks, and pre/post workout meals with macros (Calories, Protein, Carbs, Fat) and recipes."""
            
            response = query_ai(prompt, "You are an expert sports nutritionist.")
            st.session_state.generated_meal_plan = response

    if "generated_meal_plan" in st.session_state:
        st.markdown("---")
        st.markdown(st.session_state.generated_meal_plan)

# ===========================================================
# 5. RECIPE GENERATOR MODULE
# ===========================================================
elif page == "Recipe Generator":
    st.title("🍲 AI Recipe Generator")
    
    with st.form("recipe_form"):
        ingredients = st.text_input("Available Ingredients (comma separated)", "Chicken breast, broccoli, garlic, olive oil, rice")
        prep_time = st.slider("Max Preparation Time (minutes)", 10, 90, 30)
        cuisine = st.selectbox("Cuisine Preference", ["Any", "Mediterranean", "Asian", "Mexican", "Indian", "American"])
        
        gen_recipe = st.form_submit_button("Create Recipe")
        if gen_recipe:
            with st.spinner("Cooking up a custom recipe..."):
                prompt = f"Create a delicious recipe using these ingredients: {ingredients}. Max prep time: {prep_time} mins, Cuisine: {cuisine}. Include ingredients list, step-by-step instructions, and nutritional breakdown."
                st.session_state.last_recipe = query_ai(prompt)

    if "last_recipe" in st.session_state:
        st.markdown("---")
        st.markdown(st.session_state.last_recipe)

# ===========================================================
# 6. NUTRITION ANALYZER MODULE
# ===========================================================
elif page == "Nutrition Analyzer":
    st.title("🔍 Instant Food Nutrition Analyzer")
    st.markdown("Type what you ate or plan to eat, and get an instant breakdown.")

    food_item = st.text_area("What did you eat?", "I ate 2 boiled eggs, 1 banana, and a bowl of oatmeal with milk.")
    if st.button("Analyze Nutrition"):
        with st.spinner("Analyzing nutrients..."):
            prompt = f"Analyze the nutritional content of the following meal: '{food_item}'. Provide estimated total Calories, Protein, Carbs, Fat, Fiber, Vitamins, Minerals, and health suggestions."
            analysis = query_ai(prompt)
            st.markdown("### Analysis Results")
            st.markdown(analysis)

# ===========================================================
# 7. HYDRATION TRACKER MODULE
# ===========================================================
elif page == "Hydration Tracker":
    st.title("💧 Hydration & Water Tracker")
    
    target = st.session_state.user_profile.get("water_target_ml", 3000)
    current = st.session_state.water_intake
    
    progress = min(current / target, 1.0)
    st.progress(progress)
    st.markdown(f"**Current Intake:** {current} ml / **Daily Target:** {target} ml")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("+ 250 ml"):
            st.session_state.water_intake += 250
            st.rerun()
    with col2:
        if st.button("+ 500 ml"):
            st.session_state.water_intake += 500
            st.rerun()
    with col3:
        if st.button("Reset Water"):
            st.session_state.water_intake = 0
            st.rerun()

# ===========================================================
# 8. PROGRESS & GOALS MODULE
# ===========================================================
elif page == "Progress & Goals":
    st.title("📈 Progress Tracker & Goal Management")
    
    st.subheader("Log Today's Weight")
    with st.form("progress_form"):
        new_weight = st.number_input(
            "Weight (kg)",
            min_value=30.0,
            max_value=200.0,
            value=float(st.session_state.user_profile["weight_kg"])
        )
        log_date = st.date_input("Date", datetime.today())
        log_submitted = st.form_submit_button("Log Progress")
        
        if log_submitted:
            st.session_state.progress_logs.append({
                "date": str(log_date),
                "weight": new_weight,
                "calories": st.session_state.user_profile["calorie_target"],
                "water": st.session_state.water_intake
            })
            st.session_state.user_profile["weight_kg"] = new_weight
            st.success("Progress logged successfully!")

    st.markdown("---")
    st.subheader("Historical Log")
    df = pd.DataFrame(st.session_state.progress_logs)
    st.dataframe(df, use_container_width=True)

# ===========================================================
# 9. FOOD SUBSTITUTION MODULE
# ===========================================================
elif page == "Food Substitution":
    st.title("🔄 AI Food Substitution Engine")
    st.markdown("Missing an ingredient? Find smart healthy swaps instantly.")

    missing_food = st.text_input("What ingredient do you need to substitute?", "Chicken breast")
    diet_pref = st.selectbox("Diet Context", ["General", "Vegan", "Vegetarian", "Gluten-Free", "Dairy-Free"])

    if st.button("Find Substitutes"):
        with st.spinner("Finding best substitutes..."):
            prompt = f"Suggest the best healthy substitutes for '{missing_food}' keeping in mind a '{diet_pref}' diet constraint. Provide nutritional equivalents and usage tips."
            subs = query_ai(prompt)
            st.markdown(subs)

# ===========================================================
# 10. SETTINGS MODULE
# ===========================================================
elif page == "Settings":
    st.title("⚙️ App Settings")
    st.markdown("Configure preferences and system options.")

    st.toggle("Dark Mode", value=True)
    st.selectbox("Language", ["English", "Spanish", "French", "German", "Mandarin"])
    st.toggle("Enable Push Notifications", value=True)
    
    st.markdown("---")
    st.markdown("### System Information")
    st.info("**Nutrify AI v2.6.0** — Production Ready\n\nConnected via OpenRouter API Gateway.")
