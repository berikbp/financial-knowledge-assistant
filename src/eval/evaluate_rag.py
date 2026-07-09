from src.retrieval.pipeline import RetrievalPipeline
from src.generation.answer_generator import AnswerGenerator
import re

EVAL_CASES = [
    {
        "id": "inflation_kz_2026",
        "query": "Какие факторы влияли на инфляцию в Казахстане в 2026 году?",
        "filters": {
            "source": "NationalBank",
            "year": 2026,
            "document_type": "monetary_policy_report",
        },
        "expected_sources": ["NationalBank"],
        "expected_document_types": ["monetary_policy_report"],
        "expected_keywords": [
            "инфляционные ожидания",
            "внешнего инфляционного давления",
            "мировых цен",
            "продукты питания",
        ],
        "expected_concepts": [
            "inflation expectations",
            "external inflation pressure",
            "global food prices",
            "quasi-fiscal stimulus",
        ],
    },
    {
        "id": "halyk_financial_statement",
        "query": "What line items are included in Halyk Bank's consolidated statement of profit or loss for 2025?",
        "filters": {
            "source": "HalykBank",
            "document_type": "financial_statement",
        },
        "expected_sources": ["HalykBank"],
        "expected_document_types": ["financial_statement"],
        "expected_keywords": [
            "interest income",
            "interest expense",
            "net interest income",
            "fee and commission income",
        ],
        "expected_concepts": [
            "interest income",
            "interest expense",
            "net interest income",
            "fee and commission income",
        ],
    },
    {
        "id": "aml_law",
        "query": "Какие меры предусмотрены против отмывания доходов?",
        "filters": {
            "source": "BankingRegulation",
            "document_type": "aml_law",
        },
        "expected_sources": ["BankingRegulation"],
        "expected_document_types": ["aml_law"],
        "expected_keywords": [
            "отмыванию",
            "финансированию терроризма",
            "финансового мониторинга",
        ],
        "expected_concepts": [
            "AML programs",
            "state policy",
            "financial monitoring",
            "training",
            "risk reduction",
        ],
    },
]

# ------------------------------------------------------------------------------------
def check_citations(answer: str) -> dict:
    citation_pattern = r"\[\d+\]"
    citations = re.findall(citation_pattern, answer)

    return {
        "citation_pass": len(citations) > 0,
        "citations": sorted(set(citations)),
    }


def check_answer_keywords(
    answer: str,
    expected_keywords: list[str],
    min_matches: int = 2,
) -> dict:
    normalized_answer = normalize_text(answer)

    found_keywords = []
    missing_keywords = []

    for keyword in expected_keywords:
        normalized_keyword = normalize_text(keyword)

        if normalized_keyword in normalized_answer:
            found_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    return {
        "answer_keyword_pass": len(found_keywords) >= min_matches,
        "answer_found_keywords": found_keywords,
        "answer_missing_keywords": missing_keywords,
        "answer_keyword_coverage": len(found_keywords) / max(len(expected_keywords), 1),
    }



def evaluate_answer_case(case: dict, results, answer_generator: AnswerGenerator) -> dict:
    answer = answer_generator.generate_answer(
        query=case['query'],
        results=results
    )

    citation_report = check_citations(answer)

    keyword_report = check_answer_keywords(
        answer=answer,
        expected_keywords=case.get("expected_keywords", []),
        min_matches=2,
    )

    return {
        "answer": answer,
        "answer_not_empty": len(answer.strip()) > 0,
        "citation_pass": citation_report["citation_pass"],
        "citations": citation_report["citations"],
        "answer_keyword_pass": keyword_report["answer_keyword_pass"],
        "answer_found_keywords": keyword_report["answer_found_keywords"],
        "answer_missing_keywords": keyword_report["answer_missing_keywords"],
    }

