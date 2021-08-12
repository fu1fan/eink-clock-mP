# PiZeroW-eink-Clock

#### 介绍
一个由**python**编写，基于**树莓派Zero W**的**水墨屏**天气时钟。本仓库是该项目中**树莓派部分**的主程序，是本项目中最重要的部分

#### 主要目录架构

├── `main.py`                 主程序<br>
├── `updater.py`              更新程序<br>
├── `modules`                 模块<br>
│   ├── `theme`               主题文件夹<br>
│   ├── `apps`                应用文件夹<br>
│   ├── `plugins`             插件文件夹<br>
│   ├── `wheels`              轮子文件夹<br>
├── `resources`               资源文件夹<br>
│   ├── `images`              图片文件夹<br>
│   └── `fonts`               字体文件夹<br>
└── `sdk`                     sdk文件夹<br>


#### 安装教程

##### 如果有树莓派Zero W和微雪水墨屏

1.  ssh连接树莓派
2.  clone本仓库的`master`分支
3.  运行：`python3 main.py`

##### 如果没有相关硬件，仍想体验或开发

1. clone本仓库的`develop`分支

2. 运行`python3 main.py`，这时候就可以通过由 @[xuanzhi33](https://gitee.com/xuanzhi33) 开发的**水墨屏模拟器**进行体验和调试

#### 使用说明

运行后点击屏幕上方即可唤起Docker栏，这时候就可以进入应用列表或系统设置了



#### 开发文档

正在努力编写中，如果你想开发应用，可以参考一下hello_world应用



#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request

