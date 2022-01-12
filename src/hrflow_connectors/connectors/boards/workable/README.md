# Workable Connector
**Workable is a recruiting software.**

`Workable` :arrow_right: `Hrflow.ai`

## PullJobs
`PullJobs` gets all available jobs listed on ***Workable public endpoints***. It adds all these **jobs** to a ***Hrflow.ai Board***.

### Parameters

| Field | Type | Description |
| ----- | ---- | ----------- |
| `logics`  | `List[str]` | Function names to apply as filter before pushing the data. Default value : `[]`        |
| `local_scope`  | `Optional[Dict[str, Any]]` | A dictionary containing the current scope's local variables. Default value : `None`        |
| `global_scope`  | `Optional[Dict[str, Any]]` | A dictionary containing the current scope's global variables. Default value : `None`       |
| `format_function_name`  | `Optional[str]` | Function name to format job before pushing. Default value : `None`        |
| `hrflow_client` :red_circle: | `hrflow.Hrflow` | Hrflow client instance used to communicate with the Hrflow.ai API        |
| `board_key` :red_circle: | `str` | Board key where the jobs to be added will be stored        |
| `hydrate_with_parsing`  | `bool` | Enrich the job with parsing. Default value : `False`        |
| `archive_deleted_jobs_from_stream`  | `bool` | Archive Board jobs when they are no longer in the incoming job stream. Default value : `True`        |
| `subdomain` :red_circle: | `str` | Companies have jobs listed on workable public endpoints, subdomain of a company endpoint in `https://www.workable.com/api/accounts/{subdomain}` for example subdomain=`eurostar` for ***Eurostar*** company      |

:red_circle: : *required* 

### Example

```python
from hrflow import Hrflow
from hrflow_connectors.connectors.boards.workable import PullJobs
from hrflow_connectors.utils.logger import get_logger_with_basic_config
# We add a basic configuration to our logger to see the messages displayed in the standard output
# This is not mandatory. It allows you to see what the connector is doing.
logger = get_logger_with_basic_config()
client = Hrflow(api_secret="MY_X-API-KEY", api_user="MY_X-USER-EMAIL")
action = PullJobs(
    subdomain="MY_SUBDOMAIN",
    hrflow_client=client,
    board_key="MY_BOARD_KEY",
    hydrate_with_parsing=True,
)
action.execute()
```