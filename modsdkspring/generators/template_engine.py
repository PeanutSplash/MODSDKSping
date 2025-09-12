# -*- coding: utf-8 -*-
import os
import re
from ..utils.file_utils import makedirs_compat


class TemplateEngine:
    """简单的模板引擎 - 替代原始的字符串替换"""
    
    @staticmethod
    def render_file(template_path, output_path, variables):
        """渲染单个文件模板"""
        if not os.path.exists(template_path):
            raise FileNotFoundError("Template file not found: {}".format(template_path))
            
        with open(template_path, 'r') as f:
            content = f.read()
        
        rendered_content = TemplateEngine.render_string(content, variables)
        
        makedirs_compat(os.path.dirname(output_path))
        with open(output_path, 'w') as f:
            f.write(rendered_content)
    
    @staticmethod
    def render_string(template_string, variables):
        """渲染字符串模板"""
        if not template_string:
            return ""
            
        result = template_string
        for key, value in variables.items():
            # 使用 [KEY] 格式的占位符替换
            placeholder = "[{}]".format(key)
            result = result.replace(placeholder, str(value))
        
        return result
    
    @staticmethod
    def render_directory(template_dir, output_dir, variables, exclude_patterns=None):
        """递归渲染整个目录"""
        if not os.path.exists(template_dir):
            raise FileNotFoundError("Template directory not found: {}".format(template_dir))
        
        exclude_patterns = exclude_patterns or []
        
        for root, dirs, files in os.walk(template_dir):
            # 计算相对路径
            rel_path = os.path.relpath(root, template_dir)
            if rel_path == ".":
                target_dir = output_dir
            else:
                target_dir = os.path.join(output_dir, rel_path)
            
            # 创建目标目录
            makedirs_compat(target_dir)
            
            # 处理文件
            for file in files:
                if TemplateEngine._should_exclude(file, exclude_patterns):
                    continue
                
                template_file = os.path.join(root, file)
                target_file = os.path.join(target_dir, file)
                
                TemplateEngine.render_file(template_file, target_file, variables)
    
    @staticmethod
    def _should_exclude(filename, patterns):
        """检查文件是否应该被排除"""
        for pattern in patterns:
            if re.match(pattern, filename):
                return True
        return False