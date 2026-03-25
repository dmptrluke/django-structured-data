# Changelog

## 0.13.1 (2026-03-25)

### Fixed

- Fix build issue.

## 0.13.0 (2026-03-25)

### Changed

- Bump minimum Django version to 4.2.
- Add CI and release workflows, update Django classifiers.

## 0.12.0 (2026-03-18)

### Added

- `STRUCTURED_DATA_SITEWIDE` and `STRUCTURED_DATA_SITEWIDE_OG` now accept callables, invoked at render time for dynamic values (e.g. reading from a database model).

## 0.11.0 (2026-03-13)

### Added

- Added dict passthrough support to all template tags - plain dicts can now be passed directly to `json_ld_for`, `og_for`, `meta_for`, and `twitter_for`.
- Added `StructuredDataMixin` view mixin for injecting structured data into template context from class-based views.
- Added `json_ld_sitewide` template tag and `STRUCTURED_DATA_SITEWIDE` setting for rendering sitewide JSON-LD blocks.
- Added `og_sitewide` template tag and `STRUCTURED_DATA_SITEWIDE_OG` setting for rendering sitewide Open Graph tags.

### Changed

- Restructured README into a quickstart guide with detailed documentation moved to `docs/`.

## 0.10.0 (2026-03-11)

### Added

- Added explicit `twitter:image` meta tag output from the `{% twitter_for %}` template tag. ([`89e8241`](https://github.com/dmptrluke/django-structured-data/commit/89e8241))

## 0.9.0 (2026-03-11)

### Added

- Added event structured data support (`Event`, `MusicEvent`, `BusinessEvent`, etc.).
- Added Twitter Card template tag (`{% twitter_for %}`) with card type, image alt text, and creator mappings.

### Changed

- Expanded Open Graph tags to map `author`, `articleSection`, `keywords` (as `article:tag`), and `og:image:alt`.
- Expanded meta tags to map `author`, `keywords`, and `location`.

### Removed

- **Breaking:** removed `sub_defaults` helper and `DEFAULT_STRUCTURED_DATA` setting.

([`0fde038`](https://github.com/dmptrluke/django-structured-data/commit/0fde038))

## 0.8.0 (2026-03-11)

### Added

- Added `format_time` helper to auto-format `datetime`, `date`, and `time` objects in OG and meta tag values. ([`5a3663c`](https://github.com/dmptrluke/django-structured-data/commit/5a3663c))

### Changed

- Switched build system to hatchling, ruff, and uv. ([`468f98e`](https://github.com/dmptrluke/django-structured-data/commit/468f98e))
- Updated README examples to pass datetime objects directly instead of pre-formatted strings. ([`d0dbcd6`](https://github.com/dmptrluke/django-structured-data/commit/d0dbcd6))

## 0.7.0 (2026-03-05)

### Changed

- Updated supported Python versions to 3.10-3.13. ([`0803025`](https://github.com/dmptrluke/django-structured-data/commit/0803025))

## 0.6.0

Previous release.
