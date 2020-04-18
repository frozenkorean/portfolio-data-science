import time
import pandas as pd
import numpy as np
import string
from datetime import datetime as dt

CITY_DATA = {'chicago': 'chicago.csv',
             'new york city': 'new_york_city.csv',
             'washington': 'washington.csv'}

month_filter = {1: 'January',
                2: 'February',
                3: 'March',
                4: 'April',
                5: 'May',
                6: 'June'}

day_filter = {1: 'Sunday',
              2: 'Monday',
              3: 'Tuesday',
              4: 'Wednesday',
              5: 'Thursday',
              6: 'Friday',
              7: 'Saturday'}


def get_city():
    """
    Asks the user to specify a city.

    Returns:
        (str) city - name of the city to analyze
    """
    # get user input for city (chicago, new york city, washington).
    while True:
        try:
            city_temp = input('\nChoose a city to analyze its bikeshare data\n\
(Chicago, New York City, Washington): ').lower()

            # asks if the user has chosen the right city
            if city_temp in CITY_DATA:
                city = city_temp
                city_correct = input("\nYou have chosen {}. Is this correct?\
\n(Please enter 'y' or 'n'): ".format(string.capwords(city)))
                if city_correct in ('y', 'yes'):  # continues if city is correct
                    break
                else:  # goes back to city selection for all other inputs
                    print('\nRestarting...')
            # if the user input doesn't match one of the cities
            else:
                print("\nYou have entered a wrong city. Please check the spelling\
 and try again.")
        except KeyboardInterrupt:
            print('\n\nManual interruption occurred...')
            city = 999  # to break from while loop in the main function
            break

    return city


def date_filter():
    """
    Asks user to specify a month and day to filter by.

    Returns:
        (str) month - name of the month to filter by, or "All" to apply no month filter
        (str) day - name of the day of week to filter by, or "All" to apply no day filter
    """

    # initialize month and day variables
    month = 0
    day = 0

    while True:
        try:
            # gets user input for the type of date filter
            date_filter = int(input("\nWhich would you like to filter by?\
\n(1 = Month, 2 = Day, 3 = Both): "))

            # if the user selects filter 1 or 3
            if date_filter in (1, 3):
                # get user input for month
                month_choice = int(input("\nWhich month would you like to choose?\
    \n(e.g. 1 = January, 2 = February, ... 6 = June): "))
                if month_choice in month_filter:  # if user has chosen a valid month
                    month = month_filter[month_choice]
                    print("\nFiltering only {} data."
                          .format(month))
                    if date_filter == 1:
                        day = 'All'
                else:  # if user input was invalid
                    date_filter = 0  # to skip the next section and start over

            # if the user selects filter 2 or 3
            if date_filter in (2, 3):
                # get user input for day of week
                day_choice = int(input("\nWhich day would you like to choose?\
    \n(e.g. 1 = Sunday, 2 = Monday, ... 7 = Saturday): "))
                if day_choice in day_filter:  # if the user has chosen a valid day
                    day = day_filter[day_choice]
                    print("\nFiltering only {} data."
                          .format(day))
                    if date_filter == 2:
                        month = 'All'
                else:  # if user input was invalid
                    date_filter = 0  # to skip the next section and start over

            if date_filter in np.arange(1, 4):
                # display the chosen filters and ask the user if they're correct
                print("\nFilters chosen: Month = {}, Day = {}"
                      .format(month, day))
                date_filter_correct = input("\nIs this correct?\nPlease enter 'y' or 'n': ")
            else:
                date_filter_correct = 'n'
                print('\nPlease try again.\n')

        except ValueError:
            print("That's not a valid number. Please try again.")
        except KeyboardInterrupt:
            print('\n\nManual interruption occurred...')
            day, month = (999, 999)  # to break from while loop in the main function
            break
        else:
            # continue only when the user answers 'yes'
            if date_filter_correct == 'y':
                break


    return month, day


def get_filters():
    """
    Runs get_city and date_filter functions to set correct filters

    Returns:
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by, or "All" to apply no month filter
        (str) day - name of the day of week to filter by, or "All" to apply no day filter
    """

    city = get_city()
    day, month = (999, 999)  # to break from while loop in the main function

    # asks the user if the user wants to filter by month or day
    # only if the user has chosen one of the three cities
    while city in CITY_DATA:
        try:
            filter_yes = input("\nWould you like to filter the data by month or day?\
\n(Please enter 'y' or 'n'): ").lower()
        except KeyboardInterrupt:
            print('\n\nManual interruption occurred...')
            break
        else:
            if filter_yes == 'y':  # if the user answered yes, call date_filter()
                month, day = date_filter()
                break
            elif filter_yes == 'n':  # if the user answered no, continue w/o filter
                print("\nNot filtering by month or day.")
                month = 'All'
                day = 'All'
                break
            else:  # for all other answers, go back
                print("\nPlease try again.")

    print('-'*40)

    return city, month, day


