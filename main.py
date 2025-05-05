import streamlit as st
import sys
from pathlib import Path
import base64
from io import BytesIO

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Add the 'pages' directory to the Python path
sys.path.append(str(Path(__file__).parent / "pages"))

import tvetsms
import tvet15m
import partner
import staff
import teacher
import home
import internship15m
import graduated
import erpl_candidate
from PIL import Image

image = Image.open("C:\\Users\\yongy\\Documents\\INTERNSHIP II\\The TVETMIS's dashborad Project\\Dashboards\\webserver\\pages\\images\\tvetlogo1.png")
st.set_page_config(page_title="TVETMIS Dashboard", page_icon= image, layout="wide")

# Custom CSS
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #2872f0;
        color: white
        padding: 20px;
    }
    /*The style of sidebar Navigation*/
    .sidebar-button {
        background-color: #3880f0;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 12px;
        text-align: center;
        width: 100%;
        font-size: 16px;
        font-weight: bold;
        transition: background-color 0.3s, color 0.3s, transform 0.2s;
    }
    /*The hover animation of sidebar Navigation*/
    .sidebar-button:hover {
        background-color: #2a6cd8;
        color: white;
        transform: scale(1.05);
    }
    /*The button after clicked style(Noted button)*/
    .selected-button {
        background-color: white !important;
        color: #2163d8 !important;
        border-radius: 8px;
        border: 3px solid #2163d8 !important;
        font-weight: bold !important;
        font-size: 16px !important;
        text-align: center;
        padding: 12px;
        width: 100%;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    /*The subpage of TVETSMS's styles*/
    .subpage-button {
        width: 100% !important; /* Set the width to 100% so it matches the main page button width */
        margin-left: 10px; /* Optional: Adjust for better alignment */
        background-color: #3897d2;
        color: white;
        border-radius: 8px;
        padding: 10px;
        font-size: 14px;
        font-weight: normal;
    }
    /*The subpage of TVETSMS's styles hover*/
    .subpage-button:hover {
        background-color: #3b6fd0;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

#Image under the navigation
st.sidebar.markdown(
    f"""
    <div style="display: flex; justify-content: center; margin-bottom: 40px;">
        <img src="data:image/png;base64,{image_to_base64(image)}" width="120">
    </div>
    """,
    unsafe_allow_html=True,
)

#st.sidebar.title("Navigation")

pages = {
    "home": "ទំព័រដើម",
    "tevtsms": "កម្មវិធី TVETMIS",
    "tvet15m": "កម្មវិធី TVET 1.5M",
    "erpl": "ERPL",
    "tvetlearning": "TVET E-LEARNING",
}

tevtsms_subpages = {
    "page1": "មន្រ្តីបម្រើការ",
    "page2": "សាស្រ្តាចារ្យ",
    "page3": "ដៃគូសហការ",
}

# TVET1.5M Subpages
tvet15m_subpages = {
    "page4": "សិស្សចុះកម្មសិក្សា",
    "page5": "បានបញ្ចប់ការសិក្សា",
}

# Initialize session state variables
if "page" not in st.session_state:
    st.session_state.page = "home"

if "tevtsms_subpage" not in st.session_state:
    st.session_state.tevtsms_subpage = None  # No default subpage selected for TVETMS

if "tvet15m_subpage" not in st.session_state:
    st.session_state.tvet15m_subpage = None

# Display the sidebar navigation
for page_key, page_title in pages.items():
    if st.session_state.page == page_key:
        # Highlight selected main page
        st.sidebar.markdown(f'<button class="selected-button">{page_title}</button>', unsafe_allow_html=True)
        if page_key == "tevtsms":
            # Reset subpage to None when selecting TVETMS (no subpage selected by default)
            for subpage_key, subpage_title in tevtsms_subpages.items():
                if st.session_state.tevtsms_subpage == subpage_key:
                    # Highlight the selected subpage
                    st.sidebar.markdown(f'<button class="subpage-button selected-button">{subpage_title}</button>', unsafe_allow_html=True)
                else:
                    # Add subpage button with custom width (80%)
                    if st.sidebar.button(subpage_title, key=f"sub_button_{subpage_key}", help=f"Go to {subpage_title}", type="primary", use_container_width=True, on_click=lambda key=subpage_key: setattr(st.session_state, "tevtsms_subpage", key)):
                        pass

        if page_key == "tvet15m":
             # Reset subpage to None when selecting TVET1.5M
            for subpage_key, subpage_title in tvet15m_subpages.items():
                if st.session_state.tvet15m_subpage == subpage_key:
                    # Highlight the selected subpage
                    st.sidebar.markdown(f'<button class="subpage-button selected-button">{subpage_title}</button>', unsafe_allow_html=True)
                else:
                    # Add subpage button with custom width (80%)
                    if st.sidebar.button(subpage_title, key=f"sub_button_{subpage_key}", help=f"Go to {subpage_title}", type="primary", use_container_width=True, on_click=lambda key=subpage_key: setattr(st.session_state, "tvet15m_subpage", key)):
                        pass
    else:
        # If not the selected page, display normal buttons
        if st.sidebar.button(page_title, key=f"button_{page_key}", help=f"Go to {page_title}", type="primary", use_container_width=True, on_click=lambda key=page_key: setattr(st.session_state, "page", key)):
            st.session_state.page = page_key
            if page_key == "tevtsms":
                st.session_state.tevtsms_subpage = None  # Reset to no subpage selected when selecting TVETMS
            if page_key == "tvet15m":
                    st.session_state.tvet15m_subpage = None  # Reset to no subpage selected

# Display the content based on the current page and subpage
if st.session_state.page == "home":
    #st.write("This page is will available soon, Thank you from Yongyi!")
    home.main()
    st.balloons()

elif st.session_state.page == "tevtsms":
    # Show TVETMS main content when no subpage is selected
    if st.session_state.tevtsms_subpage is None:
        # Show the main content of TVETMS
        tvetsms.main()

    # Show subpages when selected
    elif st.session_state.tevtsms_subpage == "page1":
        staff.main()

        # Option to go back to TVETMS main page
        if st.button("⬅️ត្រឡប់ទៅកាន់​ កម្មវិធី TVETMS"):
            st.session_state.tevtsms_subpage = None  # Go back to the main TVETMS page
            st.rerun()  # Trigger a re-run to update the page immediately

    elif st.session_state.tevtsms_subpage == "page2":
        teacher.main()

        # Option to go back to TVETMS main page
        if st.button("⬅️ត្រឡប់ទៅកាន់​ កម្មវិធី TVETMS"):
            st.session_state.tevtsms_subpage = None  # Go back to the main TVETMS page
            st.rerun()  # Trigger a re-run to update the page immediately

    elif st.session_state.tevtsms_subpage == "page3":
        partner.main()

        # Option to go back to TVETMS main page
        if st.button("⬅️ត្រឡប់ទៅកាន់​ កម្មវិធី TVETMS"):
            st.session_state.tevtsms_subpage = None  # Go back to the main TVETMS page
            st.rerun()  # Trigger a re-run to update the page immediately

elif st.session_state.page == "tvet15m":
    # Show TVET1.5M main content when no subpage is selected
    if st.session_state.tvet15m_subpage is None:
        # Show the main content of TVET1.5M
        tvet15m.main()

    # Show subpages when selected
    elif st.session_state.tvet15m_subpage == "page4":
        #st.write("TVET1.5M Page 4 Content - TRAINEES")
        internship15m.main()

        # Option to go back to TVET1.5M main page
        if st.button("⬅️ត្រឡប់ទៅកាន់​ កម្មវិធី TVET1.5M"):
            st.session_state.tvet15m_subpage = None
            st.rerun()

    elif st.session_state.tvet15m_subpage == "page5":
        graduated.main()

        # Option to go back to TVET1.5M main page
        if st.button("⬅️ត្រឡប់ទៅកាន់​ កម្មវិធី TVET1.5M"):
            st.session_state.tvet15m_subpage = None
            st.rerun()
elif st.session_state.page == "erpl":
    #st.write("This page is will available soon, Thank you from Yongyi!")
    erpl_candidate.main()

