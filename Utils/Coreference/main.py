import os
import sys
from pathlib import Path

# Append the path to the coreference model to sys.path
sys.path.append('assets/fast-coref/src')

from inference.model_inference import Inference

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
    resolver = CoreferenceResolver("./assets")
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
    input_folder = "input"
    output_folder = "output"

    # Check if input and output folders exist
    if not os.path.exists(input_folder):
        print(f"Input folder '{input_folder}' does not exist.")
        sys.exit(1)
    if not os.path.exists(output_folder):
        print(f"Output folder '{output_folder}' does not exist.")
        sys.exit(1)

    process_files(input_folder, output_folder)
    print("Coreference resolution completed and saved to output folder.")
