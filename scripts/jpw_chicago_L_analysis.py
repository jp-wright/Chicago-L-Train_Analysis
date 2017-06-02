import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import collections as cll

"""
Warm Up questions

1. Which stop has the highest average ridership per day, and what is it?
2. Which stop has the greatest standard deviation in weekday (exclude holidays) ridership per day, and what is it?

Challenge question

1. Imagine you’re a business owner in Chicago looking to open a new location. Any kind of business will do. In the form of writing, potentially supplemented by sketches (computer-drawn or hand-drawn) and links, we want to see your response to these questions:

• What questions could you potentially explore/answer with this data?
• Ideally, what other data would you gather or combine to learn even more?
• How would you want to see data presented, to make it actionable by you or others?

Furthermore, we want to see the results of 1–3 hours of work, using the real data, towards making those ideas a reality. The results could include findings from the data, code, Jupyter/R notebooks, a spreadsheet, a visualization, results of a statistical model you built, etc. Try not to hide things or throw them away— we want to see your work!

Some additional guidelines

• We're not expecting perfection here; this is intended to be something you spend an afternoon or so on. Send us whatever you used to tackle the problem, even if it’s not pretty.
• You're not required to use any specific tools— pick your favorites. Excel is just as valid as Python and colored pencils are just as valid as d3. Think of this as an opportunity to showcase your strengths.
• Feel free to aggregate or filter the data however you see fit— if you want to focus on a particular train line, time period, season, stop, neighborhood, etc, go for it. "Big Data" isn't necessarily going to impress us more than a thoughtful approach or interesting findings from a small slice, especially if that aligns with the story you’re telling.

Datatypes:
    W=Weekday, A=Saturday, U=Sunday/Holiday.
"""

def load_data():
    """ Load Chicago "L" data.
    INPUT: none
    OUTPUT: Pandas DataFrame
    """
    return pd.read_csv('../data/CTA_-_Ridership_-__L__Station_Entries_-_Daily_Totals.csv')


def get_avg_daily_rides(df, station, daytype=None, weekday=None):
    """ Get the mean daily riders for a given station, with the ability to specify a day of the week or type of day.
    INPUT: df, station name, day of choice
    OUTPUT: mean riders for that station
    """
    dfstation = df[df['stationname'] == station]
    if daytype:
        return dfstation.loc[df['daytype'] == daytype, 'rides'].mean()
    elif weekday:
        return dfstation.loc[df['Weekday'] == weekday, 'rides'].mean()
    else:
        return dfstation['rides'].mean()


def get_all_avg_daily_rides(df):
    """ Find the mean daily riders for all sations.
    INPUT: df
    OUTPUT: list of all mean daily rides
    """
    daily_rides = list()
    for station in df['stationname'].unique():
        daily_rides.append((get_avg_daily_rides(df, station), station))
    return daily_rides


def find_max_avg_daily_rides(df, daytype=None):
    """ Find the average daily rides for each station, the number of days of operation, and the date range for those days.
    INPUT: df
    OUTPUT: dict with the highest daily average, days of operation, and date range
    """
    print("Finding stations with maximum average daily riders...")
    def rides_and_dates():
        station_dict = cll.defaultdict(list)
        for station in busiest_stations:
            dfstation = df[df['stationname'] == station]
            station_dict[station].append(max_rides)
            station_dict[station].append(dfstation.shape[0])
            station_dict[station].append(dfstation['date'].min())
            station_dict[station].append(dfstation['date'].max())
            return station_dict

    for station in df['stationname'].unique():
        df.loc[df['stationname'] == station, 'Avg_Daily_Rides'] = get_avg_daily_rides(df, station, daytype=daytype)

    # Use .unique() in case there are multiple stations with the max rides per day.  This is unlikely but possible if we enforce truncation since 'half a ride' doesn't actually exist.
    busiest_stations = df[df['Avg_Daily_Rides'] == df['Avg_Daily_Rides'].max()]['stationname'].unique()
    max_rides = df['Avg_Daily_Rides'].max()
    return rides_and_dates(), df


def get_std_daily_rides(station, daytype=None, weekday=None):
    """ Find the standard deviation for a given station's number of riders, with optional day to be specified.
    INPUT: station name, day of choice
    OUTPUT: standard deviation
    """
    dfstation = df[df['stationname'] == station]
    if daytype:
        return dfstation.loc[df['daytype'] == daytype, 'rides'].std()
    elif weekday:
        return dfstation.loc[df['Weekday'] == weekday, 'rides'].std()
    else:
        return dfstation['rides'].std()


