# Changelog

All notable changes to the Sensing Garden Client will be documented in this file.

## [0.0.13] - 2025-08-03

### Added
- Environment endpoint support via new `EnvironmentClient` class accessible via `client.environment`
- Support for submitting environmental sensor readings including:
  - Particulate matter measurements (PM1.0, PM2.5, PM4.0, PM10.0)
  - Environmental conditions (humidity, temperature)
  - Air quality indices (VOC, NOx)
- Optional location data support for environmental readings (latitude, longitude, altitude)
- `classification_data` field support for classifications to handle hierarchical taxonomy data with multiple candidates and confidence scores
- Comprehensive tests for environment endpoint functionality
- Usage examples for environment endpoints in README

### Changed
- Made `timestamp` a required parameter for environment submissions
- Location parameter is now optional for environment readings
- Updated README with environment endpoint usage examples

### Removed
- Removed invalid `test_sorting_with_invalid_sort_desc` test that was checking for TypeError

## [0.0.12] - 2025-05-12

### Added
- Support for optional `track_id` and `metadata` fields in classifications (client and backend)
- Client: `ClassificationsClient.add` now accepts `track_id` and `metadata` arguments
- Tests: Added/updated tests for submitting and verifying `track_id` and `metadata` in classifications

### Changed
- Backend: Lambda handler and DynamoDB schema updated to store and return `track_id` and `metadata`
- All tests passing after these changes

## [0.0.11] - 2025-04-28

### Added
- Support for optional `bounding_box` field in classifications, matching detections API
- Client: `ClassificationsClient.add` now accepts `bounding_box` argument
- Tests: Added tests for submitting and verifying bounding boxes in classifications

### Changed
- Backend: Lambda handler stores bounding_box as Decimal for DynamoDB compatibility
- Infra: Terraform and Lambda updated/synced for new schema
- All tests passing after bounding_box changes

## [0.0.10] - 2025-04-23

### Added
- One-time migration script for syncing device IDs from videos table to devices table
- Automated device ID deduplication and migration logic

### Changed
- Improved error handling and logging for device and video APIs
- Bugfixes and stability improvements for device management endpoints
- All tests passing after migration and Lambda redeploy

## [0.0.9] - 2025-04-23

### Changed
- `get_devices` now supports filtering, pagination, and sorting options matching backend API
- Client, Lambda handler, and tests updated for new device management logic
- Improved error handling and logging for device API
- All tests passing, including new video checks in recent data test

## [0.0.8] - 2025-04-15

### Added
- `.count()` methods for models, detections, classifications, and videos clients for efficient counting without retrieving all data
- Documentation and usage examples for count endpoints in the README

### Changed
- All test helpers now use `assert` and do not return values, ensuring pytest best practices
- Recommend using Poetry to run tests: `poetry run pytest`

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.5] - 2025-04-10

### Added
- Video upload and retrieval functionality
- New `VideosClient` class accessible via `client.videos`
- Support for filtering videos by device ID and timestamp range
- Video payload preparation utilities in shared module
- Documentation and examples for video operations

## [0.0.4] - 2025-03-23

### Changed
- Added validation for sort_desc parameter to ensure it's a boolean
- Updated API schema to properly document sort_desc as a boolean parameter
- Added test to verify sort_desc validation

## [0.0.3] - 2025-03-23

### Changed
- Removed metadata parameter from model creation method to align with API schema
- Updated client initialization to use direct constructor instead of initialize() function
- Updated example usage and documentation to reflect new API structure

## [0.0.2] - 2025-03-23

### Added
- Dedicated client classes for models, detections, and classifications (accessed via client properties)
- Comprehensive examples in README
- Shared utility functions in `shared.py` to promote code reuse
- Example script demonstrating the new API usage

### Changed
- Reverted to direct constructor initialization (`SensingGardenClient(base_url=api_base_url, api_key=api_key)`) for improved clarity and usability
- Improved type annotations throughout the codebase
- Enhanced documentation with usage examples
- Removed legacy standalone functions to simplify API structure

### Removed
- Device ID requirement from model endpoints (aligning with backend API changes)

## [0.0.1] - 2025-03-15

### Added
- Initial release of the Sensing Garden Client
- Basic client for API interactions
- GET endpoints for models, detections, and classifications
- POST endpoints for submitting detections, classifications, and models
- Basic documentation and examples
