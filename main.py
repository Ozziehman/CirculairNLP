# IMPORT EVERYTHING HERE
from Utils.FileDataExtraction import muPDF_reader_layer
from Utils.FileDataStorage import neo4j_layer
import language_tool_python

class Pipeline:
    def __init__(self, mprl, n4l) -> None:
        self.mprl = mprl
        self.n4l = n4l

    def execute(self) -> None:
        # Parse all files in the input folder
        self.mprl.parse_all_files("InputFiles")

        # Upload all files in the output folder
        self.n4l.upload_all_files("OutputFiles", upload_text=True, upload_tables=True, upload_images=True, interpreted_structure=True)

        # Structurize the db
        self.n4l.structurize_neo4j_database()

class CoreferenceInContext:
    def __init__(self, n4l) -> None:
        self.n4l = n4l

    def input(self) -> str:
        x = input("\nWhat's the name of the paragraph you wish to fetch? \nFor example: paragraph_1 \nInput: ")
        text = self.n4l.entity_replacement(x)
        return text
    
    def grammar_check(self, text) -> None:
        input_text = text
        grammar_checker = language_tool_python.LanguageTool("en-US")
        corrected_text = grammar_checker.correct(input_text)
        print("New text:", corrected_text)


if __name__ == "__main__":
    mprl = muPDF_reader_layer.muPDF_reader_layer()
    n4l = neo4j_layer.neo4j_layer()
    
    choice = input("Do you wish to load the full pipeline or apply coreference? \n 1 = Pipeline \n 2 = Coreference  \nInput: ")
    if choice == '1':
        pipeline = Pipeline(mprl, n4l)
        pipeline.execute()
        print("Pipeline Executed")
    elif choice == '2':
        coref_in_context = CoreferenceInContext(n4l)
        coref_in_context.grammar_check(coref_in_context.input())