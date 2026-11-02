# 新仓库说明

仓库名称：`embedded-vision-camera-notes`。账号：`wly63227`。可见性：按用户选择公开。

本地沿用已有 Git 工作区，在原有通用嵌入式内容上增加面向相机项目的主线。原 `docs/`、`obsidian/`、可移植 C 示例与许可证保留；`README-general.md` 是原课程入口。没有修改 convex 仓库。

首次发布前运行 Python 测试、C 应用测试、文档链接检查，再执行 `python tools/build_camera_book.py`。本次通过 GitHub 浏览器会话新建仓库、连接器提交文本源码。依赖缓存、虚拟环境、个人照片、私密日志、`.git` 和构建产物不上传。当前只发布学习资料与源码，没有把 GitHub Pages 网站部署作为已完成事项。

后续用 Git CLI 时可正常 clone 新仓库，再按课程命令运行；不需要复制本机 `build/qa-python`。不覆盖同名已有仓库，也不对历史执行强制推送。
