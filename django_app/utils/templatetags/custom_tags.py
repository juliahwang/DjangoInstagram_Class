from django import template

# 선언해줘야한다 - 문서 참고
register = template.Library()


# 커스텀 필터 만들기 - '?page=' 패턴으로 url빌드
# 해당 필터는 페이지번호를 next 파라미터와 함께 보내 1번째 페이지가 아닌 다음 페이지에서도 댓글을 달고 그 페이지에 머물러있도록
# 하기 위해서 '?page='패턴값을 돌려주는 filter를 직접 정의해준다.
@register.filter
def query_string(q):
    # q에는 QueryDict가 온다
    # key:list 형태로 전달받기 때문에 list내 value값들을 순회하며 패턴을 만들어나가야한다.
    # 이 때 QueryDict의 내장 메서드인 lists()를 사용한다
    # lists()는 쿼리딕셔너리의 list형 value값을 하나씩 꺼내서 모두 출력해준다.
    # items()로 하면 리스트의 마지막값만 패턴으로 만들어져 출력된다.
    # 아래 코드를 리스트컴프리헨션으로 줄여보기
    return '?' + '&'.join(['{}={}'.format(k, v) for k, v_list in q.lists() for v in v_list])
    # ret = '?'
    # for k, v_list in q.lists():
    #     for v in v_list:
    #         ret += '&{}={}'.format(k, v)
    #     return ret
