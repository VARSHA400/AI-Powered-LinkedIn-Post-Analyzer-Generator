import streamlit as st
from few_shot import Fewshotposts
from post_generator import generate_post

length_options = ["Short", "Medium", "Long"]
language_options = ["English", "Hinglish","malayalam"]

def main():
    st.title("LinkedIn Post Generator")
    col1,col2,col3=st.columns(3)
    fs=Fewshotposts()
    with col1:
        selected_tag=st.selectbox('Title',options=fs.get_tag())
    with col2:
        selected_length=st.selectbox('Length',options=length_options)
    with col3:
        selected_language=st.selectbox('Language',options=language_options)
    if st.button('Generate'):
        post=generate_post(selected_length,selected_language,selected_tag)
        st.write(post)
if __name__== "__main__":
    main()