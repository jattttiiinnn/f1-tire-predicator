# import os
# import time
# import streamlit as st
# import pandas as pd
# from modules.predicator import predict_tire_degradation, recommend_pit_stop
# from modules.visualizer import create_degradation_chart

# # ---------------------------------------------------------------------
# # 🌍 Page Configuration
# # ---------------------------------------------------------------------
# st.set_page_config(
#     page_title="F1 Tire Strategy AI",
#     page_icon="🏎️",
#     layout="wide",
# )

# # ---------------------------------------------------------------------
# # 🏁 Title and Description
# # ---------------------------------------------------------------------
# st.title("🏎️ F1 Tire Strategy AI")
# st.markdown(
#     """
#     ### 🧠 Intelligent Race Strategy Assistant  
#     Using **FastF1 telemetry** and **Google Gemini AI**, this app predicts tire degradation,  
#     forecasts lap times, and recommends optimal pit stops during a race.
#     """
# )

# # ---------------------------------------------------------------------
# # 🎛️ Sidebar Controls
# # ---------------------------------------------------------------------
# # --- Sidebar Track Selector ---
# st.sidebar.header("⚙️ Race Settings")

# track = st.sidebar.selectbox(
#     "Select Track",
#     options=[
#         "Bahrain GP 2024",
#         "Monaco GP 2024",
#         "British GP 2024 (Silverstone)"
#     ],
#     index=0,
# )

# current_lap = st.sidebar.slider(
#     "Select Current Lap",
#     min_value=1,
#     max_value=57,
#     value=10,
# )

# st.sidebar.markdown("---")
# st.sidebar.subheader("📊 Telemetry Info")
# tire_age_placeholder = st.sidebar.empty()
# avg_deg_placeholder = st.sidebar.empty()
# track_temp_placeholder = st.sidebar.empty()

# st.sidebar.markdown("---")
# get_prediction = st.sidebar.button("🚀 Get Prediction")

# # --- Map track to corresponding data file ---
# TRACK_FILE_MAP = {
#     "Bahrain GP 2024": "data/bahrain_2024_hamilton.csv",
#     "Monaco GP 2024": "data/monaco_2024_hamilton.csv",
#     "British GP 2024 (Silverstone)": "data/silverstone_2024_hamilton.csv",
# }

# csv_file = TRACK_FILE_MAP.get(track)


# # ---------------------------------------------------------------------
# # 🖥️ Main Display Area
# # ---------------------------------------------------------------------
# st.markdown("---")

# if not get_prediction:
#     st.info("👋 Click **'Get Prediction'** in the sidebar to start analysis.")
# else:
#     csv_file = "data/bahrain_2024_hamilton.csv"
#     progress = st.progress(0)

#     # Check data file first
#     if not os.path.exists(csv_file):
#         st.error("❌ Data file not found: `data/bahrain_2024_hamilton.csv`. Please download race data first.")
#         st.stop()

#     try:
#         st.success(f"🏁 Selected Track: **{track}** — Lap **{current_lap}**")
#         st.markdown("### 🔄 Running AI Prediction...")

#         # -------------------------------------------------------------
#         # 1️⃣ Load Race Data
#         # -------------------------------------------------------------
#         progress.progress(20, text="📂 Loading race data...")
#         time.sleep(0.5)
#         df = pd.read_csv(csv_file)

#         if df.empty:
#             st.error("❌ Race data file is empty.")
#             st.stop()

#         # Extract quick telemetry insights
#         tire_age = int(df['tire_age'].iloc[-1]) if 'tire_age' in df.columns else "N/A"
#         avg_deg_rate = round(df['lap_time'].diff().mean(), 3) if 'lap_time' in df.columns else "N/A"
#         track_temp = "38°C (estimated)"  # Placeholder; could be real from telemetry

#         tire_age_placeholder.info(f"🧱 Tire Age: **{tire_age} laps**")
#         avg_deg_placeholder.info(f"📉 Avg Degradation Rate: **{avg_deg_rate} sec/lap**")
#         track_temp_placeholder.info(f"🌡️ Track Temp: **{track_temp}**")

#         # -------------------------------------------------------------
#         # 2️⃣ Analyze Patterns
#         # -------------------------------------------------------------
#         progress.progress(40, text="📊 Analyzing patterns...")
#         time.sleep(0.5)

#         # -------------------------------------------------------------
#         # 3️⃣ Get AI Prediction
#         # -------------------------------------------------------------
#         progress.progress(60, text="🧠 Getting AI prediction...")
#         result = predict_tire_degradation(
#             track_name=track,
#             current_lap=current_lap,
#             target_laps=15
#         )

