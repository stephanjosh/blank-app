import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Peaks", layout="wide")

st.markdown("""
<style>
/* ── Age cards ── */
.age-card { 
    background: #ffffff; 
    border-radius: 16px; 
    padding: 20px; 
    border-left: 5px solid #ddd; 
    box-shadow: 0 4px 12px rgba(0,0,0,0.08); 
    transition: all 0.3s ease;
}
.age-card:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    transform: translateY(-4px);
}
.age-card.peak   { border-left-color: #FF6B6B; background: linear-gradient(135deg, #FFF8F7 0%, #FFFFFF 100%); }
.age-card.second { border-left-color: #FFA500; background: linear-gradient(135deg, #FFF9F0 0%, #FFFFFF 100%); }
.age-card.third  { border-left-color: #4CAF50; background: linear-gradient(135deg, #F1F8F4 0%, #FFFFFF 100%); }
.rank-badge        { 
    display: inline-block; 
    padding: 6px 12px; 
    border-radius: 12px; 
    font-size: 0.75rem; 
    font-weight: 700; 
    margin-bottom: 12px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.rank-badge.peak   { background: linear-gradient(135deg, #FF6B6B, #FF4444); color: white; box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3); }
.rank-badge.second { background: linear-gradient(135deg, #FFB84D, #FFA500); color: white; box-shadow: 0 4px 12px rgba(255, 165, 0, 0.3); }
.rank-badge.third  { background: linear-gradient(135deg, #81C784, #4CAF50); color: white; box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3); }
.age-group-name { 
    font-size: 1.1rem; 
    font-weight: 700; 
    color: #1e293b; 
    margin: 10px 0 6px 0;
    letter-spacing: -0.5px;
}
.case-count     { 
    font-size: 1.8rem; 
    font-weight: 900; 
    color: #0f172a; 
    margin: 8px 0;
    letter-spacing: -1px;
}
.percentage     { 
    color: #64748b; 
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 10px;
}
.progress-bar   { 
    height: 6px; 
    background: #e2e8f0; 
    border-radius: 4px; 
    margin-top: 12px; 
    overflow: hidden;
}
.progress-fill  { 
    height: 100%; 
    border-radius: 4px; 
    transition: width 0.6s ease;
}
.progress-fill.peak   { background: linear-gradient(90deg, #FF6B6B, #FF4444); }
.progress-fill.second { background: linear-gradient(90deg, #FFB84D, #FFA500); }
.progress-fill.third  { background: linear-gradient(90deg, #81C784, #4CAF50); }
</style>
""", unsafe_allow_html=True)

data = pd.read_csv('model/extracted_mental_health_data.csv')
data['diagnosis'] = data['diagnosis'].astype(str).str.strip()
data['month'] = data['month'].astype(str).str.strip()

st.header("📈 Age Group Burden Analysis")

age_col1, age_col2, age_col3 = st.columns(3)
age_columns = [col for col in data.columns if '_' in col and col not in ['total_male', 'total_female', 'total_cases']]
age_groups_raw = list(set(col.split('_')[0] for col in age_columns))
age_burden = {}
for age_group in age_groups_raw:
    age_burden[age_group] = data[[col for col in age_columns if col.startswith(age_group)]].sum().sum() 
age_items = sorted(age_burden.items(), key=lambda x: x[1], reverse=True)
max_burden_age = age_items[0][0] if len(age_items) > 0 else None

with age_col1:
    if len(age_items) > 0:
        percent = (age_items[0][1] / age_burden[max_burden_age] * 100) if max_burden_age and age_burden[max_burden_age] > 0 else 100
        st.markdown(f"""
        <div class='age-card peak'>
            <div class='rank-badge peak'>🔺 PEAK BURDEN</div>
            <div class='age-group-name'>📊 {age_items[0][0]} yrs</div>
            <div class='case-count'>{age_items[0][1]:,.0f}</div>
            <div class='percentage'>{percent:.1f}% of peak</div>
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
            <div class='age-group-name'>📊 {age_items[1][0]} yrs</div>
            <div class='case-count'>{age_items[1][1]:,.0f}</div>
            <div class='percentage'>{percent:.1f}% of peak</div>
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
            <div class='age-group-name'>📊 {age_items[2][0]} yrs</div>
            <div class='case-count'>{age_items[2][1]:,.0f}</div>
            <div class='percentage'>{percent:.1f}% of peak</div>
            <div class='progress-bar'>
                <div class='progress-fill third' style='width: {percent}%;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No data available")

st.divider()

# a prevalence plot for the top 5 diagnoses across all age groups
diagnosis_burden = data.groupby('diagnosis')[age_columns].sum().sum(axis=1).sort_values(ascending=False)
top_diagnoses = diagnosis_burden.head(5).index.tolist()
top_diagnosis_data = data[data['diagnosis'].isin(top_diagnoses)].groupby('month')[age_columns].sum().reset_index()
top_diagnosis_data['total_cases'] = top_diagnosis_data[age_columns].sum(axis=1)
# the prevalence plot
fig = go.Figure()
for diagnosis in top_diagnoses:
    diagnosis_data = data[data['diagnosis'] == diagnosis].groupby('month')[age_columns].sum().reset_index()
    diagnosis_data['total_cases'] = diagnosis_data[age_columns].sum(axis=1)
    fig.add_trace(go.Scatter(x=diagnosis_data['month'], y=diagnosis_data['total_cases'], mode='lines+markers', name=diagnosis))
fig.update_layout(title='📊 Prevalence of Top 5 Diagnoses Over Time'    , xaxis_title='Month', yaxis_title='Total Cases', template='plotly_white'
                   )
st.plotly_chart(fig)