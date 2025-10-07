import os
import re
import shutil
import sys
from datetime import datetime


def backup_file(src_path: str, backup_suffix: str = ".bak") -> str:
    if not os.path.isfile(src_path):
        return ""
    backup_path = src_path + backup_suffix
    shutil.copy2(src_path, backup_path)
    return backup_path


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_text(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def ensure_file(path: str, content: str, overwrite: bool = False) -> bool:
    if os.path.exists(path) and not overwrite:
        return False
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    write_text(path, content)
    return True


def clean_app_py(app_path: str) -> dict:
    report = {
        "removed_lines": [],
        "inserted_config_loader": False,
        "flask_app_line_found": False,
        "modified": False,
    }

    if not os.path.isfile(app_path):
        return report

    original = read_text(app_path)
    lines = original.splitlines()

    # Pattern to remove sensitive direct assignments, e.g., app.config['SECRET_KEY'] = '...'
    sensitive_re = re.compile(r"^\s*app\.config\[[^\]]+\]\s*=")

    new_lines = []
    for idx, line in enumerate(lines, start=1):
        if sensitive_re.search(line):
            report["removed_lines"].append((idx, line))
            report["modified"] = True
            continue
        new_lines.append(line)

    # Insert dynamic config after `app = Flask(__name__)`
    insert_after_index = None
    for i, line in enumerate(new_lines):
        if re.search(r"app\s*=\s*Flask\(\s*__name__\s*\)", line):
            insert_after_index = i
            report["flask_app_line_found"] = True
            break

    config_import_line = "from config import get_config  # ajouté automatiquement"
    config_apply_line = "app.config.from_object(get_config())  # charge la configuration depuis config.py"

    already_has_import = any(l.strip() == config_import_line for l in new_lines)
    already_has_apply = any(l.strip() == config_apply_line for l in new_lines)

    if insert_after_index is not None:
        insert_block = []
        if not already_has_import:
            insert_block.append(config_import_line)
        if not already_has_apply:
            insert_block.append(config_apply_line)
        if insert_block:
            # Insert after the Flask app creation line
            new_lines[insert_after_index + 1:insert_after_index + 1] = insert_block
            report["inserted_config_loader"] = True
            report["modified"] = True

    new_content = "\n".join(new_lines) + ("\n" if not new_lines or not new_lines[-1].endswith("\n") else "")

    if report["modified"]:
        write_text(app_path, new_content)

    return report


def ensure_gitignore(path: str = ".gitignore") -> bool:
    content = """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.venv/
venv/
ENV/
env/
env.bak/
venv.bak/

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
*.db
*.sqlite
*.sqlite3

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# PEP 582; used by e.g. github.com/David-OConnor/pyflow
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.env.*
.venv

# IDEs/editors
.vscode/
.idea/

# OS files
.DS_Store
Thumbs.db
    
# Node
node_modules/

# SQL and dumps
SCRIPT-SQL/
*.sql
*.dump
*.bak
""".lstrip()
    return ensure_file(path, content)


def ensure_env_example(path: str = ".env.example") -> bool:
    content = """
# Exemple de configuration (ne pas mettre de secrets réels)

FLASK_ENV=production
SECRET_KEY=change-me

# Base de données
SQLALCHEMY_DATABASE_URI=postgresql://user:pass@host:5432/dbname
SQLALCHEMY_TRACK_MODIFICATIONS=false

# Mail (optionnel)
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=example@example.com
MAIL_PASSWORD=change-me
MAIL_DEFAULT_SENDER=no-reply@example.com
""".lstrip()
    return ensure_file(path, content)


def ensure_config_py(path: str = "config.py") -> bool:
    content = """
import os


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "false").lower() == "true"

    # Mail
    MAIL_SERVER = os.getenv("MAIL_SERVER", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "0") or 0)
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "false").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "")


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV = "development"


class ProductionConfig(BaseConfig):
    DEBUG = False
    ENV = "production"


def get_config():
    # Priority: ENV then FLASK_ENV
    env = os.getenv("ENV") or os.getenv("FLASK_ENV") or "production"
    env = env.lower()
    if env.startswith("dev"):
        return DevelopmentConfig
    return ProductionConfig
""".lstrip()
    return ensure_file(path, content)


def ensure_requirements(path: str = "requirements.txt") -> bool:
    content = """
Flask
SQLAlchemy
Flask-Mail
Flask-Login
Werkzeug
""".lstrip()
    return ensure_file(path, content)


def ensure_readme(path: str = "README.md") -> bool:
    content = """
# Version publique nettoyée

Ce dépôt a été sécurisé pour publication publique :
- Configuration déplacée dans des variables d'environnement via `config.py`.
- Fichiers sensibles ignorés via `.gitignore`.
- Exemple d'environnement fourni dans `.env.example` (sans secrets).

Avant toute exécution en production, définissez vos variables d'environnement et régénérez vos secrets.
""".lstrip()
    return ensure_file(path, content)


def backup_and_remove_dirs(root: str, dir_names: list) -> list:
    moved = []
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    backup_root = os.path.join(root, f"backup_sensitive_{timestamp}")
    os.makedirs(backup_root, exist_ok=True)

    for d in dir_names:
        p = os.path.join(root, d)
        if os.path.isdir(p):
            dest = os.path.join(backup_root, d)
            try:
                shutil.move(p, dest)
                moved.append((p, dest))
            except Exception as e:
                moved.append((p, f"ERREUR: {e}"))
    return moved


def main() -> int:
    project_root = os.path.abspath(os.path.dirname(__file__))
    os.chdir(project_root)

    report = {
        "app_backup": None,
        "app_changes": {},
        "files_created": [],
        "dirs_moved": [],
    }

    app_py = os.path.join(project_root, "app.py")
    if os.path.isfile(app_py):
        report["app_backup"] = backup_file(app_py)
        report["app_changes"] = clean_app_py(app_py)
    else:
        report["app_changes"] = {"error": "app.py introuvable"}

    if ensure_gitignore():
        report["files_created"].append(".gitignore")
    if ensure_env_example():
        report["files_created"].append(".env.example")
    if ensure_config_py():
        report["files_created"].append("config.py")
    if ensure_requirements():
        report["files_created"].append("requirements.txt")
    if ensure_readme():
        report["files_created"].append("README.md")

    # Optional: move sensitive dirs if exist
    report["dirs_moved"] = backup_and_remove_dirs(project_root, ["instance", "SCRIPT-SQL"])

    # Final report
    print("\n=== Secureify Repo Report ===")
    if report["app_backup"]:
        print(f"Backup créé: {report['app_backup']}")
    else:
        print("Aucun backup app.py (fichier introuvable)")

    if report.get("app_changes", {}).get("removed_lines"):
        print("\nLignes sensibles supprimées dans app.py:")
        for num, txt in report["app_changes"]["removed_lines"]:
            print(f"  - L{num}: {txt}")
    else:
        print("\nAucune ligne sensible supprimée (ou app.py non trouvé).")

    if report.get("app_changes", {}).get("inserted_config_loader"):
        print("Ajout de chargement de configuration après app = Flask(__name__).")
    elif report.get("app_changes", {}).get("flask_app_line_found"):
        print("Chargement de configuration déjà présent.")
    else:
        print("Ligne app = Flask(__name__) non trouvée — insertion non effectuée.")

    if report["files_created"]:
        print("\nFichiers créés:")
        for f in report["files_created"]:
            print(f"  - {f}")

    if report["dirs_moved"]:
        print("\nDossiers sensibles déplacés en sauvegarde:")
        for src, dest in report["dirs_moved"]:
            print(f"  - {src} -> {dest}")

    print("\nRappels de sécurité:")
    print("  1) Vérifiez le backup app.py.bak et le diff.")
    print("  2) Exécutez un scan: gitleaks detect --source .")
    print("     ou: trufflehog filesystem --entropy=False .")
    print("  3) Révoquez et régénérez les clés précédemment exposées.")

    print("\n✅ Le dépôt est prêt à être publié sur GitHub public. Pensez à vérifier app.py.bak et à tourner vos secrets.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrompu par l'utilisateur.")
        raise


