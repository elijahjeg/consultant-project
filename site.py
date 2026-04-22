import streamlit as st
import clean_html

def main():
    """Main function that runs the Streamlit app."""
    st.title("Clean up your Html")
    st.write("Provide a CSS file for the classes to keep and an HTML file to clean up.")
    cleaned = False
    # Use a form so that it only runs the code once the user clicks the submit button
    with st.form("clean_form"):
        cssFile = st.file_uploader("Submit CSS")
        htmlFile = st.file_uploader("Submit HTML")
        st.form_submit_button("Clean up HTML")
        # Once both files are uploaded, run the cleaning process
        if htmlFile is not None and cssFile is not None:
            # Try to decode the files, if they are not valid text files show an error message and return
            try:
                htmlText = htmlFile.read().decode()
            except UnicodeDecodeError as e:
                st.error(e.reason)
                return

            try:
                cssText = cssFile.read().decode()
            except UnicodeDecodeError as e:
                st.error(e.reason)
                return

            cleanedHtml = clean_html.cleanHtml(htmlText, cssText)
      
            cleaned = True
        else:
            cleaned = False

    # If the cleaning process was successful, show a success message and provide a download button for the cleaned HTML
    if cleaned:
        st.success("Clean up successful!")
        st.download_button("Download Cleaned HTML", cleanedHtml, "cleaned.html")

main()