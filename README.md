# MorphoArbre - Engine for Arabic Morphological Analysis

## Executive Summary

MorphoArbre is a comprehensive software solution for the morphological analysis and processing of Modern Standard Arabic verbal forms. The application integrates advanced data structures (AVL Trees, Hash Tables) with sophisticated linguistic algorithms to provide accurate generation and validation of Arabic word derivatives.

Developed as a final assessment project in Algorithms and Data Structures, MorphoArbre demonstrates the practical application of computer science principles to computational linguistics.

**Project Team:** Chiheb Rezgui, Oussama Dallagi

---

## Table of Contents

1. Project Overview
2. Technical Architecture
3. Features and Capabilities
4. System Requirements
5. Installation Guide
6. Usage Instructions
7. API Documentation
8. Project Structure
9. Technical Details
10. Troubleshooting

---

## 1. Project Overview

### Objective

MorphoArbre addresses the complex challenge of Arabic morphological analysis through an integrated fullstack application. It provides automated tools for:

- Morphological generation: Creating valid word forms from three-character roots using specified morphological patterns
- Morphological validation: Verifying whether a given word can be derived from a specific root
- Automatic verb classification: Identifying verb types based on root characteristics
- Interactive visualization: Displaying hierarchical root structures using AVL Trees

### Scope

The system supports analysis of seven fundamental Arabic verb types:

1. Sahih Salim (صحيح سالم) - Regular verbs
2. Mahmuz (مهموز) - Hamzated verbs
3. Mithal (مثال) - Weak initial verbs
4. Ajwaf (أجوف) - Hollow verbs
5. Naqis (ناقص) - Defective final verbs
6. Mudaaf (مضاعف) - Doubled verbs
7. Lafif (لفيف) - Doubly weak verbs

The application manages over 50 morphological patterns and can process 1000+ root entries with their derived words.

---

## 2. Technical Architecture

### Technology Stack

**Frontend Layer:**
- Framework: React 18 with TypeScript
- Build Tool: Vite
- Styling: Tailwind CSS
- Component Library: Lucide React for icons
- Data Structures: AVL Tree implementation (TypeScript)

**Backend Layer:**
- Framework: FastAPI (Python 3.8+)
- Server: Uvicorn ASGI
- Data Validation: Pydantic
- Core Engine: AVL Tree and Hash Table implementations
- Language Support: arabic-reshaper, python-bidi

**Data Storage:**
- Format: JSON
- Files: roots_data.json, schemes_data.json, verb_rules.txt

### Architecture Overview

The application follows a client-server architecture with separation of concerns:

```
Frontend (React/TypeScript)
    |
    | HTTP REST API (JSON)
    |
Backend (FastAPI/Python)
    |
    | File I/O
    |
Data Layer (JSON Files)
```

---

## 3. Features and Capabilities

### Core Features

1. **Morphological Generation**
   - Apply morphological patterns to roots
   - Generate valid Arabic word forms
   - Support for all seven verb types
   - Automatic transformation rule application

2. **Morphological Validation**
   - Verify word-root correspondence
   - Identify applicable morphological patterns
   - Validate against multiple transformation rules
   - Support for Arabic text normalization

3. **Root Management**
   - Add and delete three-character roots
   - Automatic verb type detection
   - Track derived word frequency
   - Hierarchical organization using AVL Trees

4. **Pattern Management**
   - Create and modify morphological patterns
   - Define transformation rules
   - Efficient pattern lookup using Hash Tables
   - Pattern statistics and analysis

5. **Interactive Visualization**
   - Real-time AVL Tree visualization
   - Root hierarchical structure display
   - Performance metrics and statistics

### Advanced Capabilities

- Automatic normalization of Arabic text (handling diacritics, hamza variants, taa marbuta)
- Multi-pattern validation with ambiguity handling
- Verb type specific transformation rules
- Frequency-based word ranking
- RESTful API for programmatic access

---

## 4. System Requirements

### Minimum Requirements

**Hardware:**
- Processor: Intel Core i5 or equivalent
- RAM: 4 GB minimum
- Storage: 500 MB available space

