# Tabletop audio Player
Un simple script python pour jouer vos fichiers audio venant de Tabletop Audio (https://tabletopaudio.com/) et supportant les variants obtenus via leur Patreon (https://www.patreon.com/c/tabletopaudio)
![Capture d'écran 2025-02-02 121539](https://github.com/user-attachments/assets/ec2abfbb-6e58-4e73-bd98-10e1406b666a)

## Installation
Pour l'utiliser rien de plus simple
* Installez python 3 sur votre PC.
* Puis dans un terminal installez le plugin flask
```bash
python3 -m pip install flask waitress
```

## Utilisation
* Editez la ligne AUDIO_DIR = "Tabletop Audio" dans le script pour pointer vers le dossier contenant les fichiers Tabletop Audio.
* Les fichiers doivent avoir gardé leur nom et format par défaut tel que founis par Tabletop Audio.
* Ouvrez un terminal dans le dossier ou se trouve le script python et tappez la commande suivante :
```bash
python3 Player.py
```
Puis d'aller dans votre navigateur dans http://127.0.0.1:5000/
