import os
from datetime import timedelta, datetime
from pathlib import Path

import joblib
import sklearn
import numpy as np
from django.db.models import F, Count, Sum, Q
from django.db.models.functions import Round
from django.shortcuts import render
from django.utils import timezone
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response

from alarm.models import Alarm
from knowhow.models import Knowhow, KnowhowFile, KnowhowScrap, KnowhowTag, KnowhowView
from lecture.models import Lecture, LecturePlaceFile, LectureReview, LectureScrap, LecturePlant
from member.models import Member
from post.models import Post, PostScrap, PostTag, PostFile
from trade.models import Trade, TradeFile, TradeScrap


class SearchHistoryAPI(APIView):
    def get(self, request):
        # 세션에 담긴 최근 검색목록을 가져오는 로직
        search = request.session.get('search')
        return Response(search)

    def patch(self, request):
        # 최근 검색 기록 하나를 지웟을 때 실행될 로직
        search = request.session.get('search')
        search_data = request.data.get('data')
        for item in search:
            if item == search_data:
                search.remove(item)
        request.session.save()

        return Response('success')

    def delete(self, request):
        # 검색기록 전체 삭제
        if 'search' in request.session:
            del request.session['search']

        return Response('success')


class SearchAPI(APIView):
    def get(self, request):
        # 검색시 실행될 로직
        search_data = request.GET.get('query')
        # 검색을 상품명, 태그, 게시물 이름, 노하우 이름으로 하기로 기획
        trades = Trade.objects.filter(trade_title__contains=search_data).values('trade_title')
        knowhow_tags = KnowhowTag.objects.filter(tag_name__contains=search_data).values('tag_name')
        knowhow_title = Knowhow.objects.filter(knowhow_title__contains=search_data).values('knowhow_title')
        post_tags = PostTag.objects.filter(tag_name__contains=search_data).values('tag_name')
        post_title = Post.objects.filter(post_title__contains=search_data).values('post_title')

        combined_data = []
        # 각 겸색 결과를 list에 담아 전달
        for trade in trades:
            combined_data.append({'prev_search': trade['trade_title']})
        for tag in knowhow_tags:
            combined_data.append({'prev_search': tag['tag_name']})
        for tag in post_tags:
            combined_data.append({'prev_search': tag['tag_name']})
        for title in knowhow_title:
            combined_data.append({'prev_search': title['knowhow_title']})
        for title in post_title:
            combined_data.append({'prev_search': title['post_title']})
        return Response(combined_data)


