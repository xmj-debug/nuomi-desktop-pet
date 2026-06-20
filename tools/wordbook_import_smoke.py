import json
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import ai_moe_pet as app


def write_xlsx(path):
    shared = [
        "academic",
        "学术的",
        "access",
        "",
    ]
    shared_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        + "".join(f"<si><t>{value}</t></si>" for value in shared)
        + "</sst>"
    )
    sheet_xml = """<?xml version="1.0" encoding="UTF-8"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>
    <row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c></row>
    <row r="2"><c r="A2" t="s"><v>2</v></c><c r="B2" t="s"><v>3</v></c></row>
  </sheetData>
</worksheet>"""
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("xl/sharedStrings.xml", shared_xml)
        archive.writestr("xl/worksheets/sheet1.xml", sheet_xml)


def write_docx(path):
    document_xml = """<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>adapt 适应</w:t></w:r></w:p>
    <w:p><w:r><w:t>adequate 充足的</w:t></w:r></w:p>
  </w:body>
</w:document>"""
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document_xml)


def words(items):
    return {item["word"].lower(): item["meaning"] for item in items}


def main():
    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        app.WORDBOOK = tmp / "pet-wordbook.json"
        app.CONFIG = tmp / "pet-config.json"
        app.save_json(app.CONFIG, {"notebook_words": [{"word": "legacy", "meaning": "旧词"}]})
        app.reset_exam_word_cache()

        txt = tmp / "words.txt"
        txt.write_text("abandon 放弃\n1. abstract 抽象的\naccess\n12345\n", encoding="utf-8")
        csv_path = tmp / "words.csv"
        csv_path.write_text("abuse,滥用\naccount,账户\n", encoding="utf-8")
        xlsx = tmp / "words.xlsx"
        write_xlsx(xlsx)
        docx = tmp / "words.docx"
        write_docx(docx)

        txt_items, txt_failed = app.parse_wordbook_file(txt)
        csv_items, csv_failed = app.parse_wordbook_file(csv_path)
        xlsx_items, xlsx_failed = app.parse_wordbook_file(xlsx)
        docx_items, docx_failed = app.parse_wordbook_file(docx)

        assert txt_failed == 1, txt_failed
        assert csv_failed == 0, csv_failed
        assert xlsx_failed == 0, xlsx_failed
        assert docx_failed == 0, docx_failed
        parsed = words(txt_items + csv_items + xlsx_items + docx_items)
        for key in ("abandon", "abstract", "access", "abuse", "account", "academic", "adapt", "adequate"):
            assert key in parsed, key
        assert parsed["access"] != "待补充"

        result = app.merge_wordbook_entries(txt_items + [{"word": "ABANDON", "meaning": "重复"}])
        assert result["added"] == 3, result
        assert result["duplicate"] == 1, result
        merged = app.load_wordbook()
        assert merged[0]["word"].lower() == "abandon"
        assert any(item["word"] == "legacy" for item in merged)
        assert app.exam_word_entries()[0]["word"].lower() == "abandon"

    print("OK wordbook import smoke")


if __name__ == "__main__":
    main()
