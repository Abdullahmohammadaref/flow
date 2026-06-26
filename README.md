# Flow

## Overview

Flow is a code base visualizer that is specifically designed to help developers grasp code 
structure, analyze project, and onboard quickly.

## Features
- Supervised machine learning model that predicts file roles.
- Backend API with Flask to send analyzed project details in JSON to requesting clients.
- React frontend to visualize project details with nodes and edges.
- Numbering edges in order based on both their distance from the entry point node and runtime 
import execution order.
- Circular dependencies detection.

## Tech Stack

- `/backend`
  - Python 3.13.13
  - Flask
  - Scikit-Learn
  - Pandas
- `/frontend`
  - Node.js 26.3.0
  - Typescript
  - React + vite
  - React Flow

## Setup
Open command prompt inside preferred directory then execute the following commands in order:
```bash
# Clone repository
git clone https://github.com/Abdullahmohammadaref/flow
# Change to backend application directory
cd backend
# Install required dependencies
pip install -r requirements.txt

# Train Models
py flow.py train

# Analyze project
py flow.py analyze <Project zip file path>


```
Open another terminal inside the project root directory and execute the following commands in order:
```bash
# Change to frontend application directory
cd frontend
# Install required dependencies
npm install
# Run development server
npm run dev
```
Visit `http://localhost:5173/` to see, analyzing, and visualizing projects from backend

