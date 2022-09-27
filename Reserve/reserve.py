from datetime import datetime, timedelta, time
from bs4 import BeautifulSoup
from time import sleep
import requests
import re
import os
import logging

from Reserve import database

CONCORDIA_USERNAME = os.environ['CONCORDIA_USERNAME']
CONCORDIA_PASSWORD = os.environ['CONCORDIA_PASSWORD']

LIBCAL_AUTH_REGEX_CHECK = re.compile(r'<h2>Redirecting \.\.\.</h2>')
LIBCAL_FAILED_RESERVATION_REGEX = re.compile(r'Sorry')

RESERVATION_TIMES = [
  {
    'dow': 'Monday',
    'iso_weekday': 1,
    'startTime': '13:00:00',
    'endTime': '16:00:00',
    '30minSlots': 6
  },
  {
    'dow': 'Friday',
    'iso_weekday': 5,
    'startTime': '14:30:00',
    'endTime': '16:00:00',
    '30minSlots': 4
  },
  {
    'dow': 'Thursday',
    'iso_weekday': 4,
    'startTime': '15:00:00',
    'endTime': '16:00:00',
    '30minSlots': 2
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
  'Referer': 'https://concordiauniversity.libcal.com/reserve/webster',
}

CONCORDIA_LIBCAL_URL = 'https://concordiauniversity.libcal.com'
CONCORDIA_AUTH_URL = 'https://fas.concordia.ca'

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
      "seat_id": input['data-seat'],
      "lid": LID,
      "eid": int(input['data-eid']),
      "checksum": input['data-crc']
    } for input in inputs]
 
def getRoomAvailabilityArray(availabilityArray: dict, room = ROOMS[0][0]):
  '''
  Filters out the array to only contain the specified room information
  '''
  return list(filter(lambda array: int(array['eid']) == room['eid'], availabilityArray))

def isRoomAvailableInTime(roomArray: list[dict], reservationTime = RESERVATION_TIMES[0], room = ROOMS[0][0]):
  '''
  Checks if the room is available between the times specified in the reservation time
  If it is available, returns an array of the room slot dictionaries that was given by room aray but only the ones that are between the times
  Else, it returns False
  '''
  # turn time strings into time objects
  # the *map thing is pretty weird, it can process times much faster than datetime can on its own. idk why lol
  startTime = time(*map(int, reservationTime['startTime'].split(':')))
  endTime = time(*map(int, reservationTime['endTime'].split(':')))
  slotsInTime = []
  consecutiveSlots = reservationTime['30minSlots']
  
  for slot in roomArray:
    # room times are formatted like 'YYYY-MM-DD hh:mm:ss', take second half and do the same thing as above
    roomStartTime = time(*map(int, slot['start'].split(' ')[1].split(':')))
    
    if consecutiveSlots == 0: # we have a room that is available for every time slot that we wanted
      break
    
    if roomStartTime >= startTime and roomStartTime <= endTime: # append all the slots within the time to an array to make creating the reservations easier
      consecutiveSlots -= 1
      slotsInTime.append(slot)
      logging.debug(f"\t\t{startTime} > {roomStartTime} > {endTime}")
    else: # reset the counter if we miss a slot, so we definitely dont send a partial reservation
      consecutiveSlots = reservationTime['30minSlots']
  if consecutiveSlots == 0: 
    return slotsInTime
  else:
    return False

def createFormForRequest(slots: list):
  '''
  Converts the reservation 
  '''
  # create the stuff that doesn't change in the form and then add the extra stuff
  form = {
    "libAuth": "true",
    "blowAwayCart": "true",
    "method": 14,
    "returnUrl": f"/r/accessible?lid={LID}&gid=5032&zone=0&space=0&capacity=2&accessible=0&powered=0",
  }
  # transform the information in the slots to the gross data layout that libcal wants
  for index, slot in enumerate(slots):
      for key in slot:
        form[f'bookings[{index}][{key}]'] = slot[key]
  
  return form

def daysSinceEpoch(date: datetime):
  return (date - datetime(1970, 1, 1)).days

def dateFromReservation(reservation: list[dict]):
  return datetime(*map(int, reservation[0]['start'].split(' ')[0].split('-')))