def print_answer_report(report: dict) -> None:
    print("\nGenerated answer:")
    print("-" * 100)
    print(report["answer"])
    print("-" * 100)

    print(f"Answer not empty: {report['answer_not_empty']}")

    print(f"Citation check: {report['citation_pass']}")
    print(f"Citations found: {report['citations']}")

    print(f"Citation validity check: {report['citation_validity_pass']}")
    print(f"Used citation numbers: {report['used_citations']}")
    print(f"Invalid citations: {report['invalid_citations']}")

    print(f"Answer keyword check: {report['answer_keyword_pass']}")
    print(f"Answer keyword coverage: {report['answer_keyword_coverage']:.2f}")
    print(f"Answer found keywords: {report['answer_found_keywords']}")
    print(f"Answer missing keywords: {report['answer_missing_keywords']}")

    print(f"Completeness check: {report['completeness_pass']}")
    print(f"Concept coverage: {report['concept_coverage']:.2f}")
    print(f"Found concepts: {report['found_concepts']}")
    print(f"Missing concepts: {report['missing_concepts']}")

    print("=" * 100)
# ------------------------------------------------------------------------------------


def check_answer_completeness(
    answer: str,
    expected_concepts: list[str],
    min_matches: int = 2,
) -> dict:
    normalized_answer = normalize_text(answer)



    concept_aliases = {
    "inflation expectations": [
        "инфляционные ожидания",
        "инфляционных ожиданий",
        "инфляционными ожиданиями",
        "инфляционн",
        "inflation expectations",
    ],
    "external inflation pressure": [
        "внешнего инфляционного давления",
        "внешнее инфляционное давление",
        "внешним инфляционным давлением",
        "внешн",
        "инфляционн",
        "давлен",
        "external inflation pressure",
    ],
    "global food prices": [
        "мировых цен на продукты питания",
        "мировые цены на продукты питания",
        "мировых цен",
        "продукты питания",
        "продовольственные товары",
        "global food prices",
        "food prices",
    ],
    "quasi-fiscal stimulus": [
        "квазифискальное стимулирование",
        "квазифискального импульса",
        "квазифискальн",
        "quasi-fiscal stimulus",
    ],

    "interest income": [
        "interest income",
    ],
    "interest expense": [
        "interest expense",
    ],
    "net interest income": [
        "net interest income",
        "net interest income before credit loss expense",
    ],
    "fee and commission income": [
        "fee and commission income",
        "fee and commission",
    ],

    "AML programs": [
        "программы по противодействию",
        "противодействия легализации",
        "противодействие легализации",
        "aml programs",
    ],
    "state policy": [
        "государственная политика",
        "state policy",
    ],
    "financial monitoring": [
        "финансового мониторинга",
        "финансовый мониторинг",
        "financial monitoring",
    ],
    "training": [
        "обучен",
        "повышени",
        "повышения квалификации",
        "training",
    ],
    "risk reduction": [
        "снижени",
        "рисков",
        "снижению рисков",
        "risk reduction",
    ],
    }

    found_concepts = []
    missing_concepts = []

    for concept in expected_concepts:
        aliases = concept_aliases.get(concept, [concept])

        concept_found = any(
            normalize_text(alias) in normalized_answer
            for alias in aliases
        )

        if concept_found:
            found_concepts.append(concept)
        else:
            missing_concepts.append(concept)

    return {
        "completeness_pass": len(found_concepts) >= min_matches,
        "found_concepts": found_concepts,
        "missing_concepts": missing_concepts,
        "concept_coverage": len(found_concepts) / max(len(expected_concepts), 1),
    }


def check_citation_validity(answer: str, results) -> dict:
    citation_pattern = r"\[(\d+)\]"
    citation_numbers = [int(num) for num in re.findall(citation_pattern, answer)]

    valid_numbers = set(range(1, len(results) + 1))

    invalid_citations = [
        citation
        for citation in citation_numbers
        if citation not in valid_numbers
    ]

    return {
        "citation_validity_pass": len(invalid_citations) == 0,
        "used_citations": sorted(set(citation_numbers)),
        "invalid_citations": invalid_citations,
    }


