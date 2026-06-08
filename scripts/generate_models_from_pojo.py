#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 Java POJO 和 MyBatis Mapper XML 生成 Django Models
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# 路径配置
POJO_DIR = Path(r"D:\ZWQProject\365\JXPT\jxpt-manage\jxpt-manage-pojo\src\main\java\com\km\jxpt\pojo")
MAPPER_DIR = Path(r"D:\ZWQProject\365\JXPT\jxpt-manage\jxpt-manage-mapper\src\main\java\com\km\jxpt\mapper")
OUTPUT_DIR = Path(r"D:\ZWQProject\365\keming365-backend\apps")

# Java 类型到 Django 字段映射
JAVA_TYPE_MAP = {
    'String': 'models.CharField(max_length=255',
    'Integer': 'models.IntegerField(',
    'Long': 'models.BigIntegerField(',
    'Date': 'models.DateTimeField(',
    'Boolean': 'models.BooleanField(',
    'Double': 'models.FloatField(',
    'Float': 'models.FloatField(',
    'BigDecimal': 'models.DecimalField(max_digits=10, decimal_places=2',
}

# App 分配规则
APP_MODELS = {
    'accounts': ['TbUser', 'Jwtinfo', 'TbMechanicUser'],
    'courses': ['TbCurriculum', 'Chapter', 'TbExperiment', 'TbExperimentReport', 'TbRecordInfo', 
                'Flow', 'Node', 'UserCurriculum', 'UserExperiment', 'SchoolCurriculum', 'SchoolExperiment'],
    'quizzes': ['Question'],
    'scores': ['TbExperimentScore', 'TbExperimentUsetime', 'TbPersonScore', 'TbMechanicUserScore', 
               'TbWeightInfo', 'TbExperimentRecord'],
    'comments': ['TbItemComment'],
    'files': ['Video'],
    'payments': ['Orders', 'Product'],
    'news': ['News'],
    'home': ['TbViewpager', 'TbHot', 'TbIntro', 'TbItemCat'],
    'common': ['TbClassify', 'TbClassInfo', 'TbSchoolInfo', 'Log'],
}

# 表名映射 (POJO class name -> table name)
TABLE_NAME_MAP = {
    'TbUser': 'tb_user',
    'Jwtinfo': 'jwtinfo',
    'TbMechanicUser': 'tb_mechanic_user',
    'TbCurriculum': 'tb_curriculum',
    'Chapter': 'chapter',
    'TbExperiment': 'tb_experiment',
    'TbExperimentReport': 'tb_experiment_report',
    'TbRecordInfo': 'tb_record_info',
    'Flow': 'flow',
    'Node': 'node',
    'UserCurriculum': 'user_curriculum',
    'UserExperiment': 'user_experiment',
    'SchoolCurriculum': 'school_curriculum',
    'SchoolExperiment': 'school_experiment',
    'Question': 'question',
    'TbExperimentScore': 'tb_experiment_score',
    'TbExperimentUsetime': 'tb_experiment_usetime',
    'TbPersonScore': 'tb_person_score',
    'TbMechanicUserScore': 'tb_mechanic_user_score',
    'TbWeightInfo': 'tb_weight_info',
    'TbExperimentRecord': 'tb_experiment_record',
    'TbItemComment': 'tb_item_comment',
    'Video': 'video',
    'Orders': 'orders',
    'Product': 'product',
    'News': 'news',
    'TbViewpager': 'tb_viewpager',
    'TbHot': 'tb_hot',
    'TbIntro': 'tb_intro',
    'TbItemCat': 'tb_item_cat',
    'TbClassify': 'tb_classify',
    'TbClassInfo': 'tb_class_info',
    'TbSchoolInfo': 'tb_school_info',
    'Log': 'log',
}

def parse_pojo_file(filepath):
    """解析 Java POJO 文件，提取字段信息"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    class_name = filepath.stem
    fields = []
    
    # 提取私有字段声明
    # 匹配: private String id;
    field_pattern = r'private\s+(\w+)(?:<[^>]+>)?\s+(\w+)\s*;'
    matches = re.findall(field_pattern, content)
    
    for java_type, field_name in matches:
        # 跳过 Example 和 VM 类
        if 'Example' in class_name or 'VM' in class_name:
            continue
        
        # 转换驼峰为蛇形
        db_column = re.sub(r'(?<!^)(?=[A-Z])', '_', field_name).lower()
        
        # 获取 Django 字段类型
        django_type = JAVA_TYPE_MAP.get(java_type, 'models.CharField(max_length=255')
        
        fields.append({
            'name': field_name,
            'db_column': db_column,
            'java_type': java_type,
            'django_type': django_type,
        })
    
    return class_name, fields

def parse_mapper_xml(filepath, class_name):
    """解析 MyBatis Mapper XML，提取表名和字段映射"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取表名 (从 insert/update/select 语句)
    table_name = None
    table_pattern = r'(?:from|into|update)\s+(\w+)'
    matches = re.findall(table_pattern, content, re.IGNORECASE)
    if matches:
        table_name = matches[0]
    
    # 提取字段映射
    column_map = {}
    # <result column="id" property="id" jdbcType="INTEGER" />
    result_pattern = r'<(?:result|id)\s+column="(\w+)"\s+property="(\w+)"\s+jdbcType="(\w+)"'
    for col, prop, jdbc_type in re.findall(result_pattern, content):
        column_map[prop] = {
            'column': col,
            'jdbc_type': jdbc_type,
        }
    
    return table_name, column_map

