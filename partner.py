import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

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
def load_development_partners_data():
    query = "SELECT * FROM development_partners"
    try:
        df = pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Error loading development_partners_data: {e}")
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

    df_partners = load_development_partners_data()

    if df_partners.empty:
        st.warning("No development partners data found.")
        return

    # ---- Filters in Columns ----
    col1, col2, col3, col4 = st.columns(4)

    # ---- Province Filter ----
    with col4:
        province_options = sorted(df_partners["city_province_name"].unique())
        selected_provinces = st.multiselect("ខេត្ត/ក្រុង", province_options)

    if selected_provinces:
        filtered_partners = df_partners[df_partners["city_province_name"].isin(selected_provinces)]
    else:
        filtered_partners = df_partners.copy()

    if filtered_partners.empty:  
        st.warning("No development partners found in the selected provinces.")
        return

    # ---- School Filter ----
    with col1:
        school_options = sorted(filtered_partners["school_name"].unique())
        selected_schools = st.multiselect("ឈ្មោះគ្រឹះស្ថាន", school_options)

    if selected_schools:
        filtered_partners = filtered_partners[filtered_partners["school_name"].isin(selected_schools)]

        # ---- Type Filter (Dependent on School and Province) ----
        type_options = sorted(filtered_partners["type_development_partners"].unique())
    else:
        type_options = sorted(filtered_partners["type_development_partners"].unique())

    # ---- Type Filter ----
    with col2:
        selected_types = st.multiselect("ប្រភេទដៃគូរសហការ", type_options)

    if selected_types:
        filtered_partners = filtered_partners[filtered_partners["type_development_partners"].isin(selected_types)]

        # ---- Business Filter (Dependent on School, Type, and Province) ----
        business_options = sorted(filtered_partners["business"].unique())
    else:
        business_options = sorted(filtered_partners["business"].unique())

    # ---- Business Filter ----
    with col3:
        selected_businesses = st.multiselect("ប្រភេទអាជីវកម្ម", business_options)

    if selected_businesses:
        filtered_partners = filtered_partners[filtered_partners["business"].isin(selected_businesses)]

    if filtered_partners.empty:
        st.warning("No development partners found with the selected filters.")
        return

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

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
            total_partners = len(filtered_partners)
            st.markdown(f'<div class="metric-container"><div class="metric-label">ចំនួនដៃគូរសហការសរុប</div><div class="metric-value">{total_partners}</div></div>', unsafe_allow_html=True)

    with kpi2:
        with st.container(border=True):
            private_sector_count = len(filtered_partners[filtered_partners["type_development_partners"] == "ជាមួយវិស័យឯកជន"])
            private_sector_percent = (private_sector_count / total_partners) * 100 if total_partners > 0 else 0
            st.markdown(f'<div class="metric-container"><div class="metric-label">ភាគរយដៃគូរជាមួយវិស័យឯកជន</div><div class="metric-value">{private_sector_percent:.0f}%</div></div>', unsafe_allow_html=True)

    with kpi3:
        with st.container(border=True):
            domestic_count = len(filtered_partners[filtered_partners["type_development_partners"] == "ក្នុងប្រទេស"])
            domestic_percent = (domestic_count / total_partners) * 100 if total_partners > 0 else 0
            st.markdown(f'<div class="metric-container"><div class="metric-label">ភាគរយដៃគូរនៅក្នុងប្រទេស</div><div class="metric-value">{format_percentage(domestic_percent)}</div></div>', unsafe_allow_html=True)

    with kpi4:
        with st.container(border=True):
            abraod_count = len(filtered_partners[filtered_partners["type_development_partners"] == "ក្រៅប្រទេស"])
            abraod__percent = (abraod_count / total_partners) * 100 if total_partners > 0 else 0
            st.markdown(f'<div class="metric-container"><div class="metric-label">ភាគរយដៃគូរនៅក្រៅប្រទេស</div><div class="metric-value">{format_percentage(abraod__percent)}</div></div>', unsafe_allow_html=True)

    with kpi5:
        with st.container(border=True):
            active_count = len(filtered_partners[filtered_partners["status"] == 1])
            active__percent = (active_count / total_partners) * 100 if total_partners > 0 else 0
            st.markdown(f'<div class="metric-container"><div class="metric-label">ភាគរយដៃគូរសកម្ម</div><div class="metric-value">{active__percent:.0f}%</div></div>', unsafe_allow_html=True)
   
   
    # ---- Visualizations ----
    col1, col2 = st.columns([1.35, 2])
    #Donut chart
    with col1:
        with st.container(border=True):
            #st.subheader("ប្រភេទរបស់ដៃគូរសហការ")
            st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ប្រភេទរបស់ដៃគូរសហការ</h4>', unsafe_allow_html=True)

            # Count partner types
            partner_type_counts = filtered_partners["type_development_partners"].value_counts().reset_index()
            partner_type_counts.columns = ["Partner Type", "Count"]

            if partner_type_counts.empty:
                st.warning("គ្មានទិន្នន័យអំពីប្រភេទដៃគូ។")

                # Placeholder bar chart
                fig_placeholder = px.bar(
                    x=["Unavailable"],
                    y=[0],
                    text=["Data Unavailable"],
                )
                fig_placeholder.update_traces(textposition="outside")
                st.plotly_chart(fig_placeholder, use_container_width=True)
            else:
                # Create Donut Chart (match style)
                fig_partner_types = px.pie(
                    partner_type_counts,
                    names="Partner Type",
                    values="Count",
                    hole=0.5,
                    title="    "  # Empty title space (optional)
                )

                # Show number instead of percentage + slight pull effect
                fig_partner_types.update_traces(
                    textinfo="label+value",
                    pull=[0.05] * len(partner_type_counts)
                )

                st.plotly_chart(fig_partner_types, use_container_width=True)

    # Top 15 Bar chart of partners by province
    with col2:
        with st.container(border=True):
            st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ដៃគូរសហការតាមខេត្ត/ក្រុង​ (១៥)</h4>', unsafe_allow_html=True)
            #st.subheader("ដៃគូរសហការកំពូលទាំង ១៥ តាមខេត្ត/ក្រុង")
            
            # Count partners by province
            province_counts = filtered_partners["city_province_name"].value_counts().reset_index()
            province_counts.columns = ["Province", "Count"]
            top_15_provinces = province_counts.head(15)

            # Sort provinces by Count (ascending order) for left-to-right sequence
            top_15_provinces = top_15_provinces.sort_values(by="Count", ascending=True)

            # 🔹 Bar chart for top 15 partners by province
            fig_province_counts = px.bar(
                top_15_provinces,
                x="Province",  # X-axis = Province
                y="Count",  # Y-axis = Count
                text="Count",  # Show count on top of the bars
                labels={"Province": "ខេត្ត/ក្រុង", "Count": "ចំនួន"},  # Khmer labels
                color="Count",  # Color by count
                color_continuous_scale="blues",  # Blue color gradient
            )

            # 🔹 Adjust the text position outside the bars
            fig_province_counts.update_traces(
                textposition="outside",  # Position text outside the bars
                textfont=dict(size=12),  # Font size of text
                cliponaxis=False  # Ensure the text is not clipped
            )

            # 🔹 Update layout for proper positioning and sorting
            fig_province_counts.update_layout(
                xaxis=dict(categoryorder="total ascending"),  # Sort by total count in ascending order
                margin=dict(l=40, r=10, t=40, b=80),  # Adjust margins for label visibility
                xaxis_title="ខេត្ត/ក្រុង",  # Khmer label for Province
                yaxis_title="ចំនួន",  # Khmer label for Count
            )

            # 🔹 Handling for a single bar scenario (center the bar)
            if len(top_15_provinces) == 1:
                fig_province_counts.update_layout(
                    xaxis=dict(range=[-1, 1], tickvals=[0], ticktext=top_15_provinces["Province"].values),  # Center single bar
                    yaxis=dict(range=[0, max(top_15_provinces["Count"].values) * 1.2]),  # Adjust y-axis range
                    bargap=0.8,  # Increase gap for single bar
                    width=200,  # Reduce overall chart width
                    height=450,  # Reduce overall chart height
                    margin=dict(l=20, r=20, t=40, b=40)  # Adjust margins for better centering
                )

            # 🔹 Display the chart
            st.plotly_chart(fig_province_counts, use_container_width=True)

    col3, col4 = st.columns([1,2])

    with col3:
        with st.container(border=True):
            st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ស្ថានភាពរបស់ដៃគូរសហការ</h4>', unsafe_allow_html=True)

            # Check if 'status' column exists in filtered_partners
            if "status" in filtered_partners.columns:
                if filtered_partners["status"].isnull().all():
                    st.warning("The 'status' column exists, but all values are null. Please populate the column with status data.")

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
                    filtered_partners["status_label"] = filtered_partners["status"].map(status_label_map)

                    # Count status occurrences
                    status_counts = filtered_partners["status_label"].value_counts().reset_index()
                    status_counts.columns = ["Status", "Count"]

                    # Create donut chart
                    fig = px.pie(
                        status_counts,
                        names="Status",
                        values="Count",
                        hole=0.5,
                        title="    "  # Optional blank title
                    )

                    # Show number instead of percentage
                    fig.update_traces(textinfo="label+value", pull=[0.05]*len(status_counts))

                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("The 'status' column is missing from your dataset. Please add the column to your database and populate it with status data.")

                # Placeholder bar chart if column missing
                fig_placeholder = px.bar(
                    x=["Unavailable"],
                    y=[0],
                    text=["Data Unavailable"],
                )
                fig_placeholder.update_traces(textposition="outside")
                st.plotly_chart(fig_placeholder, use_container_width=True)
    with col4:
        with st.container(border=True):
            st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ស្ថិតិដៃគូរសហការតាមគ្រឹះស្ថាន អ.ប.វ.​ (១៥)</h4>', unsafe_allow_html=True)
            #st.subheader("ស្ថិតិដៃគូរសហការតាមគ្រឹះស្ថាន អ.ប.វ.​ (១៥)")

            # Count partners by school name
            school_counts = filtered_partners["school_name"].value_counts().reset_index()
            school_counts.columns = ["School", "Count"]
            top_15_schools = school_counts.head(15)

            # Sort schools by Count (ascending order) for left-to-right sequence
            top_15_schools = top_15_schools.sort_values(by="Count", ascending=True)

            # 🔹 Bar chart for top 15 schools
            fig_school_counts = px.bar(
                top_15_schools,
                x="School",  # X-axis = School
                y="Count",  # Y-axis = Count
                text="Count",  # Show count on top of the bars
                labels={"School": "គ្រឹះស្ថាន អ.ប.វ.", "Count": "ចំនួន"},  # Khmer labels
                color="Count",  # Color by count
                color_continuous_scale="blues",  # Blue color gradient
            )

            # 🔹 Adjust the text position outside the bars
            fig_school_counts.update_traces(
                textposition="outside",  # Position text outside the bars
                textfont=dict(size=12),  # Font size of text
                cliponaxis=False  # Ensure the text is not clipped
            )

            # 🔹 Update layout for proper positioning and sorting
            fig_school_counts.update_layout(
                xaxis=dict(categoryorder="total ascending"),  # Sort by total count in ascending order
                margin=dict(l=40, r=10, t=40, b=80),  # Adjust margins for label visibility
                xaxis_title="គ្រឹះស្ថាន អ.ប.វ.",  # Khmer label for School
                yaxis_title="ចំនួន",  # Khmer label for Count
            )

            # 🔹 Handling for a single bar scenario (center the bar)
            if len(top_15_schools) == 1:
                fig_school_counts.update_layout(
                    xaxis=dict(range=[-1, 1], tickvals=[0], ticktext=top_15_schools["School"].values),  # Center single bar
                    yaxis=dict(range=[0, max(top_15_schools["Count"].values) * 1.2]),  # Adjust y-axis range
                    bargap=0.8,  # Increase gap for single bar
                    width=200,  # Reduce overall chart width
                    height=450,  # Reduce overall chart height
                    margin=dict(l=20, r=20, t=40, b=40)  # Adjust margins for better centering
                )

            # 🔹 Display the chart
            st.plotly_chart(fig_school_counts, use_container_width=True)

    # Partner by Business graph
    with st.container(border=True):
        st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ស្ថិតិដៃគូរសហការតាមប្រភេទអាជីវកម្ម​ (២៥)</h4>', unsafe_allow_html=True)

        if "business" in filtered_partners.columns:
            # 🔹 Count partners per business
            business_counts = filtered_partners["business"].value_counts().reset_index().head(25)
            business_counts.columns = ["Business", "Partner Count"]

            # 🔹 Sort by Partner Count (ascending) for left-to-right display
            business_counts = business_counts.sort_values(by="Partner Count", ascending=True)

            # 🔹 Bar chart for business-wise partner distribution
            fig_business_bar = px.bar(
                business_counts,
                x="Business",  # X-axis = Business type
                y="Partner Count",  # Y-axis = Partner count
                text="Partner Count",
                labels={"Business": "ប្រភេទអាជីវកម្ម", "Partner Count": "ចំនួនដៃគូរ"},
                color="Partner Count",  # Color by partner count
                color_continuous_scale="blues",  # Blue color gradient
            )

            # 🔹 Ensure the x-axis follows the ascending order (left to right)
            fig_business_bar.update_traces(
                textposition="outside",  # Position text outside the bars
                textfont=dict(size=12),  # Font size of text
                cliponaxis=False  # Ensure text not clipped
            )

            # 🔹 Update layout to ensure proper positioning
            fig_business_bar.update_layout(
                xaxis=dict(categoryorder="total ascending"),  # Sort by total count
                margin=dict(l=40, r=10, t=40, b=80)  # Adjust bottom margin
            )

            # 🔹 Handling for a single bar scenario (center the bar)
            if len(business_counts) == 1:
                fig_business_bar.update_layout(
                    xaxis=dict(range=[-1, 1], tickvals=[0], ticktext=business_counts["Business"].values),  # Center bar
                    yaxis=dict(range=[0, max(business_counts["Partner Count"].values) * 1.2]),  # Adjust y-axis
                    bargap=0.8,  # Increase gap for single bar
                    width=200,
                    height=450,
                    margin=dict(l=20, r=20, t=40, b=40)
                )

            # 🔹 Display the chart
            st.plotly_chart(fig_business_bar, use_container_width=True)

        else:
            st.warning("The dataset does not contain 'business' column.")

    # Display raw data
    st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ទិន្នន័យរបស់ដៃគូរសហការជាទម្រង់តារាង</h4>', unsafe_allow_html=True)
    #st.subheader("ទិន្នន័យរបស់ដៃគូរសហការជាទម្រង់តារាង")
    st.dataframe(filtered_partners, height=400, use_container_width=True)

    # ---- Refresh Data Button ----
    if st.button("🔄Refresh Data"):
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()