def getAuth(session: requests.Session(), redirectRes: str):
  
  soup = BeautifulSoup(redirectRes, features="html.parser")
  params = {input['name']: input['value'] for input in soup.find_all('input')}
  libcalCookieAdderUrl = soup.form['action']
  libcalCookieAdderRes = session.get(libcalCookieAdderUrl, params=params, headers=HEADERS, allow_redirects=True)
  
  soup = BeautifulSoup(libcalCookieAdderRes.text, features="html.parser")
  data = {
    'UserName': CONCORDIA_USERNAME,
    'Password': CONCORDIA_PASSWORD,
    'AuthMethod': 'FormsAuthentication'
    }
  microsoftAuthUrl = f"{CONCORDIA_AUTH_URL}{soup.form['action']}"
  microsoftAuthRes = session.post(microsoftAuthUrl, data=data, headers=HEADERS, allow_redirects=True)
  
  soup = BeautifulSoup(microsoftAuthRes.text, features="html.parser")
  concordiaAuthLinkUrl = soup.form['action']
  data = {input['name']: input['value'] for input in soup.find_all('input', {'type': 'hidden'})} # theres a visible submit button that messes with the data so filter it out
  session.post(concordiaAuthLinkUrl, data=data, headers=HEADERS, allow_redirects=True)
  # we are done authenticating now
  
def main(): 
  reservations = []
  for day in RESERVATION_TIMES:
    logging.info(f"Looking to reserve a room for the following {day['dow']}s")
    reservationDates = reservationDaysInTwoWeeksFromNow(day)
    
    for date in reservationDates:
      logging.info(datetime.ctime(date))
      start = createDateStringsForRequest(date)
      createCartRes = getAvailabilityArray(start)
      reservationMade = False
      if reservationMade:
        break
      
      for priority in ROOMS: # priority is kinda redundant but wtv
        if reservationMade: 
          break
        logging.info(f"Priority: {priority[0]['priority']}")
        
        for room in priority:
          logging.info(f"\tRoom: {room['name']}")
          roomTimes = getRoomAvailabilityArray(createCartRes, room)
          slots = isRoomAvailableInTime(roomTimes, day, room)
          if slots != False:
            logging.info(f"## We have a room!! {room['name']} is available between {day['startTime']} and {day['endTime']} on {datetime.ctime(date)}")
            reservations.append(slots)
            reservationMade = True
            break
      if not reservationMade:
        logging.info(f"No possible slots found for {datetime.ctime(date)}")

  conn = database.createDBConnection()
    
  # filter out the reservations that are in the database
  reservations = list(filter(lambda reservation: database.findDay(daysSinceEpoch(dateFromReservation(reservation)), conn) == 0, reservations)) 

  if len(reservations) == 0:
    logging.info('Theres nothing to reserve! Quiting...')
    return

  # make session for all the reservation requests  
  session = requests.Session()
  
  for reservationSlots in reservations:
    
    logging.info(datetime.ctime(dateFromReservation(reservationSlots)))
        
    createCart = f'{CONCORDIA_LIBCAL_URL}/ajax/space/createcart'
    data = createFormForRequest(reservationSlots)
    createCartRes = session.post(createCart, data=data, headers=HEADERS, allow_redirects=True)
    
    authCheckUrl = f"{CONCORDIA_LIBCAL_URL}{createCartRes.json()['redirect']}"
    authCheckRes = session.get(authCheckUrl, headers=HEADERS, allow_redirects=True)
    
    if bool(LIBCAL_AUTH_REGEX_CHECK.findall(authCheckRes.text)): # we got redirected to the auth check
      getAuth(session=session, redirectRes=authCheckRes.text)
    
    confirmReservationUrl = f"{CONCORDIA_LIBCAL_URL}/ajax/equipment/checkout"
    data = {
      'forcedEmail': '',
      'returnUrl': f"/r/accessible?lid={LID}&gid=5032&zone=0&space=0&capacity=2&accessible=0&powered=0",
      'logoutUrl': "logout",
      'session': 0
    }
    confirmationRes = session.post(confirmReservationUrl, data=data, headers=HEADERS, allow_redirects=True)
    
    logging.debug(confirmationRes)
    
    if confirmationRes.status_code == 500 and bool(LIBCAL_FAILED_RESERVATION_REGEX.findall(confirmationRes.text)):
      logging.debug(confirmationRes.text)
      logging.info("Oops, it seems like we reserved this date already... Adding to database")
    elif reservationSlots != reservations[-1]: # this is not the last reservation, we should sleep to give the email service time to send before making the next reservation
      sleep(240)
            
    database.addDay(daysSinceEpoch(dateFromReservation(reservationSlots)), conn)
    
  
  database.destroyDBConnection(conn)
      
if __name__ == "__main__":
  main()
