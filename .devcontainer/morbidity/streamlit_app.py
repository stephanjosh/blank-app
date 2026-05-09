import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import numpy as np
import streamlit.components.v1 as components
from model.morbid_model import MentalHealthDataExtractor, main
import plotly.express as px
import hashlib

try:
    data = pd.read_csv('model/extracted_mental_health_data.csv')
    # st.success("✅ Data loaded successfully!") 
except FileNotFoundError:
    st.error("❌ Data file not found. Please run the data extraction first.")
    st.stop()
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# Clean the data
data['diagnosis'] = data['diagnosis'].astype(str).str.strip()
data['month'] = data['month'].astype(str).str.strip()


#Page configuration
st.set_page_config(                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
    page_title="MORBIDITY DASHBOARD",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded"
)

alt.themes.enable("default")


# CSS styling
st.markdown("""
<style>
    [data-testid="stMetric"] {
            text-align: right;
            display: flex;
            flex-direction: column;
            justify-content: left;
            align-items: center;    
            # border: 0.1px solid #eee;
            # border-radius: 20px;
            padding: 15px;
            
        }
        
        /* Center the label */
        [data-testid="stMetricLabel"] {
            text-align: center;
            justify-content: center;
        }
        
        /* Center the value */
        [data-testid="stMetricValue"] {
            text-align: right;
            justify-content: center;
        }
        
        /* Center the delta */
        [data-testid="stMetricDelta"] {
            text-align: right;
            justify-content: center;
        }
            
        div[data-testid="column"]:first-child div[data-testid="stMetric"] {
            border: 0.5px solid #eee;
            border-radius: 8px;
            padding: 10px;
        }

</style>
""", unsafe_allow_html=True)

#Logo imports

# Sidebar
with st.sidebar:
    st.title('MORBIDITY DASHBOARD')
    selected = option_menu(
    "Menu",
    ["DASHBOARD", "TRENDS", "ANALYSIS", "REPORTS", "FILTERS"],  
    icons=["tachometer", "bar-chart", "search","file-text", "filter"], 
    default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#000000"},
            "icon": {"color": "black", "font-size": "18px"},
            "nav-link": {
                "font-size": "14px",          
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#09F10100"
            },
            "nav-link-selected": {
                "background-color": "#09F10100", 
                "font-size": "14px"
            },
        }
)
data = pd.read_csv('model/extracted_mental_health_data.csv')
# print("Data", data)

# ===== SIDEBAR CONTROLS =====
with st.sidebar:
    
    # ========== DROPDOWN FILTERS ==========
    st.markdown("#### 🎯 Filter Options")

    # Extract age groups from column names in the csv files
    age_columns = [col for col in data.columns if '_' in col and col not in ['total_male', 'total_female', 'total_cases']]
    age_groups_raw = list(set(col.split('_')[0] for col in age_columns))

    # Custom sort order to handle ranges like '0-9', '10-18', and special case  and especially a case '65+'
    def sort_key(age):
        if age == '65+':
            return [float('inf')]  # Always sort last
        if age == 'Unknown':
            return [float('inf'), float('inf')]
        try:
            return [int(part) for part in age.split('-')]
        except ValueError:
            return [float('inf')]

    age_groups = ["All"] + sorted(age_groups_raw, key=sort_key)
    selected_age = st.selectbox("📊 Age Group", age_groups, index=0)

    # To handle the diagnosis column now !!!
    try:
        diagnosis_list = ["All"] + sorted(data['diagnosis'].unique().tolist())
        selected_diagnosis = st.selectbox("🏥 Diagnosis", diagnosis_list, index=0)
        st.success(f"✅ Found {len(diagnosis_list)-1} diagnoses")
    except Exception as e:
        st.error(f"Error loading diagnoses: {e}")
        selected_diagnosis = "All"
    
    # Month filter - with error handling
    try:
        month_list = ["All"] + sorted(data['month'].unique().tolist())
        selected_month = st.selectbox("📅 Time Period", month_list, index=0)
        # st.success(f"✅ Found {len(month_list)-1} months") 
    except Exception as e:
        st.error(f"Error loading months: {e}")
        selected_month = "All"    
    st.markdown("---")
     
    # ========== SUMMARY STATS ==========
    st.markdown("### 📊 Quick Stats")
    
    # Show what's currently selected
    total_records = len(data)
    # print("The total records", total_records)
    if selected_diagnosis != "All":
        filtered = data[data['diagnosis'] == selected_diagnosis]
        # st.write("Filtered data", filtered)   
        total_records = len(filtered)
        st.info(f"Showing {total_records:,} records for **{selected_diagnosis}**")
    elif selected_month != "All":
        filtered = data[data['month'] == selected_month]
        total_records = len(filtered)
        st.info(f"Showing {total_records:,} records from **{selected_month}**")
    else:
        st.info(f"Total records: **{total_records:,}**")

