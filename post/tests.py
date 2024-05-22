import csv
import random

from django.test import TestCase
from selenium.webdriver.chrome import webdriver

from member.models import Member

from post.models import Post, PostFile, PostTag, PostPlant
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os


def save_articles_from_csv(csv_file_path):
    try:
        # CSV 파일 열기
        with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            member_queryset = Member.objects.all()
            # 각 행을 반복하며 Django 모델에 저장
            for row in reader:

                # 필요한 정보 추출
                title = row['title']
                content = row['content']
                tags = row['tag'].split(',')


                post_data = {
                            'post_title': title,
                            'post_content': content,
                            'member': member_queryset[random.randint(0, len(member_queryset) - 1)],
                        }
                post = Post.objects.create(**post_data)

                # Post 모델 객체 생성 및 저장
                post_file_data = {
                            'post': post,
                            'file_url': ''
                        }
                PostFile.objects.create(**post_file_data)

                for tag in tags:
                    post_tag_data = {
                        'post': post,
                        'tag_name': tag
                    }
                    PostTag.objects.create(**post_tag_data)

                post_category_data = {
                    'post':post,
                    'plant_name' : '꽃'
                }
                PostPlant.objects.create(**post_category_data)
        # 모든 데이터가 성공적으로 저장되었음을 반환
        return True
    except Exception as e:
        # 오류 발생 시 메시지 출력 및 False 반환
        print(f"Error occurred while saving articles from CSV: {e}")
        return False


class PostTest(TestCase):


    # CSV 파일 경로
    csv_file_path = '../flower_df.csv'

    # CSV 파일에서 데이터를 Django 모델에 저장
    if save_articles_from_csv(csv_file_path):
        print("Articles saved successfully.")
    else:
        print("Failed to save articles.")
# import os
# from pathlib import Path
# from unittest import TestCase
#
# import joblib
#
#
# class SihyunTest(TestCase):
#     model_path = os.path.join(Path(__file__).resolve().parent, 'ai/commentai.pkl')
#     loaded_model = joblib.load(model_path)
#
#     # 변수로 댓글 내용 저장하기
#     names = ['김규일', '백시현', '양현', '강희주', '송서경', '김수빈', '한동석']
#
#     for name in names:
#         # Make predictions
#         new_sentence = [name]
#         transformed_X_train = loaded_model.named_steps['count_vectorizer'].transform(new_sentence)
#         loaded_model.named_steps['multinomial_NB'].fit(transformed_X_train, [0])
#         joblib.dump(loaded_model, model_path)
