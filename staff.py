import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from datetime import datetime

# ---- Database Connection ----
DB_USER = "root"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_NAME = "tvetm"

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

@st.cache_data
def load_staff_data():
    query = "SELECT * FROM tvet_staff"
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

    df_staff = load_staff_data()

    if df_staff.empty:
        st.warning("No staff data found.")
        return

    # ---- Filters in Columns ----
    col1, col2, col3 = st.columns(3)

    # ---- Province Filter ----
    with col3:
        province_options = sorted(df_staff["address_city_provinces"].unique())
        selected_provinces = st.multiselect("ខេត្ត/ក្រុង", province_options)

    if selected_provinces:
        filtered_staff = df_staff[df_staff["address_city_provinces"].isin(selected_provinces)]
    else:
        filtered_staff = df_staff.copy()

    # ---- Role Filter ----
    with col1:
        role_options = sorted(filtered_staff["role_name"].unique())
        selected_roles = st.multiselect("តួនាទី", role_options)

    if selected_roles:
        filtered_staff = filtered_staff[filtered_staff["role_name"].isin(selected_roles)]

    # ---- Gender Filter ----
    with col2:
        gender_mapping = {"female": "ស្រី", "male": "ប្រុស"}  # Mapping English to Khmer

        # Get unique gender values from filtered data
        gender_options = filtered_staff["gender"].dropna().unique()  # Remove NaN values
        gender_options = [g for g in gender_options if g in gender_mapping]  # Keep only mapped values

        if gender_options:  # Ensure options exist
            # Convert gender options to Khmer for display
            display_gender_options = [gender_mapping[g] for g in gender_options]

            # Use Khmer labels in the UI
            selected_display_genders = st.multiselect("ភេទ", display_gender_options)

            # Convert selected Khmer options back to English for filtering
            selected_genders = [key for key, value in gender_mapping.items() if value in selected_display_genders]

            if selected_genders:
                filtered_staff = filtered_staff[filtered_staff["gender"].isin(selected_genders)]
        else:
            st.warning("⚠️ No gender data available.")

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
            total_staff = len(filtered_staff)
            st.markdown(f'<div class="metric-container"><div class="metric-label">ចំនួនបុគ្គលិកសរុប</div><div class="metric-value">{total_staff} នាក់</div></div>', unsafe_allow_html=True)

    with kpi2:
        with st.container(border=True):
            total_females = len(filtered_staff[filtered_staff["gender"] == "female"])
            st.markdown(f'<div class="metric-container"><div class="metric-label">ចំនួនស្រ្តីសរុប</div><div class="metric-value">{total_females} នាក់</div></div>', unsafe_allow_html=True)

    with kpi3:
        with st.container(border=True):
            #print(f"date_of_birth column exists: {'date_of_birth' in filtered_staff.columns}")
            try:
                #print(f"date_of_birth column data type: {filtered_staff['date_of_birth'].dtype}")
                #print(f"date_of_birth column sample data: {filtered_staff['date_of_birth'].head()}")
                filtered_staff['date_of_birth'] = pd.to_datetime(filtered_staff['date_of_birth'], errors='coerce')
                filtered_staff = filtered_staff.dropna(subset=['date_of_birth'])
                #print(f"DataFrame length after dropna: {len(filtered_staff)}")
                ages = (datetime.now() - filtered_staff['date_of_birth']).dt.days // 365
                average_age = ages.mean()
                st.markdown(f'<div class="metric-container"><div class="metric-label">អាយុជាមធ្យម</div><div class="metric-value">{average_age:.0F} ឆ្នាំ</div></div>', unsafe_allow_html=True)
            except Exception as e:
                print(f"date_of_birth conversion error: {e}")
                st.markdown(f'<div class="metric-container"><div class="metric-label">អាយុជាមធ្យម</div><div class="metric-value">N/A</div></div>', unsafe_allow_html=True)

    with kpi4:
        with st.container(border=True):
            status_1_count = filtered_staff["status"].eq(1).sum()
            total_count = len(filtered_staff)
            percentage_status_1 = (status_1_count / total_count) * 100 if total_count > 0 else 0
            st.markdown(f'<div class="metric-container"><div class="metric-label">ភាគរយនៃស្ថានភាពរបស់បុគ្គលិកកំពុងបម្រើការងារ</div><div class="metric-value">{format_percentage(percentage_status_1)}</div></div>', unsafe_allow_html=True)

    with kpi5:
        with st.container(border=True):
            if not filtered_staff.empty:
                top_role = filtered_staff['role_name'].value_counts().idxmax()
                st.markdown(f'<div class="metric-container"><div class="metric-label">តួនាទីកំពូល</div><div class="metric-value">{top_role}</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="metric-container"><div class="metric-label">តួនាទីកំពូល</div><div class="metric-value">N/A</div></div>', unsafe_allow_html=True)

    # ---- Visualizations ----
    col1, col2 = st.columns([1.2, 1.5])

    # Bar chart of staff roles
    with col1:
        with st.container(border=True):
            st.markdown('<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">តួនាទីរបស់បុគ្គលិក</h4>', unsafe_allow_html=True)
            #st.subheader("តួនាទីរបស់បុគ្គលិក")
            role_counts = filtered_staff["role_name"].value_counts().reset_index()
            role_counts.columns = ["Role", "Count"]

            # Reverse the order for left-to-right display
            role_counts = role_counts.sort_values(by="Count", ascending=True)

            fig_roles = px.bar(
                role_counts,
                x="Count",  # X-axis should be the count
                y="Role",   # Y-axis should be the role
                text="Count",
                #title="Number of Staff by Role",
                labels={"Role": "តួនាទី", "Count": "ចំនួនបុគ្គលិក"},  # Khmer labels
                color="Role",
                color_discrete_sequence=px.colors.sequential.tempo,
                orientation="h",  # Horizontal bar chart
            )

            fig_roles.update_traces(textposition="outside")  # Place labels outside bars
            fig_roles.update_layout(yaxis_title="តួនាទី", xaxis_title="ចំនួនបុគ្គលិក", yaxis=dict(categoryorder="total ascending"))  # Left to right order

            st.plotly_chart(fig_roles, use_container_width=True)

    # Top 15 Bar chart of staff by province
    with col2:
        with st.container(border=True):
            st.markdown('<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ចំនួនបុគ្គលិកតាមខេត្ត/ក្រុង (១៥)</h4>', unsafe_allow_html=True)
            #st.subheader("បុគ្គលិកទាំង ១៥ ខេត្ត/ក្រុង")
            
            # Count staff by province
            province_counts = filtered_staff["address_city_provinces"].value_counts().reset_index()
            province_counts.columns = ["Province", "Count"]
            top_15_provinces = province_counts.head(15)

            # Sort provinces by Count (ascending order) for left-to-right sequence
            top_15_provinces = top_15_provinces.sort_values(by="Count", ascending=True)

            # 🔹 Bar chart for top 15 staff by province
            fig_province_counts = px.bar(
                top_15_provinces,
                x="Province",  # X-axis = Province
                y="Count",  # Y-axis = Count
                text="Count",  # Show count on top of the bars
                labels={"Province": "ខេត្ត/ក្រុង", "Count": "ចំនួនបុគ្គលិក"},  # Khmer labels
                color="Count",  # Color by count
                color_continuous_scale="tempo",  # Blue color gradient
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
            )

            # 🔹 Handling for a single bar scenario (center the bar)
            if len(top_15_provinces) == 1:
                fig_province_counts.update_layout(
                    xaxis=dict(range=[-1, 1], tickvals=[0], ticktext=top_15_provinces["Province"].values),  # Center single bar
                    yaxis=dict(range=[0, max(top_15_provinces["Count"].values) * 1.2]),  # Adjust y-axis range
                    bargap=0.8,  # Increase gap for single bar+
                    width=200,  # Reduce overall chart width
                    height=450,  # Reduce overall chart height
                    margin=dict(l=20, r=20, t=40, b=40)  # Adjust margins for better centering
                )

            # 🔹 Display the chart
            st.plotly_chart(fig_province_counts, use_container_width=True)

    col4, col5 = st.columns([2,1])

    with col4:
        # Check and calculate age
        if 'date_of_birth' in filtered_staff.columns:
            filtered_staff['date_of_birth'] = pd.to_datetime(filtered_staff['date_of_birth'], errors='coerce')
            filtered_staff = filtered_staff.dropna(subset=['date_of_birth'])
            filtered_staff['age'] = (datetime.now() - filtered_staff['date_of_birth']).dt.days // 365
        else:
            st.warning("The 'date_of_birth' column is missing from the data.")

        # Plot age distribution by gender
        if 'age' in filtered_staff.columns and 'gender' in filtered_staff.columns:
            gender_labels = {"male": "ប្រុស", "female": "ស្រី"}  # Gender dictionary

            age_distribution = filtered_staff.groupby(['age', 'gender']).size().reset_index(name='count')
            age_distribution['gender'] = age_distribution['gender'].map(gender_labels)  # Apply Khmer labels

            custom_colors = ["green", "purple"] # example colors, change it as you wish.

            fig2 = px.line(
                age_distribution,
                x='age',
                y='count',
                color='gender',
                labels={'age': 'អាយុ', 'count': 'ចំនួនបុគ្គលិក', 'gender': 'ភេទ'},
                color_discrete_sequence = custom_colors #Corrected line.
            )
            fig2.update_traces(hovertemplate='អាយុ: %{x}<br>ចំនួន: %{y:,}<extra></extra>')

            with st.container(border=True):
                st.markdown('<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ស្ថិតិបុគ្គលិកតាមអាយុ</h4>', unsafe_allow_html=True)
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("The necessary columns for plotting are missing.")

    with col5:
        with st.container(border=True):
            st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ការបែងចែកបុគ្គលិកតាមភេទ</h4>', unsafe_allow_html=True)

            # Count roles
            role_counts = filtered_staff["gender"].value_counts().reset_index()
            role_counts.columns = ["Gender", "Count"]

            gender_labels = {"male": "ប្រុស", "female": "ស្រី"}  # Gender dictionary

            # Apply Khmer labels
            role_counts["Gender"] = role_counts["Gender"].map(gender_labels)

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
                custom_colors = ["green", "purple"]
                # Create Donut Chart
                fig = px.pie(
                    role_counts,
                    names="Gender",
                    values="Count",
                    hole=0.5,
                    title="    ", # Optional blank title,
                    color_discrete_sequence=custom_colors
                )

                # Show number instead of percentage
                fig.update_traces(textinfo="label+value", pull=[0.05] * len(role_counts))

                st.plotly_chart(fig, use_container_width=True)

    # Display raw data
    st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ទិន្នន័យរបស់បុគ្គលិកជាទម្រង់តារាង</h4>', unsafe_allow_html=True)
    #st.subheader("ទិន្នន័យរបស់បុគ្គលិកជាទម្រង់តារាង")
    st.dataframe(filtered_staff, height=400, use_container_width=True)

    # ---- Refresh Data Button ----
    if st.button("🔄Refresh Data"):
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()