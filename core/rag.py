def simple_rag(query, document):
    if not document:
        return None

    return f"""
Use this document to answer:

DOCUMENT:
{document}

QUESTION:
{query}
"""