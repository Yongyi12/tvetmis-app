import streamlit as st
from PIL import Image
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# ---- Database Connection ----
DB_USER = "root"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_NAME = "tvetm"

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

# Load background image
image = Image.open("C:\\Users\\yongy\\Documents\\INTERNSHIP II\\The TVETMIS's dashborad Project\\Dashboards\\webserver\\pages\\images\\YoungYi-Coco.3.jpg")

# Khmer Dictionary for province names
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
    "Kep": {"khmer": "កែប", "coordinates": (11.9000, 105.6667)},

}

# Styles
def set_css():
    st.markdown("""
        <style>
            @font-face {
                font-family: 'Khmer OS Battambang';
                src: url('path/to/KhmerOSBattambang-Regular.ttf') format('truetype'); /* Replace with the actual path */
                font-weight: normal;
                font-style: normal;
            }
                
            /* All the font in this page is used Khmer OS battambang */
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
                margin-bottom: 25px;
                /*margin-buttom: 2px;*/
                color: white;
            }
            /* Bullet card custom */
            .custom-kpi-card ul {
                padding-left: 20px; /* Controls left indentation */
                list-style-position: outside; /* Ensures bullets are outside */
            }

            .custom-kpi-card li {
                text-indent: -18px; /* Moves the first line back */
                padding-left: 20px; /* Ensures second line aligns with the first one */
                line-height: 1.6; /* Improves readability */
                font-size: 16px;
                text-align: left;
            }

            /* the title custome card custom */
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

# Function to load student data and aggregate counts
def load_total_students():
    query_15m = "SELECT province_name FROM tvet15m_data"
    query_sms = "SELECT address_city_provinces FROM tvetsms_data"
    
    df_15m = pd.read_sql(query_15m, engine)
    df_sms = pd.read_sql(query_sms, engine)
    
    df_15m.rename(columns={'province_name': 'province'}, inplace=True)
    df_sms.rename(columns={'address_city_provinces': 'province'}, inplace=True)
    
    # Calculate the counts based on the number of entries in each dataframe
    df_15m_count = df_15m.groupby('province').size().reset_index(name='count')
    df_sms_count = df_sms.groupby('province').size().reset_index(name='count')
    
    # Combine both counts
    df_total = pd.concat([df_15m_count, df_sms_count]).groupby('province', as_index=False).sum()

    # Translate province names to Khmer using the dictionary
    df_total['province_khmer'] = df_total['province'].apply(lambda x: province_coordinates.get(x, {}).get('khmer', x))

    return df_total

# Streamlit App-
def main():
    set_css()  # Apply custom CSS styles
    st.image(image, use_container_width=True)

    # Load the total students data
    df_total = load_total_students()
    
    # Check if the data is empty
    if df_total.empty:
        st.warning("No data available to display.")
    else:
        # Display the total students by province in a dataframe
        c1, c2 = st.columns([1.5, 2])

        # Column 1: Dataframe
        with c1:
                st.markdown(
                    """
                    <style>
                    .custom-kpi-card {
                        background-color: #3f85c5; /* Custom blue color */
                        color: white; /* White text for contrast */
                        padding: 15px;
                        border-radius: 10px;
                        text-align: center;
                        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2);
                        position: relative;
                        margin: 10px 0 15px 0; /* Reduce top margin */
                        top: -10px; /* Move it up */
                    }
                    </style>
                    <div class="custom-kpi-card">
                        <h5>គោលបំណងនៃពាក្យថា TVET</h5>
                        <ul>
                            <li>រៀនដើម្បីមានជំនាញច្បាស់លាស់ រៀនដើម្បីមានការងារធ្វើ រៀនដើម្បីបង្កើនប្រាក់ចំណូល។</li>
                            <li>រៀនដោយមិនមានបង់ប្រាក់ ថែមទាំងទទួលបានប្រាក់ក្នុងរយៈពេលសិក្សាទៀតផង។</li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                    # ---- KPI Metrics ---
                kpi1, kpi2 = st.columns(2)
                #df_total = df_total.sort_values(by='count')

                total_students = int(df_total['count'].sum())  # Ensure integer
                female_students = int(total_students * 0.5)  # Convert to integer
                avg_age = int(20)  # Ensure integer
                active_students = int(total_students)  # Ensure integer

                with kpi1:
                    st.markdown(f'<div class="kpi-card"><h4>ចំនួនសិស្សសរុប</h4><h2>{total_students:,}</h2></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="kpi-card"><h4>ចំនួនសិស្សស្រីសរុប</h4><h2>{female_students:,}</h2></div>', unsafe_allow_html=True)

                with kpi2:
                    st.markdown(f'<div class="kpi-card"><h4>អាយុសិស្សជាមធ្យម</h4><h2>{avg_age}</h2></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="kpi-card"><h4>សិស្សកំពុងសិក្សា</h4><h2>{active_students:,}</h2></div>', unsafe_allow_html=True)

        
    # Column 2: Bar chart using Plotly
    with c2:
        with st.container(border=True):
            st.markdown(f'<h4 style="font-family: \'Khmer OS Battambang\', sans-serif;">ស្ថិតិសិស្សតាមខេត្ត</h4>', unsafe_allow_html=True)

            # Sort the dataframe by the 'count' column in ascending order
            df_total_sorted = df_total.sort_values(by='count', ascending=True)

            # Plotly Bar Chart with Khmer provinces
            fig = px.bar(df_total_sorted, x='province_khmer', y='count', labels={"province_khmer": "ខេត្ត", "count": "ចំនួនសិស្ស"})
            fig.update_traces(marker_color='#2872f0')  # Customize bar color
            fig.update_layout(
                xaxis_title="ខេត្ត",
                yaxis_title="ចំនួនសិស្ស",
                xaxis={'categoryorder': 'total ascending'},
                yaxis=dict(tickformat="d")  # Format y-axis numbers as decimals
            )

            # Display the Plotly chart
            st.plotly_chart(fig, use_container_width=True)

    df_total_filtered = df_total[['province_khmer', 'count']]  # Use Khmer column for province
    st.dataframe(df_total_filtered, hide_index=True)
if __name__ == "__main__":
    main()
