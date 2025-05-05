import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import warnings
import plotly.graph_objects as go

# ---- Database Connection ----
DB_USER = "root"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_NAME = "tvetm"

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

student_statuses = {
    "ACTIVE": 1,
    "INACTIVE": 0,
    "REQUESTING": 3,
    "DRAFT": 2,
    "waiting": 4,
    "RESUME_STUDY": 5,
    "FINISHED_STUDY": 8,
    "QUIT": 9,
    "REJECTED": -3,
    "DISABLED": -2,
    "ARCHIVE": -8,
    "DELETE": -9,
    "QUIT_BFORE_COURSE": 10,
    "QUIT_DURING_COURSE": 11,
    "QUIT_AFTER_COURSE": 7,
    "QUIT_NOT_ENOGUH_DOC": 6
}

@st.cache_data
def load_teacher_data():
    query = "SELECT * FROM school_staff WHERE is_teaching = 1"
    try:
        df = pd.read_sql(query, engine)

        warnings.simplefilter(action="ignore", category=UserWarning)
        df["start_work_at"] = df["start_work_at"].replace("0000-00-00 00:00:00", None)
        df["start_work_at"] = pd.to_datetime(df["start_work_at"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
        df.loc[:, "start_work_at"] = df["start_work_at"].fillna(pd.Timestamp("1970-01-01"))
        df.loc[:, "start_work_at_str"] = df["start_work_at"].astype(str)  # Keep original as datetime, create str for display
    except Exception as e:
        st.error(f"Error loading teacher data: {e}")
        return pd.DataFrame()

    return df

def main():
    # ---- Custom Khmer Font ----
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Battambang:wght@400;700&display=swap');
        body, h1, h2, h3, h4, h5, h6, p, div, span, label, button, input, select, textarea {
            font-family: 'Battambang', sans-serif !important;
        }
        * {
        font-family: 'Khmer OS Battambang', sans-serif !important;
        }
        h1, h2, h3, h4, h5, h6, p, span, label, button, input, select, textarea {
        font-family: 'Khmer OS Battambang', sans-serif !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    df_teachers = load_teacher_data()

    if df_teachers.empty:
        st.warning("No teacher data found.")
        return

    # ---- Filters ----
    col1, col2 = st.columns([1,1])

    with col1:
        # ---- Date Range Filter with Validation ----
        with st.container(border=True):
            st.subheader("រយៈពេលចាប់ផ្ដើមបម្រើការងារ")

            # Custom CSS to control height/width of date picker
            st.markdown("""
                <style>
                div[data-baseweb="input"] > div {
                    height: 29px;  /* Adjust height */
                    font-size: 16px;  /* Optional: adjust font size */
                }
                .stDateInput {
                    padding: 10px 5px;
                }
                </style>
                """, unsafe_allow_html=True)

            min_date = df_teachers["start_work_at"].min().date()
            max_date = df_teachers["start_work_at"].max().date()

            # Get the date input safely
            date_range = st.date_input(
                "ជ្រើសរើសចន្លោះកាលបរិច្ឆេទ",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )

            valid_selection = False  # flag to check if valid

            # Validation check
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date, end_date = date_range

                if start_date > end_date:
                    st.error("⚠️ កាលបរិច្ឆេទចាប់ផ្ដើមត្រូវតែតិចជាងកាលបរិច្ឆេទបញ្ចប់។ សូមជ្រើសរើសម្តងទៀត។")
                else:
                    date_filtered_teachers = df_teachers[
                        (df_teachers["start_work_at"].dt.date >= start_date) &
                        (df_teachers["start_work_at"].dt.date <= end_date)
                    ]

                    if date_filtered_teachers.empty:
                        st.warning("⚠️ គ្មានគ្រូក្នុងចន្លោះកាលបរិច្ឆេទដែលបានជ្រើស។ សូមជ្រើសរើសកាលបរិច្ឆេទផ្សេងទៀត។")
                    else:
                        df_teachers = date_filtered_teachers
                        valid_selection = True
            else:
                st.info("ℹ️ សូមជ្រើសរើសចន្លោះកាលបរិច្ឆេទ (ថ្ងៃចាប់ផ្ដើម និងថ្ងៃបញ្ចប់) មុនពេលបន្ត។")

    with col2:
        with st.container(border=True):
            # ---- Province Filter ----
            with st.container():
                province_options = sorted(df_teachers["address_city_provinces"].dropna().unique())
                selected_provinces = st.multiselect("ខេត្ត/ក្រុង", province_options)

                if selected_provinces:
                    filtered_teachers = df_teachers[df_teachers["address_city_provinces"].isin(selected_provinces)]
                else:
                    filtered_teachers = df_teachers.copy()

            # ---- Role Filter ----
            with st.container():
                role_options = sorted(filtered_teachers["role_name"].dropna().unique())
                selected_roles = st.multiselect("តួនាទី", role_options)

                if selected_roles:
                    filtered_teachers = filtered_teachers[filtered_teachers["role_name"].isin(selected_roles)]

    # ---- Gender Filter ----
    #with col2:
    #    gender_mapping = {"Female": "ស្រី", "Male": "ប្រុស"}
     #   filtered_teachers["gender"] = filtered_teachers["gender"].astype(str).str.strip().str.capitalize()
      #  gender_options = [g for g in filtered_teachers["gender"].unique() if g in gender_mapping]

       # if gender_options:
     #       display_gender_options = [gender_mapping[g] for g in gender_options]
       #     selected_display_genders = st.multiselect("ភេទ", display_gender_options)
      #      selected_genders = [key for key, value in gender_mapping.items() if value in selected_display_genders]

      #      if selected_genders:
       #         filtered_teachers = filtered_teachers[filtered_teachers["gender"].isin(selected_genders)]
       # else:
        #    st.warning("⚠️ No gender data available.")

    # ---- KPI Metrics for Teachers ----
    if valid_selection:
        total_teachers = len(filtered_teachers)

        # Total female teachers
        total_female_teachers = filtered_teachers[filtered_teachers["gender"].str.lower() == "female"].shape[0]
        
        # Active teachers
        active_teachers = filtered_teachers[filtered_teachers["status"] == 1].shape[0]
        
        # Calculate average age from date_of_birth
        if "date_of_birth" in filtered_teachers.columns and not filtered_teachers.empty:
            # Ensure date_of_birth is in datetime format
            filtered_teachers["date_of_birth"] = pd.to_datetime(filtered_teachers["date_of_birth"], errors='coerce')
            
            # Calculate age
            today = pd.to_datetime("today")
            filtered_teachers["age"] = (today - filtered_teachers["date_of_birth"]).dt.days // 365
            
            # Calculate the average age
            avg_age = int(filtered_teachers["age"].mean())
        else:
            avg_age = 0  # If no date_of_birth column or it's empty

        # KPI Cards Layout
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

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

        def format_percentage(percent):
            if percent == int(percent):
                return f"{int(percent)}%"
            else:
                return f"{percent:.2f}%"

        with kpi1:
            with st.container(border=True):
                #total_partners = len(filtered_partners)
                st.markdown(f'<div class="metric-container"><div class="metric-label">ចំនួនសាស្ត្រាចារ្យសរុប</div><div class="metric-value">{total_teachers:,} នាក់</div></div>', unsafe_allow_html=True)

        with kpi2:
            with st.container(border=True):
                #private_sector_count = len(filtered_partners[filtered_partners["type_development_partners"] == "ជាមួយវិស័យឯកជន"])
                #private_sector_percent = (private_sector_count / total_partners) * 100 if total_partners > 0 else 0
                st.markdown(f'<div class="metric-container"><div class="metric-label">អាយុជាមធ្យមនៃសាស្ត្រាចារ្យ</div><div class="metric-value">{avg_age} ឆ្នាំ</div></div>', unsafe_allow_html=True)

        with kpi3:
            with st.container(border=True):
                #domestic_count = len(filtered_partners[filtered_partners["type_development_partners"] == "ក្នុងប្រទេស"])
                #domestic_percent = (domestic_count / total_partners) * 100 if total_partners > 0 else 0
                st.markdown(f'<div class="metric-container"><div class="metric-label">ចំនួនសរុបនៃសាស្ត្រាចារ្យស្រី</div><div class="metric-value">{total_female_teachers:,} នាក់</div></div>', unsafe_allow_html=True)

        with kpi4:
            with st.container(border=True):
                #abraod_count = len(filtered_partners[filtered_partners["type_development_partners"] == "ក្រៅប្រទេស"])
                #abraod__percent = (abraod_count / total_partners) * 100 if total_partners > 0 else 0
                st.markdown(f'<div class="metric-container"><div class="metric-label">សាស្ត្រាចារ្យកំពុងបម្រើការងារ</div><div class="metric-value">{active_teachers:,} នាក់</div></div>', unsafe_allow_html=True)

    # ---- Visualizations ----
    col1, col2 = st.columns([1, 2])

    # ---- Donut Chart for Teacher Roles ----
    with col1:
        with st.container(border=True):
            st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">មុខតំណែងនៃសាស្ត្រាចារ្យ</h4>', unsafe_allow_html=True)

            # Count roles
            role_counts = filtered_teachers["role_name"].value_counts().reset_index()
            role_counts.columns = ["Role", "Count"]

            if role_counts.empty:
                st.warning("គ្មានទិន្នន័យអំពីតួនាទីសាស្ត្រាចារ្យ។")
                # Placeholder bar chart
                fig_placeholder = px.bar(
                    x=["Unavailable"],
                    y=[0],
                    text=["Data Unavailable"],
                )
                fig_placeholder.update_traces(textposition="outside")
                st.plotly_chart(fig_placeholder, use_container_width=True)
            else:
                custom_colors = px.colors.qualitative.Pastel
                # Create Donut Chart
                fig = px.pie(
                    role_counts,
                    names="Role",
                    values="Count",
                    hole=0.5,
                    title="    ", # Optional blank title
                    color_discrete_sequence=custom_colors
                )

                # Show number instead of percentage
                fig.update_traces(textinfo="label+value", pull=[0.05]*len(role_counts))

                st.plotly_chart(fig, use_container_width=True)

    # Top 15 Bar chart of teachers by province
    with col2:
        with st.container(border=True):
            #st.subheader("គ្រូកំពូលទាំង ២៥ តាមខេត្ត/ក្រុង")
            st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ចំនួនសាស្ត្រាចារ្យតាមខេត្ត/ក្រុង</h4>', unsafe_allow_html=True)
            
            # Count teachers by province
            province_counts = filtered_teachers["address_city_provinces"].value_counts().reset_index()
            province_counts.columns = ["Province", "Count"]
            top_15_provinces = province_counts.head(26)

            # Sort provinces by Count (ascending order)
            top_15_provinces = top_15_provinces.sort_values(by="Count", ascending=True)

            # 🔹 Bar chart for top 15 teachers by province with TEAL color scale
            fig_province_counts = px.bar(
                top_15_provinces,
                x="Province",
                y="Count",
                text="Count",
                labels={"Province": "ខេត្ត/ក្រុង", "Count": "ចំនួន"},
                color="Count",
                color_continuous_scale="teal",  # Changed from "blues" to "teal"
            )

            # 🔹 Adjust text outside bars
            fig_province_counts.update_traces(
                textposition="outside",
                textfont=dict(size=12),
                cliponaxis=False
            )

            # 🔹 Layout adjustment
            fig_province_counts.update_layout(
                xaxis=dict(categoryorder="total ascending"),
                margin=dict(l=40, r=10, t=40, b=80),
                xaxis_title="ខេត្ត/ក្រុង",
                yaxis_title="ចំនួន",
                height=450,  # Optional: same height as school chart
            )

            # 🔹 Handle single bar case
            if len(top_15_provinces) == 1:
                fig_province_counts.update_layout(
                    xaxis=dict(range=[-1, 1], tickvals=[0], ticktext=top_15_provinces["Province"].values),
                    yaxis=dict(range=[0, max(top_15_provinces["Count"].values) * 1.2]),
                    bargap=0.8,
                    width=200,
                    height=450,
                    margin=dict(l=20, r=20, t=40, b=40)
                )

            # 🔹 Display chart
            st.plotly_chart(fig_province_counts, use_container_width=True)

    with st.container(border=True):
        # --- Bar chart for Teachers by Schools (ALL Schools) ---
        st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ចំនួនសាស្ត្រាចារ្យតាមគ្រឹះស្ថាន អ.ប.វ.</h4>', unsafe_allow_html=True)

        # Count teachers by school name
        school_counts = filtered_teachers["schools_name"].value_counts().reset_index()
        school_counts.columns = ["School", "Count"]

        # Sort by count ascending
        school_counts = school_counts.sort_values(by="Count", ascending=True).head(25)

        # Bar chart for all schools
        fig_school_counts = px.bar(
            school_counts,
            x="School",
            y="Count",
            text="Count",
            labels={"School": "គ្រឹះស្ថាន អ.ប.វ.", "Count": "ចំនួនគ្រូ"},
            color="Count",
            color_continuous_scale="teal",
        )

        fig_school_counts.update_traces(
            textposition="outside",
            textfont=dict(size=12),
            cliponaxis=False
        )

        fig_school_counts.update_layout(
            xaxis=dict(categoryorder="total ascending"),
            margin=dict(l=40, r=10, t=40, b=150),  # Extra bottom margin for long school names
            xaxis_title="គ្រឹះស្ថាន អ.ប.វ.",
            yaxis_title="ចំនួនគ្រូ",
            height=500,  # Increase chart height if many schools
        )

        st.plotly_chart(fig_school_counts, use_container_width=True)

    # ---- Employment Type Graph ----
    col4, col5 = st.columns([1, 2])
    with col4:
            with st.container(border=True):
                st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ស្ថានភាពសាស្ត្រាចារ្យ</h4>', unsafe_allow_html=True)

                # Check if 'status' column exists
                if "status" in filtered_teachers.columns:
                    if filtered_teachers["status"].isnull().all():
                        st.warning("The 'status' column exists, but all values are null. Please populate the column with student status data.")

                        # Placeholder bar chart if data unavailable
                        fig_placeholder = px.bar(
                            x=["Unavailable"],
                            y=[0],
                            text=["Data Unavailable"],
                        )
                        fig_placeholder.update_traces(textposition="outside")
                        st.plotly_chart(fig_placeholder, use_container_width=True)
                    else:
                        # Map statuses to labels (reverse map for lookup)
                        status_label_map = {v: k for k, v in student_statuses.items()}
                        filtered_teachers["status_label"] = filtered_teachers["status"].map(status_label_map)

                        # Count status occurrences
                        status_counts = filtered_teachers["status_label"].value_counts().reset_index()
                        status_counts.columns = ["Status", "Count"]

                        custom_colors = px.colors.qualitative.Pastel

                        # Create donut chart
                        fig = px.pie(
                            status_counts,
                            names="Status",
                            values="Count",
                            hole=0.5,
                            title="    ",  # Optional blank title
                            color_discrete_sequence=custom_colors
                        )

                        # Show number of students instead of percentage
                        fig.update_traces(textinfo="label+value", pull=[0.05]*len(status_counts))

                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("The 'status' column is missing from your dataset. Please add the column to your database and populate it with student status data.")

                    # Placeholder bar chart if column missing
                    fig_placeholder = px.bar(
                        x=["Unavailable"],
                        y=[0],
                        text=["Data Unavailable"],
                    )
                    fig_placeholder.update_traces(textposition="outside")
                    st.plotly_chart(fig_placeholder, use_container_width=True)

    with col5:
        with st.container(border=True):
            st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ប្រភេទនៃការងាររបស់សាស្ត្រាចារ្យ</h4>', unsafe_allow_html=True)

            if "employment_type_name" in filtered_teachers.columns:
                if filtered_teachers["employment_type_name"].isnull().all():
                    st.warning("The 'employment_type_name' column exists, but all values are null. Please populate the column with employment type data.")

                    # Placeholder bar chart
                    fig_placeholder = px.bar(
                        x=["Unavailable"],
                        y=[0],
                        text=["Data Unavailable"],
                    )
                    fig_placeholder.update_traces(textposition="outside")
                    st.plotly_chart(fig_placeholder, use_container_width=True)
                else:
                    # Count employment types
                    employment_counts = filtered_teachers["employment_type_name"].value_counts().reset_index()
                    employment_counts.columns = ["Employment Type", "Count"]

                    # Sort ascending for better horizontal view
                    employment_counts = employment_counts.sort_values(by="Count", ascending=True)

                    # Create horizontal bar chart with TEAL color scale
                    fig = px.bar(
                        employment_counts,
                        x="Count",
                        y="Employment Type",
                        text="Count",
                        labels={"Employment Type": "ប្រភេទការងារ", "Count": "ចំនួនគ្រូ"},
                        orientation="h",  # Make sure it’s horizontal
                        color="Count",
                        color_continuous_scale="teal",  # Changed color scale
                    )

                    fig.update_traces(
                        textposition="outside",
                        textfont=dict(size=12),
                        cliponaxis=False
                    )

                    fig.update_layout(
                        margin=dict(l=40, r=10, t=40, b=40),
                        xaxis_title="ចំនួនគ្រូ",
                        yaxis_title="ប្រភេទការងារ",
                        height=450,
                    )

                    st.plotly_chart(fig, use_container_width=True)

            else:
                st.warning("The 'employment_type_name' column is missing from your dataset. Please add the column to your database and populate it with employment type data.")

                # Placeholder chart if column is missing
                fig_placeholder = px.bar(
                    x=["Unavailable"],
                    y=[0],
                    text=["Data Unavailable"],
                )
                fig_placeholder.update_traces(textposition="outside")
                st.plotly_chart(fig_placeholder, use_container_width=True)

    # ---- Display Raw Data ----
    #st.subheader("ទិន្នន័យរបស់សាស្ត្រាចារ្យជាទម្រង់តារាង")
    st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ទិន្នន័យរបស់សាស្ត្រាចារ្យជាទម្រង់តារាង</h4>', unsafe_allow_html=True)
    st.dataframe(filtered_teachers, height=400, use_container_width=True)

    # ---- Refresh Data Button ----
    if st.button("🔄Refresh Data"):
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()