import pandas as pd
import pytest

from pandasai import PandasAI


def test_date_is_the_index_of_cost_df(pandas_ai: PandasAI):
    cost_df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-02", "2021-01-03", "2021-01-04", "2021-01-05", "2021-01-06"],
            "cost": [1, 2, 3, 4, 5, 6],
        }
    )
    ai_df = pandas_ai(cost_df, prompt="Show me the cost")
    assert ai_df.index.name == "date"


@pytest.mark.skip(reason="Don't hit the API")
def test_filter_date(pandas_ai: PandasAI):
    cost_df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-02", "2021-01-03", "2021-01-04", "2021-01-05", "2021-01-06"],
            "cost": [1, 2, 3, 4, 5, 6],
        }
    )
    filtered_df = pandas_ai(cost_df, prompt="Show me the cost for 2020")
    assert type(filtered_df) == pd.DataFrame
    assert filtered_df.shape == (2, 2)


@pytest.mark.skip(reason="Don't hit the API")
def test_aggregate_rounds(pandas_ai):
    rounds_df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-02", "2021-01-03", "2021-01-04", "2021-01-05", "2021-01-06"],
            "round": [1, 1, 2, 2, 3, 3],
        }
    )
    filtered_df = pandas_ai(rounds_df, prompt="How many investments are made in different rounds?")
    assert type(filtered_df) == pd.DataFrame
    assert filtered_df.shape == (3, 2)
    assert filtered_df.columns.tolist() == ["round", "count"]
    assert filtered_df["count"].tolist() == [2, 2, 2]


@pytest.mark.skip(reason="Don't hit the API")
def test_filter_and_aggregate(pandas_ai):
    rounds_df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-02", "2021-01-03", "2021-01-04", "2021-01-05", "2021-01-06"],
            "round": [1, 1, 2, 2, 3, 3],
        }
    )
    filtered_df = pandas_ai(rounds_df, prompt="How many investments are made in different rounds in 2021?")
    assert type(filtered_df) == pd.DataFrame
    assert filtered_df.shape == (2, 2)
    assert filtered_df.columns.tolist() == ["round", "count"]
    assert filtered_df["count"].tolist() == [2, 2]


@pytest.mark.skip(reason="Don't hit the API")
def test_filter_lots_of_columns(pandas_ai):
    fruits_df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-02", "2021-01-03", "2021-01-04", "2021-01-05", "2021-01-06"],
            "round": [1, 1, 2, 2, 3, 3],
            "company": ["A", "A", "B", "B", "C", "C"],
            "investor": ["G", "H", "I", "J", "K", "L"],
            "bananas": [3, 2, 3, 4, 5, 6],
            "apples": [2, 2, 3, 4, 5, 6],
            "oranges": [1, 2, 3, 4, 5, 6],
            "pears": [1, 2, 3, 4, 5, 6],
            "grapes": [1, 2, 3, 4, 5, 6],
            "pineapples": [1, 2, 3, 4, 5, 2],
            "mangoes": [1, 2, 3, 4, 5, 6],
        }
    )
    filtered_df = pandas_ai(fruits_df, prompt="Show me bananas by company sorted low to high")
    assert type(filtered_df) == pd.DataFrame
    assert filtered_df.shape == (4, 2)


@pytest.mark.skip(reason="Don't hit the API")
def test_average_banana(pandas_ai):
    fruits_df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-02", "2021-01-03", "2021-01-04", "2021-01-05", "2021-01-06"],
            "round": [1, 1, 2, 2, 3, 3],
            "company": ["A", "A", "B", "B", "C", "C"],
            "investor": ["G", "H", "I", "J", "K", "L"],
            "bananas": [3, 2, 3, 4, 5, 6],
            "apples": [2, 2, 3, 4, 5, 6],
            "oranges": [1, 2, 3, 4, 5, 6],
            "pears": [1, 2, 3, 4, 5, 6],
            "grapes": [1, 2, 3, 4, 5, 6],
            "pineapples": [1, 2, 3, 4, 5, 2],
            "mangoes": [1, 2, 3, 4, 5, 6],
        }
    )
    filtered_df = pandas_ai(fruits_df, prompt="What is the variance of bananas as a percentage per company?")
    print(filtered_df)
    assert type(filtered_df) == pd.DataFrame
    assert filtered_df.shape == (4, 2)
    assert False
