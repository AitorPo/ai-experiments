# Hexagonal Architecture Scaffolding Guide

## 🏗️ Cookie-Cutter-Like Template System

The scaffolding system now works like a **cookie-cutter template** where you can specify a `module_name` parameter to generate a complete hexagonal architecture project with your custom entity names instead of hardcoded "Example" classes.

## 🚀 Quick Start

### Basic Usage (Example entities)
```python
from src.scaffolder.scaffolding import ProjectScaffolder

scaffolder = ProjectScaffolder()
await scaffolder.scaffold_project(
    project_path="/path/to/projects",
    project_name="my_app",
    template_type="hexagonal"
)
```

### Parameterized Usage (Custom entities)
```python
# Generate a Product management system
await scaffolder.scaffold_project(
    project_path="/path/to/projects", 
    project_name="product_management",
    template_type="hexagonal",
    module_name="product"  # 🎯 This creates ProductEntity, ProductService, etc.
)

# Generate a User Profile system
await scaffolder.scaffold_project(
    project_path="/path/to/projects",
    project_name="user_system", 
    template_type="hexagonal",
    module_name="user_profile"  # 🎯 Creates UserProfileEntity, UserProfileService, etc.
)
```

## 📋 Module Name Examples

The `module_name` parameter accepts various formats and automatically generates appropriate class names:

| Input `module_name` | Generated Classes | File Names | URLs | Tables |
|---------------------|-------------------|------------|------|---------|
| `"product"` | `ProductEntity`, `ProductService` | `product.py` | `/products/` | `products` |
| `"user_profile"` | `UserProfileEntity`, `UserProfileService` | `user_profile.py` | `/user-profiles/` | `user_profiles` |
| `"blog-post"` | `BlogPostEntity`, `BlogPostService` | `blog_post.py` | `/blog-posts/` | `blog_posts` |
| `"Order Item"` | `OrderItemEntity`, `OrderItemService` | `order_item.py` | `/order-items/` | `order_items` |
| `null` (default) | `ExampleEntity`, `ExampleService` | `example.py` | `/examples/` | `examples` |

## 🏛️ Generated Architecture

When you specify a `module_name`, the entire hexagonal architecture is generated with your custom names:

### Domain Layer
```
domain/
├── entities/
│   └── {module_name}.py          # Contains {ModuleName}Entity
└── __init__.py
```

### Application Layer  
```
application/
├── services/
│   └── {module_name}_service.py   # Contains {ModuleName}Service
├── ports/
│   ├── driving/
│   │   └── {module_name}_service_port.py      # Contains {ModuleName}ServicePort
│   └── driven/
│       └── {module_name}_repository_port.py   # Contains {ModuleName}RepositoryPort
└── __init__.py
```

### Driven Layer (Database)
```
driven/
├── db/
│   ├── models.py        # Contains {ModuleName}DBO (Django model)
│   ├── mapper.py        # Contains {ModuleName}Mapper  
│   ├── adapter.py       # Contains {ModuleName}RepositoryAdapter
│   ├── admin.py         # Contains {ModuleName}Admin
│   └── migrations/
└── external/
```

### Driving Layer (API)
```
driving/
├── api/
│   └── v1/
│       ├── models.py    # Contains {ModuleName}DTO, {ModuleName}CreateDTO, etc.
│       ├── mapper.py    # Contains {ModuleName}APIMapper
│       ├── adapter.py   # Contains {module_name}_list_create, {module_name}_detail views
│       └── urls.py      # Contains /{module-name}s/ endpoints
└── __init__.py
```

## 🔧 Class Name Generation Rules

The system automatically converts your `module_name` into appropriate naming conventions:

1. **PascalCase** for class names: `ProductEntity`, `UserProfileService`
2. **snake_case** for file/variable names: `product.py`, `user_profile_service.py`  
3. **kebab-case** for URLs: `/products/`, `/user-profiles/`
4. **Pluralized snake_case** for database tables: `products`, `user_profiles`

### Input Normalization
- Handles spaces: `"blog post"` → `BlogPostEntity`
- Handles hyphens: `"order-item"` → `OrderItemEntity`  
- Handles underscores: `"user_profile"` → `UserProfileEntity`
- Mixed formats: `"Product Item"` → `ProductItemEntity`

## 📡 Generated API Endpoints

For module_name `"product"`, you get these REST endpoints:

- `GET /api/v1/products/` - List products
- `POST /api/v1/products/` - Create product  
- `GET /api/v1/products/{id}/` - Get product
- `PUT /api/v1/products/{id}/` - Update product
- `DELETE /api/v1/products/{id}/` - Delete product

## 🗄️ Database Integration

### Django Models (DBOs)
Generated Django model with proper table naming:
```python
class ProductDBO(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "products"  # 🎯 Automatically pluralized
        ordering = ["-created_at"]
```

