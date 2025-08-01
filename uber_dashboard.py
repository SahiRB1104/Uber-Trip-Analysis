
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error
from sklearn.metrics import r2_score
from prophet import Prophet


st.set_page_config(page_title="Uber Trips Dashboard", layout="wide", page_icon="🚕")


st.markdown("""
<style>
    .main-header { font-size: 36px; color: #1E88E5; text-align: center; }
    .sub-header { font-size: 24px; color: #0D47A1; border-bottom: 2px solid #1E88E5; padding-bottom: 10px; }
    .metric-card { background-color: #f0f2f6; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px; }
    .metric-value { font-size: 32px; font-weight: bold; }
    .metric-label { font-size: 14px; color: #555; }
</style>
""", unsafe_allow_html=True)

@st.cache_data

def load_data():
    df = pd.read_csv("UberDataset_In1.csv")
    
    df['START_DATE'] = pd.to_datetime(df['START_DATE'], errors='coerce')
    df['END_DATE'] = pd.to_datetime(df['END_DATE'], errors='coerce')
    df['Duration(min)'] = (df['END_DATE'] - df['START_DATE']).dt.total_seconds() / 60
    df['Date'] = df['START_DATE'].dt.date
    df['Hour'] = df['START_DATE'].dt.hour
    df['Weekday'] = df['START_DATE'].dt.day_name()

    df['Same Route'] = df.duplicated(subset=['START', 'STOP'], keep=False)
    df['Repeated_Route'] = df.duplicated(subset=['START', 'STOP'], keep='first')
    df['Is_Business'] = df['PURPOSE'].str.lower().str.contains('meeting|customer|business', na=False)
    df['Is_Errand'] = df['PURPOSE'].str.lower().str.contains('errand|personal', na=False)
    df['Is_Airport_Trip'] = df['CATEGORY'].str.lower().str.contains('airport', na=False)
    df['Is_Meal_Trip'] = df['PURPOSE'].str.lower().str.contains('meal|lunch|dinner|breakfast|food', na=False)


    return df

df = load_data()
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# --- Check Missing Values Section ---
with st.expander("🔍 Check Missing Values"):
    st.markdown("### Null Value Report")
    
    missing = df.isnull().sum()
    total_missing = missing.sum()

    if total_missing > 0:
        st.warning(f"⚠️ Found {total_missing} missing values in the dataset.")
        st.dataframe(
            missing[missing > 0]
            .reset_index()
            .rename(columns={"index": "Column", 0: "Missing Values"})
        )
        
        original_columns = df.columns.tolist()  
        st.markdown("#### Rows with Missing Data:")
        st.dataframe(df[df.isnull().any(axis=1)][original_columns])
        

       
        st.markdown("#### Handle Missing Data")
        action = st.radio("Choose how to handle missing data:", ["Do Nothing", "Drop Rows"])

        if action == "Drop Rows":
            df.dropna(inplace=True)
            st.success("✅ Dropped all rows with missing values.")
        
            
    else:
        st.success("✅ No missing values found in the dataset.")


# --- Sidebar ---
with st.sidebar:
    st.image("https://i.ytimg.com/vi/tdhGqnBD2PU/maxresdefault.jpg", width=300)
    st.title("Uber Trip Dashboard")
    min_date = df['START_DATE'].min().date()
    max_date = df['START_DATE'].max().date()
    date_range = st.date_input("Filter by Date Range", [min_date, max_date])


    st.subheader("Filter Options")
    hour_range = st.slider("Select Hour Range", 0, 23, (0, 23))
    st.markdown("## Welcome to the Uber Trip Dashboard!")
    st.markdown("""
        This dashboard provides insights into Uber trip data, including trip trends, predictions, and visual analytics.
        Use the filters to customize the data view and explore various metrics and visualizations.
    """)
    st.info("🚕 Analyze trip data, predict future trends, and compare machine learning models for trip duration.")
    st.markdown("### Developed By:")
    st.info("603-Sahil Bhalekar")
    st.info("604-Jash Bheda")
    st.info("607-Om Chavan")
