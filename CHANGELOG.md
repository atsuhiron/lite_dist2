# Changelog

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
