import numpy as np 
import pandas as pd 
import pandas_ta as ta 

class DataGenerator():
    def __init__(self, symbol: str, fraction, settings) -> None:
        self.sample_mode = 'random'
        self.window_size = settings['window_size']
        self.df = pd.read_csv("D:/Data/" + symbol + ".csv",
                                header=0,
                                skiprows=range(1,int(fraction[0])),
                                nrows=fraction[1])
        if self.df.columns[0] == 'Date':
            self.df.columns = map(str.lower, self.df.columns)
        time = pd.to_datetime(self.df.date)
        self.df.date = time
        self.price_dependent = ['open', 'high', 'low', 'close']

        # Check Indicators and pop NaNs
        n, k = self.check_columns()
        self.price_dependent = np.concatenate([self.price_dependent,k], axis=0)
        self.df = self.df.iloc[n:,:]
        self.df.iloc[:,1:] = self.df.iloc[:, 1:].astype(np.float32)
        self.df = self.df.reset_index(drop=True)

        # Drop any NULL thats left
        self.df = self.df.loc[:, self.df.isnull().sum() == 0]

        # Adding time units
        self.df.insert(loc=1, column='minute', value=time.dt.minute.astype(np.float16))
        self.df.insert(loc=1, column='hour', value=time.dt.hour.astype(np.float16))
        self.df.insert(loc=1, column='day', value=time.dt.dayofweek.astype(np.float16))
        self.df.insert(loc=1, column='month', value=time.dt.month.astype(np.float16))

        # Get all price dependent columns
        self.price_dependent = np.array([col in self.price_dependent for col in self.df.columns.values])

        # Group by day
        self.days = [g  for n, g in self.df.groupby(pd.Grouper(key='date', freq='D')) if not len(g) < self.window_size + 100]
        days = []
        for day in self.days:
            index = day.index[0]
            day = pd.concat([self.df.iloc[index-self.window_size:index, :], day], axis=0)
            days.append(day)

        self.days = days
        self.num = len(self.days)

        print(f'\nData Generator initalized! Days available: {self.num}')

    def check_columns(self):

        logits = self.df.columns[self.df.isnull().sum() > 500]
        for logit in logits:
            print('Popped: ', logit, ' with ', self.df.loc[:, logit].isnull().sum(), ' NaNs')
            self.df.pop(logit)

        n = self.df.isnull().sum().max()
        k = [col for col in self.df.columns if '_pdt' in col]

        return n, k
            
    def get_sample(self, k):
        # CS65849+816315646
        if self.sample_mode == 'random':
            num = np.random.choice(len(self.days), k)[0]
        return self.days[num]

if __name__ == "__main__":

    symbol = "SP500_M1"
    gen = DataGenerator(symbol=symbol, fraction=[int(1), 1e4], window_size=10)

    print(f' \n\nData types: {gen.df.dtypes} \nDataFrame: \n{gen.df.iloc[0,:]}')
    print(f'\nSample days: {len(gen.days)}')
    
    null = gen.df.isnull().sum()
    print(gen.df.isnull().sum().sum())

    with open('./storage/random.txt', 'w') as f:
        for i in range(len(null)):
            f.write(f'{null[i]}\n')
