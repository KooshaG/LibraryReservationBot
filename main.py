from datetime import datetime, timedelta
import math

RESERVATION_TIMES = [
    {
        'dow': 'Monday',
        'iso_weekday': 1,
        'startTime': '13:00:00',
        'endTime': '16:00:00'
    },
    {
        'dow': 'Friday',
        'iso_weekday': 5,
        'startTime': '14:30:00',
        'endTime': '16:00:00'
    },
    {
        'dow': 'Thursday',
        'iso_weekday': 4,
        'startTime': '15:00:00',
        'endTime': '16:00:00'
    }
]

ROOMS = [
    {
        'eid': 18518,
        'tech': False,
        'name': 'LB 251 - Luxembourg',
        'priority': 2
    }
]


def reservationDaysInTwoWeeks(date=datetime.now()):
  '''
  Gets the dates that are within 14 days from now and are part of the reservation dates
  
  Returns: An array of datetime objects with the days that satisfy the requirement
  '''
  # We want to get all the days that are in our reservation days and is also less than 2 weeks from now
  dates = []
  for day in RESERVATION_TIMES:
    diff = day['iso_weekday'] - date.isoweekday() # Find difference between today and the day we are trying to reserve (Number from -6 to 6)
    if diff == 0: 
      dates.append(date) 
      dates.append(date + timedelta(days=7))
      dates.append(date + timedelta(days=14))
    elif diff < 0: # add 7 days from diff and 14 days from diff
      dates.append(date + timedelta(days=(diff+7)))
      dates.append(date + timedelta(days=(diff+14)))
    else: # diff is greater than 0, add the day of diff and 7 days from diff
      dates.append(date + timedelta(days=(diff)))
      dates.append(date + timedelta(days=(diff+7)))
  return dates
          
def createDateStringsForRequest(dates: datetime):
  dateStrings = []
reservationDates = reservationDaysInTwoWeeks()
for date in reservationDates:
  print(datetime.ctime(date))
