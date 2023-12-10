"""Написание кода загрузки модель
После того, как вы обучили модель, необходимо ее сохранить и загрузить с помощью функции get_model_path."""

import os
from catboost import CatBoostClassifier

def get_model_path(path: str) -> str:
    if os.environ.get("IS_LMS") == "1":  # проверяем где выполняется код в лмс, или локально. Немного магии
        MODEL_PATH = '/workdir/user_input/model'
    else:
        MODEL_PATH = path
    return MODEL_PATH

def load_models(path='/workdir/user_input/model'):
    model_path = get_model_path(path)

    from_file = CatBoostClassifier()
    from_file.load_model(model_path)
    return from_file

if __name__ == "__main__":
    model = load_models("/my/super/path")