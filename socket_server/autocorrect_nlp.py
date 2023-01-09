import os
import json
import tarfile
from functools import lru_cache
from contextlib import closing
from autocorrect import Speller
from deepmultilingualpunctuation import PunctuationModel

language = 'pl'
archive_name = os.path.join(f"nlp-models/{language}.tar.gz")


def load_from_tar(file_name="word_count.json"):
    with closing(tarfile.open(archive_name, "r:gz")) as tar_file:
        with closing(tar_file.extractfile(file_name)) as file:
            return json.load(file)


punctuation_model_pl = PunctuationModel(model="nlp-models/punctuate-all")


class CustomSpeller(Speller):
    """
    Creates autocorrect speller with predefined Polish language.
    """
    def __init__(self, lang='pl', fast=False):
        super(CustomSpeller, self).__init__()
        self.lang = lang
        self.fast = fast
        self.nlp_data = load_from_tar()


@lru_cache
def custom_speller_pl():
    return CustomSpeller(lang=language, fast=True)


def auto_capitalize(text: str):
    return '. '.join(list(map(lambda x: x.strip().capitalize(), text.split('.'))))


def autocorrect_with_punctuation(text: str):
    spell_pl = custom_speller_pl()
    autocorrected_text = spell_pl(text)
    text_with_punctuation = punctuation_model_pl.restore_punctuation(autocorrected_text)
    return auto_capitalize(text_with_punctuation)