**Software:**
- Operating System: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- Node.js: Version 18.0.0 or higher
- npm: Version 9.0.0 or higher
- Python: Version 3.8 or higher
- pip: Current version matching Python

### Verification

```bash
node --version      # Should output v18.0.0 or higher
npm --version       # Should output 9.0.0 or higher
python3 --version   # Should output 3.8.0 or higher
pip3 --version      # Should output matching Python version
```

---

## 5. Installation Guide

### Step 1: Clone Repository

```bash
git clone https://github.com/ChihebRz/MorphoArbre.git
cd MorphoArbre
```

### Step 2: Frontend Setup

```bash
npm install
```

This installs the following dependencies:
- React & React DOM (UI framework)
- Vite (build tool and dev server)
- TypeScript (language support)
- Tailwind CSS (styling framework)
- Lucide React (icon library)

### Step 3: Backend Setup

```bash
pip3 install -r requirements.txt
```

This installs the following dependencies:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Pydantic (data validation)
- arabic-reshaper (Arabic text processing)
- python-bidi (bidirectional text handling)

### Step 4: Verify Installation

```bash
# Test frontend
npm run build

# Test backend
python3 main.py
```

---

## 6. Usage Instructions

### Starting the Application

The application requires both frontend and backend servers running simultaneously.

#### Method 1: Dual Terminal Windows

**Terminal 1 - Backend Server:**
```bash
python3 main.py
```

The backend will initialize and listen on http://localhost:8000

**Terminal 2 - Frontend Development Server:**
```bash
npm run dev
```

The frontend will be available at http://localhost:3000

#### Method 2: Using Process Management

```bash
# In background
python3 main.py &
npm run dev
```

### Accessing the Application

Open your web browser and navigate to:
```
http://localhost:3000
```

### Available Build Commands

```bash
npm run dev           # Development server with hot reload
npm run build         # Production build
npm run preview       # Preview production build locally
npm run build:css     # Build Tailwind CSS production
npm run dev:css       # Watch Tailwind CSS development
```

---

## 7. API Documentation

### Base URL

```
http://localhost:8000/api
```

### Interactive Documentation

The API includes automatic documentation accessible at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Core Endpoints

#### Roots Management
- `GET /api/roots` - Retrieve all roots with derived words
- `POST /api/roots` - Add a new root
- `DELETE /api/roots/{root}` - Remove a root

#### Schemes Management
- `GET /api/schemes` - Retrieve all morphological patterns
- `POST /api/schemes` - Add a new pattern
- `PUT /api/schemes/{id}` - Update a pattern
- `DELETE /api/schemes/{id}` - Remove a pattern

#### Analysis Operations
- `POST /api/generate` - Generate word from root and pattern
- `POST /api/validate` - Validate word against root
- `GET /api/verb-types` - Retrieve verb type information

#### Visualization
- `GET /api/roots/visual` - Get AVL tree structure for visualization

---

## 8. Project Structure

```
MorphoArbre/
│
├── Frontend Files
│   ├── App.tsx                    # Main React application component
│   ├── index.tsx                  # Application entry point
│   ├── index.html                 # HTML template
│   ├── index.css                  # Global styles
│   ├── input.css                  # Tailwind input
│   ├── tailwind.css               # Generated Tailwind styles
│   └── vite.config.ts             # Vite configuration
│
├── Components
│   ├── components/Layout.tsx      # Application layout wrapper
│   ├── components/TreeView.tsx    # AVL Tree visualization
│   └── types.ts                   # TypeScript type definitions
│
├── Data Structures (Frontend)
│   ├── lib/avlTree.ts             # Typescript AVL Tree implementation
│   ├── lib/hashTable.ts           # Typescript Hash Table implementation
│   └── lib/morphology.ts          # Morphological analysis utilities
│
├── Backend
│   └── main.py                    # FastAPI server and core logic
│
├── Data Files
│   ├── data/roots_data.json       # Arabic root dictionary
│   ├── data/schemes_data.json     # Morphological patterns database
│   ├── data/verb_rules.txt        # Verb transformation rules
│   └── data/racine.txt            # Plain text root list
│
├── Documentation
│   ├── README.md                  # This file
│   ├── RAPPORT_TECHNIQUE.md       # Technical report
│   ├── MORPHOLOGIE_GUIDE.md       # Morphology guide
│   ├── GENERATOR_EXPLANATION.md   # Generation algorithm details
│   ├── IMPLEMENTATION_REPORT.md   # Implementation notes
│   └── metadata.json              # Project metadata
│
├── Configuration
│   ├── package.json               # NPM dependencies and scripts
│   ├── tsconfig.json              # TypeScript configuration
│   ├── requirements.txt           # Python dependencies
│   └── .gitignore                 # Git ignore rules
│
└── Testing
    └── test_morphology.py         # Unit tests for morphology
```