def evaluate_answer_case(
    case: dict,
    results,
    answer_generator: AnswerGenerator,
) -> dict:
    answer = answer_generator.generate_answer(
        query=case["query"],
        results=results,
    )

    citation_report = check_citations(answer)

    citation_validity_report = check_citation_validity(
        answer=answer,
        results=results,
    )

    keyword_report = check_answer_keywords(
        answer=answer,
        expected_keywords=case.get("expected_keywords", []),
        min_matches=2,
    )

    completeness_report = check_answer_completeness(
        answer=answer,
        expected_concepts=case.get("expected_concepts", []),
        min_matches=2,
    )

    return {
        "answer": answer,
        "answer_not_empty": len(answer.strip()) > 0,

        "citation_pass": citation_report["citation_pass"],
        "citations": citation_report["citations"],

        "citation_validity_pass": citation_validity_report["citation_validity_pass"],
        "used_citations": citation_validity_report["used_citations"],
        "invalid_citations": citation_validity_report["invalid_citations"],

        "answer_keyword_pass": keyword_report["answer_keyword_pass"],
        "answer_found_keywords": keyword_report["answer_found_keywords"],
        "answer_missing_keywords": keyword_report["answer_missing_keywords"],
        "answer_keyword_coverage": keyword_report["answer_keyword_coverage"],

        "completeness_pass": completeness_report["completeness_pass"],
        "found_concepts": completeness_report["found_concepts"],
        "missing_concepts": completeness_report["missing_concepts"],
        "concept_coverage": completeness_report["concept_coverage"],
    }


# ------------------------------------------------------------------------------------

def summarize_reports(reports: list[dict]) -> dict:
    total = len(reports)

    if total == 0:
        return {
            "total_cases": 0,
        }

    retrieval_source_passes = sum(
        report["retrieval"]["source_pass"]
        for report in reports
    )

    retrieval_type_passes = sum(
        report["retrieval"]["type_pass"]
        for report in reports
    )

    retrieval_keyword_passes = sum(
        report["retrieval"]["keyword_pass"]
        for report in reports
    )

    answer_not_empty_passes = sum(
        report["answer"]["answer_not_empty"]
        for report in reports
    )

    citation_passes = sum(
        report["answer"]["citation_pass"]
        for report in reports
    )

    citation_validity_passes = sum(
        report["answer"]["citation_validity_pass"]
        for report in reports
    )

    answer_keyword_passes = sum(
        report["answer"]["answer_keyword_pass"]
        for report in reports
    )

    completeness_passes = sum(
        report["answer"]["completeness_pass"]
        for report in reports
    )

    average_answer_keyword_coverage = sum(
        report["answer"]["answer_keyword_coverage"]
        for report in reports
    ) / total

    average_concept_coverage = sum(
        report["answer"]["concept_coverage"]
        for report in reports
    ) / total

    return {
        "total_cases": total,
        "retrieval_source_pass_rate": retrieval_source_passes / total,
        "retrieval_type_pass_rate": retrieval_type_passes / total,
        "retrieval_keyword_pass_rate": retrieval_keyword_passes / total,
        "answer_not_empty_rate": answer_not_empty_passes / total,
        "citation_pass_rate": citation_passes / total,
        "citation_validity_pass_rate": citation_validity_passes / total,
        "answer_keyword_pass_rate": answer_keyword_passes / total,
        "completeness_pass_rate": completeness_passes / total,
        "average_answer_keyword_coverage": average_answer_keyword_coverage,
        "average_concept_coverage": average_concept_coverage,
    }




