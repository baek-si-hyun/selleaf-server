import os
from pathlib import Path

import joblib

model_path = os.path.join(Path(__file__).resolve().parent, '../../ai/ai/commentai.pkl')


def profanityDetectionPredict(new_sentence):
    loaded_model = joblib.load(model_path)

    prediction = loaded_model.predict(new_sentence)
    return prediction


def profanityDetectionModel(new_sentence):
    loaded_model = joblib.load(model_path)
    transformed_X_train = loaded_model.named_steps['count_vectorizer'].transform(new_sentence)
    loaded_model.named_steps['multinomial_NB'].partial_fit(transformed_X_train, [1])
    joblib.dump(loaded_model, model_path)
