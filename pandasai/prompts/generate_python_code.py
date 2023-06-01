""" Prompt to generate Python code """

from datetime import date

from pandasai.constants import END_CODE_TAG, START_CODE_TAG

from .base import Prompt


class GeneratePythonCodePrompt(Prompt):
    """Prompt to generate Python code"""

    text: str = """
Today is {today_date}.
You are provided with a pandas dataframe (df) with {num_rows} rows and {num_columns} columns.
This is the result of `print(df.head({rows_to_display}))`:
{df_head}.

When asked about the data, your response should include a python code that describes the dataframe `df`.
If the user asks to plot or visualize the data, you should instead return a python code which only returns the data to plot or visualize the data.
Do not return any code which uses any functions from the `matplotlib` or `seaborn` libraries.
Do not return any code which uses `.plot` or `.plotting` methods on the dataframe.
Do not return any code which uses any functions from the `plotly` library.
Do not change the names of any of the columns of the dataframe.
Always return the resulting dataframe as the last line of your python code.
Using the provided dataframe, df, return the python code and make sure to prefix the requested python code with {START_CODE_TAG} exactly and suffix the code with {END_CODE_TAG} exactly to get the answer to the following question:
"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs, START_CODE_TAG=START_CODE_TAG, END_CODE_TAG=END_CODE_TAG, today_date=date.today())
