import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from streamlit_lightweight_charts import renderLightweightCharts
import plotly.graph_objects as go

# ---- Database Connection ----
DB_USER = "root"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_NAME = "tvetm"

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

@st.cache_data
def load_data():
    query = "SELECT * FROM tvet15m where scholarship_status = 8"
    try:
        df = pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Error loading staff data: {e}")
        return pd.DataFrame()
    return df

def main():
    # ---- Custom Khmer Font ----
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Battambang:wght@400;700&display=swap');
        * {
            font-family: 'Khmer OS Battambang', sans-serif !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    df = load_data()
    if df.empty:
        return

    # Initialize filtered_df with the full dataset
    filtered_df = df.copy()

    # Khmer labels for gender
    gender_dict = {
        "female": "ស្រី",
        "male": "ប្រុស"
    }

    # Define CSS for centering and styling
    centered_metric_style = """
    <style>
    .metric-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 0.5em 0; /* Reduced vertical padding */
    }
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        margin-top: 0.1em; /* Added top margin */
    }
    .metric-label {
        font-size: 0.9em;
        color: #555;
        order: -1; /* Moves the label to the top */
        margin-bottom: 0.1em; /* Added bottom margin for spacing */
    }
    </style>
    """
    st.markdown(centered_metric_style, unsafe_allow_html=True)

    if df.empty:
        st.warning("រកមិនឃើញទិន្នន័យ")
        return

    # Create columns for the filters to appear horizontally
    col1, col2, col3, col4, co5 = st.columns([1.4, 1, 0.5, 0.8, 0.5])

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

    # ---- KPI Metrics ----
    total_students = len(filtered_df)
    total_female = filtered_df[filtered_df["gender"].str.lower() == "female"].shape[0] if "gender" in filtered_df.columns else 0
    #total_internship_pass = filtered_df[filtered_df["internship_pass_fail"] == 1].shape[0]

    if "date_of_birth" in filtered_df.columns:
        filtered_df["age"] = pd.to_datetime("today").year - pd.to_datetime(df["date_of_birth"], errors="coerce").dt.year
        filtered_df.fillna({"age": 0}, inplace=True)
        
    avg_age = int(filtered_df["age"].mean()) if "age" in filtered_df.columns and not filtered_df.empty else 0

    hasjob = filtered_df[filtered_df["has_job"] == 1].shape[0]

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        with st.container(border=True):
            st.markdown(f'<div class="metric-container"><div class="metric-label">ចំនួនសិក្ខាកាមសរុប</div><div class="metric-value">{total_students:,} នាក់</div></div>', unsafe_allow_html=True)

    with kpi2:
        with st.container(border=True):
            st.markdown(f'<div class="metric-container"><div class="metric-label">អាយុសិក្ខាកាមជាមធ្យម</div><div class="metric-value">{avg_age} ឆ្នាំ</div></div>', unsafe_allow_html=True)

    with kpi3:
        with st.container(border=True):
            st.markdown(f'<div class="metric-container"><div class="metric-label">ចំនួនសិក្ខាកាមស្រីសរុប</div><div class="metric-value">{total_female:,} នាក់</div></div>', unsafe_allow_html=True)

    with kpi4:
        with st.container(border=True):
            st.markdown(f'<div class="metric-container"><div class="metric-label">ចំនួនសិក្ខាកាមមានការងារធ្វើ</div><div class="metric-value">{hasjob:,} នាក់</div></div>', unsafe_allow_html=True)
    
       # ---- Gender and Age Distribution in the same row ----
    col1, col2 = st.columns([1, 2])

    # Define gender translations and color mapping
    gender_mapping = {"male": "ប្រុស", "female": "ស្រី"}
    gender_colors = {"male": "#2d34bd", "female": "#4dc3ff"}  # Blue for male, Orange for female

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

    age_colors = {"ប្រុស": "#2d34bd", "ស្រី": "#4dc3ff"}  # match Khmer labels here too

    with col2:
        with st.container(border=True):
            st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ស្ថិតិសិស្សតាមអាយុ</h4>', unsafe_allow_html=True) 
            
            if "age" in filtered_df.columns and "gender" in filtered_df.columns:
                gender_labels = {"male": "ប្រុស", "female": "ស្រី"}
                
                # Group data by age and gender
                age_distribution = (
                    filtered_df.groupby(["age", "gender"])
                    .size()
                    .reset_index(name="count")
                )
                age_distribution["gender"] = age_distribution["gender"].map(gender_labels)
                
                # Line chart
                fig2 = px.line(
                    age_distribution,
                    x="age",
                    y="count",
                    color="gender",
                    labels={
                        "age": "អាយុ",
                        "count": "ចំនួនសិក្ខាកាម",
                        "gender": "ភេទ"
                    },
                    color_discrete_map=age_colors
                )
                
                # Hover format
                fig2.update_traces(
                    hovertemplate='អាយុ: %{x} ឆ្នាំ<br>ចំនួនសិក្ខាកាម: %{y:,}<extra></extra>'
                )
                
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
        gender_labels = {"male": "ប្រុស", "female": "ស្រី"}
        gender_colors = {"ប្រុស": "#2d34bd", "ស្រី": "#4dc3ff"}  # <-- fix here

        with st.container(border=True):
            st.markdown(
                f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif; color: #2C3E50;">ស្ថិតិសិក្ខាកាមតាមវេនសិក្សា</h4>',
                unsafe_allow_html=True
            )

            if 'gender_filter' in st.session_state:
                filtered_df = filtered_df[filtered_df['gender'] == st.session_state.gender_filter]

            if 'shift_filter' in st.session_state:
                filtered_df = filtered_df[filtered_df['shift_name'] == st.session_state.shift_filter]

            student_counts = (
                filtered_df
                .groupby(["shift_name", "gender"])
                .size()
                .reset_index(name="count")
            )
            student_counts["gender"] = student_counts["gender"].map(gender_labels)

            fig = px.bar(
                student_counts,
                x="shift_name",
                y="count",
                color="gender",
                barmode="group",
                labels={
                    "shift_name": "វេនសិក្សា",
                    "count": "ចំនួនសិក្ខាកាម",
                    "gender": "ភេទ"
                },
                color_discrete_map=gender_colors,  # Khmer keys now match
                text=student_counts["count"].map("{:,}".format),
            )

            fig.update_traces(
                texttemplate='%{text}',
                textposition="auto"
            )

            fig.update_layout(
                height=450,
                margin=dict(l=40, r=10, t=80, b=120),
                yaxis=dict(
                    tickformat=",",
                    title_text="ចំនួនសិក្ខាកាម",
                    showgrid=False,
                    range=[0, student_counts["count"].max() * 1.2]
                ),
                xaxis=dict(
                    title_text="វេនសិក្សា",
                    tickangle=-45,
                    automargin=True
                ),
                plot_bgcolor="white",
            )

            st.plotly_chart(fig, use_container_width=True)

    col5, col6 = st.columns([1,1.5])
    with col5:
        gender_labels = {"male": "ប្រុស", "female": "ស្រី"}
        gender_colors = {"ប្រុស": "#2d34bd", "ស្រី": "#4dc3ff"}  # Khmer gender label as keys

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
            student_counts["gender"] = student_counts["gender"].map(gender_labels)  # ✅ Map to Khmer here

            # Create the bar chart
            fig = px.bar(
                student_counts,
                x="has_job",
                y="count",
                color="gender",
                barmode="group",
                labels={"has_job": "ការមានការងារ", "count": "ចំនួនសិក្ខាកាម", "gender": "ភេទ"},
                color_discrete_map=gender_colors,  # ✅ Custom color map
                text=student_counts["count"].map("{:,}".format),
            )

            fig.update_traces(
                texttemplate='%{text}',
                textposition='outside'
            )

            fig.update_layout(
                height=450,
                margin=dict(l=20, r=20, t=40, b=40),
                yaxis=dict(
                    tickformat=",",
                    title_text="ចំនួនសិក្ខាកាម",
                    showgrid=False
                ),
                xaxis=dict(
                    title_text="ការមានការងារ",
                    tickangle=0
                ),
                plot_bgcolor="white",
            )

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
                line=dict(color="#2d34bd", width=3),
                marker=dict(size=8, color="#4dc3ff", line=dict(width=1, color="#2d34bd"))
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

    # Ensure data is aggregated properly
    if "position" in filtered_df.columns:
            with st.container(border=True):
                # Count students per province
                position_counts = filtered_df["position"].value_counts().reset_index().head(25)
                position_counts.columns = ["position", "Student Count"]

                # Format numbers with commas for text labels
                position_counts["Student Count Formatted"] = position_counts["Student Count"].apply(lambda x: f"{x:,}")

                # Khmer Title
                st.markdown(
                    f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">មុខតំណែងរបស់សិក្ខាកាមក្នុងបរិបទការងារ​ (២៥)</h4>',
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
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()  # Clear the data cache to force reload
        st.rerun()  # Use st.rerun() to trigger rerun

if __name__ == "__main__":
    main()