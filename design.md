# 项目设计
整个项目可以分为前端页面`html + JavaScript`，后端算法`python3`，以及数据存储`txt`三大部分。
## 前端页面
前端页面都存储在`./templates/`文件夹下。
* 管理员界面 
    * 登陆
        `./templates/admin_index.html`
        用于管理员登陆
    * 管理员主界面
        `./templates/admin_main_page.html`
        * 查看持仓
        * 删除订单
        * 查看历史成交记录（最新成交在最上方）
        * 查看市场价格
* 用户界面
    * 登陆 
        `./templates/index.html` 
    * 主界面 
        `./templates/main_page.html`
        用户的主要操作都在这个界面
        * 查看市场价格
        * 查看自己持仓
        * 查看自己的订单
        * 查看当前所有订单
            * 刷新订单

    * 删除订单 
        `./templates/user_delete_order.html`
    * 修改密码 
        `./templates/user_change_pwd.html` 
    * 查看自己的成交记录 
        `./templates/user_trade_history`
* 说明界面 
    * `./templates/explanation.html`
        关于这个游戏的规则说明，都写在这里了。
## 数据
所有数据都存储在`./data/`文件夹中
* 静态数据
    * 管理员权限密码，用于查看持仓和删除订单`admin_pwd.txt`
* 动态数据
    * 用户名和密码 
        * `user_pwd.txt`   
        * 由管理员随机生成，允许用户修改
    * 当前全部买入订单 
        * `buy_order.txt`
    * 当前全部卖出订单 
        * `sell_order.txt`
    * 当前用户持仓情况
        * `user_holding.txt`
    * 当前全部市场价格支撑订单
        * `price_order.txt`
    * 订单编号计数器  
        赋予订单编号，从0开始
        `order_cnt.txt`
* 历史记录
    * 买卖订单的历史记录  
        分成两个文件`buy_order_history.txt`，`sell_order_history.txt`，每次有订单变动则刷新一次
    * 市场价格的历史记录  
        每次价格发生变动，则记录新的价格支撑订单，记录在文件`price_order_history.txt`中
    * 用户持仓的历史记录
        每次有持仓变动则刷新一次，记录在`user_holding_history.txt`中
    * 成交订单记录
        每次有订单成交则记录一条，记录在`trade_order_history.txt`中  




## 后端
后端的流程部分定义在`backend.py`中，而各个函数的实现在`func_def.py`和`init.py`中。
* 初始化
    写在`init.py`中
    ```python
    def init_all()
    ```
    * 读入管理员权限密码
    * 读入用户名和密码
    * 读入现有买入订单
    * 读入现有卖出订单
    * 读入用户持仓
    * 读入当前市场价格支撑订单以及市场价格
    * 读入订单编号计数器
* 运行中
    在`backend.py`和`func_def.py`中
    * 登陆验证
        * 参数：用户名，密码
        * 返回值：0，1
    * 修改密码
        ```python
        def change_pwd()
        ```
        * 参数：用户名，用户密码，新密码
        * 内容：
            修改内存中的用户密码  
            修改用户密码文件
        * 返回值：
            0，代表用户名或密码出错
            1，代表修改成功
    * 删除订单 
        ```python
        def handle_delete_order_request()
        ```
        * 参数：用户名，用户密码，订单编号，
        * 内容：
            删除内存中的订单，把钱或股票还给用户  
            更新对应的当前订单文件  
            写入历史订单记录
        * 返回值：
            0，代表出错  
            1，代表成功

    * 处理提交的订单
        ```python
        def handle_order_submit()
        ```
        * 参数：用户名，用户密码，订单类型，股票编号，每股单价，总股数，用户编号
        * 内容：
            * 根据订单类型检查用户当前股票或金钱是否满足条件
            * 赋予订单编号
            * 区分买卖
                * 买入的话
                    把卖出订单按照单价从低到高排序
                    每成交一个，记录一条成交记录  
                    把卖出订单的股票给买方  
                    把买方订单的钱给卖方  
                    将内存中的变化更新到文件中
                * 卖出的话流程类似
            * 更新相关的动态数据和历史记录
        * 返回值：新的`main_page.html`页面
    * 更新记录
    ```python
        def write_user_holding()
        def write_user_holding_history()
        def write_sell_order()
        def write_sell_order_history()
        def write_buy_order()
        def write_buy_order_history()
        ```
        将内存中的各项值更新到文件中  
        更新买卖订单  
        市场价格及支撑订单
        用户持仓
### 订单设计
订单类(class)定义在`order_def.py`文件中。
* 股票单位为整数，价格也为整数
* 订单是一个实体，每下一个订单，如买入订单就要扣走相应的金钱，如卖出订单就要扣走相应的股票
* 订单类组成
    * 订单编号
    * 订单类型：买入 or 卖出
    * 股票编号
    * 总股数
    * 每股单价
    * 总价值
    * 用户编号
### 用户持仓设计
用户的持仓情况设计为一个类（class），定义在`holding_def.py`中
* 用户持仓组成
    * 用户编号
    * 用户金钱
    * 用户在各日持股

