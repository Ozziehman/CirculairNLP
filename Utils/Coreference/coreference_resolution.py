import os
from pathlib import Path
import sys
import os

# Get the absolute path of the directory containing this script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory of the current directory to the Python path
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

from Coreference.assets.inference.model_inference import Inference


class CoreferenceResolver:
    def __init__(self, model_path):
        # Initialize coreference inference model
        self.inference_model = Inference(model_path, encoder_name="shtoshni/longformer_coreference_joint")

    def resolve_coreferences(self, doc):
        # Perform coreference resolution
        output = self.inference_model.perform_coreference(doc)
        
        # Extract coreference clusters
        coreference_clusters = []
        for cluster in output["clusters"]:
            if len(cluster) > 1:
                coreference_clusters.append(cluster)
        
        return coreference_clusters

def process_files(input_folder, output_folder):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    resolver = CoreferenceResolver(script_dir)
    
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".txt"):
            with open(os.path.join(input_folder, file_name), 'r') as file:
                text = file.read().replace('\n', ' ')  # Replace newline characters with space
                clusters = resolver.resolve_coreferences(text)
                output_file_path = os.path.join(output_folder, f"{Path(file_name).stem}_coreferences.txt")
                with open(output_file_path, 'w') as output_file:
                    for cluster in clusters:
                        output_file.write(str(cluster) + '\n')


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_folder = os.path.join(script_dir, "input")
    output_folder = os.path.join(script_dir, "output")

    # Create input and output folders if they don't exist
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    process_files(input_folder, output_folder)
    print("Coreference resolution completed and saved to output folder.")
