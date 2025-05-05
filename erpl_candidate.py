import streamlit as st
import pandas as pd
import plotly.express as px
from matplotlib.colors import LinearSegmentedColormap
from sqlalchemy import create_engine
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ---- Database Connection ----
DB_USER = "root"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_NAME = "tvetm"

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

def load_data():
    """Fetch data from MySQL and ensure all data is displayed correctly."""
    query = "SELECT * FROM erpl_candidate"  # Replace with your actual table name
    try:
        df = pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Return empty DataFrame to avoid further errors

    df.fillna({"gender": "Unknown"}, inplace=True)
    return df
    
# Dictionary of marital statuses
marital_statuses = {
    "single": "នៅលីវ",
    "married": "រៀបការ",
    "divorce": "លែងលះ",
    "widow": "មេម៉ាយ"
}

def set_css():
    st.markdown("""
        <style>
            @font-face {
                font-family: 'Khmer OS Battambang';
                src: url('path/to/KhmerOSBattambang-Regular.ttf') format('truetype'); /* Replace with the actual path */
                font-weight: normal;
                font-style: normal;
            }
            * {
                font-family: 'Khmer OS Battambang', sans-serif !important;
            }
            body {
                background-color: #f7f9fc;
            }
            /* Sidebar */
            .css-1d391kg {
                background-color: #14213d !important;
            }
            .css-1aumxhk {
                color: white !important;
            }
            /* KPI Cards */
            .kpi-card {
                padding: 20px;
                border-radius: 10px;
                background: #2872f0;
                box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
                text-align: center;
                margin-bottom: 15px;
                color: white;
            }
            .kpi-card h2, .kpi-card h4 {
                color: white;
                font-family: 'Khmer OS Battambang', sans-serif;
            }
            /* Graph Sections */
            .graph-section {
                background-color: #ffffff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
                margin-bottom: 25px;
                overflow: hidden;
            }
            .plotly-container {
                width: 100% !important;
                height: auto !important;
            }
            h1, h2, h3, h4, h5, h6, p, span, label, button, input, select, textarea {
                font-family: 'Khmer OS Battambang', sans-serif !important;
            }
        </style>
    """, unsafe_allow_html=True)

