from __future__ import annotations

import re

from graphrag_lab.schema import Triple


PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(?P<s>.+?) was founded by (?P<o>.+?) in (?P<year>\d{4})\.", re.I), "FOUNDED_BY"),
    (re.compile(r"(?P<s>.+?) was founded by (?P<o>.+?)\.", re.I), "FOUNDED_BY"),
    (re.compile(r"(?P<s>.+?) was founded by .+? in (?P<year>\d{4})\.", re.I), "FOUNDED_IN"),
    (re.compile(r"(?P<s>.+?) is an? (?P<o>.+?)\.", re.I), "IS_A"),
    (re.compile(r"(?P<s>.+?) develops (?P<o>.+?)\.", re.I), "DEVELOPS"),
    (re.compile(r"(?P<s>.+?) acquired (?P<o>.+?)\.", re.I), "ACQUIRED"),
    (re.compile(r"(?P<s>.+?) invested in (?P<o>.+?)\.", re.I), "INVESTED_IN"),
    (re.compile(r"(?P<s>.+?) partnered with (?P<o>.+?)\.", re.I), "PARTNERED_WITH"),
    (re.compile(r"(?P<s>.+?) formerly worked at (?P<o>.+?)\.", re.I), "FORMERLY_WORKED_AT"),
    (re.compile(r"(?P<s>.+?) works at (?P<o>.+?)\.", re.I), "WORKS_AT"),
    (re.compile(r"(?P<s>.+?) is the CEO of (?P<o>.+?)\.", re.I), "CEO_OF"),
    (re.compile(r"(?P<s>.+?) is based in (?P<o>.+?)\.", re.I), "BASED_IN"),
    (re.compile(r"(?P<s>.+?) co-founded (?P<o>.+?)\.", re.I), "CO_FOUNDED"),
    (re.compile(r"(?P<s>.+?) supplies (?P<o>.+?) to (?P<targets>.+?)\.", re.I), "SUPPLIES_TO"),
    (re.compile(r"(?P<s>.+?) hired several (?P<o>.+?) employees\.", re.I), "HIRED_FROM"),
]


def split_objects(text: str) -> list[str]:
    cleaned = text.replace(" and ", ", ")
    return [part.strip() for part in cleaned.split(",") if part.strip()]


def normalize_entity(value: str) -> str:
    value = value.strip().strip('"').strip("'")
    value = re.sub(r"\balso\b", "", value, flags=re.I)
    value = re.sub(r"\s+", " ", value)
    return value


def extract_triples_from_doc(title: str, text: str) -> list[Triple]:
    triples: list[Triple] = []
    sentences = [sentence.strip() + "." for sentence in text.split(".") if sentence.strip()]

    for sentence in sentences:
        for pattern, predicate in PATTERNS:
            match = pattern.fullmatch(sentence)
            if not match:
                continue

            subject = normalize_entity(match.group("s"))
            if predicate == "FOUNDED_BY":
                for founder in split_objects(match.group("o")):
                    triples.append(Triple(subject, predicate, normalize_entity(founder), title))
                if "year" in match.groupdict() and match.group("year"):
                    triples.append(Triple(subject, "FOUNDED_IN", match.group("year"), title))
            elif predicate == "SUPPLIES_TO":
                for target in split_objects(match.group("targets")):
                    triples.append(Triple(subject, predicate, normalize_entity(target), title))
            elif predicate == "HIRED_FROM":
                source_company = normalize_entity(match.group("o"))
                if source_company.endswith(" AI"):
                    source_company = source_company
                triples.append(Triple(subject, predicate, source_company, title))
            elif predicate == "FOUNDED_IN":
                triples.append(Triple(subject, predicate, match.group("year"), title))
            else:
                for obj in split_objects(match.group("o")):
                    triples.append(Triple(subject, predicate, normalize_entity(obj), title))
            break

    return deduplicate_triples(triples)


def deduplicate_triples(triples: list[Triple]) -> list[Triple]:
    seen: set[tuple[str, str, str]] = set()
    output: list[Triple] = []
    for triple in triples:
        key = (triple.subject.lower(), triple.predicate, triple.object.lower())
        if key not in seen:
            seen.add(key)
            output.append(triple)
    return output


def extract_triples(docs: list[dict[str, str]]) -> list[Triple]:
    triples: list[Triple] = []
    for doc in docs:
        triples.extend(extract_triples_from_doc(doc["title"], doc["text"]))
    return deduplicate_triples(triples)
