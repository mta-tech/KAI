import os
import logging
from typing import Tuple, Optional
from flair.data import Sentence
from flair.models import SequenceTagger
from configs import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NERClassification:
    def __init__(self) -> None:
        try:
            NER_MODEL_PATH = Config.NERConf.NER_MODEL_PATH
            self.tagger = SequenceTagger.load(NER_MODEL_PATH)
        except Exception as e:
            logging.error(f"An error occurred while loading NER model: {e}", exc_info=True)

    def predict_ner_tags(self, user_question: str) -> Optional[str]:
        """ This function predicts Named Entity Recognition (NER) tags for a given user question. """
        try:
            sentence = Sentence(user_question)
            # Predict NER Tags
            self.tagger.predict(sentence)
            
            # (Text, TAG, Score)
            ner_tags = [(entity.text, entity.tag, entity.score) for entity in sentence.get_spans('ner')]
            
            if ner_tags:
                sorted_ner_tags = sorted(ner_tags, key=lambda x: x[2], reverse=True)
                keyword = sorted_ner_tags[0][0]
                logger.info("NER tags found: %s", keyword)
            else:
                logger.info("No NER tags found for the given user question.")
                keyword = None
        except Exception as e:
            logging.error(f"An error occurred while predicting NER tags: {e}", exc_info=True)
            keyword = None
        
        return keyword
