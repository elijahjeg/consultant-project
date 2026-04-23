# HTML Cleanup System with StreamLit

## Overview
This project will clean up HTML with this specific criteria: 

**1.** It removes any classes from the class list if it is not found in the provided CSS file, if there are no valid classes left, it removes the class attribute all together.

**2.** It removes the style and id attributes from all elements.

**3.** It removes all span elements from the HTML, keeping the content inside the span.

**4.** It unwraps any container elements that only contain one element or one string, and that element is not a div itself. With the exception that if the container has a class that is found in the CSS file, it will not be unwrapped.

The project uses BeautifulSoup and regular expressions to parse the HTML and clean it up. When testing and running locally, the cleaned HTML is then written to a file called cleaned.html.

## Testing and Running the Project
To test the project, run clean_html.py directly and change the HTML as necessary. To run the project with StreamLit, run `streamlit run site.py` and change the HTML in the text area on the left, the cleaned HTML will be displayed on the right.

The project is hosted on StreamLit [here](https://cleanhtml.streamlit.app).
