from django.db import transaction
from django.db.models import F, Q, Count, Value
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView

from alarm.models import Alarm
from knowhow.models import KnowhowTag, KnowhowFile
from member.models import Member, MemberProfile
from post.models import Post, PostCategory, PostTag, PostPlant, PostFile, PostReply, PostLike, PostScrap, PostReplyLike
from report.models import PostReport, PostReplyReport


# Create your views here.
class PostCreateView(View):
    def get(self, request):
        return render(request, 'community/web/post/create-post.html')

    @transaction.atomic
    def post(self, request):
        data = request.POST
        files = request.FILES

        print(data)

        # 현재 로그인된 사람의 정보
        member = Member(**request.session['member'])

        # 포스트
        post = {
            'post_title': data['post-title'],
            'post_content': data['post-content'],
            'member': member
        }

        post_data = Post.objects.create(**post)

        # 카테고리
        post_category = {
            'category_name': data['post-category'],
            'post': post_data
        }

        PostCategory.objects.create(**post_category)

        # 포스트 태그
        post_tag = {
            'tag_name': data['post-tags'],
            'post': post_data
        }

        PostTag.objects.create(**post_tag)

        plant_types = data.getlist('plant-type')

        # 식물 종류
        for plant_type in plant_types:
            # print(plant_type)
            PostPlant.objects.create(post=post_data, plant_name=plant_type)

        # 첨부파일
        for key in files:
            # print(key)
            PostFile.objects.create(post=post_data, file_url=files[key])
        return redirect(f'/post/detail/?id={post_data.id}')

class PostDetailView(View):
    def get(self, request):
        post = Post.objects.get(id=request.GET['id'])
        session_member_id = request.session['member']['id']
        session_profile = MemberProfile.objects.get(id=session_member_id)
        post_tags = PostTag.objects.filter(post_id__gte=1).values('tag_name')
        reply_count = PostReply.objects.filter(post_id=post.id).values('id').count()
        member_profile = MemberProfile.objects.get(id=post.member_id)
        post_category = PostCategory.objects.filter(post_id=post).values('category_name').first()
        post_plant = PostPlant.objects.filter(post_id=post.id).values('plant_name')

        post_scrap = PostScrap.objects.filter(post_id=post, member_id=session_member_id, status=1).exists()
        post_like = PostLike.objects.filter(post_id=post, member_id=session_member_id, status=1).exists()

        post.post_count += 1
        post.save(update_fields=['post_count'])

        print(post.id)

        post_files = list(post.postfile_set.all())
        post_file = list(post.postfile_set.all())[0]
        post_writer = Post.objects.filter(member_id=post.member_id).values('member__member_name').first()
        post_writer = post_writer['member__member_name']
        context = {
            'post': post,
            'post_files': post_files,
            'post_file': post_file,
            'post_tags': post_tags,
            'reply_count': reply_count,
            'member_profile': member_profile,
            'post_category': post_category,
            'post_plant': post_plant,
            'post_writer': post_writer,
            'post_scrap': post_scrap,
            'post_like': post_like,
            'session_profile': session_profile
        }

        return render(request, 'community/web/post/post-detail.html', context)

# post 게시글 신고
class PostReportView(View):
    def post(self, request):
        member_id = request.session['member']['id']
        data = request.POST
        post_id = request.GET['id']

        datas = {
            'member_id': member_id,
            'post_id': post_id,
            'report_content': data['report-content']
        }

        PostReport.object.create(**datas)

        return redirect(f'/post/detail/?id={post_id}')

class PostReplyReportView(View):
    def post(self, request):
        data = request.POST
        member_id = request.session['member']['id']
        post_id = request.GET['id']
        reply_id = data['reply-report-reply-id']

        datas = {
            'member_id': member_id,
            'post_reply_id': reply_id,
            'report_content': data['reply-report-content']
        }

        PostReplyReport.object.create(**datas)

        return redirect(f'/post/detail/?id={post_id}')

