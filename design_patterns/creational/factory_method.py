"""
Factory Method Pattern - Backend Implementation

This module demonstrates the Factory Method pattern in the context of backend development,
specifically for creating different types of data processors and service handlers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json
import csv
from datetime import datetime


# 1. USE CASES
"""
Backend Use Cases for Factory Method Pattern:

1. Data Processing Pipeline
   - Create different data processors for various file formats (CSV, JSON, XML)
   - Handle different types of data transformations
   - Process different input sources (files, streams, APIs)

2. Database Operations
   - Create appropriate database handlers for different databases
   - Handle different query builders
   - Manage different connection types

3. API Request Handlers
   - Create handlers for different API versions
   - Handle different authentication methods
   - Process different request formats

4. Export Services
   - Generate reports in different formats
   - Create different types of data dumps
   - Handle different export destinations

When to Use:
- When you need flexible object creation based on conditions
- When you want to delegate object creation to subclasses
- When you have a family of similar objects that need different implementations

When Not to Use:
- When object creation is simple and doesn't require complex logic
- When you don't need to extend the creation process
- When you don't need to maintain different versions or variations
"""


# 2. EXAMPLES
"""
Example Scenarios:

1. Data Processor Factory:
   ```python
   processor_factory = DataProcessorFactory()
   csv_processor = processor_factory.create_processor("csv")
   data = csv_processor.process("data.csv")
   
   json_processor = processor_factory.create_processor("json")
   data = json_processor.process("data.json")
   ```

2. Database Handler Factory:
   ```python
   db_factory = DatabaseHandlerFactory()
   postgres_handler = db_factory.create_handler("postgresql")
   result = postgres_handler.execute_query("SELECT * FROM users")
   
   mongo_handler = db_factory.create_handler("mongodb")
   result = mongo_handler.execute_query({"collection": "users"})
   ```

3. API Version Handler:
   ```python
   handler_factory = APIHandlerFactory()
   v1_handler = handler_factory.create_handler("v1")
   response = v1_handler.process_request(request)
   
   v2_handler = handler_factory.create_handler("v2")
   response = v2_handler.process_request(request)
   ```
"""


# 3. IMPLEMENTATION

class DataProcessor(ABC):
    """Abstract base class for data processors."""
    
    @abstractmethod
    def process(self, source: str) -> List[Dict[str, Any]]:
        """Process data from the given source."""
        pass


class CSVProcessor(DataProcessor):
    """Processor for CSV data."""
    
    def process(self, source: str) -> List[Dict[str, Any]]:
        """Process CSV file and return list of dictionaries."""
        result = []
        try:
            with open(source, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    result.append(row)
            return result
        except Exception as e:
            raise ValueError(f"Error processing CSV file: {e}")


class JSONProcessor(DataProcessor):
    """Processor for JSON data."""
    
    def process(self, source: str) -> List[Dict[str, Any]]:
        """Process JSON file and return list of dictionaries."""
        try:
            with open(source, 'r') as file:
                data = json.load(file)
                return data if isinstance(data, list) else [data]
        except Exception as e:
            raise ValueError(f"Error processing JSON file: {e}")


class XMLProcessor(DataProcessor):
    """Processor for XML data."""
    
    def process(self, source: str) -> List[Dict[str, Any]]:
        """Process XML file and return list of dictionaries."""
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(source)
            root = tree.getroot()
            
            def xml_to_dict(element):
                result = {}
                for child in element:
                    if len(child) == 0:
                        result[child.tag] = child.text
                    else:
                        result[child.tag] = xml_to_dict(child)
                return result
            
            return [xml_to_dict(item) for item in root]
        except Exception as e:
            raise ValueError(f"Error processing XML file: {e}")


class DataProcessorFactory:
    """Factory for creating data processors."""
    
    def __init__(self):
        self._processors = {
            'csv': CSVProcessor,
            'json': JSONProcessor,
            'xml': XMLProcessor
        }
    
    def create_processor(self, format_type: str) -> DataProcessor:
        """Create a processor for the specified format type."""
        processor_class = self._processors.get(format_type.lower())
        if not processor_class:
            raise ValueError(f"Unsupported format type: {format_type}")
        return processor_class()

    def register_processor(self, format_type: str, processor_class: type):
        """Register a new processor type."""
        if not issubclass(processor_class, DataProcessor):
            raise ValueError("Processor must inherit from DataProcessor")
        self._processors[format_type.lower()] = processor_class


# Usage Example
def main():
    # Create the factory
    factory = DataProcessorFactory()
    
    try:
        # Process CSV data
        csv_processor = factory.create_processor("csv")
        csv_data = csv_processor.process("data/sample.csv")
        print("CSV Data:", csv_data[:2])  # Show first 2 records
        
        # Process JSON data
        json_processor = factory.create_processor("json")
        json_data = json_processor.process("data/sample.json")
        print("JSON Data:", json_data[:2])  # Show first 2 records
        
        # Process XML data
        xml_processor = factory.create_processor("xml")
        xml_data = xml_processor.process("data/sample.xml")
        print("XML Data:", xml_data[:2])  # Show first 2 records
        
        # Demonstrate registering a new processor type
        class YAMLProcessor(DataProcessor):
            def process(self, source: str) -> List[Dict[str, Any]]:
                import yaml
                with open(source, 'r') as file:
                    return yaml.safe_load(file)
        
        factory.register_processor("yaml", YAMLProcessor)
        yaml_processor = factory.create_processor("yaml")
        yaml_data = yaml_processor.process("data/sample.yaml")
        print("YAML Data:", yaml_data[:2])  # Show first 2 records
        
    except Exception as e:
        print(f"Error during demonstration: {e}")


if __name__ == "__main__":
    main() 