def print_summary_report(summary: dict) -> None:
    print("\n" + "#" * 100)
    print("EVALUATION SUMMARY")
    print("#" * 100)

    print(f"Total cases: {summary['total_cases']}")

    print(f"Retrieval source pass rate: {summary['retrieval_source_pass_rate']:.2f}")
    print(f"Retrieval type pass rate: {summary['retrieval_type_pass_rate']:.2f}")
    print(f"Retrieval keyword pass rate: {summary['retrieval_keyword_pass_rate']:.2f}")

    print(f"Answer not empty rate: {summary['answer_not_empty_rate']:.2f}")
    print(f"Citation pass rate: {summary['citation_pass_rate']:.2f}")
    print(f"Citation validity pass rate: {summary['citation_validity_pass_rate']:.2f}")

    print(f"Answer keyword pass rate: {summary['answer_keyword_pass_rate']:.2f}")
    print(f"Completeness pass rate: {summary['completeness_pass_rate']:.2f}")

    print(f"Average answer keyword coverage: {summary['average_answer_keyword_coverage']:.2f}")
    print(f"Average concept coverage: {summary['average_concept_coverage']:.2f}")

    print("#" * 100)






def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def check_expected_keywords(results, expected_keywords: list[str]) -> dict:
    combined_text = " ".join(result.text for result in results)
    combined_text = normalize_text(combined_text)

    found_keywords = []
    missing_keywords = []

    for keyword in expected_keywords:
        normalized_keyword = normalize_text(keyword)

        if normalized_keyword in combined_text:
            found_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    return {
        "keyword_pass": len(missing_keywords) == 0,
        "found_keywords": found_keywords,
        "missing_keywords": missing_keywords,
    }


def evaluate_retrieval_case(case: dict, pipeline: RetrievalPipeline) -> dict:
    results = pipeline.retrieve(
        query=case["query"],
        limit=5,
        hybrid_limit=20,
        dense_limit=30,
        bm25_limit=30,
        filters=case.get("filters"),
    )

    retrieved_sources = [
        result.metadata.get("source")
        for result in results
    ]

    retrieved_types = [
        result.metadata.get("document_type")
        for result in results
    ]

    source_pass = all(
        source in case["expected_sources"]
        for source in retrieved_sources
    )

    type_pass = all(
        doc_type in case["expected_document_types"]
        for doc_type in retrieved_types
    )

    keyword_report = check_expected_keywords(
        results=results,
        expected_keywords=case.get("expected_keywords", []),
    )

    return {
        "case_id": case["id"],
        "query": case["query"],
        "source_pass": source_pass,
        "type_pass": type_pass,
        "keyword_pass": keyword_report["keyword_pass"],
        "found_keywords": keyword_report["found_keywords"],
        "missing_keywords": keyword_report["missing_keywords"],
        "results": results,
    }


def print_retrieval_report(report: dict) -> None:
    print("=" * 100)
    print(f"CASE: {report['case_id']}")
    print(f"QUERY: {report['query']}")
    print("-" * 100)

    print(f"Source check: {report['source_pass']}")
    print(f"Document type check: {report['type_pass']}")
    print(f"Keyword check: {report['keyword_pass']}")
    print(f"Found keywords: {report['found_keywords']}")
    print(f"Missing keywords: {report['missing_keywords']}")

    print("\nRetrieved chunks:")
    for i, result in enumerate(report["results"], start=1):
        metadata = result.metadata

        print("-" * 100)
        print(f"[{i}]")
        print(f"Document: {metadata.get('document_name')}")
        print(f"Source: {metadata.get('source')}")
        print(f"Year: {metadata.get('year')}")
        print(f"Document type: {metadata.get('document_type')}")
        print(f"Chunk ID: {metadata.get('chunk_id')}")
        print(f"Reranker score: {metadata.get('reranker_score')}")
        print()
        print(result.text[:700].replace("\n", " "))
        print()


def main():
    test_answer = "Hello [1]. Another claim [2]."
    print(check_citations(test_answer))


if __name__ == "__main__":
    main()
