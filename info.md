# Calendarific
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/pinkywafer/Calendarific)](https://github.com/pinkywafer/Calendarific/releases)
![GitHub Release Date](https://img.shields.io/github/release-date/pinkywafer/Calendarific)
[![GitHub](https://img.shields.io/github/license/pinkywafer/Calendarific)](LICENSE)

[![Maintenance](https://img.shields.io/badge/Maintained%3F-Yes-brightgreen.svg)](https://github.com/pinkywafer/Calendarific/graphs/commit-activity)
[![GitHub issues](https://img.shields.io/github/issues/pinkywafer/Calendarific)](https://github.com/pinkywafer/Calendarific/issues)

[![Buy me a coffee](https://img.shields.io/static/v1.svg?label=Buy%20me%20a%20coffee&logo=buy%20me%20a%20coffee&logoColor=white&labelColor=ff69b4&message=donate&color=Black)](https://www.buymeacoffee.com/V3q9id4)

[![Support Pinkywafer on Patreon][patreon-shield]][patreon]

The 'Calendarific' component is a Home Assistant custom sensor which counts down to public holidays and observances, by querying the Calendarific api

State Returned:
* The number of days remaining to the next occurance.

Attributes (both are provided by the Calendarific api):
* date:  The next date of the holiday (formatted by date_format configuration option if set)
* description: The description of the holiday.


## Platform Configuration

You will need an API key from Calendarific.com Go to the [sign up page](https://calendarific.com/signup) and open a new account.  A free tier account is limited to 1000 api calls per month.  This integration will make two calls per day (and two on home assistant start)

### The Calendarific platform MUST be configured in the configuration.yaml file.

```yaml
# Example configuration.yaml platform entry
calendarific:
  api_key: YOUR_API_KEY
  country: GB
  state: GB-WLS
```
### Platform configuration parameters
|Attribute |Optional|Description
|:----------|----------|------------
| `api_key` | No | your api key from calendarific.com
| `country` | No | your country code [here is a list of supported countries](https://calendarific.com/supported-countries)
| `state` | Yes | your state code (ISO 3166-2 subdivision code) [[USA](https://en.wikipedia.org/wiki/ISO_3166-2:US)] [[UK](https://en.wikipedia.org/wiki/ISO_3166-2:GB)] _note the state code is for the country in the uk (counties not supported) or the state in the us._   If omitted, only national holidays will be displayed

## Sensor Configuration

Individual sensors can be configured using Config flow or in configuration.yaml:


### Config Flow

In Configuration/Integrations click on the + button, select Calendarific and configure the options on the form (The available holidays will automatically appear on the list if the platform was configured correctly in the above step).
### configuration.yaml

Add `calendarific` sensor in your `configuration.yaml`. The following example adds two sensors - New Year's Day and Christmas Day _(Note that these must be entered EXACTLY as they are on the Calendarific server)_
```yaml
# Example configuration.yaml sensor entry
sensor:
  - platform: calendarific
    holiday: New Year's Day
  - platform: calendarific
    holiday: Christmas Day
```

### Sensor Configuration Parameters
|Attribute |Optional|Description
|:----------|----------|------------
| `holiday` | No | Name of holiday provided by calendarific api
| `name` | Yes | Friendly name **Default**: Holiday name
| `icon_normal` | Yes | Default icon **Default**:  `mdi:calendar-blank`
| `icon_today` | Yes | Icon if the holiday is today **Default**: `mdi:calendar-star`
| `days_as_soon` | Yes | Days in advance to display the icon defined in `icon_soon` **Default**: 1
| `icon_soon` | Yes | Icon if the holiday is 'soon' **Default**: `mdi:calendar`
| `date_format` | Yes | formats the returned date **Default**: '%Y-%m-%d' _for reference, see [http://strftime.org/](http://strftime.org/)_

[patreon-shield]: https://c5.patreon.com/external/logo/become_a_patron_button.png
[patreon]: https://www.patreon.com/pinkywafer
