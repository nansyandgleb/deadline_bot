start cmd /k "python app.py"
echo "Ожидайте"
timeout /t 5
start cmd /k "python VKBot.py"
start cmd /k "python notification.py"
python TGBot.py