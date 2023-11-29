from flask import Flask, render_template, redirect, url_for, request
from github import Github
import os
import subprocess
import re

app = Flask(__name__)

# Chemin où les applications seront installées
APPS_FOLDER = os.path.join(os.getcwd(), 'apps')

# Classe pour stocker les informations de l'application
class App:
    def __init__(self, name, preview):
        self.name = name
        self.preview = preview

def is_github_url(url):
    github_pattern = re.compile(r'https://github.com/.+/.+')
    return bool(re.match(github_pattern, url))

def install_application(git_url):
    # Générer le nom du dossier pour l'application
    app_name = git_url.split('/')[-1].replace('.git', '')
    app_folder = os.path.join(APPS_FOLDER, app_name)

    # Cloner le dépôt depuis GitHub
    github = Github()
    repo = github.get_repo(git_url.replace('https://github.com/', '').replace('.git', ''))
    repo.clone_to(app_folder)

    # Extraire une courte prévisualisation du README (par exemple, les premières lignes)
    readme_path = os.path.join(app_folder, 'README.md')
    preview_lines = []
    with open(readme_path, 'r', encoding='utf-8') as readme_file:
        for i, line in enumerate(readme_file):
            preview_lines.append(line)
            if i == 4:  # Limiter à 5 lignes pour une courte prévisualisation
                break

    # Enregistrez la prévisualisation dans un fichier texte
    preview_path = os.path.join(app_folder, 'preview.txt')
    with open(preview_path, 'w', encoding='utf-8') as preview_file:
        preview_file.writelines(preview_lines)

@app.route('/install', methods=['POST'])
def install():
    git_url = request.form.get('git_url')
    # Vérifier si l'URL est de GitHub
    if not is_github_url(git_url):
        # Rediriger vers la page d'accueil avec un message d'erreur
        return redirect(url_for('home', error='Invalid GitHub URL'))

    # Installation de l'application
    install_application(git_url)
    return redirect(url_for('home'))

@app.route('/')
def home():
    # Page d'accueil avec la liste des applications installées
    installed_apps = []
    for app_folder in os.listdir(APPS_FOLDER):
        if os.path.isdir(os.path.join(APPS_FOLDER, app_folder)):
            preview_path = os.path.join(APPS_FOLDER, app_folder, 'preview.txt')
            if os.path.exists(preview_path):
                with open(preview_path, 'r', encoding='utf-8') as preview_file:
                    preview = preview_file.read()

                app = App(name=app_folder, preview=preview)
                installed_apps.append(app)

    return render_template('home.html', apps=installed_apps)

if __name__ == '__main__':
    # Vérifier si le dossier d'installation des applications existe, sinon le créer
    if not os.path.exists(APPS_FOLDER):
        os.makedirs(APPS_FOLDER)

    app.run(debug=True)
