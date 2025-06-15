# Course Progress Integration for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]
[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

This custom integration allows Home Assistant to connect to [CourseProgress](https://www.courseprogress.co.uk/) and monitor members' class participation and skill progress through sensors and calendar entities.

---

## Features

This integration provides the following entities per member:

| Platform  | Description                                                                 |
|-----------|-----------------------------------------------------------------------------|
| `sensor`  | Shows each member's overall progress as a percentage (e.g. 83%).           |
| `calendar`| Displays upcoming class sessions (if scheduled in CourseProgress).         |

Future support is planned for binary sensors and finer competency details.

---

## Installation

1. Open your Home Assistant configuration directory (where `configuration.yaml` is located).
2. Navigate to or create the `custom_components` directory.
3. Inside `custom_components`, create a folder named `course_progress`.
4. Download _all_ files from this repository's `custom_components/course_progress/` directory and place them there.
5. Restart Home Assistant.
6. In the UI, go to **Settings → Devices & Services → + Add Integration** and search for **Course Progress**.

---

## Configuration

Configuration is done entirely through the UI. You’ll be asked to provide:

- **Instance URL** (e.g. `https://yourclub.courseprogress.co.uk`)
- **Username** and **Password**

Once authenticated, the integration will automatically retrieve all members linked to your account and expose relevant data.

---

## Debugging

Enable debug logging for more detailed output:

```yaml
logger:
  default: info
  logs:
    custom_components.course_progress: debug
```

---

## Known Issues

- Calendar entities require a `next_session` value to be populated in CourseProgress, or they will be skipped.
- If a member is not showing, ensure they are still marked as **active** in your CourseProgress account.

---

## Contributing

Contributions are welcome! Please read the [Contribution Guidelines](CONTRIBUTING.md) before submitting a PR.

---

[ha-courseprogress]: https://github.com/pantherale0/ha-courseprogress
[buymecoffee]: https://www.buymeacoffee.com/pantherale0
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/pantherale0/ha-courseprogress.svg?style=for-the-badge
[commits]: https://github.com/pantherale0/ha-courseprogress/commits/main
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/pantherale0/ha-courseprogress.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40pantherale0-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/pantherale0/ha-courseprogress.svg?style=for-the-badge
[releases]: https://github.com/pantherale0/ha-courseprogress/releases