class PostDetailApi(APIView):
    def get(self, request, post_id, page):

        row_count = 5
        offset = (page - 1) * row_count
        limit = row_count * page

        # 댓글 갯수
        reply_count = PostReply.objects.filter(post_id=post_id).count()
        # 좋아요 갯수
        like_count = PostLike.objects.filter(post_id=post_id, status=1).count()
        # 스크랩 갯수
        scrap_count = PostScrap.objects.filter(post_id=post_id, status=1).count()
        # 게시글 작성 날짜
        post_date = Post.objects.filter(id=post_id).values('created_date')

        # 댓글
        replies = PostReply.objects \
                      .filter(post_id=post_id).annotate(member_name=F('member__member_name')) \
                      .values('member_name', 'post__post_content', 'member_id', 'created_date', 'id',
                              'post_reply_content', 'member__memberprofile__file_url')[offset:limit]

        data = {
            'replies': replies,
            'reply_count': reply_count,
            'post_date': post_date,
            'like_count': like_count,
            'scrap_count': scrap_count
        }

        return Response(data)

class PostUpdateView(View):
    def get(self, request):
        post_id = request.GET.get('id')

        post = Post.objects.get(id=post_id)
        post_file = list(post.postfile_set.values('file_url'))
        # print(test)

        context = {
            'post': post,
            'post_files': post_file
        }

        return render(request, 'community/web/post/edit-post.html', context)

    @transaction.atomic
    def post(self, request):
        datas = request.POST
        files = request.FILES

        post_id = request.GET['id']

        # print(post_id)
        # print(datas)

        # test = KnowhowFile.objects.filter(knowhow_id=knowhow_id).delete()
        # print(test)

        # 지금 시간
        time_now = timezone.now()

        # 수정할 노하우 게시글 아이디
        post = Post.objects.get(id=post_id)

        # 노하우 게시글 수정
        post.post_title = datas['post-title']
        post.post_content = datas['post-content']
        post.updated_date = time_now
        post.save(update_fields=['post_title', 'post_content', 'updated_date'])

        # 노하우 카테고리 수정
        post_category = PostCategory.objects.get(post_id=post_id)

        post_category.category_name = datas['post-category']
        post_category.updated_date = time_now
        post_category.save(update_fields=['category_name', 'updated_date'])

        # 노하우 식물종류 수정
        plant_types = datas.getlist('plant-type')

        PostPlant.objects.filter(post_id=post_id).delete()

        for plant_type in plant_types:
            # print(plant_type)
            PostPlant.objects.create(post_id=post_id, plant_name=plant_type, updated_date=time_now)

        # 노하우 태그 수정
        post_tag = PostTag.objects.get(post_id=post_id)

        post_tag.tag_name = datas['post-tags']
        post_tag.updated_date = timezone.now()
        post_tag.save(update_fields=['tag_name', 'updated_date'])

        PostFile.objects.filter(post_id=post_id).delete()

        for key in files:
            PostFile.objects.create(post_id=post_id, file_url=files[key])

        return redirect(f'/post/detail/?id={post_id}')

class PostDeleteView(View):
    @transaction.atomic
    def get(self, request):
        post_id = request.GET['id']
        # print(post_id)
        PostTag.objects.filter(post_id=post_id).delete()
        PostFile.objects.filter(post_id=post_id).delete()
        PostReply.objects.filter(post_id=post_id).delete()
        PostCategory.objects.filter(post_id=post_id).delete()
        PostPlant.objects.filter(post_id=post_id).delete()
        PostScrap.objects.filter(post_id=post_id).delete()
        PostLike.objects.filter(post_id=post_id).delete()
        Post.objects.filter(id=post_id).delete()

        return redirect(f'/post/list/')

