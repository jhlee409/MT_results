import streamlit as st
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, storage

# Set page to wide mode
st.set_page_config(page_title="EGD 강의", layout="wide")

# Initialize Firebase only if it hasn't been initialized
if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": st.secrets["project_id"],
        "private_key_id": st.secrets["private_key_id"],
        "private_key": st.secrets["private_key"].replace('\\n', '\n'),
        "client_email": st.secrets["client_email"],
        "client_id": st.secrets["client_id"],
        "auth_uri": st.secrets["auth_uri"],
        "token_uri": st.secrets["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["client_x509_cert_url"]
    })
    firebase_admin.initialize_app(cred)

# Title and Instructions
st.title("동영상 업로드")
st.write("Firebase Storage에 동영상을 업로드하세요.")

# Input for name
user_name = st.text_input("이름을 입력하세요:")

# File uploader
uploaded_file = st.file_uploader("동영상(mp4, avi)을 선택하세요:", type=["mp4", "avi"])

if uploaded_file and user_name:
    # Process upload when button is clicked
    if st.button("업로드"):
        try:
            # Get current date
            current_date = datetime.now().strftime("%Y-%m-%d")

            # Generate file name
            extension = os.path.splitext(uploaded_file.name)[1]  # Extract file extension
            file_name = f"{user_name}_{current_date}{extension}"

            # Firebase Storage upload
            bucket = storage.bucket('amcgi-bulletin.appspot.com')
            blob = bucket.blob(f"MT_results/{file_name}")

            # Upload file to Firebase Storage
            blob.upload_from_file(uploaded_file, content_type=uploaded_file.type)

            # Success message
            st.success(f"{file_name} 파일이 성공적으로 업로드되었습니다!")
        except Exception as e:
            # Error message
            st.error(f"업로드 중 오류가 발생했습니다: {e}")
else:
    st.info("이름을 입력하고 파일을 선택하세요.")