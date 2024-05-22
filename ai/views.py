from rest_framework.response import Response
from rest_framework.views import APIView
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from ai.models import AiPost


class PostAiAPIView(APIView):
    @staticmethod
    def get_index_from_title(title):
        return AiPost.objects.filter(title=title).values_list('id', flat=True).first()

    @staticmethod
    def get_title_from_index(index):
        return AiPost.objects.filter(id=index).values('post_title').first()

    @staticmethod
    def find_similar_titles(input_title, tfidf_matrix, vectorizer):
        input_vec = vectorizer.transform([input_title])
        cosine_similarities = cosine_similarity(input_vec, tfidf_matrix).flatten()
        return cosine_similarities

    @staticmethod
    def concatenate(titles, contents):
        return [f"{title} {content}" for title, content in zip(titles, contents)]

    @staticmethod
    def get_tag_from_index(index):
        tags = AiPost.objects.filter(id=index).values_list('post_tags', flat=True)
        if tags.exists():
            return tags[0].split(',')
        return ['없습니다']

    def post(self, request):
        data = request.data

        # Concatenate features
        input_title = data.get('title')
        input_content = data.get('content')
        target = f"{input_title} {input_content}"

        titles = AiPost.objects.all().values_list('post_title', flat=True)
        contents = AiPost.objects.all().values_list('post_content', flat=True)
        features = self.concatenate(titles, contents)

        # TF-IDF 벡터화
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(features)

        # 코사인 유사도 계산
        cosine_similarities = self.find_similar_titles(target, tfidf_matrix, vectorizer)

        # 유사도 높은 순으로 정렬
        similar_indices = cosine_similarities.argsort()[::-1]
        print(similar_indices)
        tag_set = set()
        for idx in similar_indices[1:6]:  # 가장 유사한 5개의 포스트 선택

            if cosine_similarities[idx] >= 0.1:

                tags = self.get_tag_from_index(idx)
                joined_str = ''.join(tags)
                cleaned_str = joined_str.replace("[", "").replace("]", "").replace("'", "").strip()
                cleaned_str = cleaned_str.split(" ")
                tag_set.update(cleaned_str)
        return Response(list(tag_set)[:5])
