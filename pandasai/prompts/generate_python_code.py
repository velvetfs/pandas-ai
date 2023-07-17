""" Prompt to generate Python code
```
Today is {today_date}.
You are provided with a pandas dataframe (df) with {num_rows} rows and {num_columns} columns.
This is the metadata of the dataframe:
{df_head}.

When asked about the data, your response should include a python code that describes the
dataframe `df`. Using the provided dataframe, df, return the python code and make sure to prefix
the requested python code with {START_CODE_TAG} exactly and suffix the code with {END_CODE_TAG}
exactly to get the answer to the following question:
```
"""  # noqa: E501

from datetime import date

from pandasai.constants import END_CODE_TAG, START_CODE_TAG

from .base import Prompt


class GeneratePythonCodePrompt(Prompt):
    """Prompt to generate Python code"""

    text: str = """
Today is {today_date}.
You are provided with a pandas dataframe (df) with {num_rows} rows and {num_columns} columns.
This is the result of `print(df.to_csv().head({rows_to_display}))`:
{df_csv_head}.

When asked about the data, your response should include a python code that describes the dataframe `df`.
If the user asks to plot or visualize the data, you should instead return a python code which only returns the data to plot or visualize the data.
Do not return any code which uses any functions from the `matplotlib` or `seaborn` libraries.
Do not return any code which uses `.plot` or `.plotting` methods on the dataframe.
Do not return any code which uses any functions from the `plotly` library.
Do not attempt to access columns which are not in the original dataframe.
Explicitly set the dataframe's index to whichever single column is the best index for the dataframe.
The returned dataframe must have a single index set to the column you chose.
Always return the resulting dataframe as the last line of your python code.
If you would return a series, return a dataframe with one column instead.
Using the provided dataframe, df, return the python code and make sure to prefix the requested python code with {START_CODE_TAG} exactly and suffix the code with {END_CODE_TAG} exactly to get the answer to the following question:
"""  # noqa: E501

    def __init__(self, **kwargs):
        super().__init__(**kwargs, START_CODE_TAG=START_CODE_TAG, END_CODE_TAG=END_CODE_TAG, today_date=date.today())
