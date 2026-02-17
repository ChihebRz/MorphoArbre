# 🌳 MorphoArbre - Arabic Morphological Analysis Engine

A comprehensive Arabic morphological analysis tool that processes and analyzes Arabic verb forms using advanced data structures (AVL Trees, Hash Tables) and linguistic rules.

## 📋 Features

- **Arabic Verb Morphology Analysis**: Supports 7+ types of Arabic verbs
  - صحيح سالم (Regular verbs)
  - مهموز (Verbs with Hamza)
  - مثال (Weak initial verbs)
  - أجوف (Hollow verbs)
  - ناقص (Defective verbs)
  - مضعّف (Doubled verbs)
  - لفيف (Doubly weak verbs)

- **Advanced Data Structures**: Efficient processing using AVL Trees and Hash Tables
- **Interactive Visualization**: React-based UI for real-time morphological analysis
- **RESTful API**: FastAPI backend for morphological processing

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Node.js** (v18 or higher) and **npm** (v9 or higher)
- **Python** (v3.8 or higher)
- **pip** (Python package manager)

### Check if already installed:

```bash
node --version
npm --version
python3 --version
pip3 --version
```

### Installing Prerequisites (if needed):

#### On Ubuntu/Debian:
```bash
# Install Node.js and npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python and pip
sudo apt-get install python3 python3-pip
```

#### On macOS:
```bash
# Install Node.js and npm (using Homebrew)
brew install node

# Install Python
brew install python3
```

#### On Windows:
- Download Node.js from [nodejs.org](https://nodejs.org/)
- Download Python from [python.org](https://www.python.org/downloads/)

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/ChihebRz/MorphoArbre.git
cd MorphoArbre
```

### 2. Install Frontend Dependencies

```bash
npm install
```

This will install all required npm packages including:
- React & React DOM
- Vite (build tool)
- TypeScript
- Tailwind CSS
- Lucide React (icons)

### 3. Install Backend Dependencies

```bash
pip3 install -r requirements.txt
```

This will install:
- FastAPI (Web framework)
- Uvicorn (ASGI server)
- Arabic text processing libraries (arabic-reshaper, python-bidi)
- Pydantic (data validation)

## 🎯 Running the Application

You need to run both the backend and frontend servers simultaneously.

### Option 1: Using Two Terminal Windows

#### Terminal 1 - Start the Backend Server:

```bash
python3 main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at: `http://localhost:8000`

#### Terminal 2 - Start the Frontend Development Server:

```bash
npm run dev
```

The frontend will be available at: `http://localhost:5173`

### Option 2: Using Background Process

```bash
# Start backend in background
python3 main.py &

# Start frontend
npm run dev
```

## 📦 Available Scripts

### Frontend Scripts

```bash
# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Build Tailwind CSS (production)
npm run build:css

# Watch Tailwind CSS changes (development)
npm run dev:css
```

### Backend Commands

```bash
# Run backend server
python3 main.py

# Run with uvicorn (with auto-reload)
uvicorn main:app --reload

# Run tests
python3 test_morphology.py
```

## 🏗️ Project Structure

```
MorphoArbre/
├── components/          # React components
│   ├── Layout.tsx      # Main layout component
│   └── TreeView.tsx    # Tree visualization component
├── lib/                # Core libraries
│   ├── avlTree.ts      # AVL Tree implementation
│   ├── hashTable.ts    # Hash Table implementation
│   └── morphology.ts   # Morphological analysis logic
├── data/               # Linguistic data
│   ├── roots_data.json # Arabic root dictionary
│   ├── schemes_data.json # Morphological patterns
│   └── rules_verbs.json  # Verb transformation rules
├── App.tsx             # Main React application
├── index.tsx           # Application entry point
├── main.py             # FastAPI backend server
├── types.ts            # TypeScript type definitions
└── README.md           # This file
```

## 🔌 API Endpoints

Once the backend is running, you can access:

- **API Documentation**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`
- **Root Endpoint**: `http://localhost:8000/`

## 📚 Documentation

- [MORPHOLOGIE_GUIDE.md](MORPHOLOGIE_GUIDE.md) - Detailed guide on Arabic morphology
- [GENERATOR_EXPLANATION.md](GENERATOR_EXPLANATION.md) - Explanation of the generation algorithms
- [IMPLEMENTATION_REPORT.md](IMPLEMENTATION_REPORT.md) - Technical implementation details

## 🧪 Testing

Run the morphology tests:

```bash
python3 test_morphology.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

ISC License

## 👨‍💻 Author

ChihebRz

## 🐛 Troubleshooting

### Port Already in Use

If you get a "port already in use" error:

```bash
# For backend (port 8000)
lsof -ti:8000 | xargs kill -9

# For frontend (port 5173)
lsof -ti:5173 | xargs kill -9
```

### Python Module Not Found

Make sure you're in the correct directory and virtual environment:

```bash
pip3 install -r requirements.txt --force-reinstall
```

### Node Modules Issues

If you encounter npm errors:

```bash
rm -rf node_modules package-lock.json
npm install
```

## 💡 Quick Start Example

1. Install dependencies:
   ```bash
   npm install && pip3 install -r requirements.txt
   ```

2. Start both servers:
   ```bash
   # Terminal 1
   python3 main.py
   
   # Terminal 2
   npm run dev
   ```

3. Open your browser to `http://localhost:5173`

4. Enter an Arabic verb root to see morphological analysis!

---

Made with ❤️ for Arabic language processing
