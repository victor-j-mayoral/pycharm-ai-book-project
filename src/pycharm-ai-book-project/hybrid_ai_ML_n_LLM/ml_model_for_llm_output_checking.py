# LLM output validator
from sklearn.ensemble import GradientBoostingClassifier

class OutputValidator:

    def __init__(self):
        self.model = GradientBoostingClassifier()

    def extract_reliability_features(self, 
                                   prompt: str, 
                                   response: str) -> list:
        return [
            len(response.split()),  # Response length
            response.count('.') / len(response.split()),         # Sentence density
            len(set(response.split())) / len(response.split()),  # Vocabulary diversity
            response.lower().count('however'),                   # Hedging words
            response.count('"') / 2,                             # Number of "citations"
            self.repetition_score(response),                     # Custom repetition metric
            self.confidence_score(response)                      # Language confidence
        ]
    
    def validate(self, prompt: str, response: str) -> dict:
        features = self.extract_reliability_features(prompt, response)
        probability = self.model.predict_proba([features])[0, 1]

        return {
            'reliable': probability > 0.7,
            'confidence': probability,
            'recommendation': 'Use' if probability > 0.7 else 'Review'
        }