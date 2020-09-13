from flask import Flask, session, request, render_template, redirect
import time
import order_def
import holding_def
import init
import math
import func_def
myWeb = Flask(__name__)

trade_board_length = 60 # 交易面板容纳的最大订单数量
price_queue_length = 4 # 价格队列的长度
order_limit = 6 # 单个用户订单上限
# 运行中
admin_pwd, user_pwd, buy_order, sell_order, user_holding, price_order, market_price, order_cnt = init.init_all()

# 主页
@myWeb.route("/")
def root():
    return render_template("index.html", MSG="请登录")


# 用户登陆，成功则返回main_page.html，否则返回index.html
@myWeb.route("/login", methods=["post", "get"])
def login():
    # print(request.method, type(request.method))
    if request.method == "GET":
        return render_template("index.html", MSG="请登录")

    username = request.form['username']
    password = request.form['password']
    flag = func_def.check_user_pwd(user_pwd, username, password)
    if flag == 1:
        return render_template("main_page.html", username=username, pwd=password)
    else:
        return render_template("index.html", MSG="用户名或密码错误")


# 返回市场价格表格
@myWeb.route("/request_market_price_form", methods=["post"])
def request_market_price_form():
    return func_def.form_market_price(market_price)


# 返回单个用户持仓
@myWeb.route("/request_a_user_holding", methods=["post"])
def request_a_user_holding():
    username = request.form['username']
    password = request.form['password']
    check = func_def.check_user_pwd(user_pwd, username, password)
    if check == 0:
        return ''
    s = func_def.form_a_user_holding(user_holding, username)
    return s


# 返回单个用户的全部订单
@myWeb.route("/request_a_user_order", methods=["post"])
def request_a_user_order():
    username = request.form['_usr']
    password = request.form['_pwd']
    check = func_def.check_user_pwd(user_pwd, username, password)
    if check == 0:
        return ''
    s = func_def.form_a_user_order(buy_order, sell_order, username)
    return s


# 返回全部买入订单
@myWeb.route("/request_all_buy_order", methods=["post"])
def request_all_buy_order():
    return func_def.form_all_buy_order(buy_order)


# 返回全部卖出订单
@myWeb.route("/request_all_sell_order", methods=["post"])
def request_all_sell_order():
    return func_def.form_all_sell_order(sell_order)


# 删除订单页面
@myWeb.route("/user_delete_order.html")
def user_delete_order_page():
    return render_template("user_delete_order.html")


# 处理删除订单请求
@myWeb.route("/handle_delete_order_request", methods=["post"])
def handle_delete_order_request():
    username = request.form['_usr']
    password = request.form['_pwd']
    orderID = int(request.form['_orderID'])
    order_type = request.form['_order_type']
    # print(username, password, orderID, order_type)
    # 检查用户名和密码
    check = func_def.check_user_pwd(user_pwd, username, password)
    if check == 0:
        return '0'

    # 检查订单ID和订单类型是否匹配，检查订单是否属于用户
    order_list = buy_order
    if order_type == 'sell':
        order_list = sell_order
    flag = False
    for i in order_list:
        # print(i.orderID, i.userID)
        if i.orderID == orderID and i.userID == username:
            flag = True
            break
    if not flag:
        return '0'

    # 开始删除订单
    func_def.del_order(user_holding, order_list, orderID, order_type)

    # 更新用户持仓文件
    func_def.write_user_holding(user_holding)
    func_def.write_user_holding_history(user_holding)

    # 更新订单文件
    if order_type == 'buy':
        func_def.write_buy_order(buy_order)
        func_def.write_buy_order_history(buy_order)
    else:
        func_def.write_sell_order(sell_order)
        func_def.write_sell_order_history(sell_order)

    return '1'


# 更改密码页面
@myWeb.route("/user_change_pwd.html")
def user_change_pwd_page():
    return render_template("user_change_pwd.html")


