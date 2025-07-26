# LotusRPG Backend API

A comprehensive Flask-based API backend for the LotusRPG tabletop RPG platform, featuring user management, content management, forums, and real-time WebSocket support.

## Features

- **Authentication & Authorization**
  - User registration/login with Flask-Security
  - Role-based access control (admin/user)
  - Account lockout protection
  - Session management

- **Content Management System**
  - Hierarchical rulebook organization (Core Rules, Darkholme)
  - Chapter and section management
  - Rich content support (text, tables, images, lists)
  - Full-text search capabilities

- **Forum System**
  - Post creation and management
  - Threaded comments
  - User-specific post filtering
  - Pagination support

- **Admin Dashboard**
  - User management (ban/unban/delete)
  - Role assignment
  - System statistics
  - Content moderation

- **Real-time Features**
  - WebSocket support with Flask-SocketIO
  - Live dice rolling
  - Real-time notifications
  - Admin action broadcasting

- **API Features**
  - RESTful API design
  - Standardized JSON responses
  - CORS support for frontend integration
  - Comprehensive error handling
  - Request validation with Marshmallow

## Tech Stack

- **Backend**: Flask 3.1.1
- **Database**: SQLAlchemy with SQLite (dev) / PostgreSQL (production)
- **Authentication**: Flask-Security-Too
- **API**: Flask-RESTful
- **WebSockets**: Flask-SocketIO
- **Serialization**: Marshmallow
- **Migrations**: Flask-Migrate

## Project Structure

```
lotusrpg-backend/
├── lotusrpg/
│   ├── api/                    # API endpoints
│   │   ├── auth/              # Authentication routes
│   │   ├── admin/             # Admin management routes
│   │   ├── forum/             # Forum routes
│   │   ├── rules/             # Content management routes
│   │   └── users/             # User profile routes
│   ├── schemas/               # Marshmallow schemas
│   ├── models.py              # Database models
│   ├── config.py              # Configuration
│   └── websockets.py          # WebSocket events
├── tests/                     # API tests
├── requirements.txt           # Python dependencies
└── run.py                     # Application entry point
```

## Installation & Setup

### Prerequisites
- Python 3.12+
- pip (Python package manager)

### 1. Clone the repository
```bash
git clone https://github.com/your-username/lotusrpg-backend.git
cd lotusrpg-backend
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows Git Bash
# or
source venv/bin/activate      # On macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up database
```bash
python create_tables.py
```

### 5. Run the application
```bash
python run.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user

### Rules & Content
- `GET /api/v1/rules/{rulebook}/chapters` - Get chapters for rulebook
- `GET /api/v1/rules/sections/{slug}` - Get specific section
- `GET /api/v1/rules/search?q={query}` - Search content

### Forum
- `GET /api/v1/forum/posts` - Get forum posts (paginated)
- `POST /api/v1/forum/posts/create` - Create new post
- `GET /api/v1/forum/posts/{id}` - Get specific post with comments
- `POST /api/v1/forum/posts/{id}/comments` - Add comment to post

### Admin (Admin only)
- `GET /api/v1/admin/dashboard` - Get dashboard statistics
- `GET /api/v1/admin/users` - Get users (paginated, searchable)
- `POST /api/v1/admin/users/{id}/{action}` - User actions (ban/unban/delete)

### User Profile
- `GET /api/v1/users/profile` - Get user profile
- `PUT /api/v1/users/profile` - Update user profile
- `POST /api/v1/users/avatar` - Upload user avatar

## Testing

Run the API test suite:
```bash
# Make sure the server is running in another terminal
python run.py

# In another terminal, run tests
cd tests/api
python test_api.py
```

Or run the debug test for detailed output:
```bash
python debug_test.py
```

## Development Status

✅ **Phase 1 Complete**: Full API backend with authentication, content management, forums, and WebSocket support

🚧 **Phase 2 In Progress**: React frontend development

📋 **Future Phases**: 
- Advanced character tools
- Campaign management
- Enhanced real-time features

## Configuration

Key configuration options in `config.py`:

- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - Flask secret key
- `SECURITY_PASSWORD_SALT` - Password hashing salt
- `CORS_ORIGINS` - Allowed frontend origins

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Project Link: [https://github.com/your-username/lotusrpg-backend](https://github.com/your-username/lotusrpg-backend)