def generate_model_code(class_name, fields, table_name, column_map):
    """生成 Django Model 代码"""
    model_name = class_name
    if model_name.startswith('Tb'):
        # TbUser -> User (for model class name)
        pass  # Keep Tb prefix for now, can be renamed later
    
    lines = []
    lines.append(f'class {model_name}(models.Model):')
    lines.append(f'    """')
    lines.append(f'    {class_name} - 对应 Java POJO: com.km.jxpt.pojo.{class_name}')
    lines.append(f'    原表名: {table_name or TABLE_NAME_MAP.get(class_name, "unknown")}')
    lines.append(f'    """')
    
    # 生成字段
    for field in fields:
        field_name = field['name']
        db_column = field['db_column']
        django_type = field['django_type']
        
        # 检查是否有 column 映射
        if field_name in column_map:
            db_column = column_map[field_name]['column']
        
        # 处理主键
        if field_name == 'id':
            if 'Integer' in field['java_type'] or 'Long' in field['java_type']:
                lines.append(f'    {field_name} = models.AutoField(primary_key=True)')
            else:
                lines.append(f'    {field_name} = models.CharField(primary_key=True, max_length=255)')
            continue
        
        # 处理外键 (基于字段名推断)
        if field_name.endswith('Id') and field['java_type'] == 'String':
            # 可能是外键，先作为普通字段
            pass
        
        # 处理可空字段
        null_str = 'null=True, blank=True'
        if field['java_type'] in ['Integer', 'Long', 'Double', 'Float', 'Boolean']:
            null_str = 'null=True, blank=True'
        
        # 构建字段定义
        if django_type.endswith('('):
            field_def = f'{django_type}{null_str})'
        else:
            field_def = f'{django_type}, {null_str})'
        
        # 如果 db_column 与 field_name 不同，添加 db_column
        if db_column != field_name:
            field_def = field_def[:-1] + f", db_column='{db_column}')"
        
        lines.append(f'    {field_name} = {field_def}')
    
    # Meta 类
    lines.append('')
    lines.append('    class Meta:')
    lines.append(f"        managed = False")
    lines.append(f"        db_table = '{table_name or TABLE_NAME_MAP.get(class_name, 'unknown')}'")
    lines.append('')
    
    # __str__ 方法
    lines.append('    def __str__(self):')
    # 尝试找到合适的显示字段
    display_field = 'id'
    for field in fields:
        if field['name'] in ['name', 'title', 'username']:
            display_field = field['name']
            break
    lines.append(f'        return str(self.{display_field})')
    lines.append('')
    
    return '\n'.join(lines)

def main():
    """主函数"""
    # 按 App 分组生成 models
    for app_name, model_classes in APP_MODELS.items():
        models_code = []
        models_code.append('# -*- coding: utf-8 -*-')
        models_code.append('"""')
        models_code.append(f'{app_name.title()} App Models')
        models_code.append('从 Java POJO 逆向生成，对应原 Java 实体类')
        models_code.append('"""')
        models_code.append('')
        models_code.append('from django.db import models')
        models_code.append('')
        
        for class_name in model_classes:
            pojo_file = POJO_DIR / f"{class_name}.java"
            if not pojo_file.exists():
                models_code.append(f'# 注意: {class_name}.java 文件不存在，跳过')
                models_code.append('')
                continue
            
            # 解析 POJO
            _, fields = parse_pojo_file(pojo_file)
            
            # 尝试解析 Mapper XML
            mapper_file = MAPPER_DIR / f"{class_name}Mapper.xml"
            table_name = TABLE_NAME_MAP.get(class_name)
            column_map = {}
            if mapper_file.exists():
                table_name, column_map = parse_mapper_xml(mapper_file, class_name)
                if not table_name:
                    table_name = TABLE_NAME_MAP.get(class_name)
            
            # 生成 Model 代码
            model_code = generate_model_code(class_name, fields, table_name, column_map)
            models_code.append(model_code)
        
        # 写入文件
        output_file = OUTPUT_DIR / app_name / 'models.py'
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(models_code))
        
        print(f"✓ Generated: {output_file}")

if __name__ == '__main__':
    main()
