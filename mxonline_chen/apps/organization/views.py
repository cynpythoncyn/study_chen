from django.shortcuts import render

# Create your views here.
from django.views.generic.base import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse

from .models import CourseOrg, CityDict
from .forms import UserAskForm
from operation.models import UserFavorite


class AddfavView(View):
    """
    用户收藏,用户取消收藏
    """

    def post(self, request):
        fav_id = request.POST.get('fav_id', 0)
        fav_type = request.POST.get('fav_type', 0)

        if not request.user.is_authenticated():
            return JsonResponse({'status': 'fail', 'msg': '用户未登陆'})
        exist_records = UserFavorite.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
        if exist_records:
            # 如果记录存在，则表示用户取消收藏
            exist_records.delete()
            return JsonResponse({'status': 'success', 'msg': '收藏'})
        else:
            user_fav = UserFavorite()
            if int(fav_type) > 0 and int(fav_id) > 0:
                user_fav.user = request.user
                user_fav.fav_type = int(fav_type)
                user_fav.fav_id = int(fav_id)
                user_fav.save()
                return JsonResponse({'status': 'success', 'msg': '已收藏'})
            else:
                return JsonResponse({'status': 'fail', 'msg': '收藏出错'})


class Org_teacherView(View):
    """
    机构教师介绍
    """

    def get(self, request, org_id):
        current_page = "teacher"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            exist_records = UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2)
            if exist_records:
                has_fav = True
        all_teachers = course_org.teacher_set.all()

        return render(request, 'org-detail-teachers.html', {
            'current_page': current_page,
            'course_org': course_org,
            'all_teachers': all_teachers,
            'has_fav': has_fav,
        })


class Org_descView(View):
    """
    机构介绍
    """

    def get(self, request, org_id):
        current_page = "desc"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            exist_records = UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2)
            if exist_records:
                has_fav = True
        return render(request, 'org-detail-desc.html', {
            "course_org": course_org,
            "current_page": current_page,
            "has_fav": has_fav,

        })


class Org_courseView(View):
    """
    机构课程详情页
    """

    def get(self, request, org_id):
        current_page = "course"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            exist_records = UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2)
            if exist_records:
                has_fav = True

        all_courses = course_org.course_set.all()
        return render(request, 'org-detail-course.html', {
            'course_org': course_org,
            'all_courses': all_courses,
            'current_page': current_page,
            'has_fav': has_fav,

        })


class Org_homeView(View):
    """
    机构首页
    """

    def get(self, request, org_id):
        current_page = "home"
        course_org = CourseOrg.objects.get(id=int(org_id))

        has_fav = False
        if request.user.is_authenticated():
            exist_records = UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2)
            if exist_records:
                has_fav = True
        all_courses = course_org.course_set.all()[:3]
        all_teachers = course_org.teacher_set.all()[:1]

        return render(request, 'org-detail-homepage.html', {
            'all_courses': all_courses,
            'all_teachers': all_teachers,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class UseraskView(View):
    """
    添加用户咨询接口
    """

    def post(self, request):
        user_ask_form = UserAskForm(request.POST)
        if user_ask_form.is_valid():
            user_ask = user_ask_form.save(commit=True)
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'fail', 'msg': '添加出错！666chen'})


class OrglistView(View):
    """
    课程机构列表接口
    """

    def get(self, request):
        # 课程机构
        all_orgs = CourseOrg.objects.all()
        # 热门机构
        hot_orgs = all_orgs.order_by("-click_nums")[:3]
        # 城市
        all_citys = CityDict.objects.all()

        # 取出筛选城市
        city_id = request.GET.get('city', '')
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))

        # 机构分类
        category = request.GET.get('category', '')
        if category:
            all_orgs = all_orgs.filter(category=category)

        # 排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':

                all_orgs = all_orgs.order_by(sort="-students")
            elif sort == 'cousors':
                all_orgs = all_orgs.order_by(sort="-course_nums")

        # 机构数量
        org_nums = CourseOrg.objects.count()

        # 对课程机构进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_orgs, 5, request=request)

        orgs_c = p.page(page)

        return render(request, 'org-list.html', {
            "all_orgs": orgs_c,
            "all_citys": all_citys,
            "org_nums": org_nums,
            "category": category,
            "city_id": city_id,
            "sort": sort,
            "hot_orgs": hot_orgs,

        })
