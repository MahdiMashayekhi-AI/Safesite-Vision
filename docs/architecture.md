# Architecture

## Pipeline

```
 video / RTSP / image
          |
          v
  +----------------+     +----------------+     +------------------------+
  | YOLO detector  | --> |   ByteTrack    | --> | PPE-to-person          |
  | (Ultralytics)  |     |  (track_id)    |     | association            |
  +----------------+     +----------------+     +------------------------+
                                                          |
                                                          v
                                               +------------------------+
                                               | Compliance rule engine |
                                               | (configs/compliance_   |
                                               |  rules.yaml)           |
                                               +------------------------+
                                                          |
                                                          v
                                               +------------------------+
                                               | Temporal smoothing     |
                                               | (min consecutive frame)|
                                               +------------------------+
                                                          |
                                                          v
                                               +------------------------+
                                               | Violation events       |
                                               +------------------------+
                                                    |              |
                                                    v              v
                                             FastAPI /events   Streamlit demo
```

## Modules

| Module | Responsibility |
| ------ | -------------- |
| `safesite.detection` | Ultralytics wrapper: model loading, batched inference, raw detection records. |
| `safesite.tracking` | ByteTrack integration, track state store, id lifecycle. |
| `safesite.association` | Deciding which PPE box belongs to which person box. |
| `safesite.compliance` | Rule schema (pydantic), evaluation, temporal smoothing, event models. |
| `safesite.data` | Dataset download, format conversion, dedup and split tooling. |
| `safesite.utils` | Config loading, logging, geometry, IO helpers. |
| `safesite.pipeline` | Orchestration of all stages into a single streaming call. |
| `safesite.visualization` | Frame annotation and overlays. |
| `app.api` | FastAPI service exposing events and health. |
| `app.demo_streamlit` | Interactive demo UI. |

## Design decisions

- **Stateless stages.** Every stage is a class with an explicit `step`/`update`
  method so it can be unit-tested without video IO.
- **Config over code.** Rules, tracker parameters and training hyper-parameters
  live in `configs/`, validated with pydantic at load time.
- **Events are the contract.** The API, demo and future alerting all consume the
  same violation-event schema.
- **CPU-first.** The baseline runs on CPU; GPU is a configuration flag, not a
  code branch.

## Performance targets

| Metric | Target |
| ------ | ------ |
| Throughput (CPU, 640px) | _TBD_ FPS |
| End-to-end latency | _TBD_ ms |
| mAP50 (PPE classes) | _TBD_ |
| False-positive rate per hour | _TBD_ |

## Open questions

- _TBD_
