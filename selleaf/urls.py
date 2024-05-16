from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from main.views import MainView, KnowhowScrapAPI, TradeScrapAPI, LectureScrapAPI, PostScrapAPI, BestLectureCategoryAPI, \
    SearchView, SearchAPI, SearchHistoryAPI
from selleaf.views import ManagerLoginView, ManagerLogoutView, MemberManagementView, WriteNoticeView, \
    NoticeManagementView, UpdateNoticeView, DeleteNoticeView, WriteQnAView, QnAManagementView, \
    UpdateQnAView, DeleteQnAView, MemberInfoAPI, TeacherManagementView, TeacherInfoAPI, TeacherEntryManagementView, \
    TeacherEntriesInfoAPI, DeleteManyNoticeView, DeleteManyQnAView, DeleteManyMembersAPI, TeacherApprovalAPI, \
    TeacherDeleteAPI, LectureManagementView, LectureInfoAPI, LectureReviewManagementView, LectureReviewInfoAPI, \
    LectureTraineesManagementView, TraineesInfoAPI, PostManagementView, ReplyManagementView, \
    KnowhowPostsAPI, TradePostsAPI, KnowhowDeleteAPI, TradeDeleteAPI, \
    KnowhowCountAPI, TradeCountAPI, PostsListAPI, PostsDeleteAPI, PostsCountAPI, \
    PaymentManagementView, TagManagementView, ReplyManagementAPI, LectureReportAPI, \
    TradeReportAPI, PostReportAPI, PostReplyReportAPI, KnowhowReportAPI, KnowhowReplyReportAPI, TagManagementAPI, \
    LectureReportManagementView, TradeReportManagementView, PostReportManagementView, PostReplyReportManagementView, \
    KnowhowReportManagementView, KnowhowReplyReportManagementView, LectureReportAdjustAPI, TradeReportAdjustAPI, \
    PostReportAdjustAPI, PostReplyReportAdjustAPI, KnowhowReportAdjustAPI, KnowhowReplyReportAdjustAPI, PaymentListAPI, \
    LectureDeleteAPI, LectureReviewDeleteAPI, HeaderView

urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('header/', HeaderView.as_view(), name='main-header'),
    path('search/', SearchView.as_view(), name='search'),
    path('search/api/', SearchAPI.as_view(), name='search-api'),
    path('search-history/api/', SearchHistoryAPI.as_view(), name='search-history-api'),
    path('knowhow-scrap/api/', KnowhowScrapAPI.as_view(), name='knowhow-scrap-api'),
    path('trade-scrap/api/', TradeScrapAPI.as_view(), name='trade-scrap-api'),
    path('lecture-scrap/api/', LectureScrapAPI.as_view(), name='lecture-scrap-api'),
    path('post-scrap/api/', PostScrapAPI.as_view(), name='post-scrap-api'),
    path('lecture-category/api/', BestLectureCategoryAPI.as_view(), name='lecture-category-api'),
    # 관리자 페이지 뷰
    path('service-admin/login/', ManagerLoginView.as_view(), name='manager-login'),
    path('service-admin/logout/', ManagerLogoutView.as_view(), name='manager-logout'),

    # 회원 관리
    path('service-admin/member/', MemberManagementView.as_view(), name='manager-member'),
    path('service-admin/member-list/', MemberInfoAPI.as_view(), name='member-info'),
    path('service-admin/member/delete/<str:member_ids>', DeleteManyMembersAPI.as_view(), name='member-delete'),

    # 강사 및 강사 신청자 관리
    path('service-admin/teacher/', TeacherManagementView.as_view(), name='manager-teacher'),
    path('service-admin/teacher-list/', TeacherInfoAPI.as_view(), name='teacher-info'),
    path('service-admin/teacher-entry/', TeacherEntryManagementView.as_view(), name='manager-teacher-entry'),
    path('service-admin/teacher-entry-list/', TeacherEntriesInfoAPI.as_view(), name='teacher-entry-info'),
    path('service-admin/teacher-approve/<str:teacher_ids>', TeacherApprovalAPI.as_view(), name='teacher-entry-approval'),
    path('service-admin/teacher-delete/<str:teacher_ids>', TeacherDeleteAPI.as_view(), name='teacher-delete'),

    # 게시물 관리
    path('service-admin/posts/', PostManagementView.as_view(), name='manager-post'),
    path('service-admin/posts/posts-list/', PostsListAPI.as_view(), name='community-post-api'),
    path('service-admin/posts/knowhow-list/', KnowhowPostsAPI.as_view(), name='knowhow-post-api'),
    path('service-admin/posts/trade-list/', TradePostsAPI.as_view(), name='trade-post-api'),
    path('service-admin/posts/posts-delete/<str:post_ids>', PostsDeleteAPI.as_view(), name='community-delete-api'),
    path('service-admin/posts/knowhow-delete/<str:knowhow_ids>', KnowhowDeleteAPI.as_view(), name='knowhow-delete-api'),
    path('service-admin/posts/trade-delete/<str:trade_ids>', TradeDeleteAPI.as_view(), name='trade-delete-api'),
    path('service-admin/posts/posts-count/', PostsCountAPI.as_view(), name='community-count-api'),
    path('service-admin/posts/knowhow-count/', KnowhowCountAPI.as_view(), name='knowhow-count-api'),
    path('service-admin/posts/trade-count/', TradeCountAPI.as_view(), name='trade-count-api'),

    # 댓글 관리
    path('service-admin/reply/', ReplyManagementView.as_view(), name='manager-reply'),
    path('service-admin/replies/api/', ReplyManagementAPI.as_view(), name='manager-reply-api'),

    # 결제 내역 관리
    path('service-admin/payment/', PaymentManagementView.as_view(), name='manager-payment'),
    path('service-admin/payment-list/', PaymentListAPI.as_view(), name='payment-list'),

    # 강의 관리
    path('service-admin/lecture/', LectureManagementView.as_view(), name='manager-lecture'),
    path('service-admin/lecture-list/', LectureInfoAPI.as_view(), name='lecture-info'),
    path('service-admin/lecture/review/', LectureReviewManagementView.as_view(), name='manager-lecture-review'),
    path('service-admin/lecture/review-list/', LectureReviewInfoAPI.as_view(), name='lecture-review-info'),
    path('service-admin/lecture/trainees/', LectureTraineesManagementView.as_view(), name='manager-lecture-trainees'),
    path('service-admin/lecture/trainees-list/', TraineesInfoAPI.as_view(), name='lecture-review-info'),
    path('service-admin/lecture/delete/<str:lecture_ids>', LectureDeleteAPI.as_view(), name='lecture-delete-api'),
    path('service-admin/lecture/review/delete/<str:lecture_ids>', LectureReviewDeleteAPI.as_view(), name='review-delete-api'),

    # 공지사항 관리
    path('service-admin/notice/', NoticeManagementView.as_view(), name='manager-notice'),
    path('service-admin/notice/write/', WriteNoticeView.as_view(), name='notice-write'),
    path('service-admin/notice/update/', UpdateNoticeView.as_view(), name='notice-update'),
    path('service-admin/notice/delete/', DeleteNoticeView.as_view(), name='notice-delete'),
    path('service-admin/notice/delete/<str:notice_ids>', DeleteManyNoticeView.as_view(), name='many-notice-delete'),

    # QnA 관리
    path('service-admin/qna/', QnAManagementView.as_view(), name='manager-qna'),
    path('service-admin/qna/write/', WriteQnAView.as_view(), name='qna-write'),
    path('service-admin/qna/update/', UpdateQnAView.as_view(), name='qna-update'),
    path('service-admin/qna/delete/', DeleteQnAView.as_view(), name='qna-delete'),
    path('service-admin/qna/delete/<str:qna_ids>', DeleteManyQnAView.as_view(), name='many-qna-delete'),

    # 태그 관리
    path('service-admin/tag/', TagManagementView.as_view(), name='manager-tag'),
    path('service-admin/tags/api/', TagManagementAPI.as_view(), name='manager-tag-api'),

    # 신고 내역 관리
    path('service-admin/report/lecture/', LectureReportManagementView.as_view(), name='manager-lecture-report'),
    path('service-admin/report/trade/', TradeReportManagementView.as_view(), name='manager-trade-report'),
    path('service-admin/report/post/', PostReportManagementView.as_view(), name='manager-post-report'),
    path('service-admin/report/post-reply/', PostReplyReportManagementView.as_view(), name='manager-post-reply-report'),
    path('service-admin/report/knowhow/', KnowhowReportManagementView.as_view(), name='manager-knowhow-report'),
    path('service-admin/report/knowhow-reply/', KnowhowReplyReportManagementView.as_view(), name='manager-knowhow-reply-report'),
    path('service-admin/lecture-report/', LectureReportAPI.as_view(), name='lecture-report-api'),
    path('service-admin/trade-report/', TradeReportAPI.as_view(), name='trade-report-api'),
    path('service-admin/post-report/', PostReportAPI.as_view(), name='post-report-api'),
    path('service-admin/post-reply-report/', PostReplyReportAPI.as_view(), name='post-reply-report-api'),
    path('service-admin/knowhow-report/', KnowhowReportAPI.as_view(), name='knowhow-report-api'),
    path('service-admin/knowhow-reply-report/', KnowhowReplyReportAPI.as_view(), name='knowhow-reply-report-api'),
    path('service-admin/lecture-report-adjust/<str:report_ids>', LectureReportAdjustAPI.as_view(), name='lecture-report-adjust-api'),
    path('service-admin/trade-report-adjust/<str:report_ids>', TradeReportAdjustAPI.as_view(), name='trade-report-adjust-api'),
    path('service-admin/post-report-adjust/<str:report_ids>', PostReportAdjustAPI.as_view(), name='post-report-adjust-api'),
    path('service-admin/post-reply-report-adjust/<str:report_ids>', PostReplyReportAdjustAPI.as_view(), name='post-reply-report-adjust-api'),
    path('service-admin/knowhow-report-adjust/<str:report_ids>', KnowhowReportAdjustAPI.as_view(), name='knowhow-report-adjust-api'),
    path('service-admin/knowhow-reply-report-adjust/<str:report_ids>', KnowhowReplyReportAdjustAPI.as_view(), name='knowhow-reply-report-adjust-api'),

    # 기타 서비스 url
    path('admin/', admin.site.urls),
    path('alarm/', include('alarm.urls-web')),
    path('member/', include('member.urls-web')),
    path('lecture/', include('lecture.urls-web')),
    path('order/', include('order.urls-web')),
    path('teacher/', include('teacher.urls-web')),
    path('trade/', include('trade.urls-web')),
    path('notice/', include('notice.urls-web')),
    path('qna/', include('qna.urls-web')),
    path('report/', include('report.urls-web')),
    path('knowhow/', include('knowhow.urls-web')),
    path('post/', include('post.urls-web')),
    path('cart/', include('cart.urls-web')),
    path('oauth/', include('oauth.urls')),
    path('accounts/', include('allauth.urls')),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)