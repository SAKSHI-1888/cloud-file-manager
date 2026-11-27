"""Streamlit UI for the Cloud File Manager."""
import os
import tempfile
import streamlit as st
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
from s3_manager import S3FileManager, format_size

st.set_page_config(page_title="Cloud File Manager", page_icon="☁️", layout="wide")
st.title("Cloud File Manager")
st.caption("Upload, inspect, download and delete objects in your Amazon S3 bucket.")
bucket = os.getenv("S3_BUCKET_NAME", "").strip()
if not bucket:
    st.error("Set the S3_BUCKET_NAME environment variable before starting the app.")
    st.stop()
manager = S3FileManager(bucket)
st.info(f"Configured bucket: {bucket}. Credentials use the standard AWS provider chain.")

uploaded = st.file_uploader("Choose a file to upload")
if uploaded is not None and st.button("Upload to S3", type="primary"):
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp.write(uploaded.getvalue())
            temp_path = temp.name
        key = manager.upload_file(temp_path, uploaded.name)
        st.success(f"Uploaded {key}")
    except (BotoCoreError, ClientError, NoCredentialsError, OSError) as exc:
        st.error(f"Upload failed: {exc}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)

st.subheader("Bucket objects")
try:
    objects = manager.list_objects()
    if not objects:
        st.write("No objects found in this bucket.")
    for obj in objects:
        key = obj["Key"]
        left, middle, right = st.columns([5, 2, 2])
        left.write(f"**{key}**")
        middle.write(format_size(obj.get("Size", 0)))
        if right.button("Get download link", key=f"download-{key}"):
            try:
                st.link_button("Download file", manager.generate_download_url(key))
            except (BotoCoreError, ClientError, ValueError) as exc:
                st.error(f"Could not create link: {exc}")
        if st.button("Delete", key=f"delete-{key}"):
            try:
                manager.delete_object(key)
                st.success(f"Deleted {key}. Refresh the page to update the list.")
            except (BotoCoreError, ClientError) as exc:
                st.error(f"Delete failed: {exc}")
except (BotoCoreError, ClientError, NoCredentialsError) as exc:
    st.error(f"Could not list bucket objects: {exc}")
    st.caption("Check AWS identity, region, bucket name and IAM permissions.")