# 处理提交的订单
@myWeb.route("/handle_order_submit", methods=["post"])
def handle_order_submit():
    global user_pwd, buy_order, sell_order, user_holding, price_order, market_price, order_cnt
    username = request.form['_usr']
    password = request.form['_pwd']
    share = request.form['_share']  # type string
    unit_price = request.form['_unit_price']  # type string
    # days = ['5.08', '5.15', '5.22', '5.29', '6.05']
    shareID = request.form['_shareID']
    order_type = request.form['_order_type']  # buy or sell

    check = func_def.check_user_pwd(user_pwd, username, password)
    if check == 0:
        return '1'

    # 股票数量不为整数，小于等于零，为空
    if not share.isdigit():
        return '2'
    if int(share) <= 0:
        return '2'
    share = int(share)

    # 股票单价不为整数，小于等于零
    if not unit_price.isdigit():
        return '2'
    if int(unit_price) <= 0:
        return '2'
    if int(unit_price) > 1000:
        return '2'
    
    # 超过订单数量上限，返回错误
    cnt = 0
    for o in buy_order:
        if o.userID == username:
            cnt += 1
    for o in sell_order:
        if o.userID == username:
            cnt += 1
    if cnt >= order_limit:
        return '2'
    
    unit_price = int(unit_price)

    # 计算订单总金额
    total_price = share * unit_price

    # 用户钱不够
    if order_type == 'buy' and total_price > user_holding[username].cash:
        return '2'

    # 用户股票不够
    if order_type == 'sell' and share > user_holding[username].share_holding[shareID]:
        return '2'

    # 通过检查，创建订单
    order_cnt += 1
    o_t = order_def.order(order_cnt, order_type, shareID,
                          share, unit_price, total_price, username)

    # 将新的order计数器写入文件
    func_def.write_order_cnt(order_cnt)

    # 从用户持仓中扣除相应的cash或股票
    if order_type == 'buy':
        user_holding[o_t.userID].cash -= o_t.total_price
    else:
        user_holding[o_t.userID].share_holding[o_t.shareID] -= o_t.share

    # 更新持仓情况
    func_def.write_user_holding(user_holding)
    func_def.write_user_holding_history(user_holding)

    # 进入交易板
    if order_type == 'buy':
        if len(sell_order) != 0:
            # 把当日所有卖出订单价格从低到高排序
            ls_sell = []
            for o in sell_order:
                if o.shareID == o_t.shareID:
                    ls_sell.append(o)
            # sort为稳定排序，先排一次orderID，小的在前，即较旧的订单优先交易
            ls_sell.sort(key=lambda x: x.orderID)
            # 再排一次，价格低的在前
            ls_sell.sort(key=lambda x: x.unit_price)

            for o in ls_sell:
                # 如果买卖双方都是自己，不能成交
                if o.userID == o_t.userID:
                    continue

                if o.unit_price > o_t.unit_price:  # 剩余所有卖单都超过买单单价
                    break
                else:
                    actual_quant = min(o.share, o_t.share)

                    # 交换股票和金钱
                    o_t.share -= actual_quant
                    o_t.total_price -= actual_quant * o_t.unit_price
                    user_holding[o_t.userID].share_holding[o_t.shareID] += actual_quant
                    user_holding[o_t.userID].cash += actual_quant * \
                        (o_t.unit_price - o.unit_price)

                    o.share -= actual_quant
                    o.total_price -= actual_quant * o.unit_price
                    user_holding[o.userID].cash += actual_quant * o.unit_price

                    # 更新市场价格支撑订单队列
                    # 订单编号和用户编号都满足买方在前
                    o_p = order_def.order(str(o_t.orderID) + '+' + str(o.orderID), o.order_type, o.shareID,
                                          actual_quant, o.unit_price, actual_quant * o.unit_price, o_t.userID + '+' + o.userID)
                    price_order[o.shareID].append(o_p)
                    if len(price_order[o.shareID]) > price_queue_length:
                        price_order[o.shareID].pop(0)

                    # 更新市场价格
                    sum_cash = 0
                    sum_share = 0
                    for i in price_order[o.shareID]:
                        sum_cash += i.total_price
                        sum_share += i.share
                    market_price[o.shareID] = sum_cash/sum_share

                    # 更新市场价格文件
                    func_def.write_price_order(price_order, market_price)
                    func_def.write_price_order_history(
                        price_order, market_price)

                    # 更新成交订单记录
                    func_def.write_trade_order_history(o_p)

                    # 若卖单空了，删掉
                    if o.share == 0:
                        func_def.del_order(
                            user_holding, sell_order, o.orderID, o.order_type)

                    # 更新买卖订单文件
                        func_def.write_sell_order(sell_order)
                        func_def.write_sell_order_history(sell_order)
                    # 更新用户持仓
                        func_def.write_user_holding(user_holding)
                        func_def.write_user_holding_history(user_holding)
                    # 若买单空了，停止
                    if o_t.share == 0:
                        break

            # 有剩余金额，挂到买入面板上
            if o_t.share > 0:
                func_def.add_order(user_holding, buy_order, o_t)
                func_def.write_buy_order(buy_order)
                func_def.write_buy_order_history(buy_order)

        else:
            # 没有卖出订单，直接挂上买入面板
            func_def.add_order(user_holding, buy_order, o_t)
            func_def.write_buy_order(buy_order)
            func_def.write_buy_order_history(buy_order)

    else:  # order_type == 'sell'
        if len(buy_order) != 0:
            # 当日所有买入订单按照价格从高到低排序，价格相同按照orderID从小到大排序
            ls_buy = []
            for o in buy_order:
                if o.shareID == o_t.shareID:
                    ls_buy.append(o)
            # sort为稳定排序，先排一次orderID，小的在前
            ls_buy.sort(key=lambda x: x.orderID)
            ls_buy.sort(key=lambda x: x.unit_price, reverse=True)

            for o in ls_buy:
                # 如果是买卖双方都是自己，不能成交
                if o.userID == o_t.userID:
                    continue
                if o.unit_price < o_t.unit_price:  # 剩余所有买单都低于卖单单价
                    break
                else:
                    actual_quant = min(o.share, o_t.share)

                    # 交换股票和金钱
                    o_t.share -= actual_quant
                    o_t.total_price -= actual_quant * o_t.unit_price
                    user_holding[o_t.userID].cash += actual_quant * \
                        o.unit_price

                    o.share -= actual_quant
                    o.total_price -= actual_quant * o.unit_price
                    user_holding[o.userID].share_holding[o.shareID] += actual_quant
                    # user_holding[o.userID].cash += actual_quant * (o.unit_price - o_t.unit_price)

                    # 更新市场价格支撑订单队列
                    # 订单编号和用户编号都满足买方在前
                    o_p = order_def.order(str(o.orderID) + '+' + str(o_t.orderID), o.order_type, o.shareID,
                                          actual_quant, o_t.unit_price, actual_quant * o_t.unit_price, o.userID + '+' + o_t.userID)
                    price_order[o.shareID].append(o_p)
                    if len(price_order[o.shareID]) > price_queue_length:
                        price_order[o.shareID].pop(0)

                    # 更新市场价格
                    sum_cash = 0
                    sum_share = 0
                    for i in price_order[o.shareID]:
                        sum_cash += i.total_price
                        sum_share += i.share
                    market_price[o.shareID] = sum_cash/sum_share

                    # 更新市场价格文件
                    func_def.write_price_order(price_order, market_price)
                    func_def.write_price_order_history(
                        price_order, market_price)

                    # 更新成交订单记录
                    func_def.write_trade_order_history(o_p)

                    # 若买单空了，删掉
                    if o.share == 0:
                        func_def.del_order(
                            user_holding, buy_order, o.orderID, o.order_type)

                        # 更新买卖订单文件
                        func_def.write_buy_order(buy_order)
                        func_def.write_buy_order_history(buy_order)

                        # 更新用户持仓
                        func_def.write_user_holding(user_holding)
                        func_def.write_user_holding_history(user_holding)

                    # 若卖单空了，停止
                    if o_t.share == 0:
                        break

            # 有剩余金额，挂到买入面板上
            if o_t.share > 0:
                func_def.add_order(user_holding, sell_order, o_t)
                func_def.write_sell_order(sell_order)
                func_def.write_sell_order_history(sell_order)

        else:
            # 没有买入订单，直接挂上卖出面板
            func_def.add_order(user_holding, sell_order, o_t)
            func_def.write_sell_order(sell_order)
            func_def.write_sell_order_history(sell_order)

    # 交易成功
    return '3'


