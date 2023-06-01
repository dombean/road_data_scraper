"""
Reports Module
--------------

This module provides functionalities for generating HTML reports based on a template Jupyter notebook.

It uses the Papermill and nbconvert libraries to execute the notebook and convert it to HTML format.

Imported Libraries:
-------------------
- glob: For retrieving file paths matching a specified pattern.
- logging: For logging progress and errors.
- warnings: For managing warnings and filtering.
- pathlib.Path: For handling file paths.
- papermill: For executing Jupyter notebooks and passing parameters.
- nbconvert.exporters.HTMLExporter: For exporting notebooks to HTML format.
- nbconvert.preprocessors.TagRemovePreprocessor: For removing specific cells or tags from notebooks.
- nbconvert.writers.FilesWriter: For writing notebook outputs.
- traitlets.config.Config: For configuring nbconvert and its preprocessors.

Global Variables:
-----------------
- c (Config): Configuration object for nbconvert and preprocessors.
- exporter (HTMLExporter): Exporter object for converting notebooks to HTML format.
"""
import glob
import logging
import warnings
from pathlib import Path

import pandas as pd

with warnings.catch_warnings():
    warnings.simplefilter(action="ignore", category=FutureWarning)
    import papermill as pm

from nbconvert.exporters import HTMLExporter
from nbconvert.preprocessors import TagRemovePreprocessor
from nbconvert.writers import FilesWriter
from traitlets.config import Config

warnings.simplefilter(action="ignore")
c = Config()
c.TemplateExporter.exclude_input = True
c.TagRemovePreprocessor.remove_cell_tags = ("remove_cell",)
c.TagRemovePreprocessor.remove_all_outputs_tags = ("remove_output",)
c.TagRemovePreprocessor.remove_input_tags = ("remove_input",)
c.TagRemovePreprocessor.enabled = True
c.HTMLExporter.preprocessors = ["nbconvert.preprocessors.TagRemovePreprocessor"]

exporter = HTMLExporter(config=c)
exporter.register_preprocessor(TagRemovePreprocessor(config=c), True)


def run_reports(
    data: pd.DataFrame, full_path: str, start_date: str, end_date: str
) -> None:
    """
    Generates an HTML report by executing a template Jupyter notebook. The function populates the template with the provided data
    and saves the generated report as an HTML file.

    The function takes the following steps:
    - Specifies the input path for the template notebook.
    - Defines the output path for the generated report notebook.
    - Sets up the parameters for the notebook execution, including the report title and data to be included.
    - Executes the template notebook using Papermill, passing the parameters and enabling report mode.
    - Converts the executed notebook to HTML format using nbconvert.
    - Saves the HTML report to the specified output directory.

    Note:
    - The template notebook should have the appropriate placeholders to receive the data and generate the report.
    - The data should be in a pandas DataFrame format.
    - The full path provided should be an existing directory where the report will be saved.

    Args:
        data (pd.DataFrame): Data to be included in the report.
        full_path (str): Full path of the directory where the report will be saved.
        start_date (str): Start date of the data range used for the report.
        end_date (str): End date of the data range used for the report.

    Returns:
        None

    Example:
    ```
    data = pd.DataFrame(...)
    full_path = "/path/to/reports"
    start_date = "2022-01-01"
    end_date = "2022-01-31"

    run_reports(data, full_path, start_date, end_date)
    ```

    The above example generates an HTML report using the provided data and saves it in the specified directory.
    """

    logging.info(f"Generating HTML Report at {full_path}")

    input_path = "./report/road_data_report_template.ipynb"
    output_path = f"{full_path}/road_data_report.ipynb"

    report_date = f"{start_date} to {end_date}"
    report_title = f"__Road Data Sensors API Scraping Report__\n Date: {report_date}"

    params = {"title": report_title, "data": data.to_json()}

    logging.disable(logging.INFO)
    pm.execute_notebook(
        input_path=input_path,
        output_path=output_path,
        parameters=params,
        report_mode=True,
    )

    notebook_files = glob.glob(f"{str(full_path)}/*.ipynb")
    notebook_files = Path(notebook_files[0])

    (body, resources) = HTMLExporter(config=c).from_filename(notebook_files)
    fw = FilesWriter(config=c)
    fw.write(body, resources, notebook_name="road_data_report")
    logging.disable(logging.NOTSET)
