import os 
current_dir = os.path.dirname(__file__)
os.chdir(current_dir)

import spacy
from spacy import displacy
import langdetect
import translate

# Import language-specific language models (LLMs)
import nl_core_news_lg  # Dutch LLM
import en_core_web_trf  # English LLM
#import fr_dep_news_trf  # French LLM
#import de_dep_news_trf  # German LLM

class SpacyFunctions():
    def load_gpu(self):
        """Attempts to leverage a GPU for processing, if available."""
        spacy.prefer_gpu()
        print('Loaded GPU')

    def detect_language(self, text: str) -> str:
        """Detects the language of the provided text using langdetect library."""
        try:
            lang = langdetect.detect(text)
            return lang
        except langdetect.LangdetectException:
            print("Language detection failed. Using English (EN) by default.")
            return "en"

    def load_language(self, text: str) -> spacy.language.Language:
        """Loads the appropriate spaCy model based on the detected language."""
        lang = self.detect_language(text)
        match lang:
            case "nl":
                print("Loaded Dutch")
                return spacy.load("nl_core_news_lg")
            case "en":
                print("Loaded English")
                return spacy.load("en_core_web_trf")
            #case "fr":
            #    print("Loaded French")
            #    return spacy.load("fr_dep_news_trf")
            #case "de":
            #    print("Loaded German")
            #    return spacy.load("de_dep_news_trf")
            case _:
                print(f"Language not supported. Using English (EN) by default.")
                return spacy.load("en_core_web_trf")

    def translate_to_eng(self,text: str):
            lang = self.detect_language(text)
            if lang == "en":
                return text
            else:
                translator = translate.Translator(to_lang="en")
                translation = translator.translate(text)
                return translation

    def process_input(self, input_text: str) -> None:
        """Processes user input using the loaded model."""
        self.load_gpu()
        nlp = self.load_language(input_text)

        if nlp is not None:
            doc = nlp(input_text)
            # Identify named entities (e.g., PERSON, ORG)
            for entity in doc.ents:
                print(f"Found entity: {entity.text} ({entity.label_})")

    def calculate_similarity(self, block1: str, block2:str, lang:str="en"):
        nlp = self.load_language(lang)
        if nlp is not None:
            block1 = nlp(block1)
            block2 = nlp(block2)
            similarity_score = block1.similarity(block2)
            return similarity_score
        else:
            raise ValueError(f"Language model for '{lang}' is not loaded.")
        
    def contains_word_in_language(self, input_string: str, language_code: str):
        """Checks if the input string contains at least one word from the specified language."""
        nlp_lang = self.load_language(input_string)
        if nlp_lang is not None:
            doc = nlp_lang(input_string)
            for token in doc:
                if token.text.lower() in nlp_lang.vocab:
                    return True
            return False
        else:
            print("Language model not available.")
            return False

scy = SpacyFunctions()
scy.load_gpu()

# Example usage
text_block1 = "\u2013  We verified that the Statement presents the business \nmodel and a description of principal risks associated \nwith all the consolidated entities\u2019 activities, including \n"
text_block2 = "where relevant and proportionate, the risks associated \nwith their business relationships, their products or ser-\nvices, as well as their policies, measures and the out-\ncomes thereof, including key performance indicators \nassociated to the principal risks;\n"
similarity_score = scy.calculate_similarity(text_block1, text_block2)
print("Similarity score:", similarity_score)