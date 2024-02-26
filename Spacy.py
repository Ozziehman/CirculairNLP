import spacy
from spacy import displacy
import nl_core_news_lg
import en_core_web_trf
import fr_dep_news_trf
import de_dep_news_trf

# region pre-setup
def load_gpu():
    spacy.prefer_gpu()
    return print('Loaded GPU')

def load_language(lang):
    match lang:
        case "NL":
            nlp = spacy.load("nl_core_news_lg")
            print("Loaded Dutch")
            return nlp
        case "EN":
            nlp = spacy.load("en_core_web_trf")
            print("Loaded English")
            return nlp
        case "FR":
            nlp = spacy.load("fr_dep_news_trf")
            print("Loaded French")
            return nlp
        case "DE":
            nlp = spacy.load("de_dep_news_trf")
            print("Loaded German")
            return nlp
        case _:
            print("Language not specified. Use NL / EN / FR / DE")
            return None
        
def visualizer(doc):
    svg = displacy.render(doc, style="dep", page=True)
    output_path = "output.svg"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)  

#endregion pre-setup

# region input
def input(input: str):
    load_gpu()
    nlp = load_language("EN")
    
    if nlp != None:
        doc = nlp(input)
        print([(w.text, w.pos) for w in doc])
    
input("")