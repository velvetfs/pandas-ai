import pandas as pd


def test_date_is_the_index_of_cost_df(pandas_ai):
    cost_df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-02", "2021-01-03", "2021-01-04", "2021-01-05", "2021-01-06"],
            "cost": [1, 2, 3, 4, 5, 6],
        }
    )
    ai_df = pandas_ai(cost_df, prompt="Show me the cost")
    assert ai_df.index.name == "date"


def test_filter_date(pandas_ai):
    cost_df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-02", "2021-01-03", "2021-01-04", "2021-01-05", "2021-01-06"],
            "cost": [1, 2, 3, 4, 5, 6],
        }
    )
    filtered_df = pandas_ai(cost_df, prompt="Show me the cost for 2020")
    assert filtered_df.index.name == "date"
    assert filtered_df.shape == (2, 1)


def test_aggregate_rounds(pandas_ai):
    rounds_df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-02", "2021-01-03", "2021-01-04", "2021-01-05", "2021-01-06"],
            "round": [1, 1, 3, 2, 3, 3],
        }
    )
    filtered_df = pandas_ai(rounds_df, prompt="How many investments are made in different rounds?")
    assert filtered_df.index.name == "round"
    assert filtered_df.shape == (3, 1)
    assert filtered_df.columns.tolist() == ["count"]
    assert filtered_df.loc[1, "count"] == 2
    assert filtered_df.loc[2, "count"] == 1
    assert filtered_df.loc[3, "count"] == 3


def test_filter_and_aggregate(pandas_ai):
    rounds_df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-02", "2021-01-03", "2021-01-04", "2021-01-05", "2021-01-06"],
            "round": [1, 1, 1, 2, 3, 3],
        }
    )
    filtered_df = pandas_ai(rounds_df, prompt="How many investments are made in different rounds in 2021?")
    assert filtered_df.index.name == "round"
    assert filtered_df.shape == (3, 1)
    assert filtered_df.columns.tolist() == ["count"]
    assert filtered_df.loc[1, "count"] == 1
    assert filtered_df.loc[2, "count"] == 1
    assert filtered_df.loc[3, "count"] == 2


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
    filtered_df = pandas_ai(fruits_df, prompt="Show me total bananas by company sorted low to high")
    assert filtered_df.index.name == "company"
    assert filtered_df.shape == (3, 1)
    assert filtered_df.columns.tolist() == ["bananas"]
    assert filtered_df["bananas"].tolist() == [5, 7, 11]


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
    assert filtered_df.index.name == "company"
    assert filtered_df.shape == (3, 1)
    assert filtered_df.columns.tolist() == ["bananas"]