# ============================================
# APPLY FILTERS TO DATA
# ============================================

# Start with full dataset
filtered_data = data.copy()
if selected_age != "All":
    age_cols = [col for col in filtered_data.columns if col.startswith(f"{selected_age}_") or col.endswith(f"_{selected_age}")]
    if age_cols:
        # Sum across age-specific columns
        filtered_data['filtered_total'] = filtered_data[age_cols].sum(axis=1)
        filtered_data = filtered_data[filtered_data['filtered_total'] > 0]

# Apply diagnosis filter
if selected_diagnosis != "All":
    filtered_data = filtered_data[filtered_data['diagnosis'] == selected_diagnosis]

# Apply month filter
if selected_month != "All":
    filtered_data = filtered_data[filtered_data['month'] == selected_month]

# Create a hash of the data to detect changes
data_hash = hashlib.sha256(pd.util.hash_pandas_object(data, index=True).values.tobytes()).hexdigest()

# session state to, update previous values
if 'last_data_hash' not in st.session_state:
    st.session_state.last_data_hash = data_hash
    st.session_state.previous_total = None

# Calculate current values
total = int(data['total_cases'].sum())
male = int(data['total_male'].sum())
female = int(data['total_female'].sum())

# If data changed, calculate delta vs previous
if st.session_state.previous_total is not None and data_hash != st.session_state.last_data_hash:
    tot_source = total - st.session_state.previous_total
    male_source = male - st.session_state.previous_male
    female_source = female - st.session_state.previous_female
else:
    tot_source = None
    male_source = None
    female_source = None

# Store current as previous for next time
st.session_state.previous_total = total
st.session_state.previous_male = male
st.session_state.previous_female = female
st.session_state.last_data_hash = data_hash

filtered_data = data.copy()

# Clean the data essential to ---  ensure accurate, reliable analysis 
data['diagnosis'] = data['diagnosis'].astype(str).str.strip()
data['month'] = data['month'].astype(str).str.strip()

diagnosis_totals = filtered_data.groupby('diagnosis')['total_cases'].sum().sort_values(ascending=False)

# For use in arrangement by volume
# Convert Series to DataFrame
diagnosis_totals_vol = diagnosis_totals.head(10).reset_index()
diagnosis_totals_vol.columns = ['diagnosis', 'total_cases']


# just for display
top_5 = diagnosis_totals_vol.sort_values('total_cases', ascending=False).head(5)


# Get age groups by burden
age_groups = [col for col in filtered_data.columns if '_' in col and col not in ['total_male', 'total_female', 'total_cases']]

age_burden = {}
for age in age_groups:
    age_burden[age] = filtered_data[age].sum()

# Sort and get top 5
sorted_age_burden = dict(sorted(age_burden.items(), key=lambda item: item[1], reverse=True))
top_5_age_burden = dict(list(sorted_age_burden.items())[:5])
max_burden_age = list(sorted_age_burden.keys())[0] if sorted_age_burden else None
top_5_filtered_data = filtered_data[filtered_data['diagnosis'].isin(top_5['diagnosis'])]

# Display
col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
with col1:
    st.metric("Total People", f"{total:,}", delta=tot_source, delta_color='red')

with col2:
    st.metric("Males", f"{male:,}", delta=male_source)

with col3:
    st.metric("Females", f"{female:,}", delta=female_source)

with col4:
    # Use aggregated totals for the top 5 diagnoses to avoid overlapping bars/text
    bars = alt.Chart(top_5).mark_bar().encode(
        x=alt.X('total_cases:Q', title='Total Cases'),
        y=alt.Y('diagnosis:N', sort='-x', title='Diagnosis'),
        tooltip=['diagnosis', 'total_cases']
    )

    text = bars.mark_text(
        align='left',
        baseline='middle',
        color='white',
        dx=5
    ).encode(text=alt.Text('total_cases:Q', format=','))

    chart = (bars + text).properties(title='Top 5 Diagnoses by Volume')
    st.altair_chart(chart, use_container_width=True)

with st.container():
    # Create 3 columns for the age groups to sit below col1, col2, col3
    age_col1, age_col2, age_col3 = st.columns([1, 1, 1])
    
    # Distribute top 3 age groups across the 3 columns
    age_items = list(top_5_age_burden.items())