class SearchView(View):
    def get(self, request):
        member = request.session.get('member')
        search_data = request.GET.get('query')
        # 검색시 검색 키워드를 세션에 저장해 최근 검색 기록으로 사용 할 수 있게 만든다.
        try:
            if 'search' not in request.session:
                request.session['search'] = [search_data]
            else:
                request.session['search'].append(search_data)
            request.session.save()
        except KeyError:
            return

        # 모든 컨텐츠에서 검색 키워드에 맞는 결과를 가져온다
        knowhow_condition = Q(knowhow_title__contains=search_data) | Q(knowhowtag__tag_name__contains=search_data)
        knowhows_queryset = Knowhow.objects.filter(knowhow_condition)
        knowhows = knowhows_queryset.order_by('knowhow_count') \
                       .annotate(member_profile=F('member__memberprofile__file_url'),
                                 member_name=F('member__member_name')) \
                       .values('member_profile', 'member_name', 'id', 'knowhow_title')[:8]
        knowhow_count = knowhows_queryset.count()

        for knowhow in knowhows:
            knowhow_file = KnowhowFile.objects.filter(knowhow_id=knowhow['id']).values('file_url').first()
            knowhow['knowhow_file_url'] = knowhow_file['file_url'] if knowhow_file else None
            knowhow_scrap = KnowhowScrap.objects.filter(knowhow_id=knowhow['id'], member_id=member['id']).values(
                'status').first()
            knowhow['knowhow_scrap'] = knowhow_scrap['status'] if knowhow_scrap and 'status' in knowhow_scrap else False

        trade_condition = Q(trade_title__contains=search_data)
        trades_queryset = Trade.enabled_objects.filter(trade_condition)
        trades = trades_queryset.order_by('-id') \
                     .annotate(trade_category_name=F('trade_category__category_name')) \
                     .values('id', 'trade_title', 'trade_content', 'trade_price', 'trade_category_name')[:10]
        trade_count = trades_queryset.count()

        for trade in trades:
            trade_file = TradeFile.objects.filter(trade_id=trade['id']).values('file_url').first()
            trade['trade_file_url'] = trade_file['file_url']
            trade_scrap = TradeScrap.objects.filter(trade_id=trade['id'], member_id=member['id']).values(
                'status').first()
            trade['trade_scrap'] = trade_scrap['status'] if trade_scrap and 'status' in trade_scrap else False

        post_condition = Q(post_title__contains=search_data) | Q(posttag__tag_name__contains=search_data)
        posts_queryset = Post.objects.filter(post_condition)
        posts = posts_queryset.order_by('post_count') \
                    .annotate(member_profile=F('member__memberprofile__file_url'),
                              member_name=F('member__member_name')) \
                    .values('member_profile', 'member_name', 'id', 'post_title', 'post_content')[:8]
        post_count = posts_queryset.count()

        for post in posts:
            post_file = PostFile.objects.filter(post_id=post['id']).values('file_url').first()
            post['post_file_url'] = post_file['file_url'] if post_file else None
            post_scrap = PostScrap.objects.filter(post_id=post['id'], member_id=member['id']).values(
                'status').first()
            post['post_scrap'] = post_scrap['status'] if post_scrap and 'status' in post_scrap else False

        lecture_condition = Q(lecture_title__contains=search_data)
        lectures_queryset = Lecture.enabled_objects.filter(lecture_condition)
        lectures = lectures_queryset.annotate(review_count=Count('lecturereview'), lecture_rating=Round(
            Sum('lecturereview__review_rating') / Count('lecturereview'), 1)) \
                       .order_by('-id').values('id', 'lecture_title', 'lecture_content', 'lecture_rating',
                                               'review_count')[:8]
        lecture_count = lectures_queryset.count()

        for lecture in lectures:
            lecture_file = LecturePlaceFile.objects.filter(lecture_id=lecture['id']).values('file_url').first()
            lecture['lecture_file_url'] = lecture_file['file_url'] if lecture_file else None
            lecture_scrap = LectureScrap.objects.filter(lecture_id=lecture['id'], member_id=member['id']).values(
                'status').first()
            lecture['lecture_scrap'] = lecture_scrap['status'] if lecture_scrap and 'status' in lecture_scrap else False

        count = {
            'knowhow_count': knowhow_count,
            'trade_count': trade_count,
            'lecture_count': lecture_count,
            'post_count': post_count
        }

        context = {
            'count': count,
            'knowhows': knowhows,
            'lectures': lectures,
            'trades': trades,
            'posts': posts
        }
        return render(request, 'main/search.html', context)


