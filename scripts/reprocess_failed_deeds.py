"""
Reprocesa escrituras cobradas que quedaron en estado FAILED (INC-4092).

Uso:
    python -m scripts.reprocess_failed_deeds           # dry-run: solo reporta
    python -m scripts.reprocess_failed_deeds --apply   # reprocesa y persiste
"""
import argparse
import json

from app.db import Base, SessionLocal, engine
from app.services.document_service import reprocess_failed_deeds


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="persistir los cambios (por defecto dry-run)")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        results = reprocess_failed_deeds(db, apply=args.apply)
    finally:
        db.close()

    print(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\n{len(results)} escrituras revisadas ({'apply' if args.apply else 'dry-run'})")


if __name__ == "__main__":
    main()
