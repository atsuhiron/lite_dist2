# lite_dist2
Simple distributed computing system

## Developing
### Requirement
- uv >= 0.6.17

### run pytest
```shell
uv run pytest
```

| name                             | type | default value                    | description                                               |
|----------------------------------|------|----------------------------------|-----------------------------------------------------------|
| port                             | int  | 8000                             | The port number to use table node                         |
| trial_timeout_seconds            | int  | 600                              | Timeout seconds before a trial is reserved and registered |
| timeout_check_interval_seconds   | int  | 60                               | Interval of time to check timeout trials                  |
| curriculum_path                  | Path | {project root}/"curriculum.json" | Path to the curriculum json file                          |
| curriculum_save_interval_seconds | int  | 600                              | Interval of time to save curriculum json file             |


## 8. API のスキーマ

### StudyRegisterParam
| name  | type          | required | description         |
|-------|---------------|----------|---------------------|
| study | StudyRegistry | ✓        | `Study` to register |

### TrialReserveParam
| name               | type      | required | description                                                                       |
|--------------------|-----------|----------|-----------------------------------------------------------------------------------|
| retaining_capacity | list[str] | ✓        | The types of tasks that the worker node can handle (internal type is `set[str]`). |
| max_size           | int       | ✓        | The maximum size of parameter space reserving.                                    |

### TrialRegisterParam
| name  | type       | required | description                           |
|-------|------------|----------|---------------------------------------|
| trial | TrialModel | ✓        | Registering trial to the worker node. |




### TrialReserveResponse
| name  | type               | required | description                                                                                                                               |
|-------|--------------------|----------|-------------------------------------------------------------------------------------------------------------------------------------------|
| trial | TrialModel \| None | ✓        | Reserved trial for the worker node. None if the curriculum is empty or no trial which can be processed by the worker node's capabilities. |

### StudyRegisteredResponse
| name     | type | required | description                               |
|----------|------|----------|-------------------------------------------|
| study_id | str  | ✓        | Published `study_id` of registered study. |

## StudyResponse
| name   | type                 | required | description                                                                          |
|--------|----------------------|----------|--------------------------------------------------------------------------------------|
| status | StudyStatus          | ✓        | Status of the target Study.                                                          |
| result | StudyStorage \| None | ✗        | Results of completed study. If the study is not completed or not found, then `None`. |

### CurriculumSummaryResponse
| name      | type               | required | description                                     |
|-----------|--------------------|----------|-------------------------------------------------|
| summaries | list[StudySummary] | ✓        | The list of study (containing storage) summary. |

### OkResponse
| name | type | required | description |
|------|------|----------|-------------|
| ok   | bool | ✓        |             |