class MainView(View):
    def get(self, request):
        member = request.session.get('member')

        # 메인에 표시되는 데이터를 일주일 단위로 끊으려고 했으나 데이터가 너무 적어 기획 변경
        # today = timezone.now().date()
        # start_of_week = today - timedelta(days=today.weekday())
        # end_of_week = start_of_week + timedelta(days=6)
        # created_date__range = (start_of_week, end_of_week)

        # 메인 최상단에 표시될 노하우 게시물
        best_knowhow = Knowhow.objects.filter().order_by('-knowhow_count') \
            .annotate(member_profile=F('member__memberprofile__file_url'),
                      member_name=F('member__member_name')) \
            .values('member_profile', 'member_name', 'id').first()

        knowhow_file = KnowhowFile.objects.filter(knowhow_id=best_knowhow['id']).values('file_url').first()
        best_knowhow['knowhow_file_url'] = knowhow_file['file_url'] if knowhow_file else None

        # knowhow ai
        member_object = None
        if member:
            member_object = Member.objects.get(id=member.get('id'))

        if member_object and KnowhowView.objects.filter(member_id=member_object.id).count() >= 3:
            knowhow_model = joblib.load(os.path.join(Path(__file__).resolve().parent, f'ai/knowhow_ai{member_object.id}.pkl'))

            knowhow_id = KnowhowView.objects.filter(member_id=member_object.id).order_by('-id')[:3].values('knowhow_id')

            knowhows = [0] * len(knowhow_id)
            probas = [0] * len(knowhow_id)
            for i in range(len(knowhow_id)):
                knowhows[i] = Knowhow.objects.filter(id=knowhow_id[i].get('knowhow_id')).values('knowhow_title', 'knowhow_content')
                knowhows[i] = (knowhows[i][0]['knowhow_title']) + (knowhows[i][0]['knowhow_content'])
                probas[i] = knowhow_model.predict_proba([knowhows[i]])

            total_proba = [0] * len(probas[0][0])
            for i in range(len(total_proba)):
                total_proba[i] = (probas[0][0][i] + probas[1][0][i] + probas[2][0][i])

            print('total_proba', total_proba)
            if total_proba[0] == 3:
                total_proba = [2.7, 0.1, 0.1, 0.1]


            categories = ['꽃', '농촌', '원예', '정원']
            knowhows = []
            np_total_proba = np.array(total_proba)
            argsorted_indices = np_total_proba.argsort()[::-1]

            amounts = [5, 3, 2, 0]

            for i in range(4):
                category_name = categories[argsorted_indices[i]]
                category_amount = amounts[i]
                knowhows += list(Knowhow.objects.filter(knowhowcategory__category_name=category_name).order_by('-id')[:category_amount]\
                               .annotate(member_profile=F('member__memberprofile__file_url'),
                                         member_name=F('member__member_name')) \
                               .values('member_profile', 'member_name', 'id', 'knowhow_title'))

            for knowhow in knowhows:
                knowhow_file = KnowhowFile.objects.filter(knowhow_id=knowhow['id']).values('file_url').first()
                knowhow['knowhow_file_url'] = knowhow_file['file_url'] if knowhow_file else None
                if member is None:
                    knowhow['knowhow_scrap'] = False
                else:
                    knowhow_scrap = KnowhowScrap.objects.filter(knowhow_id=knowhow['id'], member_id=member['id']).values(
                        'status').first()
                    knowhow['knowhow_scrap'] = knowhow_scrap[
                        'status'] if knowhow_scrap and 'status' in knowhow_scrap else False

        elif member_object and KnowhowView.objects.filter(member_id=member_object.id).count() < 3:
            # 메인에 표시된 노하우 게시물
            knowhows = Knowhow.objects.filter() \
                           .annotate(member_profile=F('member__memberprofile__file_url'),
                                     member_name=F('member__member_name')) \
                           .values('member_profile', 'member_name', 'id', 'knowhow_title')[:10]

            # print(knowhows)
            for knowhow in knowhows:
                knowhow_file = KnowhowFile.objects.filter(knowhow_id=knowhow['id']).values('file_url').first()
                knowhow['knowhow_file_url'] = knowhow_file['file_url'] if knowhow_file else None
                if member is None:
                    knowhow['knowhow_scrap'] = False
                else:
                    knowhow_scrap = KnowhowScrap.objects.filter(knowhow_id=knowhow['id'],
                                                                member_id=member['id']).values(
                        'status').first()
                    knowhow['knowhow_scrap'] = knowhow_scrap[
                        'status'] if knowhow_scrap and 'status' in knowhow_scrap else False


        else:
            # 메인에 표시된 노하우 게시물
            knowhows = Knowhow.objects.filter() \
                           .annotate(member_profile=F('member__memberprofile__file_url'),
                                     member_name=F('member__member_name')) \
                           .values('member_profile', 'member_name', 'id', 'knowhow_title')[:10]

            # print(knowhows)
            for knowhow in knowhows:
                knowhow_file = KnowhowFile.objects.filter(knowhow_id=knowhow['id']).values('file_url').first()
                knowhow['knowhow_file_url'] = knowhow_file['file_url'] if knowhow_file else None
                if member is None:
                    knowhow['knowhow_scrap'] = False
                else:
                    knowhow_scrap = KnowhowScrap.objects.filter(knowhow_id=knowhow['id'], member_id=member['id']).values(
                        'status').first()
                    knowhow['knowhow_scrap'] = knowhow_scrap[
                        'status'] if knowhow_scrap and 'status' in knowhow_scrap else False

        # 데이터가 너무 적어 기획 변경
        # start_of_day = datetime(today.year, today.month, today.day, 0, 0, 0)
        # end_of_day = datetime(today.year, today.month, today.day, 23, 59, 59)

        # 메인에 표시될 상품
        trades = Trade.enabled_objects.filter() \
                     .order_by('-id') \
                     .annotate(trade_category_name=F('trade_category__category_name')) \
                     .values('id', 'trade_title', 'trade_content', 'trade_price', 'trade_category_name')[:6]
        for trade in trades:
            trade_file = TradeFile.objects.filter(trade_id=trade['id']).values('file_url').first()
            trade['trade_file_url'] = trade_file['file_url'] if trade_file else None
            if member is None:
                trade['trade_scrap'] = False
            else:
                trade_scrap = TradeScrap.objects.filter(trade_id=trade['id'], member_id=member['id']).values(
                    'status').first()
                trade['trade_scrap'] = trade_scrap['status'] if trade_scrap and 'status' in trade_scrap else False

        # 메인에 표시될 게시물
        posts = Post.objects.filter().order_by('post_count') \
                    .annotate(member_profile=F('member__memberprofile__file_url'),
                              member_name=F('member__member_name')) \
                    .values('member_profile', 'member_name', 'id', 'post_title')[:4]

        for post in posts:
            post_file = PostFile.objects.filter(post_id=post['id']).values('file_url').first()
            post['post_file_url'] = post_file['file_url'] if post_file else None
            if member is None:
                post['post_scrap'] = False
            else:
                post_scrap = PostScrap.objects.filter(post_id=post['id'], member_id=member['id']).values(
                    'status').first()
                post['post_scrap'] = post_scrap['status'] if post_scrap and 'status' in post_scrap else False

        # 메인에 표시될 강의
        lectures = Lecture.objects.filter().order_by('-id') \
                       .values('id', 'lecture_title', 'lecture_content')[:4]
        for lecture in lectures:
            lecture_file = LecturePlaceFile.objects.filter(lecture_id=lecture['id']).values('file_url').first()
            lecture['lecture_file_url'] = lecture_file['file_url'] if lecture_file else None
            if member is None:
                lecture['lecture_scrap'] = False
            else:
                lecture_scrap = LectureScrap.objects.filter(lecture_id=lecture['id'], member_id=member['id']).values(
                    'status').first()
                lecture['lecture_scrap'] = lecture_scrap[
                    'status'] if lecture_scrap and 'status' in lecture_scrap else False

        # 메인에 표시될 강의 리뷰
        lecture_reviews = LectureReview.objects.filter().order_by('-id') \
                              .annotate(lecture_title=F('lecture__lecture_title')) \
                              .values('id', 'lecture_title', 'review_content', 'lecture_id')[:3]
        for lecture_review in lecture_reviews:
            lecture_review_file = Lecture.objects.filter(id=lecture_review['lecture_id']).values(
                'lectureplacefile__file_url').first()
            lecture_review['lecture_file_url'] = lecture_review_file['lectureplacefile__file_url']

        context = {
            'best_knowhow': best_knowhow,
            'knowhows': knowhows,
            'lectures': lectures,
            'trades': trades,
            'lectureReviews': lecture_reviews,
            'posts': posts,
            'member': member
        }
        return render(request, 'main/main.html', context)


