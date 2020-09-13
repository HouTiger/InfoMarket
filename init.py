# 用于初始化data中的用户初始数据
import order_def
import holding_def
import math
days = ['5.22', '5.29', '6.05', '6.12', '6.19']
# 需要多加一个换行的 user_pwd.txt buy_order.txt sell_order.txt user_holding.txt price_order.txt
def init_all():
    # 初始化
    # 初始化管理员权限密码
    readin1 = open('./data/admin_pwd.txt', 'r', encoding='UTF-8')
    s1 = readin1.read()
    readin1.close()
    admin_pwd = s1

    # 初始化用户名和密码
    user_pwd = {}  # user-password dictionary
    readin2 = open('./data/user_pwd.txt', 'r', encoding='UTF-8')
    s2 = readin2.read()
    readin2.close()
    s2 = s2.split('\n')
    del s2[-1]
    for line in s2:
        l = line.split()
        user_pwd[l[0]] = l[1]

    # 初始化买入订单
    buy_order = []
    readin3 = open('./data/buy_order.txt', 'r', encoding='UTF-8')
    s3 = readin3.read()
    readin3.close()
    s3 = s3.split('\n')
    del s3[-1]
    for line in s3:
        l = line.split()
        if l == []:
            continue
        # orderID, order_type, shareID, share, unit_price, total_price, userID
        o = order_def.order(int(l[0]), l[1], l[2], int(l[3]), int(l[4]), int(l[5]), l[6])
        buy_order.append(o)

    # 初始化卖出订单
    sell_order = []
    readin4 = open('./data/sell_order.txt', 'r', encoding='UTF-8')
    s4 = readin4.read()
    readin4.close()
    s4 = s4.split('\n')
    del s4[-1]
    for line in s4:
        l = line.split()
        if l == []:
            continue
        # orderID, order_type, shareID, share, unit_price, total_price, userID
        o = order_def.order(int(l[0]), l[1], l[2], int(l[3]), int(l[4]), int(l[5]), l[6])
        sell_order.append(o)

    # 初始化用户持仓
    user_holding = {} # {username: class holding}
    readin5 = open('./data/user_holding.txt', 'r', encoding="UTF-8")
    s5 = readin5.read()
    readin5.close()
    s5 = s5.split('\n')
    del s5[-1]
    
    for line in s5:
        l = line.split()
        d = {}
        for i in range(2, 7):
            d[days[i - 2]] = int(l[i])
        u = holding_def.holding(l[0], int(l[1]), d)
        user_holding[u.userID] = u
    


    # 初始化市场价格和支撑订单
    # days = ['5.22', '5.29', '6.05', '6.12', '6.19']
    price_order = {'5.22': [], '5.29': [], '6.05': [], '6.12': [], '6.19': []}
    market_price = {}
    readin6 = open('./data/price_order.txt', 'r', encoding='UTF-8')
    s6 = readin6.read()
    readin6.close()
    s6 = s6.split('\n\n')
    del s6[-1]
    for d in s6:
        d = d.split("\n")
        line = d[0]
        line = line.split()
        market_price[line[0]] = float(line[1]) # 第一行为 day price
        for l in d[1:]:
            l = l.split()
            # orderID, order_type, shareID, share, unit_price, total_price, userID
            o = order_def.order(l[0], l[1], l[2], int(l[3]), int(l[4]), int(l[5]), l[6])
            price_order[o.shareID].append(o)

    # 初始化订单编号计数器
    readin7 = open('./data/order_cnt.txt', "r", encoding="UTF-8")
    s7 = readin7.read()
    readin7.close()
    order_cnt = int(s7)
    return admin_pwd, user_pwd, buy_order, sell_order, user_holding, price_order, market_price, order_cnt
