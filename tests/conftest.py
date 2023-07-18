import os

import pytest

from pandasai import PandasAI
from pandasai.llm.openai import OpenAI


@pytest.fixture()
def llm():
    return OpenAI(api_token=os.getenv("OPENAI_API_TOKEN"))


@pytest.fixture()
def pandas_ai(llm):
    return PandasAI(llm, verbose=True)
