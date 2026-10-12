"""Extracted from 网格管理工具.md (FMZ Python source). Original source preserved below.
"""

class GridPriceManager:
    def __init__(self, Data=None, upper_price=None, lower_price=None, interval=None, grid_num=None, side: Literal['long','short']='long') -> dict:
        self.interval = interval
        self.upper_price = upper_price
        self.lower_price = lower_price
        self.grid_num = grid_num
        self.side = side
        self.grid_diff = None
        self.type = None    # 网格类型
        if self.grid_num is not None:
            self.grid_diff = (self.upper_price - self.lower_price) / (self.grid_num - 1)
        if Data is None: 
            if self.interval is None:
                self.grid_list = self._generate_grid_list_difference()
                self.type = "等差"
            else:
                self.grid_list = self._generate_grids_list_ratio()
                self.type = "等比"
        else:
            self.grid_list = Data["grid_list"]
            self.interval = Data["interval"]
            self.upper_price = Data["upper_price"]
            self.lower_price = Data["lower_price"]
            self.grid_num = Data["grid_num"]
            self.side = Data["side"]
            self.grid_diff = Data["grid_diff"]
            self.type = Data["type"]
        self.data = f"网格类型: {self.type}, 网格数量: {len(self.grid_list)}, 上下区间: [{self.upper_price}-{self.lower_price}, 方向: {self.side}]"
        self.callback = {}

    def event(self, event_name):
        """事件"""
        def decorator(func):
            self.callback[event_name] = func
            return func
        return decorator

    def _generate_grid_list_difference(self) -> dict:
        """等差网格生成"""
        grid_list = {}
        price = self.lower_price
        for _ in range(self.grid_num):
            grid_list[price] = None
            price += self.grid_diff
        grid_list[self.upper_price] = None
        return grid_list

    def _generate_grids_list_ratio(self) -> dict:
        """等比网格生成"""
        ratio = 1 + self.interval / 100
        grid = [self.lower_price * (ratio ** i) for i in range(-100, 101)]
        return {round(g, 8): None for g in grid if self.lower_price <= g <= self.upper_price}


    def get_nearest_buy_price(self, current_price) -> float:
        """获取最近网格买入价格"""
        nearest_price = None
        for price in sorted(self.grid_list.keys()):
            if price > current_price:
                break
            nearest_price = price
        return nearest_price

    def get_nearest_sell_price(self, current_price) -> float:
        """获取最近网格卖出价格"""
        nearest_price = None
        for price in sorted(self.grid_list.keys(), reverse=True):
            if price < current_price:
                break
            nearest_price = price
        return nearest_price
    
    def base_position(self, ticker) -> Union[str, int]:
        """底仓"""
        if self.side == "short":
            t = self.get_nearest_sell_price(ticker)
        else:
            t = self.get_nearest_buy_price(ticker)
        order_id = self.callback["base_position"](t)
        self.grid_list[t] = order_id
        self.callback["change"](self.grid_list)
        return order_id
    
    def add_order(self, order_id) -> Union[Dict, bool]:
        """增加网格上下挂单"""
        up_price = None
        down_price = None
        ticker = None
        keys = list(self.grid_list.keys())
        for i in range(len(keys)-1):
            if self.grid_list[keys[i]] == order_id:
                ticker = keys[i]
                try:
                    if self.side is None or self.side == "long":
                        up_price = keys[i+1]
                        down_price = keys[i-1]
                    else:
                        up_price = keys[i-1]
                        down_price = keys[i+1]
                except IndexError:
                    return False
                break

        PriceDict = {"up": up_price, "down": down_price}
        d = self.callback["add_order"](PriceDict)
        d = {"up": d["up"], "down": d["down"]}
        self.grid_list[up_price] = d["up"]
        self.grid_list[down_price] = d["down"]
        self.grid_list[ticker] = None
        self.callback["change"](self.grid_list)
        return d
    
    def cancel_order(self, order_id):
        """撤销订单"""
        result = self.callback["cancel_order"](order_id)
        if result == True:
            for items in self.grid_list.items():
                if items[1] == order_id:
                    self.grid_list[items[0]] = None
                    self.callback["change"](self.grid_list)
                    break

def main():
    gm = GridPriceManager(1000, 500, 10)

    @gm.event('add_order')
    def add_order(price):
        print(price)
        return {
            'up': 36543,
            'down': 87957,
        }

    @gm.event('cancel_order')
    def cancel_order(order_id):
        return True

    @gm.event('base_position')
    def base_position(price):
        print(price)
        return 123456

    a = gm.base_position(600)
    print(a)
    a = gm.add_order(123456)
    print(gm.grid_list)
    gm.cancel_order(87957)
    print(gm.grid_list)
