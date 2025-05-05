import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

# ---- Database Connection ----
DB_USER = "root"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_NAME = "tvetm"

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

# Dictionary of marital statuses
marital_statuses = {
    1: "នៅលីវ",
    2: "រៀបការ",
    3: "លែងលះ",
    4: "មេម៉ាយ"
}

#Khmer Ditionary custome
province_coordinates = {
    "Phnom Penh": {"khmer": "ភ្នំពេញ", "coordinates": (11.5564, 104.9282)},
    "Siem Reap": {"khmer": "សៀមរាប", "coordinates": (13.3633, 103.8564)},
    "Battambang": {"khmer": "បាត់ដំបង", "coordinates": (13.0957, 103.2022)},
    "Banteay Meanchey": {"khmer": "បន្ទាយមានជ័យ", "coordinates": (13.6511, 102.9875)},
    "Kampong Cham": {"khmer": "កំពង់ចាម", "coordinates": (12.0000, 105.4500)},
    "Kampong Chhnang": {"khmer": "កំពង់ឆ្នាំង", "coordinates": (12.2500, 104.6667)},
    "Kampong Speu": {"khmer": "កំពង់ស្ពឺ", "coordinates": (11.4500, 104.5167)},
    "Kampong Thom": {"khmer": "កំពង់ធំ", "coordinates": (12.7111, 104.8889)},
    "Kampot": {"khmer": "កំពត", "coordinates": (10.6333, 104.1833)},
    "Kandal": {"khmer": "កណ្ដាល", "coordinates": (11.4833, 104.9500)},
    "Koh Kong": {"khmer": "កោះកុង", "coordinates": (11.6175, 102.9842)},
    "Kratie": {"khmer": "ក្រចេះ", "coordinates": (12.4881, 106.0189)},
    "Mondulkiri": {"khmer": "មណ្ឌលគីរី", "coordinates": (12.0000, 107.2000)},
    "Oddar Meanchey": {"khmer": "ឧត្តរមានជ័យ", "coordinates": (14.1600, 103.5000)},
    "Pailin": {"khmer": "ប៉ៃលិន", "coordinates": (12.8500, 102.6000)},
    "Preah Sihanouk": {"khmer": "ព្រះសីហនុ", "coordinates": (10.6093, 103.5296)},
    "Preah Vihear": {"khmer": "ព្រះវិហារ", "coordinates": (13.8000, 104.9667)},
    "Prey Veng": {"khmer": "ព្រៃវែង", "coordinates": (11.5000, 105.3333)},
    "Pursat": {"khmer": "ពោធិ៍សាត", "coordinates": (12.5388, 103.9193)},
    "Ratanakiri": {"khmer": "រតនគិរី", "coordinates": (13.7394, 106.9873)},
    "Stung Treng": {"khmer": "ស្ទឹងត្រែង", "coordinates": (13.5231, 105.9692)},
    "Svay Rieng": {"khmer": "ស្វាយរៀង", "coordinates": (11.0884, 105.7993)},
    "Takeo": {"khmer": "តាកែវ", "coordinates": (10.9908, 104.7850)},
    "Tboung Khmum": {"khmer": "ត្បូងឃ្មុំ", "coordinates": (11.9000, 105.6667)},
}

