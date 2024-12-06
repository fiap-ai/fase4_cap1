import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import DatabaseManager
from ml_model import IrrigationPredictor, generate_sample_data

# Page configuration
st.set_page_config(
    page_title="FarmTech Solutions Dashboard",
    page_icon="🌱",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main { 
        padding: 2rem;
    }
    .section-container {
        background-color: #0E1117;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 2rem 0;
        border: 1px solid #1E1E1E;
    }
    .stMetric {
        background-color: #1E1E1E;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .section-divider {
        margin: 3rem 0;
        border-top: 1px solid #1E1E1E;
        padding-top: 2rem;
    }
    .chart-container {
        margin: 2rem 0;
        padding: 1rem;
        background-color: rgba(30, 30, 30, 0.3);
        border-radius: 0.5rem;
    }
    .header-container {
        margin-bottom: 2rem;
        padding: 1rem;
        background-color: rgba(30, 30, 30, 0.2);
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'predictor' not in st.session_state:
    st.session_state.predictor = IrrigationPredictor()

def load_data():
    """Load data from database"""
    try:
        loading_msg = st.info("Carregando dados...")
        db = DatabaseManager()
        db.connect()
        data = db.get_all_readings()
        df = pd.DataFrame(data)
        db.disconnect()
        
        if df.empty:
            loading_msg.empty()
            st.warning("No data in database.")
            return pd.DataFrame()
        
        loading_msg.empty()
        st.success("Dados carregados com sucesso!")
        
        # Convert timestamp to datetime and add derived columns
        if 'TIMESTAMP' in df.columns:
            df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])
            df['Date'] = df['TIMESTAMP'].dt.date
            df['Hour'] = df['TIMESTAMP'].dt.hour
            df['Day'] = df['TIMESTAMP'].dt.day
            df['DayOfWeek'] = df['TIMESTAMP'].dt.day_name()
            df['TimeOfDay'] = pd.cut(
                df['Hour'],
                bins=[-1, 5, 11, 16, 21, 24],
                labels=['Night', 'Morning', 'Midday', 'Afternoon', 'Evening']
            )
            
        return df
    except Exception as e:
        if 'loading_msg' in locals():
            loading_msg.empty()
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def create_sensor_chart(df, sensor_name, color, y_label):
    """Create a line chart for sensor data"""
    fig = go.Figure()
    
    # Add raw data points with hover text
    hover_text = [
        f"Time: {row['TIMESTAMP'].strftime('%Y-%m-%d %H:%M:%S')}<br>" +
        f"Value: {row[sensor_name]:.2f}<br>" +
        f"Temperature: {row['TEMPERATURE']:.1f}°C<br>" +
        f"Humidity: {row['HUMIDITY']:.1f}%<br>" +
        f"Light: {row['LIGHT']:.0f}<br>" +
        f"Irrigation: {'ON' if row['RELAY_STATUS'] else 'OFF'}"
        for _, row in df.iterrows()
    ]
    
    # Add raw data points
    fig.add_trace(go.Scatter(
        x=df['TIMESTAMP'],
        y=df[sensor_name],
        mode='markers',
        name='Raw Data',
        marker=dict(color=color, size=6, opacity=0.5),
        hovertext=hover_text,
        hoverinfo='text'
    ))
    
    # Add smoothed line (rolling average)
    window_size = '1H'  # 1-hour window
    df_smooth = df.set_index('TIMESTAMP')[[sensor_name]].rolling(window=window_size, center=True).mean()
    
    fig.add_trace(go.Scatter(
        x=df_smooth.index,
        y=df_smooth[sensor_name],
        mode='lines',
        name='Trend',
        line=dict(color=color, width=2),
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        title=dict(
            text=f"{sensor_name.replace('_', ' ').title()} Over Time",
            y=0.99,  # Move title up even more
            x=0.5,
            xanchor='center',
            yanchor='top',
            font=dict(size=24, color='white')
        ),
        height=600,  # Increased height further
        margin=dict(l=20, r=20, t=200, b=20),  # Increased top margin significantly
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        yaxis_title=y_label,
        xaxis_title='Time',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.90,  # Adjusted legend position
            xanchor="left",
            x=0.01,
            bgcolor='rgba(30, 30, 30, 0.8)',
            bordercolor='rgba(54, 162, 235, 0.3)',
            borderwidth=1
        ),
        hovermode='closest'
    )
    
    # Add range selector with more spacing
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=12, label="12h", step="hour", stepmode="backward"),
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=2, label="2d", step="day", stepmode="backward"),
                dict(count=4, label="4d", step="day", stepmode="backward"),
                dict(step="all", label="All")
            ]),
            y=1.35,  # Move range selector up even more
            x=0.05,
            font=dict(size=14),
            bgcolor='rgba(30, 30, 30, 0.8)',
            activecolor='rgba(54, 162, 235, 0.8)',
            borderwidth=1,
            bordercolor='rgba(54, 162, 235, 0.3)'
        )
    )
    
    # Update axis properties
    fig.update_xaxes(
        title_font=dict(size=14),
        tickfont=dict(size=12),
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128, 128, 128, 0.1)',
        zeroline=False
    )
    fig.update_yaxes(
        title_font=dict(size=14),
        tickfont=dict(size=12),
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128, 128, 128, 0.1)',
        zeroline=False
    )
    
    return fig

