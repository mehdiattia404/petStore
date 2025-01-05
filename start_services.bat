@echo off
start cmd /k "cd services/auth && python app.py"
start cmd /k "cd services/products && python app.py"
start cmd /k "cd services/categories && python app.py"
start cmd /k "cd services/search && python app.py"
start cmd /k "cd services/api-gateway && python app.py"
