with open('accidentes/services/accidente_service.py', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if 'codigopostal' in line.lower():
            print(f"{i}: {line.strip()}")
