#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "maxima_snippets.txt"

WXMAXIMA_HEADER = """/* [wxMaxima batch file version 1] [ DO NOT EDIT BY HAND! ]*/
/* [ Created with wxMaxima version 22.04.0 ] */
/* [wxMaxima: comment start ]
https://oeis.org/{oeis_id}
   [wxMaxima: comment end   ] */


/* [wxMaxima: input   start ] */
{body}
/* [wxMaxima: input   end   ] */



/* Old versions of Maxima abort on loading files that end in a comment. */
"Created with wxMaxima 22.04.0"$
"""


def normalize_trailing_contributor_comment(code: str) -> tuple[str, str | None]:
    stripped = code.rstrip()
    match = re.search(r"(?P<comment>/\*.*?\*/)\s*$", stripped, re.DOTALL)
    if not match:
        return code, None

    comment = match.group("comment")
    processed_comment = normalize_contributor_markers(comment)
    body_without_comment = stripped[: match.start("comment")].rstrip()
    if body_without_comment:
        new_code_for_wxm = body_without_comment + "\n" + processed_comment # Use processed comment
    else:
        new_code_for_wxm = processed_comment
    return new_code_for_wxm, processed_comment # Both are now _-less


def normalize_contributor_markers(text: str) -> str:
    """Remove only the paired underscores marking contributor names."""
    return re.sub(
        r"(?<!\w)_+(?P<name>[A-ZÀ-Ý][^_\r\n]*?)_+(?=\s*(?:[,.;:]|\*/|[A-ZÀ-Ý]|\b(?:on|and|by|from)\b|$))",
        r"\g<name>",
        text,
    )


def extract_maxima_snippets(text: str) -> list[tuple[str, str]]:
    lines = text.splitlines()
    snippets: list[tuple[str, str]] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        # Match lines like: %o A000045 (Maxima) ... to extract individual Maxima snippet lines
        match = re.match(r"^%o\s+(?P<oeis_id>[A-Z0-9]+)\s*\(Maxima\)(?P<code_with_comment>.*)$", line)
        if match:
            # We've found a Maxima snippet line. Extract it.
            oeis_id = match.group("oeis_id")
            code_with_comment = match.group("code_with_comment").strip()
            if code_with_comment:
                snippets.append((oeis_id, code_with_comment))

        # Move to the next line regardless of whether it was a snippet or not
        i += 1
    return snippets


def collect_contributor_names(comment: str | None) -> list[str]:
    if not comment:
        return []

    body = re.sub(r"^\s*/\*​\s*", "", comment)
    body = re.sub(r"\s*\*/\s*$", "", body)
    body = body.strip()

    matches = re.findall(r"(?<!\w)(?P<name>[A-Z][A-Za-zÀ-ÿ .'-]+?)(?=,|$)", body)
    cleaned = []
    for name in matches:
        candidate = name.strip()
        if candidate and (" " in candidate or "." in candidate) and candidate.lower() not in {"by", "after", "from", "for", "with", "the", "and"}:
            cleaned.append(candidate)

    return cleaned # Return all collected names


def correct_underscores_in_wxm_comments(root: Path):
    """
    Scans all .wxm files in the given root and its subdirectories,
    finds contributor markers, and rewrites only those markers.
    """
    fixed_count = 0
    for wxm_file_path in root.glob('**/*.wxm'):
        original_content = wxm_file_path.read_text(encoding="utf-8")
        new_content = original_content

        processed_content = re.sub(
            r"/\*.*?\*/",
            lambda match: normalize_contributor_markers(match.group(0)),
            new_content,
            flags=re.DOTALL,
        )

        if processed_content != new_content:
            wxm_file_path.write_text(processed_content, encoding="utf-8")
            fixed_count += 1

    return fixed_count


def write_output_files(snippets: list[tuple[str, str]], root: Path) -> tuple[int, list[str]]:
    contributor_names: list[str] = []
    written = 0
    snippet_counts: dict[str, int] = {}
    snippet_totals: dict[str, int] = {}
    for oeis_id, _ in snippets:
        snippet_totals[oeis_id] = snippet_totals.get(oeis_id, 0) + 1

    for oeis_id, body_line in snippets:
        normalized_body_for_wxm, comment_for_contributor_extraction = normalize_trailing_contributor_comment(body_line)
        contributor_names.extend(collect_contributor_names(comment_for_contributor_extraction))

        folder = root / f"A{oeis_id[1:4]}"
        folder.mkdir(parents=True, exist_ok=True)
        snippet_counts[oeis_id] = snippet_counts.get(oeis_id, 0) + 1
        suffix = (
            f"_{snippet_counts[oeis_id]}"
            if snippet_totals[oeis_id] > 1
            else ""
        )
        output_path = folder / f"{oeis_id}{suffix}.wxm"

        # If file exists, overwrite it with the new snippet. This avoids problematic merging logic.
        final_body_for_wxm_file = normalized_body_for_wxm # Use the cleaned snippet body

        output_text = WXMAXIMA_HEADER.format(oeis_id=oeis_id, body=final_body_for_wxm_file)
        output_path.write_text(output_text, encoding="utf-8")
        written += 1

    unique_contributors = sorted(set(contributor_names))
    return written, unique_contributors


def main(process_maxima_snippets: bool = True) -> None:
    contributors = [] # Initialize contributors for scope

    if process_maxima_snippets:
        if not SOURCE.exists():
            # Create a dummy maxima_snippets.txt for testing if it doesn't exist
            dummy_content = '''%o A000001 (Maxima) Some_contributor_name
%o A000002 (Maxima) Another_Contributor, With_underscore
'''
            print(f"Source file not found: {SOURCE}. Creating a dummy file for demonstration.")
            SOURCE.write_text(dummy_content, encoding="utf-8")

        text = SOURCE.read_text(encoding="utf-8")
        snippets = extract_maxima_snippets(text)
        written, contributors = write_output_files(snippets, ROOT)

        contributors_path = ROOT / "CONTRIBUTORS.md"
        contributors_content = "# Contribuyentes detectados\n\n"
        contributors_content += "Se generó esta lista a partir de los comentarios de contribuyentes encontrados en los snippets de Maxima.\n\n"
        contributors_content += f"Total de contribuyentes únicos: {len(contributors)}\n\n"
        contributors_content += "- " + "\n- ".join(contributors) + "\n"
        contributors_path.write_text(contributors_content, encoding="utf-8")

        print(f"Se escribieron {written} archivos .wxm")

    fixed_files_count = correct_underscores_in_wxm_comments(ROOT)
    print(f"Se corrigieron guiones bajos en {fixed_files_count} archivos .wxm existentes.")

    if process_maxima_snippets:
        print(f"Se registraron {len(contributors)} contribuyentes únicos en {contributors_path.name}")
    elif fixed_files_count > 0:
        print("Solo se realizó la corrección de guiones bajos en archivos existentes. No se generaron archivos .wxm nuevos ni se actualizó CONTRIBUTORS.md basado en snippets.")
    else:
         print("Solo se realizó la corrección de guiones bajos en archivos existentes, pero no se encontraron archivos para corregir.")


if __name__ == "__main__":
    # Para ejecutar el proceso completo (generar archivos .wxm y corregir guiones bajos):
    #main(process_maxima_snippets=True)

    # Para SOLO corregir guiones bajos en archivos .wxm existentes (sin procesar 'maxima_snippets.txt'):
    main(process_maxima_snippets=False)