# IMPORT EVERYTHING HERE
#from Utils.FileDataExtraction import muPDF_reader_layer
#from Utils.FileDataStorage import neo4j_layer
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
    def __init__(self) -> None:
        pass

    def input() -> str:
        return input("Please enter your text: \n")
    
    def grammar_check(self) -> str:
        input = CoreferenceInContext.input()
        grammar_checker = language_tool_python.LanguageTool("en-US")
        grammar_checker.close()
        return print(grammar_checker.correct(input))


if __name__ == "__main__":
    #mprl = muPDF_reader_layer.muPDF_reader_layer()
    #n4l = neo4j_layer.neo4j_layer()
    
    #pipeline = Pipeline(mprl, n4l)
    coref_in_context = CoreferenceInContext()
    # pipeline.execute()
    coref_in_context.grammar_check()