---

## 9. Technical Details

### Data Structures

#### AVL Tree (Root Management)
- **Implementation Location:** backend in main.py
- **Purpose:** Hierarchical storage of three-character Arabic roots
- **Time Complexity:** O(log n) for insert, search, delete operations
- **Features:** Automatic balancing, in-order traversal, JSON serialization

#### Hash Table (Pattern Management)
- **Implementation Location:** backend in main.py
- **Purpose:** Efficient lookup of morphological patterns
- **Size:** 101 buckets (prime number for distribution)
- **Collision Resolution:** External chaining
- **Time Complexity:** O(1) average case for all operations

### Morphological Algorithm

The system uses a three-stage approach:

1. **Pattern-Based Generation:**
   - Replace root characters (ف, ع, ل) with actual root characters
   - Preserve structural elements and diacritics

2. **Verb-Type Specific Rules:**
   - Apply transformations based on detected verb category
   - Handle weak roots and special cases

3. **Arabic Text Normalization:**
   - Remove diacritical marks
   - Normalize hamza variants
   - Standardize similar characters

### Performance Characteristics

- Root insertion: ~0.5ms
- Pattern lookup: <0.1ms
- Word generation: ~1ms
- Batch operations: O(n) where n is number of operations

---

## 10. Troubleshooting

### Issue: Port Already in Use

**Symptom:** "Address already in use" error on port 8000 or 5173

**Solution:**
```bash
# Find and terminate process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Find and terminate process on port 5173 (frontend)
lsof -ti:5173 | xargs kill -9
```

### Issue: Module Not Found (Python)

**Symptom:** "ModuleNotFoundError" when running main.py

**Solution:**
```bash
pip3 install -r requirements.txt --force-reinstall --upgrade
```

### Issue: Dependencies Installation Failed

**Symptom:** npm or pip installation errors

**Solution:**
```bash
# For npm
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# For pip
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

### Issue: Asian Character Display Issues

**Symptom:** Arabic text appears corrupted or displays incorrectly

**Solution:**
- Ensure you are using a Unicode-compatible terminal
- Check that system locale is set correctly
- Verify that the browser is set to UTF-8 encoding

### Issue: CORS Errors

**Symptom:** "Cross-Origin Request Blocked" errors in browser console

**Solution:**
- Ensure both frontend (5173) and backend (8000) are running
- Check that the API_BASE in App.tsx matches your backend URL
- Verify that FastAPI CORS middleware is enabled

---

## Additional Resources

### Documentation Files
- RAPPORT_TECHNIQUE.md - Comprehensive technical report with algorithms and complexity analysis
- MORPHOLOGIE_GUIDE.md - Detailed guide to Arabic verb morphology
- GENERATOR_EXPLANATION.md - Detailed explanation of generation algorithms

### Testing
```bash
python3 test_morphology.py    # Run unit tests
```

---

## Project Information

**Project Type:** Final Assessment - Algorithms and Data Structures
**Implementation Period:** Academic Semester 2024-2026
**Team:** Chiheb Rezgui, Oussama Dallagi

**GitHub Repository:** https://github.com/ChihebRz/MorphoArbre

---

## License

This project is released under the MIT License.

---

**For technical questions or bug reports, please refer to the technical report (RAPPORT_TECHNIQUE.md) or contact the development team.**

Last Updated: February 2026
