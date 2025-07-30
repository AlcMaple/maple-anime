from pysentation import Presentation, Page

# 1. Create a Presentation instance
presentation = Presentation()

# 2. Define your first slide using the @pres.slide decorator
@presentation.slide
def title_slide(page: Page):
    """
    # Welcome to Pysentation! 🐘
    
    This presentation is created from a Python file.
    """

# 3. Define another slide for features
@presentation.slide
def features_slide(page: Page):
    """
    ## Key Features

    - Slides are defined as Python functions.
    - Markdown is written inside the function's docstring.
    - It's a very developer-centric way to build presentations!
    """

# 4. Define a slide with a code block
@presentation.slide
def code_slide(page: Page):
    """
    ## Code Example

    ```python
    def greet(name):
        print(f"Hello, {name}!")

    greet("World")
    ```
    """