class PostReplyWriteApi(APIView):
    @transaction.atomic
    def post(self, request):
        data = request.data
        post = Post.objects.filter(id=data['post_id']).values('member_id')

        Alarm.objects.create(alarm_category=5, receiver_id=post, sender_id=request.session.get('member')['id'], target_id=data['post_id'])

        # print(data)
        data = {
            'post_reply_content': data['reply_content'],
            'post_id': data['post_id'],
            'member_id': request.session.get('member')['id']
        }

        PostReply.objects.create(**data)



        return Response('success')



class PostReplyApi(APIView):
    def delete(self, request, reply_id):
        PostReply.objects.filter(id=reply_id).delete()
        return Response('success')

    def patch(self, request, reply_id):
        # print(request)
        reply_content = request.data['reply_content']
        updated_date = timezone.now()

        reply = PostReply.objects.get(id=reply_id)
        reply.post_reply_content = reply_content
        reply.updated_date = updated_date
        reply.save(update_fields=['post_reply_content', 'updated_date'])

        return Response('success')

class PostReplyLikeApi(APIView):
    def get(self, request, post_id, reply_id, member_id, like_status):

        check_like_status = True

        # 만들어지면 True, 이미 있으면 False
        reply_like, reply_like_created = PostReplyLike.objects\
            .get_or_create(post_id=post_id, post_reply_id=reply_id, member_id=member_id)

        if reply_like_created:
            check_like_status = True

        else:

            if like_status == 'True':
                update_like = PostReplyLike.objects.get(post_id=post_id, post_reply_id=reply_id, member_id=member_id)

                update_like.status = 1
                update_like.save(update_fields=['status'])
                check_like_status = True

            else:
                update_like = PostReplyLike.objects.get(post_id=post_id, post_reply_id=reply_id, member_id=member_id)

                update_like.status = 0
                update_like.save(update_fields=['status'])
                check_like_status = False

        like_count = PostReplyLike.objects.filter(post_id=post_id, post_reply_id=reply_id, status=1).count()
        # print(like_count)

        datas = {
            'check_like_status': check_like_status,
            'like_count': like_count
        }

        return Response(datas)

class PostScrapApi(APIView):
    def get(self, request, post_id, member_id, scrap_status):

        check_scrap_status = True

        # print(knowhow_id, member_id, status)

        # 만들어지면 True, 이미 있으면 False
        scrap, scrap_created = PostScrap.objects.get_or_create(post_id=post_id, member_id=member_id)

        if scrap_created:
            check_scrap_status = True

        else:

            if scrap_status == 'True':
                update_scrap = PostScrap.objects.get(post_id=post_id, member_id=member_id)

                update_scrap.status = 1
                update_scrap.save(update_fields=['status'])
                check_scrap_status = True

            else :
                update_scrap = PostScrap.objects.get(post_id=post_id, member_id=member_id)

                update_scrap.status = 0
                update_scrap.save(update_fields=['status'])
                check_scrap_status = False

        scrap_count = PostScrap.objects.filter(post_id=post_id, status=1).count()

        datas = {
            'check_scrap_status': check_scrap_status,
            'scrap_count': scrap_count
        }

        return Response(datas)

class PostLikeApi(APIView):
    def get(self, request, post_id, member_id, like_status):

        check_like_status = True

        # 만들어지면 True, 이미 있으면 False
        like, like_created = PostLike.objects.get_or_create(post_id=post_id, member_id=member_id)
        post = Post.objects.filter(id=post_id).values('member_id')

        if like_created:
            check_like_status = True
            Alarm.objects.create(alarm_category=4, receiver_id=post, sender_id=member_id, target_id=post_id)

        else:

            if like_status == 'True':
                update_like = PostLike.objects.get(post_id=post_id, member_id=member_id)

                update_like.status = 1
                update_like.save(update_fields=['status'])
                check_like_status = True

            else :
                update_like = PostLike.objects.get(post_id=post_id, member_id=member_id)

                update_like.status = 0
                update_like.save(update_fields=['status'])
                check_like_status = False

        like_count = PostLike.objects.filter(post_id=post_id, status=1).count()
        # print(like_count)


        datas = {
            'check_like_status': check_like_status,
            'like_count': like_count
        }

        return Response(datas)