def load_data(city, month, day):
    """
    Loads data for the specified city and filters by month and day if applicable.

    Args:
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or "all" to apply no day filter
    Returns:
        df - Pandas DataFrame containing city data filtered by month and day
    """

    # load the city data into pandas dataframe
    df = pd.read_csv('./data/{}'.format(CITY_DATA[city]))

    # convert the start time to datetime type and extract month, day, and hour
    df['Start Time'] = pd.to_datetime(df['Start Time'])
    df['Month'] = df['Start Time'].dt.month
    df['Day'] = df['Start Time'].dt.weekday_name
    df['Hour'] = df['Start Time'].dt.hour

    # create a new column combining start and end stations
    df['Station Combination'] = df["Start Station"] + " and " + df["End Station"]

    # filter by the month specified by the user
    if month != 'All':
        month = list(month_filter.keys())[list(month_filter.values()).index(month)]
        df = df[df['Month'] == month]

    # filter by the day specified by the user
    if day != 'All':
        df = df[df['Day'] == day]

    return df


def get_common_stats(df, category):
    """
    Finds the most common times of travel and stations.

    Args:
        (str) category - category of items to calculate the frequency from
    Returns:
        (str) name - name of the most common item among the items in the category
        (int) count - returns the frequency of the most common item
    """

    name = df[category].value_counts().index[0]
    count = df[category].value_counts()[name]

    return name, count


def time_convert(seconds):
    """
    Converts seconds into hours, minutes, and seconds

    Args:
        seconds
    Returns:
        time - list of hours, minutes, seconds (rounded to 2 decimal points)
    """

    hours = int(seconds // 3600)
    minutes = int(seconds % 3600 // 60)
    seconds = round(seconds % 3600 % 60, 2)

    time = [hours, minutes, seconds]

    return time


def time_stats(df):
    """Displays statistics on the most frequent times of travel."""

    print('\nCalculating The Most Frequent Times of Travel...\n')
    start_time = time.time()

    # display the most common month by counting number of trips for each month
    # month (int) is converted to month (str) in string using month_filter
    month, month_count = get_common_stats(df, 'Month')
    month_name = month_filter[month]

    print('The most common month: {}, Count: {}'
          .format(month_name, month_count))

    # display the most common day of week by counting number of trips for each day
    day, day_count = get_common_stats(df, 'Day')
    print('The most common day of week: {}, Count: {}'
          .format(day, day_count))

    # display the most common start hour
    hour, hour_count = get_common_stats(df, 'Hour')
    print('The most common hour of day: {}, Count: {}'
          .format(hour, hour_count))

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)


def station_stats(df):
    """Displays statistics on the most popular stations and trip."""

    print('\nCalculating The Most Popular Stations and Trip...\n')
    start_time = time.time()

    # display most commonly used start station, end station, and the combination
    for station in ['Start Station', 'End Station', 'Station Combination']:
        name, count = get_common_stats(df, station)
        print("The most common {}: {}, Count: {}"
              .format(station.lower(), name, count))

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)


def trip_duration_stats(df):
    """Displays statistics on the total and average trip duration."""

    print('\nCalculating Trip Duration...\n')
    start_time = time.time()

    # calculate total trip time and convert into hours, minutes, and seconds
    total_time = time_convert(sum(df['Trip Duration']))

    # display total travel time
    print("The total trip duration: {} Hours, {} Minutes, {} Seconds"
          .format(total_time[0], total_time[1], total_time[2]))

    # calculate mean trip time and convert into hours, minutes, and seconds
    mean_time = time_convert(np.mean(df['Trip Duration']))

    # display mean travel time
    print("The average trip duration: {} Hours, {} Minutes, {} Seconds"
          .format(mean_time[0], mean_time[1], mean_time[2]))

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)


def get_mode(x):
    """Returns a single mode regardless of how many there are"""
    m = pd.Series.mode(x)
    return m.values[0]