def find_max_std_daily_rides(day=None):
    """ Find the highest std deviation of weekday (exluding holidays) rides by stop.
    INPUT: df
    OUTPUT: highest std dev and the station it goes with.
    """
    print("Finding highest StdDev for daily rides -- this might take a few seconds...")
    station_max, std_max = None, 0
    for station in df['stationname'].unique():
        station_std = get_std_daily_rides(station, daytype=day)
        station_max, std_max = (station, station_std) if station_std > std_max else (station_max, std_max)
    return station_max, std_max


def get_weekday_avgs(df):
    """ Find the average and std. dev. of riders for all days of the week, for all stations combined.
    INPUT: df
    OUTPUT: a weekday df with all averages and std. devs.
    """
    weekdays = pd.DataFrame(df.groupby('Weekday')['rides'].mean())
    weekdays['Riders_Std'] = None
    for day in weekdays.index:
        weekdays.loc[day, 'Riders_Std'] = df.loc[df['Weekday'] == day, 'rides'].std()
    return weekdays.sort_values('rides', ascending=False)


def find_all_weekday_avgs(df):
    """ Build a dictionary of all weekday averages PER station, so we can compare stations by day.
    INPUT: df
    OUTPUT: dictionary of all the stations mean and std. dev. of riders by day of week.
    """
    weekday_dict = dict()
    for station in df['stationname'].unique():
        weekday_dict[station] = get_weekday_avgs(df[df['stationname'] == station])
    return weekday_dict


def look_at_sunday_std_cov(df):
    """ I was going to compare Sunday values initially but then changed my mind.
    INPUT: df
    OUTPUT: plot of Sundays
    """
    Std_CoV = cll.defaultdict(list)
    for station in [itm[1] for itm in sorted(daily_rides, reverse=True)[:]]:
        dfdaily = df[df['stationname'] == station]
        dfdaily = get_weekday_avgs(dfdaily)
        # print("\n{s}:\n{w}".format(s=station, w=dfdaily))
        Std_CoV[station].append(dfdaily.loc['Sunday', 'Riders_Std'])
        Std_CoV[station].append(dfdaily.loc['Saturday', 'Riders_Std'] / dfdaily.loc['Saturday', 'rides'])

    dfstd = pd.DataFrame(Std_CoV, index=['Sunday_Std', 'Sunday_CoV']).T
    sns.regplot('Sunday_Std', 'Sunday_CoV', dfstd, ci=0, color=sns.color_palette('deep')[1])
    plt.title("Sunday Std. Dev. vs. Coefficient of Variance")
    plt.tight_layout()
    plt.show()


def plot_all_std_cov(df):
    """ Look at the relationship between the mean and the std. dev. for each station's mean riders.  The Std. Dev. divided by the mean tells us the coefficient of variance, which is general guide for how consistent any given measurement is likely to be for this station.
    INPUT: df
    OUTPUT: regression plot of mean and std. dev.
    """
    Std_CoV = cll.defaultdict(list)
    for station in df['stationname'].unique():
    # for station in [itm[1] for itm in sorted(daily_rides, reverse=True)[:]]:
        dfdaily = df[df['stationname'] == station]
        # dfdaily = get_weekday_avgs(dfdaily)
        # print("\n{s}:\n{w}".format(s=station, w=dfdaily))
        Std_CoV[station].append(dfdaily['rides'].mean())
        Std_CoV[station].append(dfdaily['rides'].std())

    dfstd = pd.DataFrame(Std_CoV, index=['Mean_Daily_Riders', 'Std_Daily_Riders']).T
    sns.regplot('Mean_Daily_Riders', 'Std_Daily_Riders', dfstd, ci=0, color=sns.color_palette('deep')[3])
    plt.title("Mean Riders Relationship to Std. Dev. of Riders by Station")
    plt.tight_layout()
    plt.show()


def get_all_marginal_rides():
    """ Find the marginal values in mean riders for each station by year.  This helps us locate which stations are growing or shrinking in use compared to the average number of riders per station by year.  This is a slow function b/c of the nested loop and insert loop into dfmarginal at the end.
    INPUT: none
    OUTPUT: df with the marginal values per station by year
    """
    print("\nGetting all marginal ride averages for all stations for all years.  \nThis WILL take a few minutes...\n")
    dfmarginal = pd.DataFrame(index=['Year_Mean']+df['stationname'].sort_values().unique().tolist(), columns=df['date'].dt.year.sort_values().unique())
    for year in df['date'].dt.year.sort_values().unique():
        dfyr = df[df['date'].dt.year == year]
        yr_mean = dfyr['rides'].mean()
        for station in dfyr['stationname'].sort_values().unique():
            dfstat = dfyr['stationname'] == station
            dfyr.loc[dfstat, 'Avg_Year_Daily_Rides'] = dfyr.loc[dfstat, 'rides'].mean()
            dfyr.loc[dfstat, 'Marginal_Rides'] = dfyr.loc[dfstat, 'Avg_Year_Daily_Rides'] - yr_mean
            dfgroup = dfyr.groupby('stationname').mean()
        dfmarginal.loc['Year_Mean', year] = yr_mean

        # Every station isn't in operation every year, so I have to check station by station to insert values into final DF.  Slow.
        for name in dfgroup.index:
            dfmarginal.loc[name, year] = dfgroup.loc[name, 'Marginal_Rides']
    return dfmarginal