#         if result["status"] != "success":
#             error_msg = result.get("error", "").lower()
#             if "api key" in error_msg:
#                 st.error("🔑 Missing or invalid API key. Please check your `.env` file.")
#             elif "api" in error_msg or "network" in error_msg:
#                 st.error("🌐 API call failed. Please check your internet connection or Gemini quota.")
#             elif "parse" in error_msg:
#                 st.error("⚠️ Failed to parse AI response. The output format may be invalid.")
#             else:
#                 st.error(f"❌ Prediction failed: {result.get('error', 'Unknown error')}")
#             st.stop()

#         predictions = result["predictions"]
#         reasoning = result["reasoning"]

#         if not predictions:
#             st.warning("⚠️ No prediction data returned by AI.")
#             st.stop()

#         # -------------------------------------------------------------
#         # 4️⃣ Generate Visualization
#         # -------------------------------------------------------------
#         progress.progress(80, text="📈 Generating visualization...")
#         time.sleep(0.5)

#         st.subheader("📊 Predicted Lap Times (first 5)")
#         for p in predictions[:5]:
#             lap = p.get("lap")
#             time_ = p.get("predicted_time")
#             conf = p.get("confidence")
#             st.write(f"**Lap {lap}:** {time_:.3f} sec  |  Confidence: {conf:.2f}")

#         # Pit stop analysis
#         pit_result = recommend_pit_stop(predictions, threshold=2.0)

#         # -------------------------------------------------------------
#         # 🔥 Styled Pit Stop Recommendation Card
#         # -------------------------------------------------------------
#         st.markdown(
#             """
#             <style>
#             .pit-card {
#                 background: linear-gradient(145deg, #ffe8e6, #fff4f3);
#                 border: 3px solid #ff4d4d;
#                 border-radius: 16px;
#                 padding: 20px 25px;
#                 box-shadow: 0 4px 15px rgba(255, 0, 0, 0.25);
#                 margin-bottom: 25px;
#             }
#             .pit-header {
#                 font-size: 1.4rem;
#                 font-weight: 700;
#                 color: #d40000;
#                 display: flex;
#                 align-items: center;
#                 gap: 10px;
#                 margin-bottom: 10px;
#             }
#             .pit-lap {
#                 font-size: 2.2rem;
#                 font-weight: 800;
#                 color: #b30000;
#                 margin: 10px 0;
#             }
#             .pit-window {
#                 font-size: 1.1rem;
#                 color: #8b0000;
#                 margin-bottom: 8px;
#             }
#             .pit-reason {
#                 font-size: 1rem;
#                 color: #333;
#                 line-height: 1.5;
#                 background: rgba(255, 220, 220, 0.4);
#                 padding: 10px;
#                 border-radius: 8px;
#             }
#             </style>
#             """,
#             unsafe_allow_html=True
#         )

#         st.markdown(
#             f"""
#             <div class="pit-card">
#                 <div class="pit-header">⚠️ PIT STOP RECOMMENDATION</div>
#                 <div class="pit-lap">Lap {pit_result['recommended_lap']}</div>
#                 <div class="pit-window">Pit Window: {pit_result['window'][0]}–{pit_result['window'][1]}</div>
#                 <div class="pit-reason">
#                     💡 <b>Reasoning:</b> {pit_result['reasoning']}
#                     <br>
#                     🕒 <b>Estimated Time Lost if No Pit:</b> {pit_result['time_lost']:.2f}s
#                 </div>
#             </div>
#             """,
#             unsafe_allow_html=True
#         )

#         # AI reasoning section
#         st.subheader("🧠 AI Analysis Summary")
#         st.write(reasoning)

#         # Degradation chart
#         st.subheader("📈 Predicted Tire Degradation Trend")
#         fig = create_degradation_chart(predictions)
#         st.plotly_chart(fig, use_container_width=True)

#         # -------------------------------------------------------------
#         # ✅ Complete
#         # -------------------------------------------------------------
#         progress.progress(100, text="✅ Complete!")
#         st.success("🏆 Prediction and analysis completed successfully!")

#     except Exception as e:
#         st.error(f"❌ An unexpected error occurred: {e}")
#         st.stop()

# # ---------------------------------------------------------------------
# # 💡 Footer
# # ---------------------------------------------------------------------
# st.markdown("---")
# st.caption("Developed with ❤️ using Streamlit, FastF1, and Gemini AI")


import streamlit as st
import pandas as pd
import io
from datetime import datetime

from modules.predicator import predict_tire_degradation, recommend_pit_stop, compare_strategies
from modules.visualizer import create_degradation_chart

# ---------------------------------------------------------------------
# 🌍 Page Configuration
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="F1 Tire Strategy AI",
    page_icon="🏎️",
    layout="centered",
)

# ---------------------------------------------------------------------
# 🏁 Title and Description
# ---------------------------------------------------------------------
st.title("🏎️ F1 Tire Strategy AI")
st.markdown(
    """
    ### 🧠 Intelligent Race Strategy Assistant  
    Predict tire degradation, pit stop timing, and compare 1-stop vs 2-stop strategies
    using FastF1 telemetry and Google Gemini AI.
    """
)