def user_stats(df):
    """Displays statistics on bikeshare users."""

    print('\nCalculating User Stats...\n')
    start_time = time.time()

    # count number of trips per user type
    user_type = df['User Type'].value_counts()

    # calculate mean trip duration per age group in hh:mm:ss format (timedelta)
    avg_trip_user_type = (df['Trip Duration'].groupby(df['User Type'])
                                             .mean()
                                             .apply(pd.to_timedelta, unit='S')
                                             .dt.round(freq='S'))

    # build a dateframe of user type stats
    user_type_stats = {'Count': user_type,
                       'Avg Trip Duration': avg_trip_user_type}
    user_type_stats = pd.DataFrame(user_type_stats)

    # display counts of user types and average trip duration per user type
    print('Number of trips per user type and average trip duration per type')
    print(user_type_stats)

    # display counts of gender only if the column exists
    if 'Gender' not in df.columns:
        print('\nThere is no information on gender.\n')
    else:
        print('\nNumber of trips per gender')
        print(df['Gender'].value_counts(), '\n')

    # display earliest, most recent, and most common year of birth
    # only if the column exists
    if 'Birth Year' not in df.columns:
        print('\nThere is no information on birth year.\n')
    else:
        birth_year = {'earliest': int(sorted(df['Birth Year'])[0]),
                      'most recent': int(sorted(df['Birth Year'])[-1]),
                      'most common': int(df['Birth Year'].value_counts().index[0])}

        for i, by in enumerate(birth_year.values()):
            print('The {} birth year: {}'
                  .format(list(birth_year.keys())[i], by))

        # calculate age assuming the users' birthdays have passed
        df['Age'] = dt.now().year - df['Birth Year']

        # create bins and labels for 8 age groups
        bins = list(np.arange(20, 81, 10))
        bins.insert(0, 0)
        bins.append(120)
        labels = ['<20', '20-29', '30-39', '40-49', '50-59', '60-69',
                  '70-79', '80<=']

        # create age group column
        df['Age Group'] = pd.cut(df['Age'],
                                 bins=bins,
                                 labels=labels,
                                 right=False)

        print('\nAge group, popular day and hour of trip, and mean trip duration\n')

        age_group_count = df['Age Group'].value_counts(sort=False)
        age_group_pop_day = (df['Day'].groupby(df['Age Group'])
                                      .agg(get_mode))
        age_group_pop_hour = (df['Hour'].groupby(df['Age Group'])
                                        .agg(get_mode))

        # calculate mean trip duration per age group in hh:mm:ss format (timedelta)
        age_group_avg_trip = (df['Trip Duration'].groupby(df['Age Group'])
                                                 .mean()
                                                 .apply(pd.to_timedelta, unit='S')
                                                 .dt.round(freq='S'))

        # build and display a dateframe of age group stats
        age_group_stats = {'Count': age_group_count,
                           'Day': age_group_pop_day,
                           'Hour': age_group_pop_hour,
                           'Avg Trip Duration': age_group_avg_trip}
        age_group_stats = pd.DataFrame(age_group_stats)
        print(age_group_stats)

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)


def display_raw_data(df):
    """Displays 5 lines of raw data if requested by the user."""

    # initialize i and j so that first 5 lines of raw data can be displayed
    i = 0
    j = 5

    while True:
        try:
            raw_data_yes = input("\nWould you like to see 5 individual trips?\n\
(Please enter 'y' or 'n'): ")
            # if the user answers anything other than 'y' continue w/o data
            if raw_data_yes != 'y':
                break

        except KeyboardInterrupt:
            print('\n\nManual interruption occurred...')
            break
        else:
            print(df.iloc[i:j, ])

            # add 5 to i and j so that the next 5 lines can be displayed
            i += 5
            j += 5


def main():
    print('Hello! Let\'s explore some US bikeshare data!')

    while True:
        city, month, day = get_filters()

        # exit program in case of manual interruption
        if city == 999 or month == 999 or day == 999:
            print('\nExited without selecting a city or a date filter\n')
        else:
            df = load_data(city, month, day)

            time_stats(df)
            trip_duration_stats(df)
            station_stats(df)
            user_stats(df)

            # display the filters used by the user
            print("\nFilters used: Month = {}, Day = {}"
                  .format(month, day))

            display_raw_data(df)

        restart = input("\nWould you like to restart?\n\
(Please enter 'y' or 'n'): ")
        if restart.lower() != 'y':
            break


if __name__ == "__main__":
    main()
