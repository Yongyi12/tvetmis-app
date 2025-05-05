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
    query = "SELECT * FROM student_internships_15m"
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

    # Khmer labels for poverty_status
    poverty_dict = {
        "NEAR_POOR": "គ្រួសារងាយរងហានិភ័យ",
        "NOT_POOR": "មិនមានប័ណ្ណសមធម៍",
        "POOR_1": "គ្រួសារមានប័ណ្ណក្រីក្រកម្រិត១",
        "POOR_2": "គ្រួសារមានប័ណ្ណក្រីក្រកម្រិត២"
    }

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

    # ---- Filters in Columns ----
    col1, col2, col3 = st.columns(3)

    # ---- Province Filter ----
    with col3:
        province_options = sorted(df["province_name"].unique())
        selected_provinces = st.multiselect("ខេត្ត/ក្រុង", province_options)
        if selected_provinces:
            filtered_df = filtered_df[filtered_df["province_name"].isin(selected_provinces)]

    # ---- Role Filter ----
    with col1:
        # Use the filtered_df from the province filter
        school_options = sorted(filtered_df["school_name"].unique())
        selected_roles = st.multiselect("គ្រឹះស្ថាន អ.ប.វ.", school_options)
        if selected_roles:
            filtered_df = filtered_df[filtered_df["school_name"].isin(selected_roles)]

    # ---- Gender Filter ----
    with col2:
        gender_mapping = {"female": "ស្រី", "male": "ប្រុស"}

        # Use the filtered_df from the previous filters
        gender_options = filtered_df["gender"].dropna().unique()
        gender_options = [g for g in gender_options if g in gender_mapping]

        if gender_options:
            display_gender_options = [gender_mapping[g] for g in gender_options]
            selected_display_genders = st.multiselect("ភេទ", display_gender_options)
            selected_genders = [key for key, value in gender_mapping.items() if value in selected_display_genders]
            if selected_genders:
                filtered_df = filtered_df[filtered_df["gender"].isin(selected_genders)]
        else:
            st.warning("⚠️ No gender data available after previous filters.")

    # ---- KPI Metrics ----
    total_students = len(filtered_df)
    total_female = filtered_df[filtered_df["gender"].str.lower() == "female"].shape[0] if "gender" in filtered_df.columns else 0
    total_internship_pass = filtered_df[filtered_df["internship_pass_fail"] == 1].shape[0]

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        with st.container(border=True):
            st.markdown(f'<div class="metric-container"><div class="metric-label">ចំនួនសិក្ខាកាមសរុប</div><div class="metric-value">{total_students:,} នាក់</div></div>', unsafe_allow_html=True)

    with kpi2:
        with st.container(border=True):
            st.markdown(f'<div class="metric-container"><div class="metric-label">សិក្ខាកាមបានជាប់កម្មសិក្សា</div><div class="metric-value">{total_internship_pass:,} នាក់</div></div>', unsafe_allow_html=True)

    with kpi3:
        with st.container(border=True):
            st.markdown(f'<div class="metric-container"><div class="metric-label">ចំនួនសិក្ខាកាមស្រីសរុប</div><div class="metric-value">{total_female:,} នាក់</div></div>', unsafe_allow_html=True)

    with kpi4:
        with st.container(border=True):
            st.markdown(f'<div class="metric-container"><div class="metric-label">សិស្សបានបញ្ចប់ការសិក្សា</div><div class="metric-value">{total_internship_pass:,} នាក់</div></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    gender_mapping = {"male": "ប្រុស", "female": "ស្រី"}
    gender_colors = {"male": "#0077b3", "female": "#4dc3ff"}

    with col1:
        with st.container(border=True):
            st.markdown('<h4 style="font-family: \"Khmer OS Battambang\";">ការបែងចែកសិស្សតាមភេទ</h4>', unsafe_allow_html=True)

            if "gender" in filtered_df.columns:
                gender_count = filtered_df["gender"].str.lower().value_counts()
                gender_labels = [gender_mapping.get(g, g) for g in gender_count.index]

                fig1 = px.pie(
                    names=gender_labels,
                    values=gender_count.values,
                    color=gender_count.index,
                    color_discrete_map=gender_colors
                )
                fig1.update_traces(hovertemplate='<b>%{label}</b><br>ចំនួនសិក្ខាកាម: %{value:,}<extra></extra>')
                st.plotly_chart(fig1, use_container_width=True)

    with col2:
        with st.container(border=True):
            st.markdown(
                '<h4 style="font-family: \"Khmer OS Battambang\"; color: #2C3E50;">ស្ថិតិសិក្ខាកាមតាមវេនសិក្សា</h4>',
                unsafe_allow_html=True
            )

            # Apply filters before grouping
            if 'gender_filter' in st.session_state:
                filtered_df = filtered_df[filtered_df['gender'] == st.session_state.gender_filter]
            if 'shift_filter' in st.session_state:
                filtered_df = filtered_df[filtered_df['poverty_status'] == st.session_state.shift_filter]

            # Handle null poverty_status (fill with placeholder)
            filtered_df["poverty_status_filled"] = filtered_df["poverty_status"].fillna("")

            # Khmer labels including null
            poverty_dict_with_null = {**poverty_dict, "": "មិនមានទិន្នន័យ"}

            # Build all combinations for reindex
            all_poverty = list(poverty_dict_with_null.keys())
            all_gender = list(gender_dict.keys())

            # Group by filled poverty status + gender and include all combinations
            student_counts = (
                filtered_df.groupby(["poverty_status_filled", "gender"])
                .size()
                .reindex(
                    pd.MultiIndex.from_product(
                        [all_poverty, all_gender],
                        names=["poverty_status_filled", "gender"]
                    ),
                    fill_value=0
                )
                .reset_index(name="count")
            )

            # Map to Khmer labels
            student_counts["poverty_status_kh"] = student_counts["poverty_status_filled"].map(poverty_dict_with_null)
            student_counts["gender_kh"] = student_counts["gender"].str.lower().map(gender_dict)

            # Get y-axis max
            max_group_count = student_counts.groupby("poverty_status_kh")["count"].sum().max()

            # Create the bar chart
            fig = px.bar(
                student_counts,
                x="poverty_status_kh",
                y="count",
                color="gender_kh",
                barmode="group",
                labels={
                    "poverty_status_kh": "ប័ណ្ណសមធម៍",
                    "count": "ចំនួនសិក្ខាកាម",
                    "gender_kh": "ភេទ"
                },
                color_discrete_sequence=["#4dc3ff", "#0077b3"],
                text=student_counts["count"].map("{:,}".format)
            )

            # Format chart
            fig.update_traces(texttemplate='%{text}', textposition="auto")
            fig.update_layout(
                height=450,
                margin=dict(l=40, r=10, t=80, b=120),
                yaxis=dict(
                    tickformat=",",
                    title_text="ចំនួនសិក្ខាកាម",
                    showgrid=False,
                    range=[0, max_group_count * 1.2]
                ),
                xaxis=dict(
                    title_text="ប័ណ្ណសមធម៍",
                    tickangle=-45,
                    tickmode="array",
                    automargin=True
                ),
                plot_bgcolor="white",
            )

            # Display chart
            st.plotly_chart(fig, use_container_width=True)

    # Student by province graph
    with st.container(border=True):
        st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ស្ថិតិសិស្សតាមខេត្ត/ក្រុង</h4>', unsafe_allow_html=True)
        if "province_name" in filtered_df.columns:
            # 🔹 Count students per province
            province_counts = filtered_df["province_name"].value_counts().reset_index()
            province_counts.columns = ["Province", "Student Count"]

            # 🔹 Format the numbers with commas
            province_counts["Student Count Display"] = province_counts["Student Count"].map("{:,}".format)

            # 🔹 Sort by Student Count (ascending) for left-to-right display
            province_counts = province_counts.sort_values(by="Student Count", ascending=True)

            # 🔹 Bar chart for province-wise student distribution
            fig_bar = px.bar(
                province_counts,
                x="Province",
                y="Student Count",
                text="Student Count Display",  # ✅ formatted number here
                labels={"Province": "ខេត្ត/ក្រុង", "Student Count": "ចំនួនសិក្ខាកាម"},
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

            # 🔹 Handling for a single bar
            if len(province_counts) == 1:
                fig_bar.update_layout(
                    xaxis=dict(range=[-1, 1], tickvals=[0], ticktext=province_counts["Province"].values),
                    yaxis=dict(range=[0, max(province_counts["Student Count"].values) * 1.2]),
                    bargap=0.8,
                    width=200,
                    height=300,
                    margin=dict(l=20, r=20, t=40, b=40)
                )

            st.plotly_chart(fig_bar, use_container_width=True)

        else:
            st.warning("The dataset does not contain 'province_name' column.")

    col3, col4 = st.columns([1,1.7])
    with col3:
        with st.container(border=True):
            st.markdown(
                f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ស្ថិតិសិក្ខាកាមតាមតាមវិស័យរបស់ដៃគូសហការ</h4>',
                unsafe_allow_html=True
            )

            # 🔹 Define mapping for partner_type values
            partner_type_dict = {
                5: "ជាមួយវិស័យឯកជន",
                1: "ក្នុងប្រទេស",
                3: "ជាមួយគ្រឹះស្ថានជាតិ"
            }

            # 🔹 Check for 'partner_type' column
            if "partner_type" in filtered_df.columns:

                # 🔸 Handle case where all values are null
                if filtered_df["partner_type"].isnull().all():
                    st.warning("The 'partner_type' column exists, but all values are null. Please populate it with marital status data.")

                    # Placeholder chart for empty data
                    fig_placeholder = px.bar(
                        x=["Unavailable"],
                        y=[0],
                        text=["Data Unavailable"]
                    )
                    fig_placeholder.update_traces(textposition="outside")
                    st.plotly_chart(fig_placeholder, use_container_width=True)

                else:
                    # 🔸 Map the partner_type values to Khmer labels
                    filtered_df["partner_type_label"] = filtered_df["partner_type"].map(partner_type_dict).fillna("មិនមាន")

                    # 🔸 Count by label
                    partner_counts = filtered_df["partner_type_label"].value_counts().reset_index()
                    partner_counts.columns = ["Partner Type", "Count"]

                    # 🔸 Create pie chart
                    fig = px.pie(
                        partner_counts,
                        names="Partner Type",
                        values="Count",
                        hole=0.5
                    )

                    # ✅ Show label and count only (no percentages)
                    fig.update_traces(textinfo="label+value", pull=[0.01] * len(partner_counts))

                    st.plotly_chart(fig, use_container_width=True)

            else:
                st.warning("The 'partner_type' column is missing from your dataset. Please add and populate it.")

                # Placeholder chart when column is missing
                fig_placeholder = px.bar(
                    x=["Unavailable"],
                    y=[0],
                    text=["Data Unavailable"]
                )
                fig_placeholder.update_traces(textposition="outside")
                st.plotly_chart(fig_placeholder, use_container_width=True)

    with col4:
        # Student by Partner Name
        with st.container(border=True):
            st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ស្ថិតិសិក្ខាកាមតាម​ស្ថានប័នរបស់ដៃគូសហការ​ (២០)</h4>', unsafe_allow_html=True)
            if "partner_name" in filtered_df.columns:
                # 🔹 Count students per province
                province_counts = filtered_df["partner_name"].value_counts().reset_index().head(20)
                province_counts.columns = ["Partner", "Student Count"]

                # 🔹 Format the numbers with commas
                province_counts["Student Count Display"] = province_counts["Student Count"].map("{:,}".format)

                # 🔹 Sort by Student Count (ascending) for left-to-right display
                province_counts = province_counts.sort_values(by="Student Count", ascending=True)

                # 🔹 Bar chart for province-wise student distribution
                fig_bar = px.bar(
                    province_counts,
                    x="Partner",
                    y="Student Count",
                    text="Student Count Display",  # ✅ formatted number here
                    labels={"Partner": "ស្ថានប័ននៃដៃគូសហការ", "Student Count": "ចំនួនសិក្ខាកាម"},
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

                # 🔹 Handling for a single bar
                if len(province_counts) == 1:
                    fig_bar.update_layout(
                        xaxis=dict(range=[-1, 1], tickvals=[0], ticktext=province_counts["Partner"].values),
                        yaxis=dict(range=[0, max(province_counts["Student Count"].values) * 1.2]),
                        bargap=0.8,
                        width=200,
                        height=300,
                        margin=dict(l=20, r=20, t=40, b=40)
                    )

                st.plotly_chart(fig_bar, use_container_width=True)

            else:
                st.warning("The dataset does not contain 'province_name' column.")
    with st.container(border=True):
        st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ស្ថិតិសិក្ខាកាមតាមជំនាញ</h4>', unsafe_allow_html=True)
        # Major Name - Area Chart
        # Prepare data
        filtered_df['student_count'] = 1
        major_counts = (
            filtered_df
            .groupby('major_name')['student_count']
            .sum()
            .reset_index()
            .sort_values(by='student_count', ascending=True)  # 👈 sort ascending for left-to-right flow
        )

        # Plotly Area Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=major_counts['major_name'],  # this will now go L -> R by student count
            y=major_counts['student_count'],
            mode='lines',
            fill='tozeroy',
            line=dict(color='rgba(0, 150, 136, 1)', width=2),
            fillcolor='rgba(0, 150, 136, 0.4)'),
        )

        fig.update_layout(
            #title="ស្ថិតិសិក្ខាកាមតាមជំនាញ",
            xaxis_title="ជំនាញ",
            yaxis_title="ចំនួនសិក្ខាកាម",
            template="simple_white",
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)

    # ---- Raw Data Preview ----
    st.subheader("ទិន្នន័យជាទម្រង់តារាង")
    st.dataframe(filtered_df, height=450, use_container_width=True)

    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
if __name__ == '__main__':
    main()