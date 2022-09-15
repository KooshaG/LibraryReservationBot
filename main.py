from datetime import datetime, timedelta

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

ROOMS = [ # first index is highest priority, as it goes down the list, the less favorable the spot is
    [
      {
        'eid': 18520,
        'tech': True,
        'name': 'LB 257 - Croatia',
        'priority': 1
      },
    ],
    [
      {
        'eid': 18518,
        'tech': False,
        'name': 'LB 251 - Luxembourg',
        'priority': 2
      },
      {
        'eid': 18522,
        'tech': False,
        'name': 'LB 259 - New Zealand',
        'priority': 2
      },
    ],
    [
      {
        'eid': 18508,
        'tech': True,
        'name': 'LB 351 - Netherlands',
        'priority': 3
      },
      {
        'eid': 18535,
        'tech': True,
        'name': 'LB 353 - Kenya',
        'priority': 3
      },
      {
        'eid': 18536,
        'tech': True,
        'name': 'LB 359 - Vietnam',
        'priority': 3
      },
    ],
    [
      {
        'eid': 18529,
        'tech': True,
        'name': 'LB 311 - Haiti',
        'priority': 4
      },
      {
        'eid': 18530,
        'tech': True,
        'name': 'LB 316 - Australia',
        'priority': 4
      },
      {
        'eid': 18532,
        'tech': True,
        'name': 'LB 327 - Syria',
        'priority': 4
      },
      {
        'eid': 18533,
        'tech': True,
        'name': 'LB 328 - Zimbabwae',
        'priority': 4
      },
    ],
    [
      {
        'eid': 18510,
        'tech': True,
        'name': 'LB 451 - Brazil',
        'priority': 5
      },
      {
        'eid': 18512,
        'tech': True,
        'name': 'LB 453 - Japan',
        'priority': 5
      },
      {
        'eid': 18523,
        'tech': True,
        'name': 'LB 459 - Italy',
        'priority': 5
      },
    ],
    [
      {
        'eid': 18524,
        'tech': True,
        'name': 'LB 518 - Ukraine',
        'priority': 6
      },
      {
        'eid': 18525,
        'tech': True,
        'name': 'LB 520 - South Africa',
        'priority': 6
      },
      {
        'eid': 18526,
        'tech': True,
        'name': 'LB 522 - Peru',
        'priority': 6
      },
      {
        'eid': 18511,
        'tech': True,
        'name': 'LB 547 - Lithuania',
        'priority': 6
      },
      {
        'eid': 18528,
        'tech': True,
        'name': 'LB 583 - Poland',
        'priority': 6
      },
    ]
]


def reservationDaysInTwoWeeksFromNow(day = RESERVATION_TIMES[0]):
  '''
  Gets the dates that are within 14 days from now and are on the day that is passed in from RESERVATION_TIMES
  
  Returns: An array of datetime objects with the days that satisfy the requirement
  '''
  # We want to get all the days that are in our reservation days and is also less than 2 weeks from now
  now = datetime.now()
  dates = []
  diff = day['iso_weekday'] - now.isoweekday() # Find difference between today and the day we are trying to reserve (Number from -6 to 6)
  if diff == 0: 
    dates.append(now) 
    dates.append(now + timedelta(days=7))
    dates.append(now + timedelta(days=14))
  elif diff < 0: # add 7 days from diff and 14 days from diff
    dates.append(now + timedelta(days=(diff+7)))
    dates.append(now + timedelta(days=(diff+14)))
  else: # diff is greater than 0, add the day of diff and 7 days from diff
    dates.append(now + timedelta(days=(diff)))
    dates.append(now + timedelta(days=(diff+7)))
  return dates
          
def createDateStringsForRequest(date: datetime):
  """ 
  Gets the start and end dates that are needed for the request to the library reservation server
  
  Returns: A tuple with 2 elements, a start date and an end date, both are formatted as YYYY-MM-DD
  """
  # since the request wants a start date and an end date which is the day after, we need to format the date to be 2 strings
  nextDay = date + timedelta(days=1) 
  startDate = date.strftime("%Y-%m-%d")
  endDate = nextDay.strftime("%Y-%m-%d")
  return startDate, endDate
  
for day in RESERVATION_TIMES:
  print(f"Looking to reserve a room for the following {day['dow']}s")
  reservationDates = reservationDaysInTwoWeeksFromNow(day)
  for date in reservationDates:
    print(datetime.ctime(date))
  for date in reservationDates:
    print(createDateStringsForRequest(date))
