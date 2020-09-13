# define class order
class order:
    '''
    orderID int;    
    order_type string 'buy' or 'sell';   
    shareID 股票名称 string;   
    share 股票数量 int;   
    unit_price 单价 int;   
    total_price 总价 int;   
    userID = 'null' 用户编号 string  
    '''
    def __init__(self, _orderID, _order_type, _shareID, _share, _unit_price, _total_price, _userID):
        self.orderID = _orderID
        self.order_type = _order_type
        self.shareID = _shareID
        self.share = _share
        self.unit_price = _unit_price
        self.total_price = _total_price
        self.userID = _userID