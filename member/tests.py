import os
from pathlib import Path

import joblib
from django.test import TestCase

from knowhow.models import KnowhowCategory


# Create your tests here.

class KnowhowTest(TestCase):
    category_names = Activity.enabled_objects.filter(category__id=id)['category_name'].values_list('')

    # knowhow_model = joblib.load(
    #     os.path.join(Path(__file__).resolve().parent.parent, f'main/ai/knowhow_ai22.pkl')
    # )
    #
    # print("=" * 40)
    # print(type(knowhow_model))
    # print(knowhow_model)
    # print("=" * 40)
    # print(knowhow_ai_models['knowhow_ai111'])

    # joblib.dump(knowhow_ai_models['knowhow_ai111'], '../main/ai/knowhow_ai_test.pkl')

    # 저장할 파일의 경로를 지정
    # file_path = os.path.join(Path(__file__).resolve().parent, '../main/ai/knowhow_ai_test.pkl')
    # directory = os.path.dirname(file_path)

    # 디렉토리가 존재하지 않으면 생성
    # if not os.path.exists(directory):
    #     os.makedirs(directory)

    # 모델을 지정된 경로에 저장
    # joblib.dump(knowhow_ai_models['knowhow_ai111'], file_path)