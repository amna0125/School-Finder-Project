"""Pure transformations. Raw strings and source flags are never overwritten."""
import hashlib
import json
import re


def numeric(raw):
    if raw is None or not re.fullmatch(r"-?\d+(?:[.,]\d+)?%?", str(raw)):
        return None
    return float(str(raw).rstrip("%").replace(",", "."))


def row_id(*parts):
    return hashlib.sha256(json.dumps(parts, ensure_ascii=False).encode()).hexdigest()


def statistics(payload, code, provenance):
    if payload.get("status") != "OK" or not isinstance(payload.get("body"), dict):
        raise ValueError("Invalid statistics response")
    body = payload["body"]
    if body.get("schoolUnit") != code:
        raise ValueError("Statistics school-unit mismatch")
    rows = []
    for metric, items in body.items():
        if metric in {"schoolUnit", "_links", "docLinks"}:
            continue
        if not isinstance(items, list):
            raise ValueError(f"Unexpected metric structure: {metric}")
        for index, item in enumerate(items or [{"valueType": "EMPTY_SOURCE_ARRAY"}]):
            flag = item.get("valueType")
            raw = item.get("value")
            rows.append({**provenance, "school_unit_code": code, "metric": metric,
                         "observation_index": index, "period": item.get("timePeriod"),
                         "raw_value": raw, "value_type": flag,
                         "numeric_value": numeric(raw) if flag == "EXISTS" else None,
                         "observation_json": json.dumps(item, ensure_ascii=False),
                         "row_id": row_id(code, metric, item.get("timePeriod"), index)})
    return rows


def surveys(payload, code, respondent, provenance):
    if payload.get("status") != "OK" or not isinstance(payload.get("body"), dict):
        raise ValueError("Invalid survey response")
    body = payload["body"]
    groups = body.get("schoolYearMetrics", []) if respondent == "pupils" else [body]
    rows = []
    for group in groups:
        if group.get("schoolUnitCode") != code:
            raise ValueError("Survey school-unit mismatch")
        context = {"school_unit_code": code, "respondent": respondent,
                   "semester": group.get("semester"), "year_group": group.get("schoolYear"),
                   "answers_raw": group.get("noOfAnswers"), "group_size_raw": group.get("noInGroup"),
                   "response_rate_raw": group.get("answeringFrequency")}
        for metric, fields in group.items():
            if not metric.endswith("Metrics") or not isinstance(fields, dict):
                continue
            for measure, raw in fields.items():
                if measure in {"questionDescription", "questionSubject"}:
                    continue
                value = numeric(raw)
                rows.append({**provenance, **context, "metric": metric, "measure": measure,
                             "question": fields.get("questionDescription"),
                             "subject": fields.get("questionSubject"), "raw_value": raw,
                             "numeric_value": value,
                             "unit": "percent" if str(raw).endswith("%") else "source_index_scale_unverified",
                             "value_status": "NULL_SOURCE" if raw is None else
                             "NUMERIC" if value is not None else "SOURCE_SYMBOL_UNRESOLVED",
                             "row_id": row_id(code, respondent, context["semester"], context["year_group"], metric, measure)})
    return rows


def school(payload, code, provenance):
    data = payload["data"]
    a = data["attributes"]
    if data["schoolUnitCode"] != code or "GR" not in a["schoolTypes"]:
        raise ValueError("Invalid school identity/type")
    if a.get("status") != "AKTIV" or not a.get("municipalityCode", "").startswith("01"):
        raise ValueError("School outside active Stockholm County sample")
    return {**provenance, "school_unit_code": code, "name": a.get("schoolName"),
            "municipality_code": a.get("municipalityCode"), "status": a.get("status"),
            "grades_json": json.dumps(a.get("schoolTypeProperties", {}).get("gr", {}).get("grades")),
            "website": a.get("url"), "source_extract_date": payload.get("meta", {}).get("extractDate")}