# BURDENS CARD STYLING
st.markdown("""
    <style>
    .age-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        border-left: 4px solid #ddd;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .age-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .age-card.peak {
        border-left: 4px solid #FF4444;
        background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
    }
    
    .age-card.second {
        border-left: 4px solid #FF9800;
        background: linear-gradient(135deg, #fff8f0 0%, #ffffff 100%);
    }
    
    .age-card.third {
        border-left: 4px solid #4CAF50;
        background: linear-gradient(135deg, #f1f8f4 0%, #ffffff 100%);
    }
    
    .rank-badge {
        display: inline-block;
        background: #f0f0f0;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-bottom: 8px;
    }
    
    .rank-badge.peak { background: #FF4444; color: white; }
    .rank-badge.second { background: #FF9800; color: white; }
    .rank-badge.third { background: #4CAF50; color: white; }
    
    .age-group-name {
        font-size: 1.1rem;
        font-weight: bold;
        color: #2196F3;
        margin: 4px 0;
    }
    
    .case-count {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 4px 0;
    }
    
    .percentage {
        color: #7f8c8d;
        font-size: 0.85rem;
    }
    
    .progress-bar {
        height: 6px;
        background: #ecf0f1;
        border-radius: 3px;
        margin-top: 8px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 0.5s ease;
    }
    
    .progress-fill.peak { background: linear-gradient(90deg, #FF4444, #FF6B6B); }
    .progress-fill.second { background: linear-gradient(90deg, #FF9800, #FFB74D); }
    .progress-fill.third { background: linear-gradient(90deg, #4CAF50, #81C784); }
    </style>
""", unsafe_allow_html=True)


age_col1, age_col2, age_col3 = st.columns(3)

