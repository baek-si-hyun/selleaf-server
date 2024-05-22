import csv
import os
import pickle
import random
from pathlib import Path
import joblib
from django.test import TestCase


from ai.models import AiPostReply, AiPost
from member.models import Member
from post.models import Post, PostFile


# class AiTest(TestCase):
#     pass

    # with open(os.path.join(Path(__file__).resolve().parent, 'ai/merge_comments_data.csv'), mode='r',
    #           encoding='utf-8-sig') as file:
    #     csv_reader = csv.DictReader(file)
    #     datas = [row for row in csv_reader]
    #
    # for data in datas:
    #     reply_data = {
    #         'comment': data['Comment'],
    #         'target': data['Target'],
    #     }
    #     AiPostReply.objects.create(**reply_data)

    # # 'model.pkl' 파일을 로드
    # loaded_model = joblib.load(os.path.join(Path(__file__).resolve().parent, 'ai/commentai.pkl'))
    # print(loaded_model)

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
                tag_list = []
                for tag in tags:
                    tag_list.append(tag)

                post_data = {
                    'post_title': title,
                    'post_content': content,
                    'post_tags': tag_list,
                }
                post = AiPost.objects.create(**post_data)
        # 모든 데이터가 성공적으로 저장되었음을 반환
        return True
    except Exception as e:
        # 오류 발생 시 메시지 출력 및 False 반환
        print(f"Error occurred while saving articles from CSV: {e}")
        return False

class AiTest(TestCase):

    # CSV 파일 경로
    csv_file_path = '../pretraining_df.csv'

    # CSV 파일에서 데이터를 Django 모델에 저장
    if save_articles_from_csv(csv_file_path):
        print("Articles saved successfully.")
    else:
        print("Failed to save articles.")