def create_prediction_section(df, latest, predictor):
    """Create ML prediction section"""
    st.markdown("## ML Predictions & Insights")
    
    # Train model if we have enough data
    if len(df) > 50:  # Minimum data requirement
        try:
            # Prepare data for ML model (lowercase column names)
            ml_data = df.copy()
            ml_data.columns = ml_data.columns.str.lower()
            
            metrics = predictor.train(ml_data.to_dict('records'))
            
            # Current prediction
            current_reading = {
                'humidity': latest['HUMIDITY'],
                'temperature': latest['TEMPERATURE'],
                'light': latest['LIGHT'],
                'btn_p': int(latest['BTN_P']),  # Convert to int
                'btn_k': int(latest['BTN_K']),  # Convert to int
                'relay_status': int(latest['RELAY_STATUS'])  # Convert to int
            }
            prediction = predictor.predict(current_reading)
            
            # Display predictions and insights
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Current Prediction")
                st.metric(
                    "Irrigation Need",
                    f"{prediction:.1%}",
                    delta="Probability of needing irrigation"
                )
                
                # Model performance
                st.metric(
                    "Model Accuracy",
                    f"{metrics['r2']:.1%}",
                    delta="R² Score"
                )
            
            with col2:
                st.markdown("### Feature Importance")
                importance_df = pd.DataFrame(
                    metrics['feature_importance'].items(),
                    columns=['Feature', 'Importance']
                ).sort_values('Importance', ascending=True)
                
                fig = go.Figure(go.Bar(
                    x=importance_df['Importance'],
                    y=importance_df['Feature'],
                    orientation='h'
                ))
                
                fig.update_layout(
                    height=200,
                    margin=dict(l=20, r=20, t=20, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            # Add insights based on feature importance
            st.markdown("### Key Insights")
            insights = []
            for feature, importance in metrics['feature_importance'].items():
                if importance > 0.2:  # Significant features
                    current_value = latest[feature.upper()]
                    if feature == 'humidity':
                        if current_value < 40:
                            insights.append("🔴 Low humidity detected - irrigation may be needed soon")
                        elif current_value > 70:
                            insights.append("🔵 High humidity - irrigation can be delayed")
                    elif feature == 'temperature':
                        if current_value > 35:
                            insights.append("🌡️ High temperature - monitor moisture levels closely")
                    elif feature == 'light':
                        if current_value > 500:
                            insights.append("☀️ High light levels - check for increased water needs")
            
            if insights:
                for insight in insights:
                    st.info(insight)
            else:
                st.success("✅ All parameters within optimal ranges")
                
        except Exception as e:
            st.error(f"Error in ML predictions: {str(e)}")
            st.error("Debug info:")
            st.write("Data columns:", df.columns.tolist())
            st.write("Latest reading:", latest)
    else:
        st.warning("Not enough data for ML predictions yet. Need at least 50 readings.")

def main():
    # Header
    with st.container():
        st.markdown('<div class="header-container">', unsafe_allow_html=True)
        st.title("🌱 FarmTech Solutions Dashboard")
        st.markdown("### Real-time Irrigation Monitoring System")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.error("No data available.")
        return

    # Get latest readings
    latest = df.iloc[-1]
    
    # Debug information
    with st.expander("🔍 Debug Information", expanded=False):
        st.write("Data Shape:", df.shape)
        st.write("Date Range:", df['TIMESTAMP'].min().strftime('%Y-%m-%d'), "to", df['TIMESTAMP'].max().strftime('%Y-%m-%d'))
        st.write("Number of Days:", len(df['Date'].unique()))
        # Convert dates to strings in the readings per day dict
        readings_per_day = {date.strftime('%Y-%m-%d'): count for date, count in df.groupby('Date').size().items()}
        st.write("Readings per Day:", readings_per_day)
        st.write("Time Distribution:", df.groupby(['Date', 'TimeOfDay']).size().unstack(fill_value=0))
        st.write("Latest Reading:", latest.to_dict())

    # Current Status Section
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown("## Current Status")
    col1, col2, col3 = st.columns(3)
    
    # Current Readings
    with col1:
        st.markdown("### Current Readings")
        st.metric(
            "Temperature",
            f"{latest['TEMPERATURE']:.1f}°C",
            delta=f"{latest['TEMPERATURE'] - df['TEMPERATURE'].mean():.1f}°C"
        )
        st.metric(
            "Humidity",
            f"{latest['HUMIDITY']:.1f}%",
            delta=f"{latest['HUMIDITY'] - df['HUMIDITY'].mean():.1f}%"
        )
        st.metric(
            "Light Level",
            f"{latest['LIGHT']:.0f}",
            delta=f"{latest['LIGHT'] - df['LIGHT'].mean():.0f}"
        )

    # System Status
    with col2:
        st.markdown("### System Status")
        st.metric(
            "Phosphorus (P)",
            "Active" if latest['BTN_P'] else "Inactive",
            delta="ON" if latest['BTN_P'] else "OFF"
        )
        st.metric(
            "Potassium (K)",
            "Active" if latest['BTN_K'] else "Inactive",
            delta="ON" if latest['BTN_K'] else "OFF"
        )
        st.metric(
            "Irrigation",
            "ON" if latest['RELAY_STATUS'] else "OFF",
            delta="Active" if latest['RELAY_STATUS'] else "Inactive"
        )

    # Statistics
    with col3:
        st.markdown("### Statistics")
        days_of_data = (df['TIMESTAMP'].max() - df['TIMESTAMP'].min()).days
        total_readings = len(df)
        irrigation_time = (df['RELAY_STATUS'] == 1).mean() * 100
        
        st.metric(
            "Data Period",
            f"{days_of_data + 1} days",
            delta=f"{total_readings} readings"
        )
        st.metric(
            "Irrigation Active",
            f"{irrigation_time:.1f}%",
            delta=f"of total time"
        )
        st.metric(
            "Reading Frequency",
            "Every 20 min",
            delta=f"{total_readings // (days_of_data + 1)} per day"
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Sensor Trends Section
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown("## Sensor Trends")
    
    # Time range selector
    time_range = st.selectbox(
        "Select Time Range",
        ["Last 12 Hours", "Last Day", "Last 2 Days", "Last 4 Days", "All Time"],
        index=4  # Default to "All Time"
    )
    
    # Filter data based on time range
    end_time = df['TIMESTAMP'].max()
    if time_range == "Last 12 Hours":
        start_time = end_time - timedelta(hours=12)
    elif time_range == "Last Day":
        start_time = end_time - timedelta(days=1)
    elif time_range == "Last 2 Days":
        start_time = end_time - timedelta(days=2)
    elif time_range == "Last 4 Days":
        start_time = end_time - timedelta(days=4)
    else:
        start_time = df['TIMESTAMP'].min()
    
    df_filtered = df[df['TIMESTAMP'].between(start_time, end_time)]
    
    # Temperature Chart
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(
        create_sensor_chart(df_filtered, 'TEMPERATURE', '#ff4b4b', 'Temperature (°C)'),
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Humidity Chart
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(
        create_sensor_chart(df_filtered, 'HUMIDITY', '#36a2eb', 'Humidity (%)'),
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Light Level Chart
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(
        create_sensor_chart(df_filtered, 'LIGHT', '#ffcd56', 'Light Level'),
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Data Analysis Section
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown("## Data Analysis")
    
    # Daily Statistics
    daily_stats = df.groupby('Date').agg({
        'TEMPERATURE': ['mean', 'min', 'max', 'std'],
        'HUMIDITY': ['mean', 'min', 'max', 'std'],
        'LIGHT': ['mean', 'min', 'max', 'std'],
        'RELAY_STATUS': ['mean', 'sum']
    }).round(2)
    
    # Rename columns for better display
    daily_stats.columns = [
        f"{col[0]}_{col[1]}".title().replace('_', ' ')
        for col in daily_stats.columns
    ]
    
    # Convert relay status mean to percentage and sum to hours
    daily_stats['Irrigation Time (%)'] = (daily_stats['Relay Status Mean'] * 100).round(1)
    daily_stats['Irrigation Hours'] = (daily_stats['Relay Status Sum'] * 20 / 60).round(1)  # 20 min intervals
    
    # Drop original relay status columns
    daily_stats = daily_stats.drop(['Relay Status Mean', 'Relay Status Sum'], axis=1)
    
    st.dataframe(daily_stats, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Historical Data Section
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown("## Historical Data")
    
    # Add filters
    col1, col2 = st.columns(2)
    with col1:
        selected_date = st.date_input(
            "Select Date",
            value=latest['TIMESTAMP'].date(),
            min_value=df['TIMESTAMP'].min().date(),
            max_value=df['TIMESTAMP'].max().date()
        )
    with col2:
        records = st.slider('Number of records to display', 5, 100, 20)
    
    # Filter data
    df_selected = df[df['Date'] == selected_date]
    
    # Display data table
    st.dataframe(
        df_selected.sort_values('TIMESTAMP', ascending=False)
        .head(records)
        .style.format({
            'TEMPERATURE': '{:.1f}°C',
            'HUMIDITY': '{:.1f}%',
            'LIGHT': '{:.0f}',
            'TIMESTAMP': lambda x: x.strftime('%Y-%m-%d %H:%M:%S')
        }),
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ML Predictions Section
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    create_prediction_section(df, latest, st.session_state.predictor)
    st.markdown('</div>', unsafe_allow_html=True)

    # Refresh button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    with col2:
        st.text(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
