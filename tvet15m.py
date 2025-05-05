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

#Khmer Ditionary custome
province_coordinates = {
    "Phnom Penh": {"khmer": "ភ្នំពេញ"},
    "Siem Reap": {"khmer": "សៀមរាប"},
    "Battambang": {"khmer": "បាត់ដំបង"},
    "Banteay Meanchey": {"khmer": "បន្ទាយមានជ័យ"},
    "Kampong Cham": {"khmer": "កំពង់ចាម"},
    "Kampong Chhnang": {"khmer": "កំពង់ឆ្នាំង"},
    "Kampong Speu": {"khmer": "កំពង់ស្ពឺ"},
    "Kampong Thom": {"khmer": "កំពង់ធំ"},
    "Kampot": {"khmer": "កំពត"},
    "Kandal": {"khmer": "កណ្ដាល"},
    "Koh Kong": {"khmer": "កោះកុង"},
    "Kratie": {"khmer": "ក្រចេះ"},
    "Mondulkiri": {"khmer": "មណ្ឌលគីរី"},
    "Oddar Meanchey": {"khmer": "ឧត្តរមានជ័យ"},
    "Pailin": {"khmer": "ប៉ៃលិន"},
    "Preah Sihanouk": {"khmer": "ព្រះសីហនុ"},
    "Preah Vihear": {"khmer": "ព្រះវិហារ"},
    "Prey Veng": {"khmer": "ព្រៃវែង"},
    "Pursat": {"khmer": "ពោធិ៍សាត"},
    "Ratanakiri": {"khmer": "រតនគិរី"},
    "Stung Treng": {"khmer": "ស្ទឹងត្រែង"},
    "Svay Rieng": {"khmer": "ស្វាយរៀង"},
    "Takeo": {"khmer": "តាកែវ"},
    "Tboung Khmum": {"khmer": "ត្បូងឃ្មុំ"},
    "Kep": {"khmer": "កែប"},
}

