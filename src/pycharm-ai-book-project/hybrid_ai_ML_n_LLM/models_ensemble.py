# Intelligent ensemble example
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier


class FraudDetectionEnsemble:

    def __init__(self):
        self.numerical_model = XGBClassifier()  # For structured features
        self.text_model = None                  # LLM for text analysis
        self.meta_model = LogisticRegression()  # Combines predictions
        
    def predict(self, transaction: dict) -> float:
        # Traditional ML on numerical features
        numerical_features = [
            transaction['amount'],
            transaction['days_since_last'],
            transaction['merchant_risk_score'],
            transaction['location_risk']
        ]
        ml_score = self.numerical_model.predict_proba([numerical_features])[0, 1]
         # LLM analysis on text
        text_prompt = f"Analyze fraud risk: {transaction['description']}"
        llm_score = self.get_llm_fraud_score(text_prompt)
         # Meta-model combines scores intelligently
        meta_features = [
            ml_score,
            llm_score,
            transaction['amount'] > 1000,  # High-value flag
            len(transaction['description'])  # Text complexity
        ]
        final_score = self.meta_model.predict_proba([meta_features])[0, 1]
        
        return final_score