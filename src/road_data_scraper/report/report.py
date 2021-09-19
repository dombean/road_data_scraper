import glob
import logging
import warnings
from pathlib import Path

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


def run_reports(data, full_path, start_date, end_date):

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
