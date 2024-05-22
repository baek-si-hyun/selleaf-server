import math

from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from qna.models import QnA

class QnAListAPI(APIView):
    # QnA 목록 조회 API 뷰
    def get(self, request):
        # 쿼리 스트링에서 검색 키워드와 페이지 값 받아오기
        keyword = request.GET.get('keyword', '')
        page = int(request.GET.get('page', 1))

        # 한 페이지에 띄울 QnA 수
        row_count = 10

        # 한 페이지에 표시할 QnA를 슬라이싱 하기 위한 변수들
        offset = (page - 1) * row_count
        limit = page * row_count

        # 검색 조건식 선언
        condition = Q()

        # keyword로 뭐라도 받았다면
        # keyword가 포함된 QnA 제목 or QnA 내용을 검색
        if keyword:
            condition |= Q(qna_title__icontains=keyword)
            condition |= Q(qna_content__icontains=keyword)

        # QnA 표시에 필요한 컬럼들
        columns = [
            'id',
            'qna_title',
            'qna_content'
        ]

        # 게시 중인 QnA의 목록을 최신순으로 가져옴
        qnas = QnA.enabled_objects.values(*columns).filter(condition, id__isnull=False)

        # 게시된 QnA의 총 개수
        total = qnas.count()

        # 페이지네이션에 필요한 정보들
        page_count = 5  # 화면에 표시할 페이지 숫자 버튼의 최대 개수

        # 다음 페이지에 표시할 정보가 있는지 없는지 확인하기 위한 변수(bool)
        has_next_page = QnA.enabled_objects.values(*columns)\
                            .filter(condition, id__isnull=False)[limit:limit+1].exists()

        end_page = math.ceil(page / page_count) * page_count  # 화면에 표시할 페이지 숫자 버튼 중 마지막 페이지
        start_page = end_page - page_count + 1  # 화면에 표시할 페이지 숫자 버튼 중 첫 페이지
        real_end = math.ceil(total / row_count)  # 전체 리스트의 마지막 페이지

        # end_page의 값이 real_end 보다 커지지 않게 조정
        end_page = real_end if end_page > real_end else end_page

        # end_page의 값이 0보다 작아지지 않게 조정
        if end_page == 0:
            end_page = 1

        # 페이지네이션에 사용할 정보 완성
        page_info = {
            'totalCount': total,
            'startPage': start_page,
            'endPage': end_page,
            'page': page,
            'realEnd': real_end,
            'pageCount': page_count,
            'hasNext': has_next_page
        }

        # QnA 목록을 QuerySet -> list 타입으로 변경하고, QnA 10개씩 슬라이싱(페이지 하나)
        qnas = list(qnas[offset:limit])

        # QnA 목록의 맨 뒤에 페이지네이션 정보 추가
        qnas.append(page_info)

        # 요청한 QnA 및 페이지네이션에 사용할 정보 반환
        return Response(qnas)
