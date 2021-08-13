# PiZeroW-eink-Clock

#### 介绍
一个由**python**编写，基于**树莓派Zero W**的**水墨屏**天气时钟。本仓库是该项目中**树莓派部分**的主程序，是本项目中最重要的部分

#### 效果图 - 真机

![6925946BCF48F25D47ED4209F10AF77B_20210813](https://gitee.com/xuanzhi33/files/raw/master/files/6925946BCF48F25D47ED4209F10AF77B_20210813.jpg)
![8528615B597D05F8A0D5265AC3AFC413_20210813](https://gitee.com/xuanzhi33/files/raw/master/files/8528615B597D05F8A0D5265AC3AFC413_20210813.jpg)
![48C65EB190F020FDE17DFA644712DE70_20210813](https://gitee.com/xuanzhi33/files/raw/master/files/48C65EB190F020FDE17DFA644712DE70_20210813.jpg)
![79916940D49FBE76391C4795C800533F_20210813](https://gitee.com/xuanzhi33/files/raw/master/files/79916940D49FBE76391C4795C800533F_20210813.jpg)
![4B107544771F757540B6CA4D206ADE77_20210813](https://gitee.com/xuanzhi33/files/raw/master/files/4B107544771F757540B6CA4D206ADE77_20210813.jpg)
![7BDAC8CC7098A358D92DFE8D43F90D69_20210813](https://gitee.com/xuanzhi33/files/raw/master/files/7BDAC8CC7098A358D92DFE8D43F90D69_20210813.jpg)

#### 效果图 - 模拟器

![j23MFY_20210813](https://gitee.com/xuanzhi33/files/raw/master/files/j23MFY_20210813.png)
![6IAEed_20210813](https://gitee.com/xuanzhi33/files/raw/master/files/6IAEed_20210813.png)
![Cvcjgo_20210813](https://gitee.com/xuanzhi33/files/raw/master/files/Cvcjgo_20210813.png)
![pYd0DK_20210813](https://gitee.com/xuanzhi33/files/raw/master/files/pYd0DK_20210813.png)
![z1BBhR_20210813](https://gitee.com/xuanzhi33/files/raw/master/files/z1BBhR_20210813.png)
![rLX2zk_20210813](https://gitee.com/xuanzhi33/files/raw/master/files/rLX2zk_20210813.png)

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