### Repository Pattern
Complete repository implementation:
```python
class ProductRepositoryAdapter(ProductRepositoryPort):
    async def save(self, entity: ProductEntity) -> ProductEntity: ...
    async def find_by_id(self, entity_id: int) -> Optional[ProductEntity]: ...
    # ... more methods
```

## 🔗 Dependency Injection

The generated code includes proper dependency injection:

```python
# Service factory
def get_product_service() -> ProductService:
    repository = ProductRepositoryAdapter()
    return ProductService(repository)

# Usage in views
@api_view(["GET", "POST"])
async def product_list_create(request):
    service = get_product_service()
    # ... view logic
```

## 🧪 Generated Tests

The scaffolding includes comprehensive test suites for each layer:

```
tests/
├── domain/
│   └── test_entities.py       # Tests for {ModuleName}Entity
├── application/
│   └── test_services.py       # Tests for {ModuleName}Service  
├── driven/
│   └── test_adapters.py       # Tests for {ModuleName}RepositoryAdapter
└── driving/
    └── test_api.py            # Tests for API endpoints
```

## 🎯 Usage with MCP Tools

### Via MCP Server
```json
{
  "project_path": "/path/to/projects",
  "project_name": "ecommerce_system", 
  "template_type": "hexagonal",
  "module_name": "product",
  "cursor_rules": "# Custom rules for ecommerce..."
}
```

### Via REST API
```bash
curl -X POST http://localhost:8000/tools/scaffold_project \
  -H "Content-Type: application/json" \
  -d '{
    "project_path": "/path/to/projects",
    "project_name": "blog_system",
    "template_type": "hexagonal", 
    "module_name": "blog_post"
  }'
```

## 🏗️ Real-World Examples

### E-commerce Product Management
```python
await scaffolder.scaffold_project(
    project_path="/projects",
    project_name="ecommerce",
    template_type="hexagonal",
    module_name="product"
)
# Generates: ProductEntity, ProductService, /api/v1/products/, etc.
```

### User Management System
```python
await scaffolder.scaffold_project(
    project_path="/projects", 
    project_name="user_system",
    template_type="hexagonal",
    module_name="user_profile"
)
# Generates: UserProfileEntity, UserProfileService, /api/v1/user-profiles/, etc.
```

### Blog Platform
```python
await scaffolder.scaffold_project(
    project_path="/projects",
    project_name="blog_platform", 
    template_type="hexagonal",
    module_name="blog_post"
)
# Generates: BlogPostEntity, BlogPostService, /api/v1/blog-posts/, etc.
```

### Order Management
```python
await scaffolder.scaffold_project(
    project_path="/projects",
    project_name="order_system",
    template_type="hexagonal", 
    module_name="order-item"
)
# Generates: OrderItemEntity, OrderItemService, /api/v1/order-items/, etc.
```

## 🔧 Advanced Configuration

### With Cursor Rules
```python
cursor_rules = """
# Project-Specific Rules
- Use async/await for all database operations
- Implement comprehensive error handling
- Follow domain-driven design principles
- Write tests for all business logic
"""

await scaffolder.scaffold_project(
    project_path="/projects",
    project_name="advanced_system",
    template_type="hexagonal",
    module_name="inventory_item", 
    cursor_rules=cursor_rules
)
```

## 🧪 Testing Your Generated Project

After scaffolding, you can immediately:

1. **Install dependencies:**
   ```bash
   cd your_project
   pip install -r requirements.txt
   ```

2. **Run Django migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Start development server:**
   ```bash
   python manage.py runserver
   ```

4. **Run tests:**
   ```bash
   pytest
   ```

5. **Access API:**
   - Admin: `http://localhost:8000/admin/`
   - API: `http://localhost:8000/api/v1/{module-name}s/`

## 🎯 Key Benefits

1. **🚀 Zero Boilerplate**: No more copy-pasting and renaming classes
2. **🏗️ Consistent Architecture**: Every project follows the same hexagonal patterns
3. **📝 Proper Naming**: Automatic conversion between naming conventions
4. **🔗 Complete Integration**: All layers properly connected with dependency injection
5. **🧪 Test Coverage**: Comprehensive test suites included
6. **📖 Documentation**: README and inline documentation generated
7. **⚡ Ready to Run**: Immediately functional Django project

## 🚀 Next Steps

After scaffolding your project:

1. **Customize the Entity**: Modify the generated entity to match your domain model
2. **Add Business Logic**: Implement domain-specific validation in the service layer  
3. **Extend the API**: Add more endpoints as needed
4. **Add Relationships**: Create foreign keys and relationships between entities
5. **Implement Authentication**: Add user authentication and authorization
6. **Deploy**: The project is production-ready with proper architecture

---

**Happy Scaffolding! 🎉** Your hexagonal architecture project is ready for development. 