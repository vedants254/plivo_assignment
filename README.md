# Multi-Modal AI Application

A full-stack application for image analysis and document summarization using AI models.

## 🏗️ Project Structure

```
├── backend/                 # Python FastAPI Backend
│   ├── main.py             # Main FastAPI application
│   ├── model_config.py     # Model configurations
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variables template
├── frontend/               # React Frontend
│   ├── public/             # Static files
│   ├── src/                # React source code
│   │   ├── components/     # React components
│   │   ├── App.js          # Main App component
│   │   ├── index.js        # Entry point
│   │   └── index.css       # Global styles
│   └── package.json        # Node.js dependencies
├── api/                    # Vercel serverless functions
│   └── index.py           # Vercel entry point
├── vercel.json            # Vercel configuration
└── README.md              # This file
```

## 🚀 Features

- **Image Analysis**: Upload images and get detailed descriptions using DeepSeek-VL
- **Document Summarization**: Summarize PDF, DOCX, and URLs using Mistral 7B
- **User Authentication**: JWT-based authentication system
- **History Tracking**: View past analyses and summaries
- **Responsive UI**: Clean, modern interface

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Python web framework
- **Hugging Face API**: AI model inference
- **JWT**: Authentication
- **PyMuPDF**: PDF processing
- **BeautifulSoup**: Web scraping

### Frontend
- **React**: UI framework
- **CSS**: Styling
- **Fetch API**: HTTP requests

### Deployment
- **Vercel**: Serverless deployment
- **Hugging Face**: AI model hosting

## 📋 Prerequisites

- Node.js (for frontend development)
- Python 3.11+ (for backend development)
- Hugging Face API token
- Vercel account (for deployment)

## 🔧 Setup Instructions

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

5. Run the backend:
   ```bash
   python main.py
   ```

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm start
   ```

## 🌐 API Endpoints

- `GET /` - Health check
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login
- `POST /image/analyze` - Image analysis
- `POST /doc/summarize` - Document/URL summarization
- `GET /history` - User history

## 🚀 Deployment

### Backend (Vercel)
The backend is automatically deployed to Vercel when you push to the main branch.

### Frontend (Vercel/Netlify)
Deploy the frontend to Vercel or Netlify:

```bash
cd frontend
npm run build
# Upload the build folder to your hosting platform
```

## 🔑 Environment Variables

### Backend (.env)
```
JWT_SECRET=your-jwt-secret
HF_TOKEN=your-huggingface-token
```

## 📝 Usage

1. **Register/Login**: Create an account or login
2. **Image Analysis**: Upload an image to get AI-generated description
3. **Document Summarization**: Upload a document or provide a URL for summarization
4. **View History**: Check your past analyses and summaries

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
