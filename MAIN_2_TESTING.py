import streamlit as st
from PIL import Image


# Set page config
image = Image.open("C:\\Users\\yongy\\Documents\\INTERNSHIP II\\The TVETMIS's dashborad Project\\Dashboards\\webserver\\pages\\images\\tvetlogo1.png")
st.set_page_config(page_title="TVETMIS Dashboard", page_icon=image, layout="wide")

# Sidebar Logo
st.sidebar.image(image, width=120)

# Define Navigation Structure
pages = {
   "TVETMIS": [
      st.Page("C:\\Users\\yongy\\Documents\\INTERNSHIP II\\The TVETMIS's dashborad Project\\Dashboards\\webserver\\pages\\tvetsms.py", title="Overview"),
      st.Page("C:\\Users\\yongy\\Documents\\INTERNSHIP II\\The TVETMIS's dashborad Project\\Dashboards\\webserver\\pages\\staff.py", title="STAFFS"),
      st.Page("C:\\Users\\yongy\\Documents\\INTERNSHIP II\\The TVETMIS's dashborad Project\\Dashboards\\webserver\\pages\\teacher.py", title="LECTURERS"),
      st.Page("C:\\Users\\yongy\\Documents\\INTERNSHIP II\\The TVETMIS's dashborad Project\\Dashboards\\webserver\\pages\\partner.py", title="PARTNERS"),],
 "TVET 1.5M": [
      st.Page("C:\\Users\\yongy\\Documents\\INTERNSHIP II\\The TVETMIS's dashborad Project\\Dashboards\\webserver\\pages\\tvet15m.py", title="Overview"),
 ],
 "ERPL": [
      st.write("Teste")
 ],
 "TVET E-LEARNING": [
      st.write("Teste")
 ],
}

# Create Navigation
nav = st.navigation(pages)

# Run the selected page
nav.run()