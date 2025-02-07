# Tabletop audio by Rehvaro
# Version 1.0 (2025-02-02)
import os
import re
from flask import Flask, render_template_string, send_from_directory

app = Flask(__name__)

AUDIO_DIR = "Tabletop Audio"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lecteur Audio</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; background-color: #f4f4f9; color: #333; }
        .grid { display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; padding: 10px; }
        .item { border: 1px solid #ccc; padding: 10px; border-radius: 8px; width: 200px; background-color: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .item button { display: block; width: 100%; margin: 5px 0; padding: 6px; background-color: #007bff; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
        .item button:hover { background-color: #0056b3; }
        #current-track { margin-bottom: 10px; font-size: 1.1em; }
        #controls { margin-bottom: 10px; display: flex; justify-content: center; align-items: center; gap: 10px; }
        #search-container { position: sticky; top: 0; background-color: #f4f4f9; padding: 5px; z-index: 1000; border-bottom: 2px solid #ccc; }
        #search { padding: 6px; width: 70%; max-width: 250px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 4px; }
        #clear-search { cursor: pointer; margin-left: -25px; }
        .radio-group { margin-bottom: 10px; display: flex; justify-content: center; gap: 10px; }
    </style>
</head>
<body>
    <div id="search-container">
        <h1 id="current-track">Aucun fichier en cours</h1>
        <div id="controls">
            <span id="progress">00:00 / 00:00</span>
            <input type="range" id="volume" min="0" max="1" step="0.1" value="1" title="Volume">
            <button onclick="stopAudio()">Stop</button>
        </div>
        <input type="text" id="search" placeholder="Rechercher..." onkeyup="filterItems()">
        <span id="clear-search" onclick="clearSearch()">&#10006;</span>
        <div class="radio-group">
            <label><input type="radio" name="search-type" value="title" checked> Titre</label>
            <label><input type="radio" name="search-type" value="num"> Numéro</label>
            <label><input type="radio" name="search-type" value="filename"> Nom de fichier</label>
        </div>
    </div>
    <div class="grid" id="file-grid">
        {% for num, title, files in sorted_files %}
        <div class="item" data-title="{{ title }}" data-num="{{ num }}" data-filename="{{ files[0][0] }}">
            <small>{{ num }}</small>
            <h3>{{ files[0][1] }}</h3>
            {% for file, label in files %}
            <button onclick="playAudio('{{ file }}', '{{ title }}')">{{ label }}</button>
            {% endfor %}
        </div>
        {% endfor %}
    </div>

    <audio id="audio-player" loop></audio>

    <script>
        const audioPlayer = document.getElementById("audio-player");
        const currentTrack = document.getElementById("current-track");
        const progress = document.getElementById("progress");
        const volumeControl = document.getElementById("volume");
        const searchInput = document.getElementById("search");
        const searchTypeRadios = document.getElementsByName("search-type");

        function fadeAudio(targetVolume, duration, callback) {
            const initialVolume = audioPlayer.volume;
            const volumeChange = targetVolume - initialVolume;
            const stepTime = 50; // 50ms per step
            const steps = duration / stepTime;
            let currentStep = 0;

            function step() {
                currentStep++;
                audioPlayer.volume = initialVolume + (volumeChange * (currentStep / steps));
                if (currentStep < steps) {
                    setTimeout(step, stepTime);
                } else if (callback) {
                    callback();
                }
            }
            step();
        }

        function playAudio(file, title) {
            fadeAudio(0, 2000, function() {
                audioPlayer.src = file;
                audioPlayer.play();
                currentTrack.textContent = "Lecture: " + title;
                fadeAudio(volumeControl.value, 2000);
            });
        }

        function stopAudio() {
            fadeAudio(0, 2000, function() {
                audioPlayer.pause();
                audioPlayer.currentTime = 0;
                currentTrack.textContent = "Aucun fichier en cours";
            });
        }

        volumeControl.addEventListener("input", function() {
            audioPlayer.volume = this.value;
        });

        audioPlayer.addEventListener("timeupdate", function() {
            const currentTime = formatTime(audioPlayer.currentTime);
            const duration = formatTime(audioPlayer.duration);
            progress.textContent = `${currentTime} / ${duration}`;
        });

        function formatTime(seconds) {
            if (isNaN(seconds)) return "00:00";
            const min = Math.floor(seconds / 60);
            const sec = Math.floor(seconds % 60);
            return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
        }

        function filterItems() {
            const search = searchInput.value.toLowerCase();
            const items = document.querySelectorAll(".item");
            const searchType = Array.from(searchTypeRadios).find(radio => radio.checked).value;

            items.forEach(item => {
                const title = item.getAttribute("data-title").toLowerCase();
                const num = item.getAttribute("data-num").toLowerCase();
                const filename = item.getAttribute("data-filename").toLowerCase();

                let match = false;
                if (searchType === "title") {
                    match = title.includes(search);
                } else if (searchType === "num") {
                    match = num === search;
                } else if (searchType === "filename") {
                    match = filename.includes(search) || Array.from(item.querySelectorAll("button")).some(button => {
                        return button.textContent.toLowerCase().includes(search);
                    });
                }

                item.style.display = match ? "block" : "none";
            });
        }

        function clearSearch() {
            searchInput.value = '';
            filterItems();
        }

        window.onload = function() {
            if (searchInput.value) {
                filterItems();
            }
            const savedSearchType = localStorage.getItem('searchType');
            if (savedSearchType) {
                document.querySelector(`input[name="search-type"][value="${savedSearchType}"]`).checked = true;
            }
        };

        searchTypeRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                localStorage.setItem('searchType', this.value);
                filterItems();
            });
        });
    </script>
</body>
</html>
"""

def scan_audio_files(directory):
    files_dict = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".mp3"):
                match = re.match(r"(\d+)_([\w_]+)\.mp3", file)
                if match:
                    num, full_title = match.groups()
                    file_path = f"/{AUDIO_DIR}/{file}"
                    
                    if num not in files_dict:
                        files_dict[num] = []
                    
                    files_dict[num].append((full_title, file_path))
    
    final_files = []
    for num, file_list in files_dict.items():
        file_list.sort()  # Sort by full title to get the smallest lexicographical order
        base_title = file_list[0][0]
        base_title_parts = base_title.split('_')
        
        file_info_list = []
        for full_title, file_path in file_list:
            title_parts = full_title.split('_')
            if len(title_parts) > len(base_title_parts):
                tags = "_".join(title_parts[len(base_title_parts):])
            else:
                tags = ""
            label = full_title.replace('_', ' ') if not tags else tags.replace('_', ' ')
            file_info_list.append((file_path, label))
        
        final_files.append((num, file_list[0][0], file_info_list))
    
    sorted_files = sorted(final_files, key=lambda x: int(x[0]))
    return sorted_files

@app.route("/")
def index():
    sorted_files = scan_audio_files(AUDIO_DIR)
    return render_template_string(HTML_TEMPLATE, sorted_files=sorted_files)

@app.route(f"/{AUDIO_DIR}/<path:filename>")
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)