def load_data():
    """Fetch data from MySQL and ensure all data is displayed correctly."""
    query = "SELECT * FROM tvetsms_data"  # Replace with your actual table name
    try:
        df = pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Return empty DataFrame to avoid further errors

    df.fillna({"gender": "Unknown", "apply_major_name": "Unknown", "sector_name": "Unknown", "status": "Unknown"}, inplace=True)
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
    col1, col2, col3, col4, col5 = st.columns([1,1,1,1,0.6])

    # Create a copy of the dataframe to prevent modifications to the original data
    filtered_df = df.copy()

    # ---- 1️⃣ Filter by Province ----
    with col1:
        # Get Khmer names for provinces
        khmer_provinces = [province_coordinates[province]["khmer"] for province in province_coordinates]
        selected_provinces = st.multiselect("ខេត្ត/ក្រុង", khmer_provinces)

        if selected_provinces:
            # Map selected Khmer provinces back to English for filtering
            selected_english_provinces = [
                province for province, data in province_coordinates.items() if data["khmer"] in selected_provinces
            ]
            # Filter data based on selected provinces (address_city_provinces column)
            filtered_df = filtered_df[filtered_df["address_city_provinces"].isin(selected_english_provinces)]

        # Dynamically update institution options based on filtered province selection
        if selected_provinces:
            institution_options = sorted(filtered_df["school_name"].unique()) if not filtered_df.empty else []
        else:
            institution_options = sorted(df["school_name"].unique()) if not df.empty else [] # reset the institution list.

    # ---- 2️⃣ Filter by Institution ----
    with col2:
        selected_institutions = st.multiselect("គ្រឹះស្ថាន អ.ប.វ.", institution_options)

        if selected_institutions:
            # Filter data based on selected institutions (school_name column)
            filtered_df = filtered_df[filtered_df["school_name"].isin(selected_institutions)]

        # Update sector options based on selected institution
        sector_options = sorted(filtered_df["sector_name"].unique()) if not filtered_df.empty else []

    # ---- 3️⃣ Filter by Sector ----
    with col3:
        selected_sectors = st.multiselect("វិស័យ", sector_options)

        if selected_sectors:
            filtered_df = filtered_df[filtered_df["sector_name"].isin(selected_sectors)]

        # Update major options based on selected sector
        major_options = sorted(filtered_df["apply_major_name"].unique()) if not filtered_df.empty else []

    # ---- 4️⃣ Filter by Major ----
    with col4:
        selected_majors = st.multiselect("ជំនាញ", major_options)
        if selected_majors:
            filtered_df = filtered_df[filtered_df["apply_major_name"].isin(selected_majors)]

    # ---- 5️⃣ Gender Filter ----
    with col5:
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

    # If no data matches the filters
    if filtered_df.empty:
        st.warning("No data matches your filter criteria.")
        st.stop()  # Stop further processing if no data is available after filtering.

    # ---- KPI Metrics ----
    total_students = len(filtered_df)  # Use filtered_df for all calculations
    avg_age = int(filtered_df["age"].mean()) if "age" in filtered_df.columns and not filtered_df.empty else 0
    total_female = filtered_df[filtered_df["gender"].str.lower() == "female"].shape[0] if "gender" in filtered_df.columns else 0
    students_status_1 = filtered_df[filtered_df["status"] == 1].shape[0] if "status" in filtered_df.columns else 0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.markdown(f'<div class="kpi-card"><h4>ចំនួនសិស្សសរុប</h4><h2>{total_students:,} នាក់</h2></div>', unsafe_allow_html=True)

    with kpi3:
        st.markdown(f'<div class="kpi-card"><h4>ចំនួនសិស្សស្រីសរុប</h4><h2>{total_female:,} នាក់</h2></div>', unsafe_allow_html=True)

    with kpi2:
        st.markdown(f'<div class="kpi-card"><h4>អាយុសិស្សជាមធ្យម</h4><h2>{avg_age} ឆ្នាំ</h2></div>', unsafe_allow_html=True)

    with kpi4:
        st.markdown(f'<div class="kpi-card"><h4>សិស្សកំពុងសិក្សា</h4><h2>{students_status_1:,} នាក់</h2></div>', unsafe_allow_html=True)

    # ---- Gender and Age Distribution in the same row ----
    col1, col2 = st.columns([0.7, 2])

    with col1:
        with st.container(border=True):  # Add border here
            st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ការបែងចែកសិស្សតាមភេទ</h4>', unsafe_allow_html=True) 
            
            if "gender" in filtered_df.columns:
                gender_labels = {"male": "ប្រុស", "female": "ស្រី"}  # Gender dictionary
                
                gender_count = filtered_df["gender"].value_counts().reset_index()
                gender_count.columns = ["gender", "count"]
                gender_count["gender"] = gender_count["gender"].map(gender_labels)  # Apply Khmer labels
                
                fig1 = px.pie(
                    names=gender_count["gender"],
                    values=gender_count["count"]
                    # title="Gender Distribution"
                )
                fig1.update_traces(hovertemplate='<b>%{label}</b><br>Count: %{value:,}<extra></extra>')
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
                    # title="Age Distribution by Gender"
                    labels={"age": "អាយុ", "count": "ចំនួនសិស្ស", "gender": "ភេទ"}
                )
                fig2.update_traces(hovertemplate='Age: %{x}<br>Count: %{y:,}<extra></extra>')
                st.plotly_chart(fig2, use_container_width=True)

    # ---- Marital Status Graph----
    col3, col4 = st.columns([1, 2])
    with col3:
        with st.container(border=True):
            st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ស្ថានភាពអាពាហ៍ពិពាហ៍របស់សិស្ស</h4>', unsafe_allow_html=True)
            
            if "marital_status" in filtered_df.columns:
                if filtered_df["marital_status"].isnull().all():
                    st.warning("The 'marital_status' column exists, but all values are null. Please populate the column with marital status data.")
                    
                    # Create a placeholder bar chart if data is unavailable
                    fig_placeholder = px.bar(
                        x=["Unavailable"],
                        y=[0],
                        text=["Data Unavailable"],
                    )
                    fig_placeholder.update_traces(textposition="outside")
                    st.plotly_chart(fig_placeholder, use_container_width=True)
                else:
                    # Map the marital status to labels
                    filtered_df["marital_status_label"] = filtered_df["marital_status"].map(marital_statuses)
                    marital_counts = filtered_df["marital_status_label"].value_counts().reset_index()
                    marital_counts.columns = ["Marital Status", "Count"]

                    # Create the pie chart
                    fig = px.pie(
                        marital_counts,
                        names="Marital Status",
                        values="Count",
                        hole=0.5,
                        title="    "  # Optional title
                    )

                    # ✅ Show the number of students instead of percentage
                    fig.update_traces(textinfo="label+value", pull=[0.1, 0.1, 0.1])

                    st.plotly_chart(fig, use_container_width=True)

            else:
                st.warning("The 'marital_status' column is missing from your dataset. Please add the column to your database and populate it with marital status data.")
                
                # Create a placeholder bar chart if the column is missing
                fig_placeholder = px.bar(
                    x=["Unavailable"],
                    y=[0],
                    text=["Data Unavailable"],
                )
                fig_placeholder.update_traces(textposition="outside")
                st.plotly_chart(fig_placeholder, use_container_width=True)

    # ---- Sector Distribution ----
    with col4:
        with st.container(border=True):
            st.markdown(
                f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ស្ថិតិសិស្សតាមវិស័យ</h4>',
                unsafe_allow_html=True
            )

            if "sector_name" in filtered_df.columns:
                # 🔹 Count students per sector
                sector_count = filtered_df["sector_name"].value_counts().reset_index()
                sector_count.columns = ["Sector", "Count"]

                # 🔹 Format Count for display (1,000 format)
                sector_count["student_count"] = sector_count["Count"].map("{:,}".format)

                # 🔹 Sort by count (ascending) for left-to-right display
                sector_count = sector_count.sort_values(by="Count", ascending=True)

                # 🔹 Bar chart
                fig3 = px.bar(
                    sector_count,
                    x="Sector",
                    y="Count",
                    text="student_count",  # ✅ Use formatted numbers here
                    labels={"Sector": "វិស័យ", "Count": "ចំនួនសិស្ស"},
                    color="Count",
                    color_continuous_scale="blues",
                )

                # 🔹 Adjust text and layout
                fig3.update_traces(
                    textposition="outside",
                    textfont=dict(size=12),
                    cliponaxis=False
                )

                fig3.update_layout(
                    xaxis=dict(categoryorder="total ascending"),
                    margin=dict(l=40, r=10, t=40, b=80)
                )

                # 🔹 Special layout for single bar
                if len(sector_count) == 1:
                    fig3.update_layout(
                        xaxis=dict(range=[-1, 1], tickvals=[0], ticktext=sector_count["Sector"].values),
                        yaxis=dict(range=[0, max(sector_count["Count"].values) * 1.2]),
                        bargap=0.8,
                        width=200,
                        height=300,
                        margin=dict(l=20, r=20, t=40, b=40)
                    )

                # 🔹 Display the chart
                st.plotly_chart(fig3, use_container_width=True)

            else:
                st.warning("The dataset does not contain 'sector_name' column.")


    # Student by province graph
    with st.container(border=True):
        st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ស្ថិតិសិស្សតាមខេត្ត/ក្រុង</h4>', unsafe_allow_html=True)
        if "address_city_provinces" in filtered_df.columns:
            # 🔹 Map the province names to Khmer names
            filtered_df["province_khmer"] = filtered_df["address_city_provinces"].map(lambda x: province_coordinates.get(x, {}).get("khmer", x))

            # 🔹 Count students per province
            province_counts = filtered_df["province_khmer"].value_counts().reset_index()
            province_counts.columns = ["Province", "Student Count"]

            # 🔹 Format numbers with commas
            province_counts["Student Count Display"] = province_counts["Student Count"].map("{:,}".format)

            # 🔹 Sort for left-to-right
            province_counts = province_counts.sort_values(by="Student Count", ascending=True)

            # 🔹 Create the bar chart
            fig_bar = px.bar(
                province_counts,
                x="Province",
                y="Student Count",
                text="Student Count Display",  # ✅ Use formatted text here
                labels={"Province": "ខេត្ត/ក្រុង", "Student Count": "ចំនួនសិស្ស"},
                color="Student Count",
                color_continuous_scale="blues",
            )

            # 🔹 Style adjustments
            fig_bar.update_traces(
                textposition="outside",
                textfont=dict(size=12),
                cliponaxis=False
            )

            fig_bar.update_layout(
                xaxis=dict(categoryorder="total ascending"),
                margin=dict(l=40, r=10, t=40, b=80)
            )

            # 🔹 Single bar display adjustment
            if len(province_counts) == 1:
                fig_bar.update_layout(
                    xaxis=dict(range=[-1, 1], tickvals=[0], ticktext=province_counts["Province"].values),
                    yaxis=dict(range=[0, max(province_counts["Student Count"].values) * 1.2]),
                    bargap=0.8,
                    width=200,
                    height=300,
                    margin=dict(l=20, r=20, t=40, b=40)
                )

            # 🔹 Display chart
            st.plotly_chart(fig_bar, use_container_width=True)

        else:
            st.warning("The dataset does not contain 'address_city_provinces' column.")

    # Student by Institution graph
    with st.container(border=True):
        st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ស្ថិតិសិស្សតាមគ្រឹះស្ថាន អ.ប.វ.</h4>', unsafe_allow_html=True)

        if "school_name" in filtered_df.columns:
            # 🔹 Count students per institution
            inti_counts = filtered_df["school_name"].value_counts().reset_index()
            inti_counts.columns = ["Institution", "Student Count"]

            # 🔹 Format the numbers with commas
            inti_counts["Student Count Display"] = inti_counts["Student Count"].map("{:,}".format)

            # 🔹 Sort and limit to top 30 institutions
            inti_counts = inti_counts.sort_values(by="Student Count", ascending=True).head(30)

            # 🔹 Bar chart
            fig_bar = px.bar(
                inti_counts,
                x="Institution",
                y="Student Count",
                text="Student Count Display",  # ✅ Use formatted text here
                labels={"Institution": "គ្រឹះស្ថាន អ.ប.វ.", "Student Count": "ចំនួនសិស្ស"},
                color="Student Count",
                color_continuous_scale="blues",
            )

            fig_bar.update_traces(
                textposition="outside",
                textfont=dict(size=12),
                cliponaxis=False
            )

            fig_bar.update_layout(
                xaxis=dict(categoryorder="total ascending"),
                margin=dict(l=40, r=10, t=40, b=80)
            )

            if len(inti_counts) == 1:
                fig_bar.update_layout(
                    xaxis=dict(range=[-1, 1], tickvals=[0], ticktext=inti_counts["Institution"].values),
                    yaxis=dict(range=[0, max(inti_counts["Student Count"].values) * 1.2]),
                    bargap=0.8,
                    width=200,
                    height=300,
                    margin=dict(l=20, r=20, t=40, b=40)
                )

            st.plotly_chart(fig_bar, use_container_width=True)

        else:
            st.warning("The dataset does not contain 'school_name' column.")

    # ---- Raw Data Preview ----
    st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ទិន្នន័យជាទម្រង់តារាង</h4>', unsafe_allow_html=True)
    #st.subheader("ទិន្នន័យជាទម្រង់តារាង")
    st.dataframe(filtered_df, height=400, use_container_width=True)

    # ---- Refresh Data Button ----
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()  # Clear the data cache to force reload
        st.rerun()  # Use st.rerun() to trigger rerun

if __name__ == "__main__":
    main()