# 更改密码
@myWeb.route("/change_pwd", methods=["post"])
def change_pwd():
    # 检查用户名和密码
    username = request.form["username"]
    password = request.form["password"]
    n_password = request.form["new_password"]
    if (username in user_pwd and user_pwd[username] != password) or (username not in user_pwd):
        return '0'
        # 若用户名密码有一个不正确，报错
    if len(n_password) > 10 or len(n_password) <= 0:  # 长度过限，也报错
        return '0'

    # 更改密码
    user_pwd[username] = n_password
    output = open("./data/user_pwd.txt", "w+", encoding="UTF-8")
    for name in user_pwd:
        output.write("{} {}\n".format(name, user_pwd[name]))
    output.close()
    return '1'


# 查询交易历史界面
@myWeb.route("/user_trade_history.html")
def user_trade_history():
    return render_template("user_trade_history.html")


# 返回交易历史记录
@myWeb.route("/user_trade_history_request", methods=['post'])
def user_trade_history_request():
    username = request.form["_usr"]
    password = request.form["_pwd"]
    check = func_def.check_user_pwd(user_pwd, username, password)
    if check == 0:
        return '0'
    return func_def.form_user_trade_history(username)


# 网站说明页面
@myWeb.route("/explanation.html", methods=["get", "post"])
def explanation():
    return render_template("explanation.html")


# 管理员登陆页面
@myWeb.route("/admin_index.html")
def admin_index():
    return render_template("admin_index.html", MSG="请登录")


# 管理员主页面
@myWeb.route("/admin_main_page.html", methods=["get", "post"])
def admin_main_page():
    if request.method == "GET":
        return render_template("admin_index.html", MSG="请登录")
    pwd = request.form['password']
    if pwd != admin_pwd:
        return render_template("admin_index.html", MSG='密码错误')
    return render_template("admin_main_page.html", pwd=pwd)
    

# 返回所有用户持仓情况
@myWeb.route("/request_all_user_holding", methods=["post"])
def request_all_user_holding():
    pwd = request.form['password']
    if pwd != admin_pwd:
        return ''
    return func_def.form_all_user_holding(user_holding)


    


if __name__ == "__main__":
    myWeb.run(host="0.0.0.0", port=80, debug=True)
