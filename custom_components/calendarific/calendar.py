# Adapted from  bruxy70/Garbage-Collection
# https://github.com/bruxy70/Garbage-Collection/blob/master/custom_components/garbage_collection/calendar.py

"""Calendarific calendar."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.util import Throttle

from .const import (
    CALENDAR_NAME, 
    CALENDAR_PLATFORM, 
    DOMAIN, 
    SENSOR_PLATFORM, 
    DEFAULT_DATE_FORMAT,
)

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=1)

async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
) -> None:
    """Add calendar entities to HA, of there are calendar instances."""
    # pylint: disable=unused-argument
    # Only single instance allowed
    if not CalendarificCalendar.instances:
        async_add_entities([CalendarificCalendar()], True)


class CalendarificCalendar(CalendarEntity):
    """The Calendarific collection calendar class."""

    instances = False

    def __init__(self) -> None:
        """Create empty calendar."""
        self._cal_data: dict = {}
        self._attr_name = CALENDAR_NAME
        CalendarificCalendar.instances = True

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        return self.hass.data[DOMAIN][CALENDAR_PLATFORM].event

    @property
    def name(self) -> str | None:
        """Return the name of the entity."""
        return self._attr_name

    async def async_update(self) -> None:
        """Update all calendars."""
        await self.hass.data[DOMAIN][CALENDAR_PLATFORM].async_update()

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Get all events in a specific time frame."""
        return await self.hass.data[DOMAIN][CALENDAR_PLATFORM].async_get_events(
            hass, start_date, end_date
        )

    @property
    def extra_state_attributes(self) -> dict | None:
        """Return the device state attributes."""
        if self.hass.data[DOMAIN][CALENDAR_PLATFORM].event is None:
            # No tasks, we don't need to show anything.
            return None
        return {}


class EntitiesCalendarData:
    """Class used by the Entities Calendar class to hold all entity events."""

    __slots__ = "_hass", "event", "entities", "_throttle"

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize an Entities Calendar Data."""
        self._hass = hass
        self.event: CalendarEvent | None = None
        self.entities: list[str] = []

    def add_entity(self, entity_id: str) -> None:
        """Append entity ID to the calendar."""
        if entity_id not in self.entities:
            self.entities.append(entity_id)

    def remove_entity(self, entity_id: str) -> None:
        """Remove entity ID from the calendar."""
        if entity_id in self.entities:
            self.entities.remove(entity_id)

    async def async_get_events(
        self, hass: HomeAssistant, start_datetime: datetime, end_datetime: datetime
    ) -> list[CalendarEvent]:
        """Get all tasks in a specific time frame."""
        events: list[CalendarEvent] = []
        _LOGGER.debug("Async Get Events")
        if SENSOR_PLATFORM not in hass.data[DOMAIN]:
            return events
        start_date = start_datetime.date()
        end_date = end_datetime.date()
        for entity in self.entities:
            _LOGGER.debug("Get Events Entity: %s" % (entity))
            if (
                entity not in hass.data[DOMAIN][SENSOR_PLATFORM]
                #or hass.data[DOMAIN][SENSOR_PLATFORM][entity].hidden
            ):
                continue
            calendarific = hass.data[DOMAIN][SENSOR_PLATFORM][entity]
            _LOGGER.debug("Get Events Sensor Entity: %s" % (calendarific))
            #start = calendarific.get_next_date(start_date, True)
            start = calendarific.extra_state_attributes()
            #start = datetime.strptime(date_string, CONF_DATE_FORMAT)
            _LOGGER.debug("Start Date: %s" % (start))
            #while start is not None and start_date <= start <= end_date:
            if start is not None and start_date <= start <= end_date:
                #try:
                    #end = start + timedelta(days=1)
                #except TypeError:
                    #end = start
                name = (
                    calendarific.name
                    if calendarific.name is not None
                    else "Unknown"
                )
                #if calendarific.expire_after is None:
                #    event = CalendarEvent(
                #        summary=name,
                #        start=start,
                #        end=end,
                #    )
                #else:
                #    event = CalendarEvent(
                #        summary=name,
                #        start=datetime.combine(start, datetime.min.time()),
                #        end=datetime.combine(start, calendarific.expire_after),
                #    )
                
                #event = CalendarEvent(
                #    summary=name,
                #    start=start,
                #    end=end,
                #)
                #events.append(event)

                #start = calendarific.get_next_date(
                #    start + timedelta(days=1), True
                #)
        return events

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self) -> None:
        """Get the latest data."""
        #next_dates = {}
        _LOGGER.debug("Async Update")
        for entity in self.entities:
            _LOGGER.debug("Update Entity: %s" % (entity))
            name = self._hass.data[DOMAIN][SENSOR_PLATFORM][entity].name
            _LOGGER.debug("Update Entity Name: %s" % (name))
            raw_date = self._hass.data[DOMAIN][SENSOR_PLATFORM][entity].extra_state_attributes["date"]
            _LOGGER.debug("Update Entity Raw Date: %s" % (raw_date))
            holiday_date = datetime.strptime(raw_date, DEFAULT_DATE_FORMAT).date()
            _LOGGER.debug("Update Entity Holiday Date: %s" % (holiday_date))
            description = self._hass.data[DOMAIN][SENSOR_PLATFORM][entity].extra_state_attributes["description"]
            _LOGGER.debug("Update Entity Description: %s" % (description))
        #if len(next_dates) > 0:
            #_LOGGER.debug("Update Next Dates: %s" % (str(next_dates)))
            #entity_id = min(next_dates.keys(), key=(lambda k: next_dates[k]))
            #start = next_dates[entity_id]
            #end = start + timedelta(days=1)
            #name = self._hass.data[DOMAIN][SENSOR_PLATFORM][entity_id].name
            #self.event = CalendarEvent(
            #    summary=name,
            #    start=start,
            #    end=end,
            #)
