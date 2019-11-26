""" Calendarific Holidays sensor """
import logging
from datetime import date, datetime, timedelta
import homeassistant.helpers.config_validation as cv
import requests
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import ATTR_DATE
from homeassistant.helpers.entity import Entity
from typing import NamedTuple

__version__ = '1.0.0'

_LOGGER = logging.getLogger(__name__)

CONF_COUNTRY = 'country'
CONF_API_KEY = 'api_key'
CONF_LOCALE = 'state'
CONF_HOLIDAYS = 'holidays'

ATTR_DESCRIPTION = 'description'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY, default=''): cv.string,
    vol.Required(CONF_HOLIDAYS, default=[]): vol.All(cv.ensure_list, [cv.string]),
    vol.Optional(CONF_LOCALE, default=''): cv.string,
    vol.Required(CONF_COUNTRY, default='gb'): cv.string,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    _LOGGER.debug("Setting up Calendarific")

    country = config.get(CONF_COUNTRY)
    locale = config.get(CONF_LOCALE)
    api_key = config.get(CONF_API_KEY)
    requiredHolidays = config.get(CONF_HOLIDAYS)

    reader = CalendarificApiReader(api_key, country, locale, requiredHolidays)

    reader.update()

    entities = []

    for holiday in requiredHolidays:
        entities.append(CalendarificSensor(reader, holiday))

    add_entities(entities)


DEFAULT_BASEURL = 'https://calendarific.com/api/v2/holidays?&api_key={}&country={}&year={}/json'

class CalendarificApiException(Exception):
    pass

HolidayInfo = NamedTuple('HolidayInfo', [('holiday_date', date), ('holiday_name', str), ('holiday_description', str)])

class CalendarificApiReader:

    def __init__(self, api_key, country, locale, requiredHolidays):
        self.country = country
        self.locale = locale
        self.api_key = api_key
        self._baseurl = DEFAULT_BASEURL
        self._requiredHolidays = requiredHolidays
        self._lastupdated = None
        self._holidays = []
    
    def get_holiday_date(self,holiday_name):
        for holiday in self._holidays:
            if holiday.holiday_name == holiday_name:
                return holiday.holiday_date
    
    def get_holiday_description(self,holiday_name):
        for holiday in self._holidays:
            if holiday.holiday_name == holiday_name:
                return holiday.holiday_description

    def update(self):
        if self._lastupdated == datetime.now().date():
            return

        self._lastupdated = datetime.now().date()
        _LOGGER.error("Updating from Calendarific API")
        today = date.today()
        year = today.year
        try:
            response = requests.get(self._baseurl.format(self.api_key,self.country,year))
            nextresponse = requests.get(self._baseurl.format(self.api_key,self.country,year+1))
        except requests.exceptions.RequestException as x:
            self._holidays = []
            raise CalendarificApiException(
                "Error occurred while fetching data: %r", x)
        res = response.json()
        hols = res['response']['holidays']
        nextres = nextresponse.json()
        nexthols = nextres['response']['holidays']

        for holidayName in self._requiredHolidays:
            holiday = [i for i in hols if i['name'] == holidayName]
            holiday_name = holidayName
            if len(holiday) > 1 and self.locale != "" :
                holiday = [i for i in hols if (i['name'] == holidayName) and ([b for b in i['states'] if b['abbrev'] == self.locale])]
            if len(holiday) > 0:
                holiday_description = holiday[0]['description']
                holiday_date = datetime.strptime(holiday[0]['date']['iso'],"%Y-%m-%d")
                if holiday_date.date() < today:
                    nextholiday = [i for i in nexthols if i['name'] == holidayName]
                    if len(nextholiday) > 1 and self.locale != "":
                        nextholiday = [i for i in nexthols if (i['name'] == holidayName) and ([b for b in i['states'] if b['abbrev'] == self.locale])]
                    holiday_date = datetime.strptime(nextholiday[0]['date']['iso'],"%Y-%m-%d")
            else:
                holiday_date = datetime.strptime("2000-01-01", "%Y-%m-%d")
                holiday_description = "Holiday NOT found"



            _LOGGER.error("done: %r", holiday_name)
            self._holidays.append(HolidayInfo(holiday_date, holiday_name, holiday_description))
        _LOGGER.debug("Holidays found: %r", self._holidays)

class CalendarificSensor(Entity):

    def __init__(self, reader, holiday):
        self._reader = reader
        self._name = holiday
        self._icon = "mdi:calendar-star"
        self._date = self._reader.get_holiday_date(self._name)
        self._description = self._reader.get_holiday_description(self._name)
        today = date.today()
        nextDate = self._date.date()
        daysRemaining = (nextDate - today).days
        if self._description == "Holiday NOT found":
            self._state = "unavailable"
        else:
            self._state = daysRemaining

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        res = {}
        res[ATTR_DATE] = self._date
        res[ATTR_DESCRIPTION] = self._description
        return res

    def update(self):
        _LOGGER.debug("updating reader")
        self._reader.update()
        self._date = self._reader.get_holiday_date(self._name)
        self._description = self._reader.get_holiday_description(self._name)
        today = date.today()
        nextDate = self._date.date()
        daysRemaining = (nextDate - today).days
        if self._description == "Holiday NOT found":
            self._state = "unavailable"
        else:
            self._state = daysRemaining