with age_col1:
    if len(age_items) > 0:
        percent = (age_items[0][1] / age_burden[max_burden_age] * 100) if max_burden_age and age_burden[max_burden_age] > 0 else 100
        st.markdown(f"""
        <div class='age-card peak'>
            <div class='rank-badge peak'>🔺 PEAK BURDEN</div>
            <div class='age-group-name'>📊 {age_items[0][0]} years</div>
            <div class='case-count'>{age_items[0][1]:,}</div>
            <div class='percentage'>cases ({percent:.1f}% of peak)</div>
            <div class='progress-bar'>
                <div class='progress-fill peak' style='width: {percent}%;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No data available")

with age_col2:
    if len(age_items) > 1:
        percent = (age_items[1][1] / age_burden[max_burden_age] * 100) if max_burden_age and age_burden[max_burden_age] > 0 else 100
        st.markdown(f"""
        <div class='age-card second'>
            <div class='rank-badge second'>🥈 SECOND</div>
            <div class='age-group-name'>📊 {age_items[1][0]} years</div>
            <div class='case-count'>{age_items[1][1]:,}</div>
            <div class='percentage'>cases ({percent:.1f}% of peak)</div>
            <div class='progress-bar'>
                <div class='progress-fill second' style='width: {percent}%;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No data available")

with age_col3:
    if len(age_items) > 2:
        percent = (age_items[2][1] / age_burden[max_burden_age] * 100) if max_burden_age and age_burden[max_burden_age] > 0 else 100
        st.markdown(f"""
        <div class='age-card third'>
            <div class='rank-badge third'>🥉 THIRD</div>
            <div class='age-group-name'>📊 {age_items[2][0]} years</div>
            <div class='case-count'>{age_items[2][1]:,}</div>
            <div class='percentage'>cases ({percent:.1f}% of peak)</div>
            <div class='progress-bar'>
                <div class='progress-fill third' style='width: {percent}%;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No data available")
st.divider()

col1, col2 = st.columns([1, 1])

with col1:    
    # Aggregate filtered data by month for trend analysis
    trend_data = filtered_data.groupby('month', as_index=False).agg({
        'total_male': 'sum',
        'total_female': 'sum', 
        'total_cases': 'sum'
    })
    
    # Sort by month chronologically
    trend_data = trend_data.sort_values('month')
    
    # Dynamic title based on current filter
    if selected_diagnosis != "All":
        chart_title = f'📈 {selected_diagnosis} Trend'
    else:
        chart_title = 'Trend Summary'
    
    fig = px.line(trend_data, 
                  x='month',
                  y=['total_male', 'total_female', 'total_cases'], 
                  title=chart_title,
                  labels={'value': 'Number of Cases', 'variable': 'Group', 'month': 'Month'},
                  color_discrete_map={
                      'total_male': '#3498db', 
                      'total_female': '#e74c3c',
                      'total_cases': '#2ecc71'
                  },
                  markers=True)
    
    fig.update_layout(
        xaxis_tickangle=-35, 
        height=400,
        xaxis_title="Month",
        yaxis_title="Number of Cases",
        legend_title="Case Type",
        hovermode="x unified"
    )
    fig.update_traces(mode='lines+markers', line=dict(width=3))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    
    # Aggregate filtered data by month for bar chart
    bar_data = filtered_data.groupby('month', as_index=False).agg({
        'total_male': 'sum',
        'total_female': 'sum'
    })
    
    # Dynamic title based on current filter
    if selected_diagnosis != "All":
        bar_title = f'📊 {selected_diagnosis} - Monthly Cases by Gender'
    else:
        bar_title = '📊 Overall Monthly Cases by Gender'
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(x=bar_data['month'], y=bar_data['total_male'], 
                         name='Male Cases', marker_color='#3498db'))
    fig.add_trace(go.Bar(x=bar_data['month'], y=bar_data['total_female'], 
                         name='Female Cases', marker_color='#e74c3c'))
    
    fig.update_layout(
        title=bar_title,
        xaxis_title='Month',
        yaxis_title='Number of Cases',
        barmode='group',
        height=400,
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.divider()


col = st.columns([1])

# Get top diagnoses for the filtered data
diagnosis_totals = filtered_data.groupby('diagnosis')['total_cases'].sum().sort_values(ascending=False)

# Take top 10 diagnoses to avoid clutter, or all if less than 10
top_diagnoses = diagnosis_totals.head(10).index.tolist()

# Filter to only top diagnoses
chart_data = filtered_data[filtered_data['diagnosis'].isin(top_diagnoses)].copy()

# Aggregate by month and diagnosis
diag_monthly = chart_data.groupby(['month', 'diagnosis'])['total_cases'].sum().reset_index()

# Dynamic title based on current filter
if selected_diagnosis != "All":
    plotly_title = f'📊 {selected_diagnosis} - Monthly Cases by Diagnosis'
else:
    plotly_title = f'📊 Top {len(top_diagnoses)} Diagnoses - Monthly Cases'

fig = px.bar(diag_monthly,
             x='month',
             y='total_cases',
             color='diagnosis',
             title=plotly_title,
             labels={'total_cases': 'Number of Cases', 'diagnosis': 'Diagnosis', 'month': 'Month'},
             height=500,
             barmode='stack')  # Stacked bars

fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Number of Cases",
    legend_title="Diagnosis",
    xaxis_tickangle=-45,
    hovermode="x unified"
)

# Add hover template for better interactivity
fig.update_traces(
    hovertemplate="<b>%{fullData.name}</b><br>Month: %{x}<br>Cases: %{y}<extra></extra>"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

filtered_data = data.copy()
# Apply diagnosis filter
if selected_diagnosis != "All":
    filtered_data = filtered_data[filtered_data['diagnosis'] == selected_diagnosis]

# Apply month filter (assuming you have a 'month' column)
if selected_month != "All":
    filtered_data = filtered_data[filtered_data['month'] == selected_month]

# Apply age filter (assuming you have an 'age_group' column)
if selected_age != "All":
    age_cols = [col for col in filtered_data.columns if col.startswith(f"{selected_age}_") or col.endswith(f"_{selected_age}")]
    if age_cols:
        # Sum across age-specific columns
        filtered_data['filtered_total'] = filtered_data[age_cols].sum(axis=1)
        filtered_data = filtered_data[filtered_data['filtered_total'] > 0]

# Calculate totals
total_male = filtered_data['total_male'].sum()
total_female = filtered_data['total_female'].sum()

col_left, col_right = st.columns(2)

with col_left:
    st.metric("Total Male Cases", f"{int(total_male):,}")
    
    fig = px.bar(
        pd.DataFrame({'Category': ['Male'], 'Count': [int(total_male)]}),
        x='Count', y='Category', orientation='h',
        color_discrete_sequence=['#3498db']
    )
    fig.update_layout(height=150, showlegend=False, xaxis_title='', yaxis_title='')
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.metric("Total Female Cases", f"{int(total_female):,}")
    
    fig = px.bar(
        pd.DataFrame({'Category': ['Female'], 'Count': [int(total_female)]}),
        x='Count', y='Category', orientation='h',
        color_discrete_sequence=['#e74c3c']
    )
    fig.update_layout(height=150, showlegend=False, xaxis_title='', yaxis_title='')
    st.plotly_chart(fig, use_container_width=True)
