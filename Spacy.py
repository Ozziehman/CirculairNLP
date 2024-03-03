import spacy
from spacy import displacy
import langdetect

# Import language-specific language models (LLMs)
import nl_core_news_lg  # Dutch LLM
import en_core_web_trf  # English LLM
import fr_dep_news_trf  # French LLM
import de_dep_news_trf  # German LLM

def load_gpu():
    """Attempts to leverage a GPU for processing, if available."""
    spacy.prefer_gpu()
    print('Loaded GPU')



def detect_language(text: str) -> str:
  """Detects the language of the provided text using langdetect library."""
  try:
    lang = langdetect.detect(text)
    return lang
  except langdetect.LangdetectException:
    print("Language detection failed. Using English (EN) by default.")
    return "en"



def load_language(text: str) -> spacy.language.Language:
    """Loads the appropriate spaCy model based on the detected language."""
    lang = detect_language(text)
    match lang:
        case "nl":
            print("Loaded Dutch")
            return spacy.load("nl_core_news_lg")
        case "en":
            print("Loaded English")
            return spacy.load("en_core_web_trf")
        case "fr":
            print("Loaded French")
            return spacy.load("fr_dep_news_trf")
        case "de":
            print("Loaded German")
            return spacy.load("de_dep_news_trf")
        case _:
            print(f"Language not supported. Using English (EN) by default.")
            return spacy.load("en_core_web_trf")


def process_input(input_text: str) -> None:
    """Processes user input using the loaded model."""
    load_gpu()
    nlp = load_language(input_text)

    if nlp is not None:
        doc = nlp(input_text)
        # Identify named entities (e.g., PERSON, ORG)
        for entity in doc.ents:
            print(f"Found entity: {entity.text} ({entity.label_})")



# Example usage
user_input = input("Enter a sentence for processing:\n ")
process_input(user_input)
