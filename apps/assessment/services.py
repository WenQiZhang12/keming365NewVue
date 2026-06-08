# -*- coding: utf-8 -*-
"""
Assessment App - 业务逻辑层
提供给第三方考试系统的数据查询接口
"""

from apps.accounts.models import TbUser
from apps.courses.models import TbExperiment, TbCurriculum
from apps.common.models import TbClassify
from django.db import connection


class AssessmentService:
    """对应 Java AssessmentServiceImpl"""

    @staticmethod
    def get_class_info(user_id: str) -> dict:
        """
        获取用户的班级信息和实验列表
        对应 Java: getClassInfo
        """
        class_ids = []
        experiment_ids = []

        try:
            user = TbUser.objects.get(pk=user_id)
            if user.type == 1:  # 教师
                with connection.cursor() as cur:
                    cur.execute(
                        "SELECT id FROM tb_class_info WHERE teacher_id=%s AND type!=%s",
                        [user_id, '0']
                    )
                    class_ids = [r[0] for r in cur.fetchall()]
            else:  # 学生
                if user.classId:
                    class_ids = [user.classId]

            # 获取学校授权课程下的实验
            with connection.cursor() as cur:
                cur.execute(
                    "SELECT curriculum_id FROM school_curriculum WHERE school_id=%s",
                    ['1']  # 对应 Java 中硬编码的 schoolId = "1"
                )
                curriculum_ids = [r[0] for r in cur.fetchall()]
                if curriculum_ids:
                    placeholders = ','.join(['%s'] * len(curriculum_ids))
                    cur.execute(
                        f"SELECT id FROM tb_experiment WHERE parent_id IN ({placeholders})",
                        curriculum_ids
                    )
                    experiment_ids = [r[0] for r in cur.fetchall()]
        except TbUser.DoesNotExist:
            pass

        return {
            'ClassID': class_ids,
            'CourseID': experiment_ids,
        }

    @staticmethod
    def site_member(user_id: str) -> TbUser:
        """获取用户信息（对应 Java siteMember）"""
        try:
            return TbUser.objects.get(pk=user_id)
        except TbUser.DoesNotExist:
            return None

    @staticmethod
    def site_class(class_id: str) -> dict:
        """获取班级信息（对应 Java siteClass）"""
        with connection.cursor() as cur:
            cur.execute(
                "SELECT id, class_card, school_id, teacher_id, type FROM tb_class_info WHERE id=%s AND type!=%s",
                [class_id, '0']
            )
            row = cur.fetchone()
            if row:
                return {'id': row[0], 'name': row[1], 'classCard': row[1],
                        'schoolId': row[2], 'teacherId': row[3], 'type': row[4]}
        return None

    @staticmethod
    def site_course(course_id: str) -> TbCurriculum:
        """获取课程信息（对应 Java siteCourse）"""
        try:
            return TbCurriculum.objects.get(pk=course_id)
        except TbCurriculum.DoesNotExist:
            return None

    @staticmethod
    def site_section(experiment_id: str) -> TbExperiment:
        """获取实验信息（对应 Java siteSection）"""
        try:
            return TbExperiment.objects.get(pk=experiment_id)
        except TbExperiment.DoesNotExist:
            return None

    @staticmethod
    def course_index(classify_id: str, user_or_class_id: str, flag: int) -> list:
        """
        获取分类下的课程列表
        flag=1: 通过 userId 查学校; flag=2: 通过 classId 查学校
        对应 Java: CourseIndex
        """
        school_id = None
        if flag == 1:  # member
            try:
                user = TbUser.objects.get(pk=user_or_class_id)
                school_id = user.schoolId
            except TbUser.DoesNotExist:
                pass
        else:  # class
            with connection.cursor() as cur:
                cur.execute(
                    "SELECT school_id FROM tb_class_info WHERE id=%s",
                    [user_or_class_id]
                )
                row = cur.fetchone()
                if row:
                    school_id = row[0]

        if not school_id:
            return []

        with connection.cursor() as cur:
            cur.execute(
                "SELECT curriculum_id FROM school_curriculum WHERE classify_id=%s AND school_id=%s",
                [classify_id, school_id]
            )
            curriculum_ids = [r[0] for r in cur.fetchall()]

        results = []
        for cid in curriculum_ids:
            try:
                course = TbCurriculum.objects.get(pk=cid)
                if course.curriculumName:
                    results.append({
                        'id': course.id,
                        'name': course.curriculumName,
                        'curriculumName': course.curriculumName,
                    })
            except TbCurriculum.DoesNotExist:
                pass
        return results

    @staticmethod
    def class_index(member_id: str) -> list:
        """
        获取用户所属班级列表
        对应 Java: ClassIndex
        """
        try:
            user = TbUser.objects.get(pk=member_id)
        except TbUser.DoesNotExist:
            return []

        if user.type == 1:  # 教师
            with connection.cursor() as cur:
                cur.execute(
                    "SELECT id, class_card, school_id, teacher_id, type, create_time, update_time FROM tb_class_info WHERE teacher_id=%s AND type!=%s ORDER BY create_time",
                    [member_id, '0']
                )
                rows = cur.fetchall()
                results = []
                for r in rows:
                    results.append({
                        'id': r[0],
                        'name': r[1],
                        'classCard': r[1],
                        'schoolId': r[2],
                        'teacherId': r[3],
                        'type': r[4],
                        'createTime': str(r[5]) if r[5] else None,
                        'updateTime': str(r[6]) if r[6] else None,
                    })
                return results
        else:  # 学生
            if not user.classId:
                return []
            with connection.cursor() as cur:
                cur.execute(
                    "SELECT id, class_card, school_id, teacher_id, type, create_time, update_time FROM tb_class_info WHERE id=%s AND type!=%s",
                    [user.classId, '0']
                )
                row = cur.fetchone()
                if row:
                    return [{
                        'id': row[0],
                        'name': row[1],
                        'classCard': row[1],
                        'schoolId': row[2],
                        'teacherId': row[3],
                        'type': row[4],
                        'createTime': str(row[5]) if row[5] else None,
                        'updateTime': str(row[6]) if row[6] else None,
                    }]
            return []

    @staticmethod
    def section_index(course_id: str) -> list:
        """
        获取课程下的实验列表
        对应 Java: SectionIndex
        """
        with connection.cursor() as cur:
            cur.execute(
                "SELECT id, title, price, image, type, appli_id, parent_id FROM tb_experiment WHERE parent_id=%s",
                [course_id]
            )
            rows = cur.fetchall()
            results = []
            for r in rows:
                if r[1]:  # title 不为空
                    results.append({
                        'id': r[0],
                        'name': r[1],
                        'title': r[1],
                        'price': str(r[2]) if r[2] else '0',
                        'image': r[3] or '',
                        'type': r[4],
                        'appliId': r[5] or '',
                        'parentId': r[6] or '',
                    })
            return results

    @staticmethod
    def major_info(classify_id: str) -> dict:
        """获取分类信息（对应 Java MajorInfo）"""
        try:
            c = TbClassify.objects.get(pk=classify_id)
            return {'id': c.id, 'name': c.className or c.name or ''}
        except TbClassify.DoesNotExist:
            return None

    @staticmethod
    def classify_index(member_id: str) -> list:
        """
        获取用户可访问的分类列表（通过学校授权）
        对应 Java: ClassifyIndex
        """
        try:
            user = TbUser.objects.get(pk=member_id)
            school_id = user.schoolId or '1'
        except TbUser.DoesNotExist:
            school_id = '1'

        with connection.cursor() as cur:
            cur.execute(
                "SELECT DISTINCT classify_id FROM school_curriculum WHERE school_id=%s AND classify_id IS NOT NULL",
                [school_id]
            )
            classify_ids = [r[0] for r in cur.fetchall()]

        results = []
        for cid in classify_ids:
            try:
                c = TbClassify.objects.get(pk=cid)
                if c.className:
                    results.append({
                        'id': c.id,
                        'name': c.className,
                        'className': c.className,
                    })
            except TbClassify.DoesNotExist:
                pass
        return results