# ---------------------------------------------------------------------
# 🎛️ Sidebar Controls
# ---------------------------------------------------------------------
st.sidebar.header("⚙️ Race Settings")

track = st.sidebar.selectbox(
    "Select Track",
    options=["Bahrain GP 2024", "Monaco GP 2024", "British GP 2024 (Silverstone)"],
    index=0,
)

track_map = {
    "Bahrain GP 2024": "data/bahrain_2024_hamilton.csv",
    "Monaco GP 2024": "data/monaco_2024_hamilton.csv",
    "British GP 2024 (Silverstone)": "data/silverstone_2024_hamilton.csv",
}

csv_file = track_map[track]

current_lap = st.sidebar.slider(
    "Select Current Lap",
    min_value=1,
    max_value=57,
    value=15,
)

show_strategy = st.sidebar.checkbox("📊 Show strategy comparison")

get_prediction = st.sidebar.button("🚀 Get Prediction")

# ---------------------------------------------------------------------
# 🖥️ Main Area
# ---------------------------------------------------------------------
st.markdown("---")

if not get_prediction:
    st.info("👋 Click **'Get Prediction'** to start analysis.")
else:
    try:
        with st.spinner("Analyzing race data and generating prediction..."):
            result = predict_tire_degradation(track, current_lap=current_lap, target_laps=15)
            if result["status"] != "success":
                raise RuntimeError(result.get("error", "Unknown error."))

            predictions = result["predictions"]
            reasoning = result["reasoning"]

            # --- Pit Stop Recommendation ---
            st.subheader("🛠️ Pit Stop Recommendation")
            pit_result = recommend_pit_stop(predictions, threshold=2.0)

            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(145deg, #ffe8e6, #fff4f3);
                    border: 3px solid #ff4d4d;
                    border-radius: 16px;
                    padding: 20px 25px;
                    box-shadow: 0 4px 15px rgba(255, 0, 0, 0.25);
                    margin-bottom: 25px;">
                    <h3 style="color:#b30000;">⚠️ PIT STOP RECOMMENDATION</h3>
                    <h1 style="color:#d40000;">Lap {pit_result['recommended_lap']}</h1>
                    <p><b>Pit Window:</b> {pit_result['window'][0]}–{pit_result['window'][1]}</p>
                    <p><b>Reasoning:</b> {pit_result['reasoning']}</p>
                    <p><b>Estimated Time Lost:</b> {pit_result['time_lost']:.2f}s</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # --- Strategy Comparison ---
            if show_strategy:
                st.subheader("🧩 Strategy Comparison")
                strategy_result = compare_strategies(csv_file, current_lap=current_lap)

                if strategy_result["status"] == "success":
                    strategies = pd.DataFrame(strategy_result["strategies"])
                    st.dataframe(strategies[["name", "pit_laps", "finish_time", "pros", "cons"]])
                    st.success(f"🏆 **Recommended Strategy:** {strategy_result['recommended']}")
                else:
                    st.warning(f"⚠️ Failed to generate strategy comparison: {strategy_result['error']}")

            # --- AI Reasoning ---
            st.markdown("---")
            st.subheader("🧠 AI Reasoning Summary")
            st.write(reasoning)

            # --- Chart ---
            st.markdown("---")
            st.subheader("📈 Predicted Tire Degradation Trend")

            fig = create_degradation_chart(predictions)
            st.plotly_chart(fig, use_container_width=True)

            # ---------------------------------------------------------------------
            # 📥 Export Section
            # ---------------------------------------------------------------------
            st.markdown("---")
            st.subheader("📦 Export & Report")

            try:
                predictions_df = pd.DataFrame(predictions)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                csv_buffer = io.StringIO()
                predictions_df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()

                st.download_button(
                    label="⬇️ Download Predictions CSV",
                    data=csv_data,
                    file_name=f"predictions_{track.replace(' ', '_')}_lap{current_lap}.csv",
                    mime="text/csv",
                )

                st.button("📄 Download Report PDF (Coming Soon)", disabled=True)

                st.caption(f"🕒 Prediction generated at: {timestamp}")

            except Exception as e:
                st.warning(f"⚠️ Could not prepare export: {e}")

            # --- Success message ---
            st.success("✅ Analysis complete!")

    except FileNotFoundError:
        st.error("❌ Data file not found. Please download race data first.")
    except KeyError:
        st.error("❌ Missing API key. Check your .env and config.py.")
    except Exception as e:
        st.error(f"❌ Prediction failed: {e}")

# ---------------------------------------------------------------------
# 💡 Footer
# ---------------------------------------------------------------------
st.markdown("---")
st.caption("Developed with ❤️ using Streamlit, FastF1, and Gemini AI")
