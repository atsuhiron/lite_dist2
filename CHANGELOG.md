# Changelog

## [0.2.3] - 2025-06-21

### Fixed
- Fixed a bug that caused grid values to change slightly (rounding error) depending on the segment start position ([#10](https://github.com/atsuhiron/lite_dist2/pull/10)).

## [0.2.2] - 2025-06-18

### Fixed
- Fixed a bug that occurred when using multiple worker nodes ([#7](https://github.com/atsuhiron/lite_dist2/pull/7)).
- Bump up `ruff` version to 0.12.0. and fix some new warnings ([#8](https://github.com/atsuhiron/lite_dist2/pull/8)).

## [0.2.1] - 2025-06-14

### Fixed
- Fixed a bug that table threads were not terminated ([#4](https://github.com/atsuhiron/lite_dist2/pull/5)).

## [0.2.0] - 2025-06-14

### Added
- Added Worker node ID ([#2](https://github.com/atsuhiron/lite_dist2/pull/2))
  - When Trial registers, it will look at this ID and only accept results from the same node as the reserved node.
- Added DELETE /study API ([#3](https://github.com/atsuhiron/lite_dist2/pull/3))
- Added flag to automatically terminate the worker thread
  - Set a flag like `worker.start(stop_at_no_trial=True)` to automatically terminate the worker node when a Trial is not obtained.
- Added `.stop()` method to table node thread (getting `start_in_thread()` function)
- Added `.save()` method to `TableNodeClient`.

### Fixed
- Fixed type hinting of `*args` and `**kwargs`.
