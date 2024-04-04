import sys
import os

# Get the absolute path of the directory containing this script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory of the current directory to the Python path
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

from Coreference.assets.model.memory.base_memory import BaseMemory
from Coreference.assets.model.memory.entity_memory import EntityMemory
