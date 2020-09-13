# 信息市场

这是一个模拟预测市场交易的网站，用于[李晓明教授](http://eecs.pku.edu.cn/info/1424/7020.htm)在北京大学信息科学技术学院开设的课程《社会与市场中的计算问题选讲》的课程教学，项目作者是[侯太格](https://houtiger.github.io/)。


# 游戏说明
关于本游戏的规则说明，见[这里](./templates/explanation.html). 

# 使用说明
* 依赖
你需要安装`flask`这个python库。
* 运行
在`backend.py`所在目录下，命令行运行`$ python3 backend.py`
* 登陆
把网站运行在一个拥有公网IP的服务器上，学生们直接在浏览器中输入IP即可访问网站。有时默认的80端口被占用，需要调整不同的端口。
* 数据
你需要手动初始化学生的账号、密码，以及管理员密码。这些数据都存储在`./data/user_pwd.txt`和`./data/admin_pwd.txt`之中。
整个运行期间产生的日志数据也全部存储在`./data/`文件夹中。

# 设计思路
本项目详细的设计文档,在[这里](./design.md)。

# Language
If you need an English Version README, see [here](README-EN.md).

# 联系作者
如果你对该项目有任何疑问，欢迎发邮件至houtiger@pku.edu.cn联系作者。