def plot_bar(df, ycol, ycol2=None, xcol=None, yerr_col=None):
    """ Make a bar plot
    INPUT: df, columns, error bars optional
    OUTPUT: bar plot
    """
    xcol = df[xcol] if xcol else df.index
    yerr = df[yerr_col] if yerr_col else None
    fig = plt.figure(figsize=(10, 10))
    if ycol2:
        ax = fig.add_subplot(1,1,1)
        ax = plt.bar(np.arange(df.index.shape[0]), df[ycol].values, yerr=yerr, color=sns.color_palette('deep')[0])
        ax = plt.bar(np.arange(df.index.shape[0])+1, df[ycol2].values, yerr=yerr, color=sns.color_palette('deep')[1])
    else:
        plt.bar(range(df.index.shape[0]), df[ycol].values, yerr=yerr)

    # Must change title and xticks manually
    plt.title("Mean Total L-Train Riders by Day of Week")
    plt.xticks(range(df.index.shape[0]), xcol.values, rotation=90)
    plt.xlabel("{x}".format(x=xcol.name))
    plt.ylabel("{y}".format(y=df[ycol].name))
    plt.tight_layout()
    plt.show()
    plt.close()


def plot_marginal(df, cols):
    """Plot the marginal values for a list of given stations along with the overall "L" system mean as a dashed line.
    INPUT: df, names of stations
    OUTPUT: line plot showing marginal growth or shrinkage
    """
    df = df.T
    fig = plt.figure(figsize=(10, 10))
    kwargs = dict(lw=2.5, marker='o', ms=6, mec='k', mew=1)
    for col in cols:
        plt.plot(df[col], **kwargs)
    plt.plot(df['Year_Mean'], color='k', ls=':', lw=1.5, marker=None)
    ymin, ymax = plt.ylim()
    plt.yticks([x for x in range(int(ymin), int(ymax)) if x % 1000 == 0])
    plt.title("Marginal Daily Riders Each Year by Station")
    plt.xlabel('Year')
    plt.ylabel('Marginal Daily Riders')
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.show()
    plt.close()


def find_seasonal_means(df, n=5):
    """ Find the daily rider means per station for the N (default 5) most used stations per year for hot and cold seasons. Hot months are defined as June-Sep, cold months are Dec-Mar.
    INPUT: df
    OUTPUT: df with the averages for each station for hot and cold months
    """
    # dftemp = pd.DataFrame(index=sorted(daily_rides, reverse=True)[:5], )
    dd = cll.defaultdict(list)
    dfcold = df[df['date'].dt.month.isin([1, 2, 3, 12])]
    dfhot = df[df['date'].dt.month.isin([6, 7, 8, 9])]
    # for dfseason in [dfcold, dfhot]:
    for year in df['date'].dt.year.sort_values().unique():
        for station in [itm[1] for itm in sorted(daily_rides, reverse=True)[:n]]:
            dfstation_hot = dfhot[(dfhot['date'].dt.year == year) & (dfhot['stationname'] == station)]
            dfstation_cold = dfcold[(dfcold['date'].dt.year == year) & (dfcold['stationname'] == station)]
            print("{yr} {st} - Hot: {h}, Cold: {c}".format(yr=year, st=station, h=dfstation_hot['rides'].mean(), c=dfstation_cold['rides'].mean()))
            dd[station].append(dfstation_hot['rides'].mean())
            dd[station].append(dfstation_cold['rides'].mean())

    cols = np.array(list(zip(range(2001, 2017), range(2001, 2017)))).ravel()
    cols = [str(yr)+temp for yr, temp in zip(cols, ['_Hot', '_Cold']*16)]
    dftemp = pd.DataFrame(dd).T
    dftemp.columns = cols
    return dftemp.T


