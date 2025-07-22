# FitCount Pro - AI Fitness Tracker


**FitCount Pro** is a modern, offline-first desktop fitness assistant that uses your webcam to track physical exercises in real-time. Plan your workout, let the AI count your reps and sets, and get a summary of your session, all with a clean, intuitive UI.

---

## ✨ Features

-   **Workout Planner**: Define custom workouts with specific exercises, sets, and reps before you start.
-   **Real-Time Pose Detection**: Utilizes MediaPipe to track 33 body landmarks accurately.
-   **Automatic Rep & Set Counting**: Intelligent logic counts full reps and automatically advances through your planned workout.
-   **Multi-Exercise Support**: Comes with pre-configured tracking for:
    -   Bicep Curls
    -   Squats
    -   Push-ups
-   **Modern UI**: A polished, responsive, and beautiful dark-themed interface built with Tkinter.
-   **Session Summary**: Get an end-of-session popup summarizing all completed sets and total reps.
-   **Local Data Logging**: All session data is saved locally to a `session_log.csv` file for privacy and easy progress tracking.
-   **Extensible Design**: The modular code structure makes it easy to add new exercises.

---

## 🛠️ Tech Stack

-   **Python 3**: Core programming language.
-   **OpenCV**: For handling the webcam feed.
-   **MediaPipe**: For high-fidelity pose estimation.
-   **Tkinter**: For the graphical user interface.
-   **Pillow**: For integrating OpenCV images with Tkinter.

---

## 🚀 Getting Started

### Prerequisites

-   Python 3.8 or higher
-   A webcam connected to your computer.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/huzaifakhallid/FitCountPro.git
    cd FitCountPro
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    # On Windows
    python -m venv venv
    venv\Scripts\activate

    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

To start the tracker, run the `main.py` script from the root `FitCountPro/` directory:

```bash
python src/main.py
```

---


## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/your-username/FitCountPro/issues).

## 🔐 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
