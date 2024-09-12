scrollBarStyle = """
             QScrollBar:vertical {
                background: #f0f0f0;
                width: 10px;
                border-radius: 5px; /* Make edges round */
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 30px;
                border-radius: 5px; /* Make edges round */
            } """

userMessageBackground = """
    background-color: rgb(10, 10, 10);
    border-radius: 12px;
"""

chatButtonStyle = """
            QPushButton {
                background-color: rgb(50, 50, 50)
                border: outset;
                border-coloer: rgb(255, 255, 255)
                color: rgb(150, 150, 150);
                padding: 10px 24px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 10px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgb(100, 100, 100);
            }
        """

positiveGrowthLabels = """
    color: green;
    font: 12 8pt "Cascadia Mono";
    border-style: none;
    border-width: 0px;
"""

negetiveGrowthLabels = """
    color: red;
    font: 12 8pt "Cascadia Mono";
    border-style: none;
    border-width: 0px;
"""

chatScrollBarStyle = """
             QScrollBar:vertical {
                background: #f0f0f0;
                width: 3px;
                border-radius: 1px; /* Make edges round */
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 10px;
                border-radius: 5px; /* Make edges round */
            } """

 # Customize the buttons with styles
msgBoxStyleSheet = """
    QPushButton {
        background-color: #f0f0f0;
        border: 1px solid #ccc;
        padding: 5px 10px;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: rgb(0, 150, 0);
    }
    QPushButton:pressed {
        background-color: #a0a0a0;
    }
"""

progressBarStyle = """
        QProgressBar {
                border: 2px solid black;
                border-radius: 0px;
                background-color: #E0E0E0;
                text-align: center;
                padding: 1px; /* Adjust padding if necessary */
            }

            QProgressBar::chunk {
                background-color: #00BFFF;
                width: 10px;
                margin: 1px;
            }

            QProgressBar::text {
                color: transparent; /* Hide the text */
            }
        """