def plot_temp(df, cols):
    """ Plot the mean daily riders for a list of stations for hot and cold months.
    INPUT: df, station names
    OUTPUT: line plot with hot months in red and cold months in blue.
    """
    hot_idx = [idx for idx in df.index if 'Hot' in idx]
    cold_idx = [idx for idx in df.index if 'Cold' in idx]
    hot_pal = sns.color_palette('Reds_r')
    cold_pal = sns.color_palette('Blues_r')
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1,1,1)
    kwargs = dict(lw=2.1, ms=7)
    markers = ['o', 's', '^', 'd']
    for idx, col in enumerate(cols):
        ax.plot(range(2001, 2017), df.loc[hot_idx, col].values, **kwargs, marker=markers[idx], color=hot_pal[idx], label=col+'_Hot')
        ax.plot(range(2001, 2017), df.loc[cold_idx, col].values, **kwargs, marker=markers[idx], color=cold_pal[idx], label=col+'_Cold')
    # ymin, ymax = plt.ylim()
    # plt.yticks([x for x in range(int(ymin), int(ymax)) if x % 1000 == 0])
    plt.title("Seasonal Impact on Mean Daily Riders")
    plt.xlabel('Year')
    plt.ylabel('Mean Daily Riders')
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.show()
    plt.close()




if __name__ == '__main__':
    df = load_data()

    ## Number of unique stops
    df['station_id'].unique().shape[0]

    ## Convert date to datetime and add weekdays
    df['date'] = pd.to_datetime(df['date'], format='%m/%d/%Y')
    df['Weekday'] = df['date'].dt.weekday_name

    """
    ## WARM UP Q1: Which stop has the highest average ridership per day, and what is it?
    # Busiest Station: Clark/Lake, Avg. Daily Rides: 13662.78 -> 13662
    station_dict, df = find_max_avg_daily_rides(df)
    print("The following are the busiest stations:")
    for key, values in station_dict.items():
        print("Station: {s} averaged {r:.2f} rides per day \
            \nTotal Days of Operation: {d} \
            \nStart Date: {start} \
            \nFinish Date: {finish}\n".format(s=key, r=values[0], d=values[1], start=values[2].strftime('%Y-%m-%d'), finish=values[3].strftime('%Y-%m-%d')))

    ## WARM UP Q2: Which stop has the greatest standard deviation in weekday (exclude holidays) ridership per day, and what is it?
    # Station: Lake/State.   Std Dev: 4302.62
    station_max, std_max = find_max_std_daily_rides(day='W')
    print("The following station has the highest variance in riders per weekday: \
        \nStation: {s} \
        \nStd. Deviation (riders): {std:.2f} \
        \nTotal Days of Operation: {d} \
        \nStart Date: {start} \
        \nFinish Date: {finish}\n".format(s=station_max, std=std_max, d=values[1], start=values[2].strftime('%Y-%m-%d'), finish=values[3].strftime('%Y-%m-%d')))




    ## CHALLENGE:
    # Let's see the overall trends per day of the week:
    weekdays = get_weekday_avgs(df)
    print("{w}".format(w=weekdays.round()))


    # Check the top 10 busiest stations and then find their weekday avgs:
    daily_rides = get_all_avg_daily_rides(df)
    print('\n'.join([itm[1]+": "+str(itm[0]).split('.')[0] for itm in sorted(daily_rides, reverse=True)[:10]]))


    # Check the weekday averages for those top N stations:
    plot_all_std_cov(df)


    # Plot ALL stations daily averages just to get an idea of the overall trend for the Appendix.
    daily_df = pd.DataFrame(daily_rides, columns=['Daily_Rides', 'Station'])
    # plot_bar(daily_df.sort_values('Daily_Rides', ascending=False), 'Daily_Rides', xcol='Station')
    """

    # Look at marginal annual changes
    dfmarginal = get_all_marginal_rides()
    top5 = ['Clark/Lake', 'Lake/State', 'Chicago/State', '95th/Dan Ryan', 'Belmont-North Main']
    plot_marginal(dfmarginal, top5 + ['Ashland-Lake'])


    # Look at seasonal changes:
    dftemp = find_seasonal_means(df)
    plot_temp(dftemp, top5[:-1])
    hot_idx = [idx for idx in dftemp.index if 'Hot' in idx]
    cold_idx = [idx for idx in dftemp.index if 'Cold' in idx]
    print("Mean daily riders for the five busiest stations (rounded). \
        \nHot months: \
        \n{ht} \
        \n\nCold months: \
        \n{cd} \
        \n\nDifference: \
        \n{d}".format(ht=dftemp.loc[hot_idx].mean().round(), cd=dftemp.loc[cold_idx].mean().round(), d=(dftemp.loc[hot_idx].mean() - dftemp.loc[cold_idx].mean()).round()))
