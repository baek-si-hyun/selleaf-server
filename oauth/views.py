from allauth.socialaccount.models import SocialAccount
from django.views import View
from django.shortcuts import render, redirect

from member.models import Member, MemberProfile
from member.serializers import MemberSerializer


class OAuthLoginView(View):
    def get(self, request):
        # 소셜 로그인 로직
        user = SocialAccount.objects.get(user=request.user)
        # 소셜 로그인 플랫폼에서 유저의 정보를 가져오는 로직
        oauth_data = user.extra_data
        # 소셜 로그인 했을 시 어느 플랫폼을 이용했는지 확인
        member_type = user.provider
        # 카카오는 데이터 형식이 달라서 별도로 로직 구성
        if member_type == "kakao":
            member_email = oauth_data.get("kakao_account").get("email")
            member_name = oauth_data.get("properties").get("nickname")
            member_profile = oauth_data.get("properties").get("profile_image")
        else:
            member_email = oauth_data.get("email")
            member_name = oauth_data.get("name")
            member_profile = oauth_data.get("picture")
        # 이미 가입이 되어있는 사용자인지 확인
        member_data = {
            'member_email': member_email,
            'member_type': member_type
        }
        is_member = Member.objects.filter(**member_data)

        path = '/'
        # 만약 가입하지 않은 사용자라면 회원가입으로 이동
        # redirect에서 데이터를 전달하기 위해서는 쿼리스트링으로 전달하거나 세션을 이용해야한다.
        if not is_member.exists():
            path = f'/member/join?member_email={member_email}&member_name={member_name}&member_profile={member_profile}&member_type={member_type}'
        # 이미 회원가입이 완료된 회원이라면 메인화면으로 이동
        else:
            member = is_member.first()
            # 사용자의 정보를 세션에 저장
            # serializer로 직렬화 한다.
            request.session['member'] = MemberSerializer(member).data
            print(request.session['member'])
            # 역참조를 통해 사용자 프로필을 가져온다.
            member_files = list(member.memberprofile_set.values('file_url'))
            # 사용자의 프로필 데이터가 존재하면 세션에 넣는다.
            if len(member_files) != 0:
                request.session['member_files'] = member_files

            previous_uri = request.session.get('previous_uri')

            if previous_uri is not None:
                path = previous_uri
                del request.session['previous_uri']

        return redirect(path)
