# Flow

## Overview

Flow is a code base visualizer that is specifically designed to help developers grasp code 
structure, analyze project, and onboard quickly.

## 🚧 Project Status
Flow is currently under active development and will be complete before 26.06.2026.

## Features
- Supervised machine learning model that predicts file roles.
- Backend API with Flask to send analyzed project details in JSON to requesting clients.
- React frontend to visualize project details with nodes and edges.
- Numbering edges in order based on both their distance from the entry point node and runtime 
import execution order.
- Circular dependencies detection.

**What's achieved till now?**
- Built the backend to scrape, analyze, and build datasets from coding projects.
- Labeled some of the scraped data manually
- Engineered a multi-model pipeline that currently stratifies and balances data from 
our original dataset to train on 295 file rows and achieve a 75% macro F1-score 
with logistic regression model.
    
**Currently working on:**
- Labeling more data to expand the training dataset and improve other heavy models' output
- Optimizing pipeline
- Developing a React Flow web interface

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
  - Vanilla Extract CSS

## Setup
Open command prompt inside preferred directory then execute the following commands in order:
```bash
# Clone repository
git clone https://github.com/Abdullahmohammadaref/flow
# Change to backend application directory
cd backend
# Install required dependencies
pip install -r requirements.txt
# Start flask server
py server.py
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
Visit `http://localhost:5173/` to start uploading, analyzing, and visualizing projects