def main():
    set_css()

    df = load_data()
    if df.empty:
        return
    
    if "date_of_birth" in df.columns:
        df["age"] = pd.to_datetime("today").year - pd.to_datetime(df["date_of_birth"], errors="coerce").dt.year
        df.fillna({"age": 0}, inplace=True)

    # Initialize filtered dataframe
    filtered_df = df.copy()  # Start with the original data

    # If no data matches the filters
    if filtered_df.empty:
        st.warning("No data matches your filter criteria.")
        return  # Stop further processing if no data is available after filtering.

    # ---- KPI Metrics ----
    total_students = len(filtered_df)  # Use filtered_df for all calculations
    avg_age = int(filtered_df["age"].mean()) if "age" in filtered_df.columns and not filtered_df.empty else 0
    total_female = filtered_df[filtered_df["gender"].str.lower() == "female"].shape[0] if "gender" in filtered_df.columns else 0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.markdown(f'<div class="kpi-card"><h4>ចំនួនសិស្សសរុប</h4><h2>{total_students:,} នាក់</h2></div>', unsafe_allow_html=True)

    with kpi3:
        st.markdown(f'<div class="kpi-card"><h4>ចំនួនសិស្សស្រីសរុប</h4><h2>{total_female:,} នាក់</h2></div>', unsafe_allow_html=True)

    with kpi2:
        st.markdown(f'<div class="kpi-card"><h4>អាយុសិស្សជាមធ្យម</h4><h2>{avg_age} ឆ្នាំ</h2></div>', unsafe_allow_html=True)

    with kpi4:
        st.markdown(f'<div class="kpi-card"><h4>សិស្សបានបញ្ចប់ការសិក្សា</h4><h2> នាក់</h2></div>', unsafe_allow_html=True)

    # ---- Marital Status Graph----
    col1, col2, col3 = st.columns([1, 1, 1.5])
    with col1:
        with st.container(border=True):
            st.markdown(
                f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ស្ថានភាពអាពាហ៍ពិពាហ៍របស់សិស្ស</h4>',
                unsafe_allow_html=True
            )

            if "marital_status" in filtered_df.columns:
                if filtered_df["marital_status"].isnull().all():
                    st.warning("The 'marital_status' column exists, but all values are null.")
                    
                    # Placeholder chart
                    fig_placeholder = px.bar(
                        x=["Unavailable"],
                        y=[0],
                        text=["Data Unavailable"]
                    )
                    fig_placeholder.update_traces(textposition="outside")
                    st.plotly_chart(fig_placeholder, use_container_width=True)

                else:
                    # Map and count
                    filtered_df["marital_status_label"] = filtered_df["marital_status"].map(marital_statuses)
                    marital_counts = filtered_df["marital_status_label"].value_counts().reset_index()
                    marital_counts.columns = ["Marital Status", "Count"]

                    # Pie chart (styled like gender chart)
                    fig = px.pie(
                        marital_counts,
                        names="Marital Status",
                        values="Count",
                        hole=0.5  # Donut style
                    )

                    fig.update_layout(
                        margin=dict(t=60, b=30, l=30, r=30),
                        height=350  # Match gender chart
                    )

                    fig.update_traces(
                        hovertemplate='<b>%{label}</b><br>Count: %{value:,}<extra></extra>',
                        textinfo="percent+label",
                        textfont_size=14,
                        marker=dict(line=dict(color='#fff', width=2)),
                        pull=[0 for _ in marital_counts["Marital Status"]],
                        domain=dict(x=[0.1, 0.9], y=[0.1, 0.9])  # Match gender chart
                    )

                    st.plotly_chart(fig, use_container_width=True)

            else:
                st.warning("The 'marital_status' column is missing.")
                fig_placeholder = px.bar(x=["Unavailable"], y=[0], text=["Data Unavailable"])
                fig_placeholder.update_traces(textposition="outside")
                st.plotly_chart(fig_placeholder, use_container_width=True)

    with col2:
        with st.container(border=True):
            st.markdown(
                f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ការបែងចែកសិស្សតាមភេទ</h4>',
                unsafe_allow_html=True
            )

            if "gender" in filtered_df.columns:
                gender_labels = {"male": "ប្រុស", "female": "ស្រី"}
                gender_count = filtered_df["gender"].value_counts().reset_index()
                gender_count.columns = ["gender", "count"]
                gender_count["gender"] = gender_count["gender"].map(gender_labels)

                fig1 = px.pie(
                    names=gender_count["gender"],
                    values=gender_count["count"],
                    hole=0.5  # Make this a donut too, for consistency
                )

                fig1.update_layout(
                    margin=dict(t=60, b=30, l=30, r=30),
                    height=350  # Match height
                )

                fig1.update_traces(
                    hovertemplate='<b>%{label}</b><br>Count: %{value:,}<extra></extra>',
                    textinfo='percent+label',
                    textfont_size=14,
                    marker=dict(line=dict(color='#fff', width=2)),
                    pull=[0 for _ in gender_count["gender"]],
                    domain=dict(x=[0.1, 0.9], y=[0.1, 0.9])  # Match domain
                )
                st.plotly_chart(fig1, use_container_width=True)

    with col3:
        with st.container(border=True):
            st.markdown(
                f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif; color: #2C3E50;">ស្ថិតិសិក្ខាកាមតាមវេនសិក្សា</h4>',
                unsafe_allow_html=True
            )

            # Apply filters
            if 'gender_filter' in st.session_state:
                filtered_df = filtered_df[filtered_df['gender'] == st.session_state.gender_filter]

            if 'verified' in st.session_state:
                filtered_df = filtered_df[filtered_df['verified'] == st.session_state.shift_filter]

            # Define mapping dictionaries
            gender_labels = {"male": "ប្រុស", "female": "ស្រី"}
            verified_labels = {0: "រង់ចាំពិនិត្យ", 1: "បានពិនិត្យ"}

            # Group by shift_name and gender
            student_counts = filtered_df.groupby(["verified", "gender"]).size().reset_index(name="count")

            # Map labels
            student_counts["gender"] = student_counts["gender"].map(gender_labels)
            student_counts["verified"] = student_counts["verified"].map(verified_labels)

            # Create the bar chart
            fig = px.bar(
                student_counts,
                x="verified",
                y="count",
                color="gender",
                barmode="group",
                labels={"verified": "ស្ថានភាពនៃការធ្វើតេស្ត", "count": "ចំនួនអ្នកធ្វើតេស្ត", "gender": "ភេទ"},
                color_discrete_sequence=["#4dc3ff", "#0077b3"],
                text=student_counts["count"].map("{:,}".format),
            )

            fig.update_traces(
                texttemplate='%{text}',
                textposition="auto"
            )

            fig.update_layout(
                height=350,
                margin=dict(l=40, r=10, t=80, b=120),
                yaxis=dict(
                    tickformat=",",
                    title_text="ចំនួនអ្នកធ្វើតេស្ត",
                    showgrid=False,
                    range=[0, student_counts["count"].max() * 1.2]
                ),
                xaxis=dict(
                    title_text="ស្ថានភាពនៃការធ្វើតេស្ត",
                    tickangle=-45,
                    tickmode="array",
                    automargin=True
                ),
                plot_bgcolor="white",
            )
            st.plotly_chart(fig, use_container_width=True)

        # Ensure data is aggregated properly
    if "address_city_provinces" in filtered_df.columns:
        with st.container(border=True):
            # Count students per province
            province_counts = filtered_df["address_city_provinces"].value_counts().reset_index()
            province_counts.columns = ["Province", "ចំនួនសិក្ខាកាម"]

            # Format numbers with commas for text labels
            province_counts["Student Count Formatted"] = province_counts["ចំនួនសិក្ខាកាម"].apply(lambda x: f"{x:,}")

            # Khmer Title
            st.markdown(
                f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ការបែងចែកចំនួនសិស្សតាមខេត្ត</h4>',
                unsafe_allow_html=True
            )

            # 🔹 Create the bar chart
            fig_bar = px.bar(
                province_counts,
                x="Province",
                y="ចំនួនសិក្ខាកាម",
                text="Student Count Formatted",  # Formatted text
                labels={"Province": "ខេត្ត/ក្រុង", "Student Count Formatted": "ចំនួនសិក្ខាកាម"},
                color="ចំនួនសិក្ខាកាម",
                color_continuous_scale="blues",
            )

            # 🔹 Improve text positioning
            fig_bar.update_traces(
                textposition="outside",
                textfont=dict(size=12),
                cliponaxis=False
            )

            # 🔹 Update layout for better display
            fig_bar.update_layout(
                xaxis=dict(categoryorder="total ascending"),
                yaxis=dict(tickformat="~s"),  # Uses compact format (10K, 100K)
                margin=dict(l=40, r=10, t=40, b=80),
            )

            # 🔹 Special Handling for a single bar
            if len(province_counts) == 1:
                fig_bar.update_layout(
                    xaxis=dict(
                        range=[-1, 1],
                        tickvals=[0],
                        ticktext=province_counts["Province"].values
                    ),
                    yaxis=dict(
                        range=[0, max(province_counts["ចំនួនសិក្ខាកាម"].values) * 1.2]
                    ),
                    bargap=0.8,
                    width=200,
                    height=450,
                    margin=dict(l=20, r=20, t=40, b=40)
                )

            # 🔹 Show the chart
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("The dataset does not contain 'address_city_provinces' column.")

    # ---- Raw Data Preview ----
    st.subheader("ទិន្នន័យជាទម្រង់តារាង")
    st.dataframe(filtered_df, height=450, use_container_width=True)

    # ---- Refresh Data Button ----
    if st.button("🔄Refresh Data"):
        st.cache_data.clear()  # Clear the data cache to force reload
        st.rerun()  # Use st.rerun() to trigger rerun

if __name__ == "__main__":
    main()