class PostLikeCountApi(APIView):
    def get(self, request, post_id):

        like_count = PostLike.objects.filter(post_id=post_id, status=1).count()

        # print(like_count)


        return Response(like_count)

class PostScrapCountApi(APIView):
    def get(self, request, post_id):

        scrap_count = PostScrap.objects.filter(post_id=post_id, status=1).count()

        # print(scrap_count)


        return Response(scrap_count)

class PostListView(View):
    def get(self, request):

        post_count = Post.objects.count()

        context = {
            'post_count': post_count
        }

        return render(request, 'community/web/post/post.html', context)

class PostListApi(APIView):
    def get(self, request, page, sorting, filters, types):
        row_count = 6
        offset = (page - 1) * row_count
        limit = row_count * page

        member = request.session.get('member')

        print(types)

        condition = Q()
        condition2 = Q()
        sort1 = '-id'
        sort2 = '-id'

        if types == '식물 키우기':
            condition2 |= Q(postcategory__category_name__contains='식물 키우기')
        elif types == '관련 제품':
            condition2 |= Q(postcategory__category_name__contains='관련 제품')
        elif types == '테라리움':
            condition2 |= Q(postcategory__category_name__contains='테라리움')
        elif types == '스타일링':
            condition2 |= Q(postcategory__category_name__contains='스타일링')
        elif types == '전체':
            condition2 |= Q()

        filters = filters.split(',')
        for filter in filters:
            # print(filter.replace(',', ''))
            if filter.replace(',', '') == '관엽식물':
                condition |= Q(postplant__plant_name__contains='관엽식물')

            elif filter.replace(',', '') == '침엽식물':
                condition |= Q(postplant__plant_name__contains='침엽식물')

            elif filter.replace(',', '') == '희귀식물':
                condition |= Q(postplant__plant_name__contains='희귀식물')

            elif filter.replace(',', '') == '다육':
                condition |= Q(postplant__plant_name__contains='다육')

            elif filter.replace(',', '') == '선인장':
                condition |= Q(postplant__plant_name__contains='선인장')

            elif filter.replace(',', '') == '기타':
                condition |= Q(postplant__plant_name__contains='기타')

            elif filter.replace(',', '') == '전체':
                condition = Q()

        # print(condition2)

        columns1 = [
            'post_title',
            'member_id',
            'post_count',
            'id',
            'like_count'
        ]

        columns2 = [
            'post_title',
            'member_id',
            'post_count',
            'id',
            'scrap_count',
        ]

        columns3 = [
            'post_title',
            'member_id',
            'post_count',
            'id'
        ]

        if sorting == '최신순':
            sort1 = '-id'
            sort2 = '-created_date'

            posts = Post.objects.filter(condition, condition2).values(*columns3).order_by(sort1, sort2)[
                       offset:limit]

            for post in posts:
                member_name = Member.objects.filter(id=post['member_id']).values('member_name').first().get(
                    'member_name')
                post['member_name'] = member_name

                like_count = PostLike.objects.filter(status=1, post=post['id']).count()
                post['like_count'] = like_count

                scrap_count = PostScrap.objects.filter(status=1, post=post['id']).count()
                post['scrap_count'] = scrap_count

        elif sorting == '인기순':
            sort1 = '-like_count'
            sort2 = '-post_count'

            posts = Post.objects.filter(condition, condition2) \
                           .annotate(like_count=Count('postlike__id', filter=Q(postlike__status=1))) \
                           .values(*columns1) \
                           .order_by(sort1, sort2)[offset:limit]

            for post in posts:
                member_name = Member.objects.filter(id=post['member_id']).values('member_name').first().get(
                    'member_name')
                post['member_name'] = member_name

                scrap_count = PostScrap.objects.filter(status=1, post=post['id']).count()
                post['scrap_count'] = scrap_count

        elif sorting == "스크랩순":
            sort1 = '-scrap_count'
            sort2 = '-id'

            posts = Post.objects.filter(condition, condition2) \
                           .annotate(scrap_count=Count('postscrap__id', filter=Q(postscrap__status=1))) \
                           .values(*columns2) \
                           .order_by(sort1, sort2)[offset:limit]

            for post in posts:
                member_name = Member.objects.filter(id=post['member_id']).values('member_name').first().get(
                    'member_name')
                post['member_name'] = member_name

                like_count = PostLike.objects.filter(status=1, post=post['id']).count()
                post['like_count'] = like_count

        print(condition, condition2)
        print(sort1, sort2)

        posts_count = Post.objects.select_related('postlike', 'postscrap').filter(condition, condition2) \
            .annotate(member_name=F('member__member_name')) \
            .values(*columns3) \
            .annotate(like_count=Count(Q(postlike__status=1)), scrap_count=Count(Q(postscrap__status=1))) \
            .values('post_title', 'member__member_name', 'post_count', 'id', 'member_id', 'like_count',
                    'scrap_count') \
            .order_by(sort1, sort2).distinct().count()

        # knowhow에 가상 컬럼을 만들어서 하나씩 추가해줌
        for post in posts:
            post_file = PostFile.objects.filter(post_id=post['id']).values('file_url').first()
            profile = MemberProfile.objects.filter(member_id=post['member_id']).values('file_url').first()
            post['post_file'] = post_file['file_url']
            post['profile'] = profile['file_url']
            # knowhow_scrap = KnowhowScrap.objects.filter(knowhow_id=knowhow['id'], member_id=member['id']).values('status').first()
            # knowhow['knowhow_scrap'] = knowhow_scrap['status'] if knowhow_scrap and 'status' in knowhow_scrap else False
            # knowhow_like = KnowhowLike.objects.filter(knowhow_id=knowhow['id'], member_id=member['id']).values(
            #     'status').first()
            # knowhow['knowhow_like'] = knowhow_like['status'] if knowhow_like and 'status' in knowhow_like else False
            # print(knowhow)


        datas = {
            'posts': posts,
            'posts_count': posts_count
        }

        return Response(datas)


