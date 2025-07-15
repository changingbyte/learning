"""
Composite Pattern - Backend Implementation

This module demonstrates the Composite pattern in the context of backend development,
specifically for handling hierarchical data structures like organization charts,
file systems, and menu systems.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import json
from datetime import datetime


# 1. USE CASES
"""
Backend Use Cases for Composite Pattern:

1. Organization Structure
   - Manage hierarchical employee relationships
   - Handle department structures
   - Process organizational queries

2. File System Operations
   - Handle directory structures
   - Process file operations recursively
   - Manage file permissions

3. Menu Systems
   - Build dynamic menu structures
   - Handle nested menu items
   - Process menu permissions

4. Category Management
   - Manage product categories
   - Handle nested taxonomies
   - Process category relationships

When to Use:
- When you need to represent part-whole hierarchies
- When clients should treat individual objects and compositions uniformly
- When you need recursive operations on tree structures

When Not to Use:
- When the structure is flat (non-hierarchical)
- When you don't need uniform treatment of objects
- When the hierarchy is fixed and won't change
"""


# 2. EXAMPLES
"""
Example Scenarios:

1. Organization Structure:
   ```python
   ceo = Employee("John Doe", "CEO")
   cto = Employee("Jane Smith", "CTO")
   dev_manager = Employee("Bob Wilson", "Dev Manager")
   
   ceo.add(cto)
   cto.add(dev_manager)
   ceo.get_subordinates()  # Returns all employees in hierarchy
   ```

2. File System:
   ```python
   root = Directory("/")
   etc = Directory("/etc")
   config = File("/etc/config")
   
   root.add(etc)
   etc.add(config)
   root.get_size()  # Returns total size of all files
   ```

3. Menu System:
   ```python
   main_menu = Menu("Main")
   settings = Menu("Settings")
   profile = MenuItem("Profile")
   
   main_menu.add(settings)
   settings.add(profile)
   main_menu.get_structure()  # Returns full menu structure
   ```
"""


# 3. IMPLEMENTATION

class OrganizationComponent(ABC):
    """Abstract base class for organization components."""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.parent: Optional['OrganizationComponent'] = None
    
    @abstractmethod
    def get_cost(self) -> float:
        """Calculate total cost including subordinates."""
        pass
    
    @abstractmethod
    def get_headcount(self) -> int:
        """Calculate total headcount including subordinates."""
        pass
    
    @abstractmethod
    def get_structure(self, level: int = 0) -> Dict[str, Any]:
        """Get hierarchical structure as dictionary."""
        pass
    
    def get_path(self) -> str:
        """Get path from root to current component."""
        if self.parent is None:
            return self.name
        return f"{self.parent.get_path()} > {self.name}"


class Employee(OrganizationComponent):
    """Leaf component representing an individual employee."""
    
    def __init__(self, name: str, role: str, salary: float = 0.0):
        super().__init__(name, role)
        self.salary = salary
    
    def get_cost(self) -> float:
        """Get employee's salary."""
        return self.salary
    
    def get_headcount(self) -> int:
        """Individual employee counts as 1."""
        return 1
    
    def get_structure(self, level: int = 0) -> Dict[str, Any]:
        """Get employee details as dictionary."""
        return {
            "name": self.name,
            "role": self.role,
            "level": level,
            "type": "employee",
            "salary": self.salary,
            "path": self.get_path()
        }


class Department(OrganizationComponent):
    """Composite component representing a department."""
    
    def __init__(self, name: str, role: str, budget: float = 0.0):
        super().__init__(name, role)
        self.budget = budget
        self.components: List[OrganizationComponent] = []
    
    def add(self, component: OrganizationComponent) -> None:
        """Add a component to the department."""
        self.components.append(component)
        component.parent = self
    
    def remove(self, component: OrganizationComponent) -> None:
        """Remove a component from the department."""
        self.components.remove(component)
        component.parent = None
    
    def get_cost(self) -> float:
        """Calculate total cost including all subordinates."""
        return sum(component.get_cost() for component in self.components) + self.budget
    
    def get_headcount(self) -> int:
        """Calculate total headcount including all subordinates."""
        return sum(component.get_headcount() for component in self.components)
    
    def get_structure(self, level: int = 0) -> Dict[str, Any]:
        """Get department structure as dictionary."""
        return {
            "name": self.name,
            "role": self.role,
            "level": level,
            "type": "department",
            "budget": self.budget,
            "path": self.get_path(),
            "headcount": self.get_headcount(),
            "total_cost": self.get_cost(),
            "components": [
                component.get_structure(level + 1)
                for component in self.components
            ]
        }


class Organization:
    """Helper class to manage organization structure."""
    
    def __init__(self, name: str):
        self.name = name
        self.root = Department(name, "Organization")
    
    def add_department(self, name: str, role: str, parent: Optional[Department] = None,
                      budget: float = 0.0) -> Department:
        """Add a new department to the organization."""
        department = Department(name, role, budget)
        if parent is None:
            self.root.add(department)
        else:
            parent.add(department)
        return department
    
    def add_employee(self, name: str, role: str, department: Department,
                    salary: float = 0.0) -> Employee:
        """Add a new employee to a department."""
        employee = Employee(name, role, salary)
        department.add(employee)
        return employee
    
    def get_structure(self) -> Dict[str, Any]:
        """Get complete organization structure."""
        return self.root.get_structure()
    
    def get_total_cost(self) -> float:
        """Get total organization cost."""
        return self.root.get_cost()
    
    def get_total_headcount(self) -> int:
        """Get total organization headcount."""
        return self.root.get_headcount()
    
    def find_component(self, name: str) -> Optional[OrganizationComponent]:
        """Find a component by name."""
        def _find(component: OrganizationComponent) -> Optional[OrganizationComponent]:
            if component.name == name:
                return component
            if isinstance(component, Department):
                for child in component.components:
                    result = _find(child)
                    if result:
                        return result
            return None
        
        return _find(self.root)


# Usage Example
def main():
    # Create organization structure
    org = Organization("Tech Corp")
    
    try:
        # Add departments
        engineering = org.add_department("Engineering", "Technical", budget=100000)
        sales = org.add_department("Sales", "Business", budget=50000)
        
        # Add sub-departments
        backend = org.add_department("Backend", "Technical", engineering, budget=40000)
        frontend = org.add_department("Frontend", "Technical", engineering, budget=30000)
        
        # Add employees
        org.add_employee("John Doe", "CTO", engineering, salary=150000)
        org.add_employee("Jane Smith", "Backend Lead", backend, salary=120000)
        org.add_employee("Bob Wilson", "Frontend Lead", frontend, salary=110000)
        org.add_employee("Alice Brown", "Sales Manager", sales, salary=100000)
        
        # Print organization structure
        print("Organization Structure:")
        print(json.dumps(org.get_structure(), indent=2))
        
        # Print statistics
        print(f"\nTotal Headcount: {org.get_total_headcount()}")
        print(f"Total Cost: ${org.get_total_cost():,.2f}")
        
        # Find and print component details
        backend_dept = org.find_component("Backend")
        if backend_dept:
            print("\nBackend Department Details:")
            print(json.dumps(backend_dept.get_structure(), indent=2))
            print(f"Backend Path: {backend_dept.get_path()}")
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 