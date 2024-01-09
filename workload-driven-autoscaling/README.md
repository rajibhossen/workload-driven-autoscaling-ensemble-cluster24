# Workload Driven Autoscaling

File Structure

| Filename | Description                                                    |
|----------|----------------------------------------------------------------|
| [metrics-collection.py](metrics-collector.py)  | collect metrics from kubernetes custom metrics server          |
| [action-agent.py](action-agent.py) | Change value in yaml file, apply changes in kubernetes cluster |

```bash
python3 action-agent.py
```
