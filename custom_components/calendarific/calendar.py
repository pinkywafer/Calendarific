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
        """Get all events in a specific time frame."""
        events: list[CalendarEvent] = []
        _LOGGER.debug("Get Events")
        if SENSOR_PLATFORM not in hass.data[DOMAIN]:
            return events
        start_date = start_datetime.date()
        end_date = end_datetime.date()
        for entity in self.entities:
            #_LOGGER.debug("Get Events: Entity: %s" % (entity))
            if (
                entity not in hass.data[DOMAIN][SENSOR_PLATFORM]
                #or hass.data[DOMAIN][SENSOR_PLATFORM][entity].hidden
            ):
                continue
            calendarific = hass.data[DOMAIN][SENSOR_PLATFORM][entity]
            #_LOGGER.debug("Get Events: Sensor Entity: %s" % (calendarific))
            raw_date = calendarific.extra_state_attributes["date"]
            #_LOGGER.debug("Get Events: Raw Date: %s" % (raw_date))
            holiday_date = datetime.strptime(raw_date, DEFAULT_DATE_FORMAT).date()
            #_LOGGER.debug("Get Events: Holiday Date: %s" % (holiday_date))
            if holiday_date is not None and start_date <= holiday_date <= end_date:
                name = calendarific.name
                #_LOGGER.debug("Get Events Name: %s" % (name))
                descript = calendarific.extra_state_attributes["description"]
                #_LOGGER.debug("Get Events: Description: %s" % (descript))
                _LOGGER.debug("Showing Event: %s (%s)" % (name, holiday_date))
                event = CalendarEvent(
                    summary=name,
                    start=holiday_date,
                    end=holiday_date,
                    description=descript,
                )
                events.append(event)
        return events

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self) -> None:
        """Get the latest data."""
        #next_dates = {}
        _LOGGER.debug("Update")
        for entity in self.entities:
            #_LOGGER.debug("Update Entity: %s" % (entity))
            name = self._hass.data[DOMAIN][SENSOR_PLATFORM][entity].name
            #_LOGGER.debug("Update: Name: %s" % (name))
            raw_date = self._hass.data[DOMAIN][SENSOR_PLATFORM][entity].extra_state_attributes["date"]
            #_LOGGER.debug("Update: Raw Date: %s" % (raw_date))
            holiday_date = datetime.strptime(raw_date, DEFAULT_DATE_FORMAT).date()
            #_LOGGER.debug("Update: Holiday Date: %s" % (holiday_date))
            descript = self._hass.data[DOMAIN][SENSOR_PLATFORM][entity].extra_state_attributes["description"]
            #_LOGGER.debug("Update: Description: %s" % (descript))
            self.event = CalendarEvent(
                summary=name,
                start=holiday_date,
                end=holiday_date,
                description=descript,
            )
