# -*- coding: utf-8 -*-
import os
import json
import shutil
from ..config.project_config import ProjectConfig, ManifestConfig
from ..utils.uuid_utils import generate_uuid, generate_random_string
from ..utils.file_utils import makedirs_compat, copytree_compat
from .template_engine import TemplateEngine


class ProjectGenerator:
    """项目生成器 - 替代原来的巨型函数"""
    
    def __init__(self, package_path):
        self.package_path = package_path
        self.templates_path = os.path.join(package_path, "templates")
    
    def create_project(self, mod_name, target_dir=None):
        """创建新项目"""
        if target_dir is None:
            target_dir = os.getcwd()
            
        config = ProjectConfig(mod_name)
        project_path = os.path.join(target_dir, config.mod_dir_name)
        
        # 生成UUIDs
        behavior_pack_uuid = generate_uuid()
        behavior_module_uuid = generate_uuid()
        resource_pack_uuid = generate_uuid()
        resource_module_uuid = generate_uuid()
        
        # 生成随机文件夹名
        behavior_folder = "behavior_pack_{}".format(generate_random_string(8))
        resource_folder = "resource_pack_{}".format(generate_random_string(8))
        
        project_info = ProjectInfo(
            config=config,
            behavior_pack_uuid=behavior_pack_uuid,
            behavior_module_uuid=behavior_module_uuid,
            resource_pack_uuid=resource_pack_uuid,
            resource_module_uuid=resource_module_uuid,
            behavior_folder=behavior_folder,
            resource_folder=resource_folder,
            project_path=project_path
        )
        
        self._create_directory_structure(project_info)
        self._create_manifest_files(project_info)
        self._create_config_files(project_info)
        self._copy_project_templates(project_info)
        self._copy_framework_templates(project_info)
        
        return project_info
    
    def _create_directory_structure(self, info):
        """创建目录结构"""
        behavior_path = os.path.join(info.project_path, info.behavior_folder)
        resource_path = os.path.join(info.project_path, info.resource_folder)
        
        makedirs_compat(behavior_path)
        makedirs_compat(os.path.join(behavior_path, "entities"))
        makedirs_compat(resource_path)
        makedirs_compat(os.path.join(resource_path, "textures"))
        
        # 创建 .gitkeep 文件
        self._create_gitkeep(os.path.join(behavior_path, "entities"))
        self._create_gitkeep(os.path.join(resource_path, "textures"))
    
    def _create_gitkeep(self, directory):
        """创建.gitkeep文件"""
        gitkeep_path = os.path.join(directory, ".gitkeep")
        with open(gitkeep_path, 'w') as f:
            f.write("")
    
    def _create_manifest_files(self, info):
        """创建manifest文件"""
        behavior_manifest = ManifestConfig(
            info.behavior_pack_uuid, 
            info.behavior_module_uuid,
"{} Behavior Pack".format(info.config.mod_name)
        )
        
        resource_manifest = ManifestConfig(
            info.resource_pack_uuid,
            info.resource_module_uuid, 
"{} Resource Pack".format(info.config.mod_name)
        )
        
        behavior_path = os.path.join(info.project_path, info.behavior_folder, "manifest.json")
        resource_path = os.path.join(info.project_path, info.resource_folder, "manifest.json")
        
        with open(behavior_path, 'w') as f:
            json.dump(behavior_manifest.to_dict(), f, indent=2)
            
        with open(resource_path, 'w') as f:
            json.dump(resource_manifest.to_dict(), f, indent=2)
    
    def _create_config_files(self, info):
        """创建配置文件"""
        # world_behavior_packs.json
        behavior_config = [{
            "pack_id": info.behavior_pack_uuid,
            "type": "Addon",
            "version": [0, 0, 1]
        }]
        
        # world_resource_packs.json
        resource_config = [{
            "pack_id": info.resource_pack_uuid,
            "type": "Addon",
            "version": [0, 0, 1]
        }]
        
        # studio.json
        studio_config = {
            "EditName": info.config.mod_name,
            "NameSpace": info.config.mod_name
        }
        
        with open(os.path.join(info.project_path, "world_behavior_packs.json"), 'w') as f:
            json.dump(behavior_config, f, indent=4)
            
        with open(os.path.join(info.project_path, "world_resource_packs.json"), 'w') as f:
            json.dump(resource_config, f, indent=4)
            
        with open(os.path.join(info.project_path, "studio.json"), 'w') as f:
            json.dump(studio_config, f, indent=2)
    
    def _copy_project_templates(self, info):
        """复制项目模板"""
        scripts_path = os.path.join(info.project_path, info.behavior_folder, info.config.scripts_folder)
        project_template_path = os.path.join(self.templates_path, "project", "template")
        
        if os.path.exists(project_template_path):
            TemplateEngine.render_directory(
                project_template_path,
                scripts_path,
                info.config.get_template_vars(),
                exclude_patterns=[r"manifest_.*\.json"]
            )
        
        # 创建系统目录
        client_dir = os.path.join(scripts_path, "ClientSystem")
        server_dir = os.path.join(scripts_path, "ServerSystem")
        makedirs_compat(client_dir)
        makedirs_compat(server_dir)
        
        # 创建 __init__.py
        for system_dir in [client_dir, server_dir]:
            with open(os.path.join(system_dir, "__init__.py"), 'w') as f:
                f.write("")
    
    def _copy_framework_templates(self, info):
        """复制框架模板"""
        scripts_path = os.path.join(info.project_path, info.behavior_folder, info.config.scripts_folder)
        plugins_path = os.path.join(scripts_path, "plugins")
        core_template_path = os.path.join(self.templates_path, "core", "plugins")
        
        if os.path.exists(core_template_path):
            copytree_compat(core_template_path, plugins_path)


class ProjectInfo:
    """项目信息类"""
    
    def __init__(self, config, behavior_pack_uuid, behavior_module_uuid, 
                 resource_pack_uuid, resource_module_uuid, behavior_folder, 
                 resource_folder, project_path):
        self.config = config
        self.behavior_pack_uuid = behavior_pack_uuid
        self.behavior_module_uuid = behavior_module_uuid
        self.resource_pack_uuid = resource_pack_uuid
        self.resource_module_uuid = resource_module_uuid
        self.behavior_folder = behavior_folder
        self.resource_folder = resource_folder
        self.project_path = project_path
    
    def print_summary(self):
        """打印项目信息摘要"""
        print("Generated project information:")
        print("   Mod Name: {}".format(self.config.mod_name))
        print("   Client System: {}".format(self.config.client_system_name))
        print("   Server System: {}".format(self.config.server_system_name))
        print("   Scripts Folder: {}".format(self.config.scripts_folder))
        print("   Behavior Pack: {}".format(self.behavior_folder))
        print("   Resource Pack: {}".format(self.resource_folder))
        print("Generated UUIDs:")
        print("   Behavior Pack Header: {}".format(self.behavior_pack_uuid))
        print("   Behavior Pack Module: {}".format(self.behavior_module_uuid))
        print("   Resource Pack Header: {}".format(self.resource_pack_uuid))
        print("   Resource Pack Module: {}".format(self.resource_module_uuid))