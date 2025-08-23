# Release Guide

本指南说明如何发布 MODSDKSpring 的新版本。

## 自动化发布流程

项目已配置 GitHub Actions 自动化 CI/CD 流程，包括：

- **持续集成 (CI)**: 每次推送代码时自动构建和测试
- **自动发布**: 创建版本标签时自动发布到 PyPI 和 GitHub Release
- **包构建**: 自动构建 Python wheel 和源码包

## 发布新版本

### 方法 1: 使用发布脚本（推荐）

```bash
# 发布新版本（例如 1.0.1）
python scripts/release.py --version 1.0.1

# 预览模式（不实际执行）
python scripts/release.py --version 1.0.1 --dry-run
```

脚本将自动：
1. 验证版本格式
2. 更新 `setup.py` 中的版本号
3. 提交并推送版本变更
4. 创建并推送 git 标签
5. 触发 GitHub Actions 自动发布

### 方法 2: 手动发布

1. **更新版本号**
   ```bash
   # 编辑 setup.py，修改 version 字段
   vim setup.py
   ```

2. **提交版本变更**
   ```bash
   git add setup.py
   git commit -m "Bump version to 1.0.1"
   git push
   ```

3. **创建版本标签**
   ```bash
   # 创建标签
   git tag -a v1.0.1 -m "Release 1.0.1"
   
   # 推送标签到远程仓库
   git push origin v1.0.1
   ```

## 自动化流程说明

当推送版本标签（格式：`v*`）时，GitHub Actions 将：

### 1. 构建和测试 (`test` job)
- 使用 Python 2.7 环境
- 安装依赖并构建包
- 上传构建产物

### 2. 发布到 PyPI (`publish` job)
- 自动下载构建产物
- 使用 Trusted Publishers 认证发布到 PyPI
- 需要在 PyPI 中配置 Trusted Publishers

### 3. 创建 GitHub Release (`release` job)
- 创建 GitHub Release
- 附加构建的包文件
- 自动生成 Release Notes

## PyPI 配置要求

为了自动发布到 PyPI，需要配置 Trusted Publishers：

1. 访问 [PyPI 项目管理页面](https://pypi.org/manage/project/mc-creatormc-sdkspring/)
2. 进入 "Publishing" 选项卡
3. 添加 Trusted Publisher：
   - **Owner**: `CreatorMC`
   - **Repository**: `MODSDKSping`
   - **Workflow**: `ci.yml`
   - **Environment**: `pypi`

## 版本规范

使用[语义化版本](https://semver.org/lang/zh-CN/)规范：

- **主版本号**：不兼容的 API 修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

示例：
- `1.0.0` - 首个稳定版本
- `1.0.1` - 修复问题
- `1.1.0` - 新增功能
- `2.0.0` - 不兼容的重大更新

## 故障排除

### 发布失败
- 检查 GitHub Actions 日志
- 确认 PyPI Trusted Publishers 配置正确
- 验证版本号格式是否正确

### 权限问题
- 确保有仓库的 push 权限
- 确认 GitHub Actions 有必要的权限

### 构建错误
- 检查 Python 2.7 兼容性
- 确认 setup.py 配置正确

## 发布清单

发布前请确认：

- [ ] 代码已合并到 main 分支
- [ ] 测试通过
- [ ] 文档已更新
- [ ] CHANGELOG 已更新
- [ ] 版本号符合语义化版本规范
- [ ] PyPI Trusted Publishers 已配置