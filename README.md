# Prometheus Monitoring Framework

Welcome to the Prometheus Monitoring Framework! This framework is designed to facilitate the integration of Prometheus
monitoring into your applications, providing a structured approach to exporting metrics.

## Overview

The Prometheus Monitoring Framework offers a streamlined method to instrument your applications and export metrics to
Prometheus. It supports both synchronous and asynchronous operations, allowing for flexible integration based on your
application's requirements.

## Features

- **Dynamic Exporter Bootstrapping**: Load and initialize exporters dynamically from a specified directory.
- **Configurable Logging**: Adjust logging levels and configurations to suit different environments and debugging needs.
- **Flexible Execution Modes**: Choose between synchronous, asynchronous, or multithreaded execution for exporting
  metrics.
- **Prometheus Integration**: Seamlessly integrate with Prometheus to expose metrics via an HTTP server.

## Getting Started

### Prerequisites

- **Python 3.8+**: Ensure you have Python installed. You can download it from
  the [official Python website](https://www.python.org/).
- **Prometheus**: Set up Prometheus to scrape metrics from your application. Refer to
  the [Prometheus documentation](https://prometheus.io/docs/introduction/overview/) for guidance.

### Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/DavOstx7/prometheus-monitor-framework.git
    cd prometheus-monitor-framework
    ```

2. **Install Dependencies**: It's recommended to use a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use venv\Scripts\activate
    pip install -r requirements.txt
    ```

### Configuration

The framework uses a configuration file to manage settings. Below is an example configuration:

```yaml
app:
  execution_mode: "async"  # Options: sync, async, multithreaded
  export_interval_seconds: 60
  prometheus_port: 9090

logging:
  version: 1
  disable_existing_loggers: False
  formatters:
    standard:
      format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
  handlers:
    console:
      class: logging.StreamHandler
      formatter: standard
      level: DEBUG
  exporters: # Parent logger of all exporters
    handlers: [ console ]
    level: INFO
  src: # Parent logger of all source modules
    handlers: [ console ]
    level: INFO

exporters:
  - type: "your_exporter_type" # Required. Must match your exporter subpackage name.
    name: "your_exporter_name" # Optional (defaults to None). Any name to differentiate between your exporter instances.
    enabled: true # Optional (defaults to True). Whether to bootstrap this exporter.
    config: # Optional (defaults to None). The configuration to inject to this exporter instance.
      config_key_one: "1"
      config_key_two: "2"
```

### Usage

1. **Develop Exporters**:
    * Create a directory for your exporters (e.g., `src/exporters/`).
    * Each exporter should have its own subdirectory containing an `exporter.py` and
      `config.py` (only if it supports configuration injection).
    * Implement the `BaseExporter` class and define the `export_metrics` method.

2. **Run the Application**: Execute the main script with the necessary arguments (all cli-arguments are optional):
    ```bash
   python main.py
    ```
    * `--config-file`: Path to your configuration file (must be yaml or json).
    * `--exporters-dir`: Directory containing your exporters (should be a relative path).
    * `--dry-run`: Run the application without starting the prometheus server & executing the export_metrics methods.
    * `--verbose`: Enable verbose logging.

### Exporter Example

A dummy-example already exists in the current project template under [src/exporters](src/exporters/s3_size).
Here is a more realistic example though:

**Defining the configuration model of the exporter**:
```python
# src/exporters/s3_size/config.py
from pydantic import BaseModel
from typing import List

class Config(BaseModel):  # Class name must be 'Config'
    metric_name: str
    bucket_names: List[str]
```

**Defining the class and export logic of the exporter**:
```python
# src/exporters/s3_size/exporter.py
import boto3
from prometheus_client import Gauge

from src.exporters import BaseExporter
from .config import Config


class Exporter(BaseExporter[Config]):  # Class name must be 'Exporter'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.client = boto3.client("s3")
        self.metric = Gauge(self.config.metric_name, "Size of the S3 bucket in bytes", ["bucket_name"])

    def export_metrics(self): # Can also be an async function (if the execution mode is set to 'async')
        for bucket_name in self.config.bucket_names:
            try:
                bucket_size = self.get_bucket_size(bucket_name)
                self.logger.info(f"Bucket '{self.config.bucket_name}' size: {bucket_size} bytes")
    
                self.metric.labels(bucket_name=bucket_name).set(bucket_size)
            except Exception as e:
                self.logger.error(f"Failed to retrieve S3 bucket size for '{bucket_name}': {e}")

    def get_bucket_size(self, bucket_name: str) -> int:
        """
        Calculates the total size (in bytes) of all objects in the given S3 bucket.
        """
        ...
```

## Future Improvements & Features

While the framework is functional and flexible, there are several exciting ideas for future improvements and
enhancements. Here are some concepts we're considering for the next steps in development:

### 1. **Exporter-Specific Configuration Overrides**

- Allow the ability to configure specific exporters with custom settings. This can include execution mode adjustments,
  such as the number of threads or worker pool size.
- Provide control over export behavior, particularly for managing asynchronous and non-asynchronous exporters in mixed
  environments. For example, users may want to specify how to handle synchronous exports when the framework is in async
  mode.
- Enable fine-tuning of the export interval, with options for relative intervals based on the start time, absolute
  intervals, or even maximum intervals between exports.

### 2. **Flexible Exporter Configuration Structure**

- Support more flexible configurations by allowing exporters to be defined within an "exporters config" directory. Each
  exporter will be defined by its own configuration file, providing a modular approach to managing exporter settings.
- Allow custom naming conventions for exporter and configuration classes, removing the strict requirement to use 
  "Exporter" and "Config" as the default class names. This would make the framework more adaptable for a wider range of
  use cases and naming preferences.

### 3. **User Interface (UI) for Configuration and Monitoring**

- Consider adding a simple, intuitive user interface to configure exporters, monitor their status, and view metrics. A
  UI could streamline user interactions with the framework and provide real-time feedback on exporter performance and
  metrics.

### 4. **Framework Packaging and CLI Generation**

- Explore the possibility of converting the framework into a more complete package, similar to Django, to enhance its
  extensibility and usability. This could include a well-structured set of tools, clear documentation, and a standard
  approach to adding new exporters and configurations.
- Provide a CLI tool to automatically generate basic templates for new exporters, configurations, and setups, allowing
  users to quickly get started with a working exporter setup.

### 5. **Refactoring and Structural Improvements**

- Redesign and refine the framework's structure to ensure it is more purposeful and maintainable. This might involve
  better naming conventions for packages and modules to clarify their purpose.
- Remove "static methods" from classes by ensuring all external functions are properly placed outside the class
  modules, making the class structure more coherent and class methods more self-contained.

These improvements will continue to evolve based on community feedback, contributing to a more powerful, flexible, and
user-friendly framework. Stay tuned for updates and new features!