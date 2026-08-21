# Import the Gradio library
import gradio as gr

# Define a function that reverses any input text
def reverse_text(text):
    # The [::-1] slice notation reverses the string
    return text[::-1]

# Create a Gradio interface to connect the function with a simple web UI
demo = gr.Interface(
    fn=reverse_text,       # Function to call when the user submits input
    inputs="text",         # Type of input (a text box for user input)
    outputs="text",        # Type of output (a text box to display reversed text)
    title="Text Reversal App",          # Title displayed on the app
    description="Type any text and see it reversed instantly."  # Short description for users
)

# Launch the web app in the browser
demo.launch()