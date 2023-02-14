import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet

def paraphrase(sentence):
    # Tokenize the sentence into words
    words = word_tokenize(sentence)

    # Create a list to store the paraphrased sentences
    paraphrases = []

    # For each word in the sentence
    for word in words:
        # Get the synonyms of the word from WordNet
        synonyms = wordnet.synsets(word)

        # For each synonym of the word
        for synonym in synonyms:
            # Get the lemmas (different forms) of the synonym
            lemmas = synonym.lemmas()

            # For each lemma of the synonym
            for lemma in lemmas:
                # Get the name of the lemma (as a string)
                name = lemma.name()

                # If the name is different from the original word
                if name != word:
                    # Create a new sentence by replacing the word with the synonym
                    new_sentence = sentence.replace(word, name)
                    # Add the new sentence to the list of paraphrases
                    paraphrases.append(new_sentence)

    # Return the list of paraphrased sentences
    print(paraphrases)
    return paraphrases

input_string = "NLTK is a leading platform for building Python programs to work with human language data."
output_string = paraphrase(input_string)