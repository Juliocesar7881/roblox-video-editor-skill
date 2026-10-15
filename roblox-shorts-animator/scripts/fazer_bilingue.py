"""Nome antigo do produtor de Shorts (quando saiam em portugues e espanhol). Hoje e so portugues: use
fazer_short.py; este arquivo so repassa os argumentos para ele."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fazer_short import main  # noqa: E402

if __name__ == '__main__':
    main()