# channel
class ChannelView(View):
    def get(self, request):
        # 노하우태그와 포스트 태그를 중복제거한 후 union
        # 어노테이트에 파일 추가
        # 중복 제거된 태그이름으로 조회
        post_tags = PostTag.objects.annotate(posts=F('post_id'), knowhows=Value(0), tag_names=Count('id')).values('tag_name', 'posts', 'knowhows').order_by('-tag_names')
        knowhow_tags = KnowhowTag.objects.annotate(posts=Value(0), knowhows=F('knowhow_id'), tag_names=Count('id')).values('tag_name', 'posts', 'knowhows').order_by('-tag_names')
        tags = post_tags.union(knowhow_tags)

        filtering_tags = []

        for tag in tags:
            print(tag)
            filtering_tags.append(tag['tag_name'])

        filtering_tags = set(filtering_tags)

        print(filtering_tags)

        filtered_tags = PostTag.objects.values('tag_name').annotate(tag_names=Count('id')).values('tag_names', 'tag_name').order_by('-tag_names')

        for tag in filtered_tags:
            print(tag)
        # for tag in tags:




        # for tag in tags:
        #     if tag['posts'] != 0:
        #         post_file = PostFile.objects.filter(post_id=tag['posts']).values('file_url').first()
        #         tag['post_file'] = post_file['file_url']
        #
        #     else:
        #         knowhow_file = KnowhowFile.objects.filter(knowhow_id=tag['knowhows']).values('file_url').first()
        #         tag['knowhow_file'] = knowhow_file['file_url']

            # print(tag)

        # print(type(tags))

        context = {
            'filtering_tags': filtering_tags,
        }

        return render(request, 'community/web/channel.html', context)
