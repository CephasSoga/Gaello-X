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