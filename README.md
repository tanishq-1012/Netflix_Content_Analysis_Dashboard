# 🎬 Netflix Content Strategy Dashboard

An interactive Streamlit dashboard that visualizes and analyzes Netflix content and viewer engagement trends using a clean, dynamic interface.

![Streamlit App](https://img.shields.io/badge/Built%20with-Streamlit-orange)
![Status](https://img.shields.io/badge/status-active-success)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 📊 Overview

This project provides a powerful dashboard to explore and visualize the Netflix 2023 content dataset. Users can interactively analyze content distribution, language trends, seasonality, and holiday impacts on viewer behavior.

### 🔍 Key Features

- 📅 Time-based trend analysis (day, month, season)
- 🌍 Top languages and countries visualization
- 🔥 Holiday content consumption patterns
- 📈 Bar charts, pie charts, heatmaps, line plots
- 📁 Upload your own dataset or use default CSV

## 📁 Folder Structure

netflix-dashboard/
│
├── app.py # Main Streamlit dashboard code
├── netflix_content_2023.csv # Sample dataset
├── requirements.txt # Dependencies
└── README.md # Project documentation

## 🚀 Installation & Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/your-username/netflix-dashboard.git
cd netflix-dashboard

### 2. Install dependencies

pip install -r requirements.txt

3. Run the dashboard

streamlit run app.py

# 📂 Dataset

The sample dataset netflix_content_2023.csv includes the following columns:

Title, Language, Release_Date, Views, Duration, etc.
Used to explore patterns in global content consumption and release strategies.
