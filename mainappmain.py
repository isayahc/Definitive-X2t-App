from app.Tw import CloudTw, LocalTw
from app.frequency import CloudDailyFreq, CloudWeeklyFreq, CloudMonthlyFreq, LocalDailyFreq, LocalWeeklyFreq, LocalMonthlyFreq, CloudIntraDayFreq, LocalIntraDayFreq
from datetime import date
import asyncio

a = 'spy',1
b = 'spy'

# Tw = [CloudTw(*a),LocalTw(*a)]
# cloud_multidays = [CloudDailyFreq(b),CloudWeeklyFreq(b),CloudIntraDayFreq(*a)]
# intradays = [CloudIntraDayFreq(*a),LocalIntraDayFreq(*a)]

# CloudDailyFreq(b)
# LocalDailyFreq(b)

# CloudWeeklyFreq(b)
# LocalWeeklyFreq(b)

# CloudMonthlyFreq(b)
# LocalMonthlyFreq(b)

# CloudIntraDayFreq(*a).collect_data_to_cloudII()
la = LocalIntraDayFreq(*a)
# x = {'a':1}
# y = {'b':2, 'a':4}
ct = CloudTw(*a)
lt = LocalTw('spy',1)
x = lt.get_data()
print(lt.add_data(x,{'a':3}))
print(ct.combine_dicts(x,{'a':None}))


# async def main():
#     await lt.data_listener({'a',1})
#     await la.data_stream()
    
# if __name__ == '__main__':
#     asyncio.run( lt.d_l({'a':1}) )










    