class BestLectureCategoryAPI(APIView):
    def post(self, request):
        member = request.session.get('member')
        data = request.data
        catagory = data.get('category')
        if not catagory == '전체':
            condition = Q(lectureplant__plant_name=catagory)
        else:
            condition = Q()

        best_lectures = Lecture.enabled_objects.filter(condition) \
                            .annotate(review_count=Count('lecturereview'),
                                      lecture_rating=Round(Sum('lecturereview__review_rating') / Count('lecturereview'),
                                                           1)) \
                            .order_by('-id') \
                            .values('id', 'lecture_title', 'lecture_content', 'review_count',
                                    'lecture_rating', 'lecture_price')[:3]

        for best_lecture in best_lectures:
            lecture_file = LecturePlaceFile.objects.filter(lecture_id=best_lecture['id']).values('file_url').first()
            best_lecture['lecture_file_url'] = lecture_file['file_url'] if lecture_file else None
            tags = LecturePlant.objects.filter(lecture_id=best_lecture['id']).values('plant_name')
            best_lecture['lecture_tags'] = [tag['plant_name'] for tag in tags]
            if member is None:
                best_lecture['lecture_scrap'] = False
            else:
                lecture_scrap = LectureScrap.objects.filter(lecture_id=best_lecture['id'],
                                                            member_id=member['id']).values(
                    'status').first()
                best_lecture['lecture_scrap'] = lecture_scrap[
                    'status'] if lecture_scrap and 'status' in lecture_scrap else False
                best_lecture['member_id'] = member['id']
            if best_lecture['lecture_rating'] is None:
                best_lecture['lecture_rating'] = 0
        return Response(best_lectures)


