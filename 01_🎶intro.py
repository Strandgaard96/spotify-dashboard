import streamlit as st
from util.util import get_file_content_as_string


st.set_page_config(page_title="Intro", layout="wide", page_icon=":fire:")

readme_text = st.markdown(get_file_content_as_string("intro.md"))


# Hack to try and center image.
_, col2, _ = st.sidebar.columns([1, 1, 1])
# Sombra logo in sidebar
col2.image("images/sombra.png", width=110)
# What to put under the sidebar
st.sidebar.markdown(
    '<h4>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png"\
     alt="Streamlit logo" \
     height="16">&nbsp by <a href="https://github.com/Strandgaard96">Strandgaard96</a></h4>',
    unsafe_allow_html=True,
)

st.sidebar.success("Select a page above!")