def load_data():
    """Fetch data from MySQL and ensure all data is displayed correctly."""
    query = "SELECT * FROM tvet15m"  # Replace with your actual table name
    try:
        df = pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Return empty DataFrame to avoid further errors

    df.fillna({"gender": "Unknown", "apply_major_name": "Unknown"}, inplace=True)
    return df
    
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

    # Create columns for the filters to appear horizontally
    col1, col2, col3, col4, co5 = st.columns([1.4, 1, 0.5, 0.8, 0.5])

    # Initialize filtered dataframe
    filtered_df = df.copy()  # Start with the original data

    # ---- Date Range Filter with Validation ----
    with st.container(border=True):
        st.subheader("រយៈពេលនៃការចុះឈ្មោះរបស់សិក្ខាកាម")

        # Ensure date column exists and convert to datetime
        if "rtimeline_created_at" in filtered_df.columns:
            filtered_df["rtimeline_created_at"] = pd.to_datetime(filtered_df["rtimeline_created_at"], errors="coerce")

            min_date = filtered_df["rtimeline_created_at"].min().date()
            max_date = filtered_df["rtimeline_created_at"].max().date()

            # Date input for selecting date range
            date_range = st.date_input(
                "ជ្រើសរើសចន្លោះកាលបរិច្ឆេទ",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )

            # Ensure valid date selection
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date, end_date = date_range

                if start_date > end_date:
                    st.error("⚠️ កាលបរិច្ឆេទចាប់ផ្ដើមត្រូវតែតិចជាងកាលបរិច្ឆេទបញ្ចប់។ សូមជ្រើសរើសម្តងទៀត។")
                else:
                    filtered_df = filtered_df[
                        (filtered_df["rtimeline_created_at"].dt.date >= start_date) &
                        (filtered_df["rtimeline_created_at"].dt.date <= end_date)
                    ]

                    if filtered_df.empty:
                        st.warning("⚠️ គ្មានទិន្នន័យក្នុងចន្លោះកាលបរិច្ឆេទដែលបានជ្រើស។ សូមជ្រើសរើសកាលបរិច្ឆេទផ្សេងទៀត។")

    # ---- Filter by Sector ----
    with col1:
        sector_options = sorted(df["school_name"].unique())  # Unique sector options
        selected_sectors = st.multiselect("គ្រឹះស្ថាន អ.ប.វ.", sector_options)

        if selected_sectors:
            filtered_df = filtered_df[filtered_df["school_name"].isin(selected_sectors)]

            # Filter by Major based on selected sectors
            major_options = sorted(filtered_df[filtered_df["school_name"].isin(selected_sectors)]["apply_major_name"].unique())
        else: 
            major_options = sorted(df["apply_major_name"].unique())  # Show all majors if no sector is selected

    # ---- Filter by Major ----
    with col2:
        selected_majors = st.multiselect("ជំនាញ", major_options)
        if selected_majors:
            filtered_df = filtered_df[filtered_df["apply_major_name"].isin(selected_majors)]

    # ---- Gender Filter ----
    with col3:
        gender_mapping = {"female": "ស្រី", "male": "ប្រុស"}  # Mapping English to Khmer
        gender_options = sorted(df["gender"].unique())

        # Convert gender options to Khmer for display
        display_gender_options = [gender_mapping.get(g, g) for g in gender_options]

        # Use Khmer labels in the UI
        selected_display_genders = st.multiselect("ភេទ", display_gender_options)

        # Convert selected Khmer options back to English for filtering
        selected_genders = [key for key, value in gender_mapping.items() if value in selected_display_genders]

        if selected_genders:
            filtered_df = filtered_df[filtered_df["gender"].isin(selected_genders)]

    # ---- Filter by Province ----
    with col4:
        # Get Khmer names for provinces
        #khmer_provinces = [province_coordinates[province]["khmer"] for province in province_coordinates]
        province_options = sorted(df["address_city_province_name"].unique())  # Unique sector options
        selected_provinces = st.multiselect("ខេត្ត/ក្រុង", province_options)

        if selected_provinces:
            filtered_df = filtered_df[filtered_df["address_city_province_name"].isin(selected_provinces)]
            major_options = sorted(filtered_df[filtered_df["address_city_province_name"].isin(selected_provinces)]["school_name"].unique())
        else:
            major_options = sorted(df["school_name"].unique())  # Show all majors if no sector is selected

    # ---- Work Status Filter ----
    with co5:
        # Get unique has_job options
        has_job_options = sorted(df["has_job"].astype(str).unique())  # Ensure values are strings for UI
        selected_job_statuses = st.multiselect("ស្ថានភាពការងារ", has_job_options)

        if selected_job_statuses:
            filtered_df = filtered_df[filtered_df["has_job"].astype(str).isin(selected_job_statuses)]
            major_options = sorted(filtered_df[filtered_df["has_job"].astype(str).isin(selected_job_statuses)]["school_name"].unique())
        else:
            major_options = sorted(df["school_name"].unique())  # Show all majors if no job status is selected

    # If no data matches the filters
    if filtered_df.empty:
        st.warning("No data matches your filter criteria.")
        return  # Stop further processing if no data is available after filtering.

    # ---- KPI Metrics ----
    total_students = len(filtered_df)  # Use filtered_df for all calculations
    avg_age = int(filtered_df["age"].mean()) if "age" in filtered_df.columns and not filtered_df.empty else 0
    total_female = filtered_df[filtered_df["gender"].str.lower() == "female"].shape[0] if "gender" in filtered_df.columns else 0
    
    if "scholarship_status" in filtered_df.columns:
        filtered_df["scholarship_status"] = pd.to_numeric(filtered_df["scholarship_status"], errors="coerce")
        filtered_df = filtered_df.dropna(subset=["scholarship_status"])
        students_status_8 = filtered_df[filtered_df["scholarship_status"] == 8].shape[0]
    else:
        students_status_8 = 0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.markdown(f'<div class="kpi-card"><h4>ចំនួនសិស្សសរុប</h4><h2>{total_students:,} នាក់</h2></div>', unsafe_allow_html=True)

    with kpi3:
        st.markdown(f'<div class="kpi-card"><h4>ចំនួនសិស្សស្រីសរុប</h4><h2>{total_female:,} នាក់</h2></div>', unsafe_allow_html=True)

    with kpi2:
        st.markdown(f'<div class="kpi-card"><h4>អាយុសិស្សជាមធ្យម</h4><h2>{avg_age} ឆ្នាំ</h2></div>', unsafe_allow_html=True)

    with kpi4:
        st.markdown(f'<div class="kpi-card"><h4>សិស្សបានបញ្ចប់ការសិក្សា</h4><h2>{students_status_8:,} នាក់</h2></div>', unsafe_allow_html=True)

    # ---- Gender and Age Distribution in the same row ----
    col1, col2 = st.columns([1, 2])

    # Define gender translations and color mapping
    gender_mapping = {"male": "ប្រុស", "female": "ស្រី"}
    gender_colors = {"male": "#4dc3ff", "female": "#0077b3"}  # Blue for male, Orange for female

    with col1:
        with st.container(border=True):  # Add border here
            st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ការបែងចែកសិស្សតាមភេទ</h4>', unsafe_allow_html=True) 
            
            if "gender" in filtered_df.columns:
                gender_count = filtered_df["gender"].value_counts()

                # Map gender labels using the dictionary
                gender_labels = [gender_mapping.get(g, g) for g in gender_count.index]

                # Create pie chart
                fig1 = px.pie(
                    names=gender_labels,  # Use translated labels
                    values=gender_count.values,
                    color=gender_count.index,
                    color_discrete_map=gender_colors
                );
                fig1.update_traces(hovertemplate='<b>%{label}</b><br>ចំនួនសិក្ខាកាម: %{value:,}<extra></extra>')
                st.plotly_chart(fig1, use_container_width=True)

    with col2:
        with st.container(border=True):  # Add border here
            st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ស្ថិតិសិស្សតាមអាយុ</h4>', unsafe_allow_html=True) 
            
            if "age" in filtered_df.columns and "gender" in filtered_df.columns:
                gender_labels = {"male": "ប្រុស", "female": "ស្រី"}  # Gender dictionary
                
                age_distribution = filtered_df.groupby(["age", "gender"]).size().reset_index(name="count")
                age_distribution["gender"] = age_distribution["gender"].map(gender_labels)  # Apply Khmer labels
                
                fig2 = px.line(
                    age_distribution,
                    x="age",
                    y="count",
                    color="gender",
                    labels={"age": "អាយុ", "count": "ចំនួនសិក្ខាកាម", "gender": "ភេទ"}  #Added Khmer label for gender
                )
                fig2.update_traces(hovertemplate='អាយុ: %{x} ឆ្នាំ<br>ចំនួនសិក្ខាកាម: %{y:,}<extra></extra>')
                st.plotly_chart(fig2, use_container_width=True)

    # Ensure data is aggregated properly
    if "address_city_province_name" in filtered_df.columns:
        with st.container(border=True):
            # Count students per province
            province_counts = filtered_df["address_city_province_name"].value_counts().reset_index()
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
        st.warning("The dataset does not contain 'address_city_province_name' column.")

    col3, col4 = st.columns([1, 1])
    with col3:
        with st.container(border=True):
            st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ស្ថិតិសិក្ខាកាមតាមអត្រាអវត្តមាន</h4>', unsafe_allow_html=True) 
            
            if "average_attendance" in filtered_df.columns:
                # Ensure 'average_attendance' is numeric and drop NaN values
                filtered_df = filtered_df.dropna(subset=["average_attendance"])
                
                # Group data by average_attendance only (without gender)
                attendance_distribution = (
                    filtered_df.groupby("average_attendance")
                    .size()
                    .reset_index(name="count")
                )
                
                if not attendance_distribution.empty:
                    # Create scatter plot
                    fig2 = px.scatter(
                        attendance_distribution,
                        x="average_attendance",
                        y="count",
                        size="count",  # Size points based on count
                        labels={"average_attendance": "អត្រាអវត្តមាន (%)", "count": "ចំនួនសិក្ខាកាម"},
                        color="count",  # Use color scale based on count
                        color_continuous_scale="blues",
                    )

                    # Improve hover format
                    fig2.update_traces(
                        hovertemplate='អត្រាអវត្តមាន: %{x}%<br>ចំនួនសិក្ខាកាម: %{y:,} នាក់<extra></extra>',
                        marker=dict(opacity=0.7, line=dict(width=1, color="black"))
                    )

                    # Display chart
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.warning("No data available for visualization.")
            else:
                st.warning("Missing required column: 'average_attendance'.")

    with col4:
        with st.container(border=True):
            st.markdown(
                f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif; color: #2C3E50;">ស្ថិតិសិក្ខាកាមតាមវេនសិក្សា</h4>',
                unsafe_allow_html=True
            )

            # Apply filters
            if 'gender_filter' in st.session_state:
                filtered_df = filtered_df[filtered_df['gender'] == st.session_state.gender_filter]

            if 'shift_filter' in st.session_state:
                filtered_df = filtered_df[filtered_df['shift_name'] == st.session_state.shift_filter]

            # Group by shift_name and gender
            student_counts = filtered_df.groupby(["shift_name", "gender"]).size().reset_index(name="count")

            # Create the bar chart
            fig = px.bar(
                student_counts,
                x="shift_name",
                y="count",
                color="gender",
                barmode="group",
                labels={"shift_name": "វេនសិក្សា", "count": "ចំនួនសិក្ខាកាម", "gender": "ភេទ"},
                color_discrete_sequence=["#4dc3ff", "#0077b3"],  # Custom colors
                text=student_counts["count"].map("{:,}".format),  # Format numbers with commas
            )

            # Adjust text position: outside for large bars, inside for small bars
            fig.update_traces(
                texttemplate='%{text}',
                textposition="auto"  # Auto adjusts label position based on bar height
            )

            # Adjust layout to prevent label cutoff
            fig.update_layout(
                height=450,  # Increase height to fit labels
                margin=dict(l=40, r=10, t=80, b=120),  # Increase top margin for labels
                yaxis=dict(
                    tickformat=",",  
                    title_text="ចំនួនសិក្ខាកាម",  
                    showgrid=False,
                    range=[0, student_counts["count"].max() * 1.2]  # Increase y-axis range for label space
                ),
                xaxis=dict(
                    title_text="វេនសិក្សា",
                    tickangle=-45,
                    tickmode="array",
                    automargin=True
                ),
                plot_bgcolor="white",
            )

            # Display the chart
            st.plotly_chart(fig, use_container_width=True)

    col5, col6 = st.columns([1,1.5])
    with col5:
        with st.container(border=True):
            st.markdown(
                f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif; color: #2C3E50;">ស្ថិតិសិក្ខាកាមតាមការមានការងារធ្វើ</h4>',
                unsafe_allow_html=True
            )

            # Apply filters if they exist in session state
            if 'gender_filter' in st.session_state:
                filtered_df = filtered_df[filtered_df['gender'] == st.session_state.gender_filter]

            if 'job_filter' in st.session_state:
                filtered_df = filtered_df[filtered_df['has_job'] == st.session_state.job_filter]

            # Ensure 'has_job' is categorical for correct visualization
            filtered_df["has_job"] = filtered_df["has_job"].astype(str) 

            # Group by has_job and gender
            student_counts = filtered_df.groupby(["has_job", "gender"]).size().reset_index(name="count")

            # Create the bar chart
            fig = px.bar(
                student_counts,
                x="has_job",
                y="count",
                color="gender",
                barmode="group",
                labels={"has_job": "ការមានការងារ", "count": "ចំនួនសិក្ខាកាម", "gender": "ភេទ"},
                color_discrete_sequence=["#4dc3ff", "#0077b3"],  # Custom colors
                text=student_counts["count"].map("{:,}".format),  # Format numbers with commas
            )

            # Improve label positioning for better visibility
            fig.update_traces(
                texttemplate='%{text}',  # Ensure formatted text is displayed properly
                textposition='outside'  # Position labels outside bars for better visibility
            )

            fig.update_layout(
                height=450,  # Reduce the height to fit content
                margin=dict(l=20, r=20, t=40, b=40),  # Reduce margins for better spacing
                yaxis=dict(
                    tickformat=",",  # Format numbers with commas
                    title_text="ចំនួនសិក្ខាកាម",  # Label for Y-axis
                    showgrid=False  # Remove background grid for cleaner look
                ),
                xaxis=dict(
                    title_text="ការមានការងារ",  # Label for X-axis
                    tickangle=0  # Keep labels horizontal
                ),
                plot_bgcolor="white",  # Clean white background
            )

            # Display the chart
            st.plotly_chart(fig, use_container_width=True)

    with col6:
        with st.container(border=True):
            st.markdown(
                f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ស្ថិតិប្រាក់ចំណូលរបស់សិក្ខាកាម</h4>',
                unsafe_allow_html=True
            )

            # Apply filters if they exist in session state
            if 'gender_filter' in st.session_state:
                filtered_df = filtered_df[filtered_df['gender'] == st.session_state.gender_filter]

            if 'income_filter' in st.session_state:
                filtered_df = filtered_df[filtered_df['income'] == st.session_state.income_filter]

            # Ensure 'income' is numeric and clean
            filtered_df["income"] = pd.to_numeric(filtered_df["income"], errors="coerce")
            filtered_df = filtered_df.dropna(subset=["income"])

            # Define income bins
            bins = list(range(50, 1551, 50))  # 50 to 1500, step 50
            labels = [f"{i}-{i+49}" for i in bins[:-1]]

            # Bin income data
            filtered_df["income_range"] = pd.cut(filtered_df["income"], bins=bins, labels=labels, right=False)

            # Count students in each income range
            income_counts = filtered_df["income_range"].value_counts().sort_index().reset_index()
            income_counts.columns = ["Income Range", "Student Count"]

            # Plot line chart
            fig = px.line(
                income_counts,
                x="Income Range",
                y="Student Count",
                markers=True,
                text=income_counts["Student Count"].map("{:,}".format),
                labels={
                    "Income Range": "ចន្លោះប្រាក់ចំណូល ($)",
                    "Student Count": "ចំនួនសិក្ខាកាម"
                }
            )

            # Beautify the chart
            fig.update_traces(
                textposition="top center",
                line=dict(color="#0077b3", width=3),
                marker=dict(size=8, color="#4dc3ff", line=dict(width=1, color="#0077b3"))
            )

            fig.update_layout(
                height=450,
                margin=dict(l=40, r=10, t=40, b=100),
                yaxis=dict(tickformat=",", title="ចំនួនសិក្ខាកាម"),
                xaxis=dict(title="ចន្លោះប្រាក់ចំណូល ($)", tickangle=-45),
                plot_bgcolor="white"
            )

            # Show chart
            st.plotly_chart(fig, use_container_width=True)

    col7, col8 = st.columns([1,1.2])

    # Donut chart for scholarship status
    with col7:
        with st.container(border=True):
            st.markdown(
                '<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ស្ថានភាពរបស់សិក្ខាកាម</h4>',
                unsafe_allow_html=True
            )

            # Dictionary for Khmer status
            status_dict = {
                1: "សកម្ម",
                0: "អសកម្ម",
                3: "កំពុងស្នើសុំ",
                2: "របៀបព្រៀង",
                4: "រង់ចាំ",
                5: "បន្តសិក្សា",
                8: "បញ្ចប់ការសិក្សា",
                9: "ចេញ",
                -3: "បដិសេធ",
                -2: "សកម្មតិច",
                -8: "ស្តុក",
                -9: "លុប",
                10: "ចេញមុនពេលរៀន",
                11: "ចេញកំឡុងពេលរៀន",
                7: "ចេញក្រោយការសិក្សា",
                6: "ចេញមុនពេលរៀនខ្វះឯកសារ"
            }

            # Clean and map
            cleaned_df = filtered_df[filtered_df["scholarship_status"].notna()]
            cleaned_df = cleaned_df[cleaned_df["scholarship_status"].astype(str).isin([str(k) for k in status_dict])]
            cleaned_df["scholarship_status_kh"] = cleaned_df["scholarship_status"].astype(int).map(status_dict)

            # Count values
            schola_counts = cleaned_df["scholarship_status_kh"].value_counts().reset_index()
            schola_counts.columns = ["ស្ថានភាពរបស់សិក្ខាកាម", "ចំនួនសិក្ខាកាម"]

            if schola_counts.empty:
                st.warning("គ្មានទិន្នន័យអំពីស្ថានភាពអាហារូបករណ៍។")
            else:
                fig_scholarship = px.pie(
                    schola_counts,
                    names="ស្ថានភាពរបស់សិក្ខាកាម",
                    values="ចំនួនសិក្ខាកាម",
                    hole=0.5
                )

                fig_scholarship.update_traces(
                    textinfo="label+value",
                    textposition="outside",
                    pull=[0.05] * len(schola_counts),
                    showlegend=True,
                    textfont_size=14
                )

                fig_scholarship.update_layout(
                    margin=dict(t=120, b=0, l=200, r=150),  # Increased right margin, reduced left
                    showlegend=True,
                    legend_title_text="",
                    legend=dict(
                        orientation="v",
                        x=1.2,  # Shift legend slightly left
                        y=1
                    ),
                    annotations=[dict(
                        text="",
                        showarrow=False
                    )]
                )

                # Shift donut chart just a little bit to the left
                fig_scholarship.update_traces(domain=dict(x=[0.0, 0.0]))

                st.plotly_chart(fig_scholarship, use_container_width=True)

        with col8:
                # Ensure data is aggregated properly
                if "position" in filtered_df.columns:
                    with st.container(border=True):
                        # Count students per province
                        position_counts = filtered_df["position"].value_counts().reset_index().head(15)
                        position_counts.columns = ["position", "Student Count"]

                        # Format numbers with commas for text labels
                        position_counts["Student Count Formatted"] = position_counts["Student Count"].apply(lambda x: f"{x:,}")

                        # Khmer Title
                        st.markdown(
                            f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">មុខតំណែងរបស់សិក្ខាកាមក្នុងបរិបទការងារ​ (១៥)</h4>',
                            unsafe_allow_html=True
                        )

                        # 🔹 Create the bar chart
                        fig_bar = px.bar(
                            position_counts,
                            x="position",
                            y="Student Count",
                            text="Student Count Formatted",  # Formatted text
                            labels={"position": "មុខតំណែង", "Student Count": "ចំនួនសិក្ខាកាម"},
                            color="Student Count",
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
                                    ticktext=province_counts["position"].values
                                ),
                                yaxis=dict(
                                    range=[0, max(province_counts["Student Count"].values) * 1.2]
                                ),
                                bargap=0.8,
                                width=200,
                                height=450,
                                margin=dict(l=20, r=20, t=40, b=40)
                            )

                        # 🔹 Show the chart
                        st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.warning("The dataset does not contain 'address_city_province_name' column.")

    # ---- Raw Data Preview ----
    st.subheader("ទិន្នន័យជាទម្រង់តារាង")
    st.dataframe(filtered_df, height=450, use_container_width=True)

    # ---- Refresh Data Button ----
    if st.button("🔄Refresh Data"):
        st.cache_data.clear()  # Clear the data cache to force reload
        st.rerun()  # Use st.rerun() to trigger rerun

if __name__ == "__main__":
    main()