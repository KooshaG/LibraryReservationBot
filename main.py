from datetime import datetime, timedelta, time
from bs4 import BeautifulSoup
import requests
import json

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
  # [ # some presentation rooms don't have tables, so we wont look at those
  #   {
  #     'eid': 18529,
  #     'tech': True,
  #     'name': 'LB 311 - Haiti',
  #     'priority': 4
  #   },
  #   {
  #     'eid': 18530,
  #     'tech': True,
  #     'name': 'LB 316 - Australia',
  #     'priority': 4
  #   },
  #   {
  #     'eid': 18532,
  #     'tech': True,
  #     'name': 'LB 327 - Syria',
  #     'priority': 4
  #   },
  #   {
  #     'eid': 18533,
  #     'tech': True,
  #     'name': 'LB 328 - Zimbabwae',
  #     'priority': 4
  #   },
  # ],
  [
    {
      'eid': 18510,
      'tech': True,
      'name': 'LB 451 - Brazil',
      'priority': 4
    },
    {
      'eid': 18512,
      'tech': True,
      'name': 'LB 453 - Japan',
      'priority': 4
    },
    {
      'eid': 18523,
      'tech': True,
      'name': 'LB 459 - Italy',
      'priority': 4
    },
  ],
  [
    {
      'eid': 18524,
      'tech': True,
      'name': 'LB 518 - Ukraine',
      'priority': 5
    },
    {
      'eid': 18525,
      'tech': True,
      'name': 'LB 520 - South Africa',
      'priority': 5
    },
    {
      'eid': 18526,
      'tech': True,
      'name': 'LB 522 - Peru',
      'priority': 5
    },
    {
      'eid': 18511,
      'tech': True,
      'name': 'LB 547 - Lithuania',
      'priority': 5
    },
    {
      'eid': 18528,
      'tech': True,
      'name': 'LB 583 - Poland',
      'priority': 5
    },
  ]
]

LID = 2161 # library id

HEADERS = {
  'User-Agent': 'Mozilla/5.0',
  'Referer': 'https://concordiauniversity.libcal.com/reserve/webster'
}

def reservationDaysInTwoWeeksFromNow(day = RESERVATION_TIMES[0]):
  '''
  Gets the dates that are within 14 days from now and are on the day that is passed in from RESERVATION_TIMES
  
  Returns: An array of datetime objects with the days that satisfy the requirement
  '''
  # We want to get all the days that are in our reservation days and is also less than 2 weeks from now
  now = datetime.now()
  dates = []
  diff = day['iso_weekday'] - now.isoweekday() # Find difference between today and the day we are trying to reserve (Number from -6 to 6)
  if diff == 0: # A day we want to reserve is also today, so add this to array
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
  Gets the start date that is needed for the request to the library reservation server
  
  Returns: a start date formatted as YYYY-MM-DD
  """
  # since the request wants a start date and an end date which is the day after, we need to format the date to be 2 strings
  # nextDay = date + timedelta(days=1) 
  startDate = date.strftime("%Y-%m-%d")
  # endDate = nextDay.strftime("%Y-%m-%d")
  return startDate #, endDate

def getAvailabilityArray(startStr: str):
  '''
  Queries the availablilty grid in libcal with the time string created in createDateStringsForRequest and returns a list of all the availablilities for that day
  '''
  url = f"https://concordiauniversity.libcal.com/r/accessible/availability?lid={LID}&date={startStr}"
  soup = BeautifulSoup(requests.get(url).text, features="html.parser")                       # use the information contained in the html, the checkboxes on the accessibility website 
  divs = soup.find_all('div', {'class': 'panel panel-default'}) # have hidden properties that we can take advantage of
  inputs = [div.find_all('input') for div in divs] # using array generator notation to compile all the input tags that contain the availability information
  inputs = [inputTag for sublist in inputs for inputTag in sublist] #flatten array
  return [
    {
      "start": input['data-start'],
      "end": input['data-end'],
      "itemId": int(input['data-eid']),
      "checksum": input['data-crc']
    } for input in inputs]
 
def getRoomAvailabilityArray(availabilityArray: dict, room = ROOMS[0][0]):
  '''
  Filters out the array to only contain the specified room information
  '''
  return list(filter(lambda array: array['itemId'] == room['eid'], availabilityArray))

def isRoomAvailableInTime(roomArray: list[dict], startTimeStr: str, endTimeStr: str):
  '''
  Checks if the room is available between the times specified in startTimeStr and endTimeStr
  If it is available, returns an array of the room slot dictionaries that was given by room aray but only the ones that are between the times
  Else, it returns False
  '''
  # turn time strings into time objects
  # the *map thing is pretty weird, it can process times much faster than datetime can on its own. idk why lol
  startTime = time(*map(int, startTimeStr.split(':')))
  endTime = time(*map(int, endTimeStr.split(':')))
  # room times are formatted like 'YYYY-MM-DD hh:mm:ss', take second half and do the same thing as above
  roomStartTime = time(*map(int, roomArray[0]['start'].split(' ')[1].split(':')))
  print(startTime)
  print(endTime)
  print(roomStartTime)
  

def main(): 
  for day in RESERVATION_TIMES:
    print(f"Looking to reserve a room for the following {day['dow']}s")
    reservationDates = reservationDaysInTwoWeeksFromNow(day)
    for date in reservationDates:
      print(datetime.ctime(date))
      start = createDateStringsForRequest(date)
      res = getAvailabilityArray(start)
      print(res[:10])
      
  reservationDates = reservationDaysInTwoWeeksFromNow()
  start = createDateStringsForRequest(reservationDates[0])
  print("\n\n")
  availabilities = getAvailabilityArray(start)
  print(availabilities[:30])
  print("\n\n")
  print(json.dumps(getRoomAvailabilityArray(availabilities), indent=2))
  print("\n\n")
  isRoomAvailableInTime(getRoomAvailabilityArray(availabilities), RESERVATION_TIMES[0]['startTime'], RESERVATION_TIMES[0]['endTime'])
  
if __name__ == "__main__":
  main()
