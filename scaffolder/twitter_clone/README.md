# Twitter Clone - Hexagonal Architecture

A full-featured Twitter-like social media platform built with Django following hexagonal architecture principles. This project demonstrates clean architecture patterns, domain-driven design, and modern Python development practices.

## 🚀 Features

### Core Social Media Features
- **User Management**: Registration, authentication, profiles with bios, avatars, and banners
- **Posts (Tweets)**: Create, read, update, delete posts with 280 character limit
- **Social Interactions**: Follow/unfollow users, like posts, retweets, quote tweets
- **Replies & Threads**: Threaded conversations and reply chains
- **Media Support**: Image, video, and GIF attachments with metadata
- **Visibility Control**: Public, followers-only, and private posts
- **Search**: Full-text search for users and posts
- **Timeline**: Personalized feeds based on followed users
- **Hashtags**: Trending topics and hashtag tracking
- **Real-time Features**: Ready for WebSocket integration

### Technical Features
- **Hexagonal Architecture**: Clean separation of concerns with domain, application, and infrastructure layers
- **Async Support**: Built for high-performance async operations
- **Domain-Driven Design**: Rich domain entities with business logic
- **CQRS Pattern**: Separated read and write operations
- **Repository Pattern**: Abstract data access with multiple implementations
- **Dependency Injection**: Loose coupling through interface-based design
- **Comprehensive Testing**: Unit and integration tests across all layers
- **API Documentation**: RESTful API with comprehensive endpoints

## 🏗️ Architecture

This project follows hexagonal architecture (ports and adapters) with clear separation of layers:

```
┌─────────────────────────────────────┐
│             Domain Layer            │
│   - User, Post, Follow, Like        │
│   - Business rules and validation   │
│   - Pure Python, no dependencies    │
└─────────────────────────────────────┘
                    ↑
┌─────────────────────────────────────┐
│          Application Layer          │
│   - User, Post, Social Services     │
│   - Use cases and orchestration     │
│   - Port interfaces                 │
└─────────────────────────────────────┘
                 ↑     ↓
┌─────────────────┐   ┌─────────────────┐
│  Driving Layer  │   │  Driven Layer   │
│  - REST API     │   │  - Database     │
│  - Controllers  │   │  - Repositories │
│  - DTOs         │   │  - Adapters     │
│  - Mappers      │   │  - Django ORM   │
└─────────────────┘   └─────────────────┘
```

### Domain Layer (`domain/`)
- **Entities**: Core business objects (User, Post, Follow, Like)
- **Value Objects**: MediaAttachment, PostType, PostVisibility
- **Business Rules**: Validation, constraints, and domain logic

### Application Layer (`application/`)
- **Services**: Business logic orchestration
- **Ports**: Interfaces for external dependencies
  - **Driving Ports**: Input interfaces (service contracts)
  - **Driven Ports**: Output interfaces (repository contracts)

### Driving Layer (`driving/api/v1/`)
- **Controllers**: HTTP request handling
- **DTOs**: Data transfer objects for API communication
- **Mappers**: Entity ↔ DTO conversion
- **Serializers**: Request/response formatting

### Driven Layer (`driven/db/`)
- **Models**: Django ORM models (DBOs)
- **Repositories**: Data access implementations
- **Mappers**: Entity ↔ DBO conversion
- **Migrations**: Database schema management

## 📋 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout

### User Management
- `GET /api/v1/users/{username}` - Get user profile
- `PUT /api/v1/users/profile` - Update profile
- `GET /api/v1/users/search?q={query}` - Search users

### Posts
- `POST /api/v1/posts` - Create post
- `GET /api/v1/posts/{id}` - Get specific post
- `POST /api/v1/posts/reply` - Create reply
- `POST /api/v1/posts/{id}/retweet` - Retweet post
- `POST /api/v1/posts/quote` - Create quote tweet
- `GET /api/v1/timeline` - Get user timeline
- `GET /api/v1/users/{username}/posts` - Get user's posts
- `GET /api/v1/posts/search?q={query}` - Search posts

### Social Interactions
- `POST /api/v1/social/follow` - Follow user
- `DELETE /api/v1/social/follow/{user_id}` - Unfollow user
- `POST /api/v1/posts/{id}/like` - Like post
- `DELETE /api/v1/posts/{id}/like` - Unlike post

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- pip or pipenv
- Git

### Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd twitter_clone
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Database setup**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

5. **Run development server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/v1/`

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific layer tests
pytest tests/domain/
pytest tests/application/
pytest tests/driven/
pytest tests/driving/
```

## 📊 Example Usage

### Register a new user
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword",
    "display_name": "John Doe",
    "bio": "Software developer and coffee enthusiast"
  }'
```

### Create a post
```bash
curl -X POST http://localhost:8000/api/v1/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "content": "Just shipped a new feature! 🚀 #coding #django",
    "visibility": "public",
    "is_sensitive": false
  }'
```

## 🚀 Key Features Implemented

### User System
- Custom user model extending Django's AbstractUser
- Profile management with social stats
- Privacy controls and verification status
- Search functionality

### Post System
- 280-character limit enforcement
- Rich media attachment support
- Post types: original, retweet, quote tweet, reply
- Threading and conversation support
- Visibility controls (public, followers-only, private)

### Social Features
- Follow/unfollow relationships with status tracking
- Like system with engagement metrics
- Real-time ready architecture
- Hashtag support and trending capabilities

### Technical Implementation
- Async-ready codebase throughout
- Comprehensive input validation
- Domain-driven design patterns
- Clean API with proper error handling
- Extensive test coverage

This Twitter clone showcases enterprise-grade architecture patterns while maintaining the simplicity and familiarity of the Twitter user experience.