class KnowhowScrapAPI(APIView):
    def patch(self, request):
        data = request.data
        member = request.session.get('member')
        if member:
            data = {
                'knowhow_id': data['knowhow_id'],
                'member_id': member['id']
            }
            knowhow_scrap, created = KnowhowScrap.objects.get_or_create(knowhow_id=data['knowhow_id'],
                                                                        member_id=data['member_id'])
            if not created:
                is_scrap = False if knowhow_scrap.status else True
                knowhow_scrap.status = is_scrap
                knowhow_scrap.save()

            scrap_status = KnowhowScrap.objects.filter(knowhow_id=data['knowhow_id'],
                                                       member_id=data['member_id']).values('status').first()
            return Response(scrap_status)
        else:
            return Response('')


class TradeScrapAPI(APIView):
    def patch(self, request):
        data = request.data
        member = request.session.get('member')
        if member:
            data = {
                'trade_id': data['trade_id'],
                'member_id': member['id']
            }

            trade_scrap, created = TradeScrap.objects.get_or_create(trade_id=data['trade_id'],
                                                                    member_id=data['member_id'])
            if not created:
                is_scrap = False if trade_scrap.status else True
                trade_scrap.status = is_scrap
                trade_scrap.save()

            scrap_status = TradeScrap.objects.filter(trade_id=data['trade_id'], member_id=data['member_id']).values(
                'status').first()
            return Response(scrap_status)
        else:
            return Response('')


class LectureScrapAPI(APIView):
    def patch(self, request):
        data = request.data
        member = request.session.get('member')
        if member:
            data = {
                'lecture_id': data['lecture_id'],
                'member_id': member['id']
            }
            lecture_scrap, created = LectureScrap.objects.get_or_create(lecture_id=data['lecture_id'],
                                                                        member_id=data['member_id'])
            if not created:
                is_scrap = False if lecture_scrap.status else True
                lecture_scrap.status = is_scrap
                lecture_scrap.save()

            scrap_status = LectureScrap.objects.filter(lecture_id=data['lecture_id'],
                                                       member_id=data['member_id']).values('status').first()
            return Response(scrap_status)
        else:
            return Response('')


class PostScrapAPI(APIView):
    def patch(self, request):
        data = request.data
        member = request.session.get('member')
        if member:
            data = {
                'post_id': data['post_id'],
                'member_id': member['id']
            }

            post_scrap, created = PostScrap.objects.get_or_create(post_id=data['post_id'], member_id=data['member_id'])
            if not created:
                is_scrap = False if post_scrap.status else True
                post_scrap.status = is_scrap
                post_scrap.save()

            scrap_status = PostScrap.objects.filter(post_id=data['post_id'], member_id=data['member_id']).values(
                'status').first()
            return Response(scrap_status)
        else:
            return Response('')
