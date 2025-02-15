""" PandasAI is a wrapper around a LLM to make dataframes convesational """
import ast
import io
import re
from contextlib import redirect_stdout

import astor
import matplotlib.pyplot as plt
import pandas as pd

from .constants import WHITELISTED_BUILTINS, WHITELISTED_LIBRARIES
from .exceptions import LLMNotFoundError, MaxRetriesExceededError
from .helpers.anonymizer import anonymize_dataframe_head
from .helpers.notebook import Notebook
from .llm.base import LLM
from .prompts.correct_error_prompt import CorrectErrorPrompt
from .prompts.correct_wrong_type_prompt import CorrectWrongTypePrompt
from .prompts.generate_python_code import GeneratePythonCodePrompt


# pylint: disable=too-many-instance-attributes disable=too-many-arguments
class PandasAI:
    """PandasAI is a wrapper around a LLM to make dataframes conversational"""

    _llm: LLM
    _verbose: bool = False
    _enforce_privacy: bool = False
    _max_retries: int = 3
    _is_notebook: bool = False
    _original_instructions: dict = {
        "question": None,
        "df_head": None,
        "num_rows": None,
        "num_columns": None,
        "rows_to_display": None,
    }
    last_code_generated: str | None = None
    last_run_code: str | None = None
    code_output: pd.DataFrame | None = None

    def __init__(self, llm: LLM | None = None, verbose: bool = False, enforce_privacy: bool = False):
        if llm is None:
            raise LLMNotFoundError("An LLM should be provided to instantiate a PandasAI instance")
        self._llm = llm
        self._verbose = verbose
        self._enforce_privacy = enforce_privacy

        self.notebook = Notebook()
        self._in_notebook = self.notebook.in_notebook()

    def run(
        self,
        data_frame: pd.DataFrame,
        prompt: str,
        show_code: bool = False,
        anonymize_df: bool = True,
        use_error_correction_framework: bool = True,
    ) -> pd.DataFrame:
        """Run the LLM with the given prompt"""
        self.log(f"Running PandasAI with {self._llm.type} LLM...")
        self._df = data_frame.copy()

        rows_to_display = 0 if self._enforce_privacy else 5

        df_head = data_frame.head(rows_to_display)
        if anonymize_df:
            df_head = anonymize_dataframe_head(df_head)

        df_csv_head = df_head.to_csv(index=False)

        code = self._llm.generate_code(
            GeneratePythonCodePrompt(
                prompt=prompt,
                df_csv_head=df_csv_head,
                num_rows=data_frame.shape[0],
                num_columns=data_frame.shape[1],
                rows_to_display=rows_to_display,
            ),
            prompt,
        )
        self._original_instructions = {
            "question": prompt,
            "df_head": df_head,
            "num_rows": data_frame.shape[0],
            "num_columns": data_frame.shape[1],
            "rows_to_display": rows_to_display,
        }
        self.last_code_generated = code
        self.log(
            f"""
Code generated:
```
{code}
```"""
        )
        if show_code and self._in_notebook:
            self.notebook.create_new_cell(code)

        answer = self.run_code(code, use_error_correction_framework=use_error_correction_framework)
        self.code_output = answer
        self.log(f"Answer: {answer}")
        return answer

    def __call__(
        self,
        data_frame: pd.DataFrame,
        prompt: str,
        show_code: bool = False,
        anonymize_df: bool = True,
        use_error_correction_framework: bool = True,
    ) -> pd.DataFrame:
        """Run the LLM with the given prompt"""
        return self.run(data_frame, prompt, show_code, anonymize_df, use_error_correction_framework)

    def remove_unsafe_imports(self, code: str) -> str:
        """Remove non-whitelisted imports from the code to prevent malicious code execution"""

        tree = ast.parse(code)
        new_body = [
            node
            for node in tree.body
            if not (
                isinstance(node, ast.Import | ast.ImportFrom)
                and any(alias.name not in WHITELISTED_LIBRARIES for alias in node.names)
            )
        ]
        new_tree = ast.Module(body=new_body)
        return astor.to_source(new_tree).strip()

    def remove_df_overwrites(self, code: str) -> str:
        """Remove df declarations from the code to prevent malicious code execution"""

        tree = ast.parse(code)
        new_body = [
            node
            for node in tree.body
            if not (
                isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "df"
            )
        ]
        new_tree = ast.Module(body=new_body)
        return astor.to_source(new_tree).strip()

    def remove_plots(self, code: str) -> str:
        """Remove plots from the code"""

        tree = ast.parse(code)
        new_body = [
            node
            for node in tree.body
            if not (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and node.value.func.attr == "show"
            )
        ]
        new_tree = ast.Module(body=new_body)
        return astor.to_source(new_tree).strip()

    def clean_code(self, code: str) -> str:
        """Clean the code to prevent malicious code execution"""

        # TODO: avoid iterating over the code twice # pylint: disable=W0511
        code = self.remove_unsafe_imports(code)
        code = self.remove_plots(code)
        return code

    def run_code(self, code: str, use_error_correction_framework: bool = True) -> pd.DataFrame:
        # pylint: disable=W0122 disable=W0123 disable=W0702:bare-except
        """Run the code in the current context and return the result"""

        # Get the code to run removing unsafe imports and df overwrites
        code_to_run = self.clean_code(code)
        self.last_run_code = code_to_run
        self.log(
            f"""
Code running:
```
{code_to_run}
```"""
        )

        # Redirect standard output to a StringIO buffer
        with redirect_stdout(io.StringIO()):
            count = 0
            while count < self._max_retries:
                try:
                    loc = {}
                    data_frame = self._df.copy()
                    exec(  # noqa: S102
                        code_to_run,
                        {
                            "pd": pd,
                            "df": data_frame,
                            "plt": plt,
                            "__builtins__": {**{builtin: __builtins__[builtin] for builtin in WHITELISTED_BUILTINS}},
                        },
                        loc,
                    )
                    code = code_to_run

                    # Evaluate the last line and return its value or the captured output
                    lines = code.strip().split("\n")
                    last_line = lines[-1].strip()

                    pattern = r"^print\((.*)\)$"
                    if match := re.match(pattern, last_line):
                        last_line = match[1]

                    last_line_value = eval(  # noqa: S307, PGH001
                        last_line,
                        {
                            "pd": pd,
                            "df": self._df,
                            "__builtins__": {**{builtin: __builtins__[builtin] for builtin in WHITELISTED_BUILTINS}},
                        },
                        loc,
                    )
                    if isinstance(last_line_value, pd.DataFrame):
                        return last_line_value
                    count += 1
                    error_correcting_instruction = CorrectWrongTypePrompt(
                        code=code,
                        return_type=type(last_line_value),
                        question=self._original_instructions["question"],
                        df_head=self._original_instructions["df_head"],
                        num_rows=self._original_instructions["num_rows"],
                        num_columns=self._original_instructions["num_columns"],
                        rows_to_display=self._original_instructions["rows_to_display"],
                    )
                    code_to_run = self.clean_code(self._llm.generate_code(error_correcting_instruction, ""))
                    code_to_run = self.clean_code(code)
                    self.last_run_code = code_to_run
                    self.log(
                        f"""
                             Code running:
                             ```
                             {code_to_run}
                             ```"""
                    )
                except Exception as e:  # pylint: disable=W0718 disable=C0103  # noqa: BLE001
                    if not use_error_correction_framework:
                        raise e  # noqa: TRY201

                    count += 1
                    error_correcting_instruction = CorrectErrorPrompt(
                        code=code,
                        error_returned=e,
                        question=self._original_instructions["question"],
                        df_head=self._original_instructions["df_head"],
                        num_rows=self._original_instructions["num_rows"],
                        num_columns=self._original_instructions["num_columns"],
                        rows_to_display=self._original_instructions["rows_to_display"],
                    )
                    code_to_run = self._llm.generate_code(error_correcting_instruction, "")
        raise MaxRetriesExceededError(f"Maximum number of retries exceeded ({self._max_retries}).")

    def log(self, message: str):
        """Log a message"""
        if self._verbose:
            print(message)
