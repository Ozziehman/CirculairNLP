# IMPORT EVERYTHING HERE
from Utils.FileDataExtraction import muPDF_reader_layer
from Utils.FileDataStorage import neo4j_layer
from Utils.Similarity import similarity_checker
import language_tool_python

class Pipeline:
    def __init__(self) -> None:
        self.mprl = muPDF_reader_layer.muPDF_reader_layer()
        self.n4l = neo4j_layer.neo4j_layer()

    def execute(self) -> None:
        # Parse all files in the input folder
        self.mprl.ParseAllFiles("InputFiles")

        # Upload all files in the output folder
        self.n4l.upload_all_files("OutputFiles", upload_text=True, upload_tables=True, upload_images=True, interpreted_structure=True)

        # Structurize the db
        self.n4l.structurize_neo4j_database()

class CoreferenceInContext:
    def __init__(self) -> None:
        self.n4l = neo4j_layer.neo4j_layer()

    def input(self) -> str:
        x = input("\nWhat's the name of the paragraph you wish to fetch? \nFor example: paragraph_1 \nInput: ")
        text = self.n4l.entity_replacement(x)
        return text
    
    def grammar_check(self, text) -> None:
        input_text = text
        grammar_checker = language_tool_python.LanguageTool("en-US")
        corrected_text = grammar_checker.correct(input_text)
        print("New text:", corrected_text)
        return corrected_text


if __name__ == "__main__":
    choice = input("Do you wish to load the full pipeline or apply coreference? \n 1 = Pipeline \n 2 = Coreference  \nInput: ")
    if choice == '1':
        pipeline = Pipeline()
        pipeline.execute()
        print("Pipeline Executed")
    elif choice == '2':
        coref_in_context = CoreferenceInContext()
        text = coref_in_context.grammar_check(coref_in_context.input())
        sim = similarity_checker.similarity_calculator()
        print("Similarity between the input text and circularity corpus: ")
        print(sim.text_similarity(text, "Circularity environmental sustainability pivotal quest greener future. Recycling, upcycling, reusing resources paramount minimize waste conserve ecosystems. Circular economy models promote closed-loop systems products designed reused repurposed, reducing strain natural resources. Renewable energy sources solar wind power embody circular principles harnessing nature's resources depletion. Biodegradable materials offer sustainable alternative traditional plastics, fostering circular approach packaging waste management. Eco-friendly practices, composting rainwater harvesting, enhance circularity, ensuring harmonious relationship humanity environment."))
    