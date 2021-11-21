import os
from pathlib import Path

from pkg_resources import get_distribution

__version__ = get_distribution("road_data_scraper").version

package_path = Path(__file__).parent
os.chdir(package_path)