filtered_df = df[
    (df['START_DATE'].dt.date >= date_range[0]) &
    (df['START_DATE'].dt.date <= date_range[1]) &
    (df['Hour'] >= hour_range[0]) &
    (df['Hour'] <= hour_range[1])
]
# --- Header & Metrics ---
st.markdown("<h1 class='main-header'>Uber Trips Dashboard</h1>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
        st.markdown(f"<div class='metric-card'><p class='metric-label'>Total Trips</p><p class='metric-value'>{len(filtered_df)}</p></div>", unsafe_allow_html=True)
with col2:
        st.markdown(f"<div class='metric-card'><p class='metric-label'>Total Miles</p><p class='metric-value'>{filtered_df['MILES'].sum():.2f}</p></div>", unsafe_allow_html=True)
with col3:
        st.markdown(f"<div class='metric-card'><p class='metric-label'>Avg Duration (min)</p><p class='metric-value'>{filtered_df['Duration(min)'].mean():.2f}</p></div>", unsafe_allow_html=True)


# ---------------------- TAB LAYOUT ----------------------
tab1, tab2, tab3, tab4, = st.tabs([
    "\U0001F4CA Trip Duration & Features",
    "\U0001F52E Predict Future Trips",
    "\U0001F916 ML insights",
    "\U0001F4BB ML models",
])



with tab1:
    st.header("\U0001F4CA Trip Duration &  Features")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Trip Duration Distribution (in minutes)")
        fig = px.histogram(filtered_df, x='Duration(min)', nbins=50, title="Distribution of Trip Duration")
        st.plotly_chart(fig, use_container_width=True)


    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Trips by Hour of Day")
        fig = px.histogram(filtered_df, x='Hour', title="Number of Trips by Pickup Hour")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("Trips by Day of Month")
        filtered_df['Day'] = filtered_df['START_DATE'].dt.day
        fig = px.histogram(filtered_df, x='Day', title="Number of Trips by Day of Month")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Trips by Weekday")
    fig = px.histogram(filtered_df, x='Weekday', title="Number of Trips by Weekday")
    st.plotly_chart(fig, use_container_width=True)


    st.subheader("Same Route vs Unique Route")
    same_route_counts = filtered_df['Same Route'].value_counts().rename({True: 'Same Route', False: 'Different Route'})
    fig = px.pie(names=same_route_counts.index, values=same_route_counts.values, title="Same vs Different Routes", hole=0.3)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Trip Purposes")
    purpose_counts = filtered_df[['Is_Business', 'Is_Errand']].sum().rename(index={'Is_Business': 'Business', 'Is_Errand': 'Task'})
    fig = px.bar(purpose_counts, x=purpose_counts.index, y=purpose_counts.values, title="Purpose-based Trip Counts", text=purpose_counts.values)
    st.plotly_chart(fig, use_container_width=True)


# --- Tab 2: Predict Future Trips ---
with tab2:
    st.markdown("<h2 class='sub-header'>\U0001F52E Predict Future Trips (Prophet)</h2>", unsafe_allow_html=True)

    
    trip_df = filtered_df.groupby('Date').size().reset_index(name='y')
    trip_df.rename(columns={'Date': 'ds'}, inplace=True)

    
    from prophet import Prophet
    model = Prophet(daily_seasonality=True)
    model.fit(trip_df)

   
    days_ahead = st.slider("Days to Predict Ahead", 1, 10, 3)
    future = model.make_future_dataframe(periods=days_ahead)
    forecast = model.predict(future)

    forecast_result = forecast[['ds', 'yhat']].tail(days_ahead)
    forecast_result['Predicted Trips'] = forecast_result['yhat'].round().astype(int)
    forecast_result = forecast_result[['ds', 'Predicted Trips']]
    forecast_result.columns = ['Date', 'Predicted Trips']
    st.dataframe(forecast_result.set_index("Date"))

    
    fig = px.line(forecast_result, x='Date', y='Predicted Trips', title="Forecast of Uber Trips")
    st.plotly_chart(fig, use_container_width=True)

    


# --- Tab 3: Visual Insights ---
with tab3:
    st.markdown("<h2 class='sub-header'>\U0001F916 Insights</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.pie(filtered_df, names='PURPOSE', title="Trips by Purpose")
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.bar(filtered_df, x='CATEGORY', y='MILES', color='CATEGORY', title="Miles by Category", barmode='group')
        st.plotly_chart(fig2, use_container_width=True)

    route_counts = filtered_df.groupby(['START', 'STOP']).size().reset_index(name='Trips')
    route_counts = route_counts[route_counts['Trips'] > 1]
    st.markdown("#### Frequently Traveled Routes (Heatmap)")
    fig3 = px.density_heatmap(route_counts, x='START', y='STOP', z='Trips', color_continuous_scale="Viridis")
    st.plotly_chart(fig3, use_container_width=True)

# --- Tab 4: ML Model ---
with tab4:
    st.markdown("<h2 class='sub-header'>🤖 Compare ML Models </h2>", unsafe_allow_html=True)

    ml_df = filtered_df.dropna(subset=['MILES', 'Hour', 'Duration(min)'])

    if ml_df.empty:
        st.warning("No data available for ML model training. Please adjust your filters.")
    else:
        X = ml_df[['MILES', 'Hour']]
        y = ml_df['Duration(min)']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

        models = {
            "Linear Regression": LinearRegression(),
            "Decision Tree": DecisionTreeRegressor(random_state=0),
            "Random Forest": RandomForestRegressor(n_estimators=100, random_state=0)
        }

        rmse_scores = []
        r2_scores = []

        for name, model in models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            rmse_scores.append(root_mean_squared_error(y_test, y_pred))
            r2_scores.append(r2_score(y_test, y_pred))


        model_option = st.selectbox("Choose a Regression Model for Prediction", list(models.keys()))
        selected_model = models[model_option]
        selected_model.fit(X_train, y_train)

        st.markdown("### Predict Duration for a New Trip")
        miles = st.number_input("Enter Miles", value=5.0)
        hour = st.slider("Enter Start Hour", 0, 23, 9)
        input_df = pd.DataFrame({'MILES': [miles], 'Hour': [hour]})
        predicted_duration = selected_model.predict(input_df)[0]
        st.success(f"Predicted Duration using {model_option}: {predicted_duration:.2f} minutes")

        st.markdown("### 📊 Model Comparison Metrics")
        metric_df = pd.DataFrame({
            'Model': list(models.keys()),
            'RMSE': rmse_scores,
            'R2 Score': r2_scores
        })
        st.dataframe(metric_df.style.format({"RMSE": "{:.2f}", "R2 Score": "{:.2f}"}))

        st.markdown("#### RMSE Comparison")
        fig_rmse = px.bar(metric_df, x='Model', y='RMSE', color='Model', text_auto='.2s')
        st.plotly_chart(fig_rmse, use_container_width=True)

        st.markdown("#### R² Score Comparison")
        fig_r2 = px.bar(metric_df, x='Model', y='R2 Score', color='Model', text_auto='.2s')
        st.plotly_chart(fig_r2, use_container_width=True)
