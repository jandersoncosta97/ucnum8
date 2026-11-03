from decimal import Decimal

class TicksFormatter:
    
    def __init__(self, ax):
        self.ax = ax
        
    def __get_digits(self, ticks):
        ticks_list = []
        non_zeros = {}
        for tick in ticks:
            tick = f"{tick:.9f}"
            aux = True
            cont = 0
            for keys, values in enumerate(tick.split('.')[1]):
                while aux == True and cont <= keys:
                    if values != '0':
                        non_zeros[keys] = values
                        cont += 1
                    else:
                        aux = False

            ticks_list.append(float(tick))
        digits = max([len(str(tick).split('.')[1]) for tick in ticks_list if len(str(tick).split('.')) > 1])
        return digits


    def modify_ticks(self):

        def format_ticks(value, num_digits):
            return str(Decimal(value).quantize(Decimal(f"1.{'0' * num_digits}")))

        ticks = self.ax.get_yticks() #TODO is this going to work?
        digits = self.__get_digits(ticks)
        
        return lambda value: format_ticks(value, digits)
