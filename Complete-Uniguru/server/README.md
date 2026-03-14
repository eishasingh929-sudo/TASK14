# UniGuru Backend Server

A production-ready Node.js/Express backend server for the UniGuru AI chatbot application with role-playing capabilities using local Ollama AI models.

## Features

- **Authentication System**: JWT-based authentication with Google OAuth support
- **Guru Management**: Create, manage, and interact with AI gurus with custom personalities
- **Chat System**: Real-time chat with AI gurus using local Ollama models
- **Role-Playing AI**: Each guru has a unique personality and expertise area
- **File Processing**: PDF reading, OCR text scanning, and image processing
- **Security**: Rate limiting, input validation, CORS, and security headers
- **Database**: MongoDB with Mongoose ODM
- **Production Ready**: Error handling, logging, and environment configuration

## Tech Stack

- **Runtime**: Node.js with ES6 modules
- **Framework**: Express.js
- **Database**: MongoDB with Mongoose
- **AI Integration**: Local Ollama for LLM responses
- **Authentication**: JWT + Google OAuth
- **File Processing**: PDF-parse, Tesseract.js, Sharp
- **Security**: Helmet, CORS, Rate limiting
- **Validation**: Express-validator

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Setup

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required environment variables:
- `MONGODB_URI`: Your MongoDB connection string
- `OLLAMA_BASE_URL`: Your local Ollama server URL (default: http://localhost:11434)
- `OLLAMA_NGROK_URL`: Your ngrok URL for external access (optional, takes priority over local)
- `JWT_SECRET`: Secret key for JWT tokens

Required setup:
- Install Ollama and pull the llama3.1 model: `ollama pull llama3.1`
- Optional: Expose Ollama via ngrok for external access: `ngrok http 11434`

### 3. Start the Server

Development mode:
```bash
npm run dev
```

Production mode:
```bash
npm start
```

The server will start on `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/v1/user/signup` - User registration
- `POST /api/v1/user/login` - User login
- `GET /api/v1/user/auth-status` - Check auth status
- `GET /api/v1/user/logout` - Logout user
- `POST /api/v1/auth/google` - Google OAuth login

### Guru Management
- `GET /api/v1/guru/g-g` - Get user's gurus
- `POST /api/v1/guru/n-g/:userid` - Create new guru
- `POST /api/v1/guru/custom-guru/:userid` - Create custom guru
- `GET /api/v1/guru/:id` - Get guru details
- `PUT /api/v1/guru/:id` - Update guru
- `DELETE /api/v1/guru/g-d/:id` - Delete guru
- `GET /api/v1/guru/models` - Get available AI models

### Chat System
- `POST /api/v1/chat/new` - Send chat message
- `GET /api/v1/chat/all-chats` - Get all user chats
- `GET /api/v1/chat/:id` - Get specific chat
- `PUT /api/v1/chat/:id` - Update chat
- `DELETE /api/v1/chat/delete` - Delete all chats
- `DELETE /api/v1/chat/:id` - Delete specific chat

### Features
- `POST /api/v1/feature/pdf/r` - Read PDF content
- `POST /api/v1/feature/pdf/t` - Talk with PDF using AI
- `POST /api/v1/feature/pdf/c` - Create PDF
- `POST /api/v1/feature/image/s` - Scan text from image
- `POST /api/v1/feature/image/e` - Edit image text
- `GET /api/v1/feature/tools` - Get available tools

## Database Models

### User
- Authentication and profile information
- Preferences and settings
- Google OAuth integration

### Guru
- AI personality and expertise
- Custom system prompts for role-playing
- Model settings and statistics

### Chat
- Conversation history
- Message threading
- Chat metadata and settings

## Security Features

- **Rate Limiting**: Different limits for auth, chat, and upload endpoints
- **Input Validation**: Comprehensive validation using express-validator
- **CORS**: Configured for frontend integration
- **Security Headers**: Helmet.js for security headers
- **File Upload**: Secure file handling with size limits
- **Error Handling**: Comprehensive error handling and logging

## Environment Variables

See `.env.example` for all available configuration options.

## Deployment

1. Set `NODE_ENV=production`
2. Configure production MongoDB URI
3. Set secure JWT secrets
4. Configure CORS for production frontend URL
5. Set up SSL/TLS certificates
6. Configure reverse proxy (nginx recommended)

## Development

### Project Structure
```
server/
├── config/          # Configuration files
├── controller/      # Route controllers
├── middleware/      # Custom middleware
├── models/          # Database models
├── routes/          # API routes
├── uploads/         # File uploads directory
├── server.js        # Main server file
└── package.json     # Dependencies
```

### Adding New Features
1. Create model in `models/`
2. Create controller in `controller/`
3. Create routes in `routes/`
4. Add middleware if needed
5. Update server.js to include routes

## License

This project is licensed under the ISC License.
